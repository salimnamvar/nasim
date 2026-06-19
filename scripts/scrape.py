import asyncio
import concurrent.futures
import csv
import logging
import multiprocessing
import os
import re
import time

import aiohttp
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm_asyncio

# ==========================================
# 0. LOGGING INFRASTRUCTURE
# ==========================================
os.makedirs("log", exist_ok=True)
log_filename = f"log/ollama_scraper_{time.strftime('%Y%m%d_%H%M%S')}.log"

logger = logging.getLogger("OllamaScraper")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(file_handler)

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info("uvloop enabled for high-performance Async I/O.")
except ImportError:
    logger.info("uvloop not found, using standard asyncio.")


# ==========================================
# 1. CONSTANTS
# ==========================================
# Strict allowlist — only known Ollama capability badges.
# The heuristic approach caught Python code keywords (Await, Const, From, Import, Print)
# visible in page code examples. An allowlist is the only safe filter.
_CAPABILITIES_ALLOWLIST = frozenset([
    "Audio",
    "Chat",
    "Code",
    "Embedding",
    "Instruct",
    "Multimodal",
    "Reasoning",
    "Thinking",
    "Tools",
    "Video",
    "Vision",
])

_VALID_CONTAINER_KEYS = frozenset([
    "Arch",
    "Architecture",
    "Context",
    "Family",
    "Parameters",
    "Quantization",
    "Size",
    "Usage",
])


# ==========================================
# 2. CPU-BOUND HTML PARSING (MULTIPROCESSING)
# ==========================================
def extract_dynamic_features(html_bytes):
    """Parse raw HTML bytes into structured columns.

    Accepts bytes (not str) so the caller can pass response.read() directly.
    Decodes with errors='replace' to handle non-UTF-8 pages (e.g. glm4, codegeex4).
    """
    html_content = html_bytes.decode("utf-8", errors="replace")
    soup = BeautifulSoup(html_content, "lxml")
    features = {}

    # Strict key-value parsing from definition lists
    for dt in soup.find_all("dt"):
        dd = dt.find_next_sibling("dd")
        if dd:
            key = dt.text.strip().title()
            val = dd.text.strip()
            if re.match(r"^[A-Za-z\s]+$", key) and len(key) < 30:
                features[key] = val

    # Two-child containers (label + value pairs)
    for container in soup.find_all(["div", "li"]):
        children = container.find_all(["div", "span", "p"], recursive=False)
        if len(children) == 2:
            t1 = children[0].text.strip()
            t2 = children[1].text.strip()
            if t1.title() in _VALID_CONTAINER_KEYS:
                features[t1.title()] = t2
            elif t2.title() in _VALID_CONTAINER_KEYS:
                features[t2.title()] = t1

    page_text = soup.get_text(separator=" ")

    # Pulls count (e.g. "1.2M Pulls")
    pulls_match = re.search(r"([\d\.]+[KMBTkmbt]?)\s+Pulls", page_text, re.IGNORECASE)
    if pulls_match:
        features["Pulls"] = pulls_match.group(1).upper()

    # Updated date (e.g. "Updated 3 months ago")
    updated_match = re.search(r"Updated\s+(.*?ago)", page_text, re.IGNORECASE)
    if updated_match:
        features["Date / Updated"] = updated_match.group(1)

    # File size from page text (e.g. "4.7 GB") when not already captured above
    if "Size" not in features:
        size_match = re.search(r"(\d+\.?\d*\s*(?:GB|MB|KB))", page_text, re.IGNORECASE)
        if size_match:
            features["Size"] = size_match.group(1).upper().replace(" ", "")

    # Span badge classification
    capabilities = set()
    for span in soup.find_all("span"):
        text = span.get_text(strip=True)
        if not text:
            continue

        # Parameter sizes: 8B, 70B, 0.5B, 235B
        if re.match(r"^[\d\.]+[bmtBMT]$", text):
            if "Parameters" not in features:
                features["Parameters"] = text.upper()
            continue

        # Context windows: 128K, 32K
        if re.match(r"^[\d\.]+[kK]$", text):
            if "Context" not in features:
                features["Context"] = text.upper()
            continue

        # Quantization strings: q4_0, q8_k_m, F16
        if re.match(r"^q\d_[A-Za-z0-9_]+$", text, re.IGNORECASE):
            if "Quantization" not in features:
                features["Quantization"] = text.lower()
            continue

        # Capabilities — strict allowlist only; never heuristic
        if text.title() in _CAPABILITIES_ALLOWLIST:
            capabilities.add(text.title())

    if capabilities:
        features["Capabilities"] = ", ".join(sorted(capabilities))

    return features


# ==========================================
# 3. ADAPTIVE NETWORK FETCHER
# ==========================================
class AdaptiveNetworkFetcher:
    """Throttles concurrency and backs off on 429 / 5xx responses."""

    def __init__(self, start_concurrency=15, max_concurrency=80):
        self.concurrency = start_concurrency
        self.max_concurrency = max_concurrency
        self.active_requests = 0
        self.lock = asyncio.Lock()

    async def _wait_for_capacity(self):
        while self.active_requests >= self.concurrency:
            await asyncio.sleep(0.01)

    async def fetch(self, session, url, params=None, retries=4):
        """Return raw bytes on success, None after all retries are exhausted."""
        timeout = aiohttp.ClientTimeout(total=20)

        for attempt in range(retries):
            await self._wait_for_capacity()
            async with self.lock:
                self.active_requests += 1

            status = 0
            content = None
            try:
                async with session.get(url, params=params, timeout=timeout) as response:
                    status = response.status
                    if status == 200:
                        # Read bytes — avoids codec errors on non-UTF-8 pages
                        content = await response.read()
            except asyncio.TimeoutError:
                status = 504
                logger.debug(f"Timeout on {url} (attempt {attempt + 1})")
            except Exception as e:
                status = 500
                logger.debug(f"Network error on {url}: {e!r}")
            finally:
                async with self.lock:
                    self.active_requests -= 1
                    if status == 200:
                        self.concurrency = min(self.max_concurrency, self.concurrency + 2)
                    elif status == 429:
                        self.concurrency = max(5, self.concurrency // 2)
                        logger.warning(
                            f"Rate limited (429) on {url}. concurrency → {self.concurrency}"
                        )

            if content:
                return content
            if status == 429 or status >= 500:
                await asyncio.sleep(1.5 ** attempt)
            else:
                break

        logger.error(f"Failed to fetch {url} after {retries} attempts.")
        return None


# ==========================================
# 4. CORE ORCHESTRATION
# ==========================================
async def get_model_links(fetcher, session, page):
    content = await fetcher.fetch(session, "https://ollama.com/library", params={"page": page})
    if not content:
        return []
    soup = BeautifulSoup(content.decode("utf-8", errors="replace"), "lxml")
    return [
        link["href"]
        for link in soup.find_all("a", href=re.compile(r"^/library/[^/]+$"))
    ]


async def get_version_links(fetcher, session, model_href):
    content = await fetcher.fetch(session, f"https://ollama.com{model_href}/tags")
    if not content:
        return [model_href]
    soup = BeautifulSoup(content.decode("utf-8", errors="replace"), "lxml")
    # re.escape prevents regex injection for model names with special chars
    pattern = re.compile(rf"^{re.escape(model_href)}:[^/]+$")
    links = list(set(t["href"] for t in soup.find_all("a", href=pattern)))
    return links if links else [model_href]


async def scrape_version(fetcher, session, process_pool, v_href, model_name, global_features, all_rows):
    url = f"https://ollama.com{v_href}"
    content = await fetcher.fetch(session, url)
    if not content:
        return

    version = v_href.split(":")[-1] if ":" in v_href else "latest"
    loop = asyncio.get_running_loop()
    try:
        dynamic_features = await loop.run_in_executor(process_pool, extract_dynamic_features, content)
        row_data = {"Model Name": model_name, "Version": version, "URL": url}
        for key, val in dynamic_features.items():
            row_data[key] = val
            global_features.add(key)
        all_rows.append(row_data)
        logger.debug(f"Processed: {model_name}:{version}")
    except Exception as e:
        logger.error(f"Parsing failed for {url}: {e!r}")


# ==========================================
# 5. MAIN EXECUTION
# ==========================================
async def main():
    start_time = time.time()
    all_rows = []
    global_features = set()

    fetcher = AdaptiveNetworkFetcher(start_concurrency=15, max_concurrency=80)
    cpu_cores = max(1, multiprocessing.cpu_count() - 1)

    logger.info(f"Engine Active: {cpu_cores} CPU Workers")
    print(f"\nEngine Active: {cpu_cores} CPU Workers | Logs → {log_filename}")

    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_cores) as process_pool:
        connector = aiohttp.TCPConnector(limit=150)
        async with aiohttp.ClientSession(
            connector=connector,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"},
        ) as session:

            # Phase 1: discover base model hrefs
            logger.info("Phase 1: Discovering Base Models...")
            # Ollama has ~30 pages; 60 is a safe upper bound without wasting 120 requests
            page_tasks = [get_model_links(fetcher, session, p) for p in range(1, 61)]
            page_results = await tqdm_asyncio.gather(*page_tasks, desc="Scanning Pages", leave=True)

            # dict.fromkeys preserves insertion order and deduplicates
            model_href_list = list(dict.fromkeys(
                href for sublist in page_results for href in sublist
            ))
            logger.info(f"Discovered {len(model_href_list)} Base Models.")

            # Phase 2: expand version tags
            logger.info("Phase 2: Expanding Version Tags...")
            tag_tasks = [get_version_links(fetcher, session, href) for href in model_href_list]
            tags_results = await tqdm_asyncio.gather(*tag_tasks, desc="Fetching Tags", leave=True)

            # zip ensures model_href_list[i] and tags_results[i] always align
            version_tasks = []
            for href, versions in zip(model_href_list, tags_results):
                model_name = href.split("/")[-1]
                for v_href in versions:
                    version_tasks.append(
                        scrape_version(
                            fetcher, session, process_pool,
                            v_href, model_name, global_features, all_rows,
                        )
                    )

            # Phase 3: scrape all versions in parallel
            logger.info(f"Phase 3: Scraping {len(version_tasks)} versions...")
            await tqdm_asyncio.gather(*version_tasks, desc="Parsing HTML", leave=True)

    # ==========================================
    # 6. DATA EXPORT
    # ==========================================
    if all_rows:
        fixed_cols = [
            "Model Name",
            "Version",
            "Parameters",
            "Context",
            "Quantization",
            "Size",
            "Pulls",
            "Date / Updated",
            "Capabilities",
            "URL",
        ]
        dynamic_cols = sorted(f for f in global_features if f not in fixed_cols)
        final_columns = fixed_cols + dynamic_cols

        csv_filename = "ollama_master_db.csv"
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
            # extrasaction="ignore" silently drops any unexpected keys
            writer = csv.DictWriter(f, fieldnames=final_columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_rows)

        elapsed = time.time() - start_time
        msg = f"SUCCESS! {len(all_rows)} records in {elapsed:.1f}s"
        logger.info(msg)
        print(f"\n{msg}")
        print(f"CSV  → {csv_filename}")
        print(f"Logs → {log_filename}")
    else:
        logger.error("No records collected — CSV not written.")
        print("\nERROR: No records collected.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    asyncio.run(main())
