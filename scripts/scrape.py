import asyncio
import concurrent.futures
import csv
import logging
import multiprocessing
import os
import re
import sys
import time

import aiohttp
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm_asyncio

# ==========================================
# 0. LOGGING INFRASTRUCTURE
# ==========================================
os.makedirs("log", exist_ok=True)
log_filename = f"log/ollama_scraper_{time.strftime('%Y%m%d_%H%M%S')}.log"

# Setup Logger
logger = logging.getLogger("OllamaScraper")
logger.setLevel(logging.DEBUG)

# File Handler (Detailed Logging)
file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
file_handler.setFormatter(file_fmt)
logger.addHandler(file_handler)

# Optional: Fast I/O on Linux
try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info("uvloop enabled for high-performance Async I/O.")
except ImportError:
    logger.info("uvloop not found, using standard asyncio.")


# ==========================================
# 1. CPU-BOUND HTML PARSING (MULTIPROCESSING)
# ==========================================
def extract_dynamic_features(html_content):
    """Parses HTML and classifies badges/text into strict, clean columns."""
    soup = BeautifulSoup(html_content, "lxml")
    features = {}

    # 1. Strict Key-Value parsing
    for dt in soup.find_all("dt"):
        dd = dt.find_next_sibling("dd")
        if dd:
            key = dt.text.strip().title()
            val = dd.text.strip()
            # Only accept alphabetical keys to prevent "8B" from becoming a column
            if re.match(r"^[A-Za-z\s]+$", key) and len(key) < 30:
                features[key] = val

    for container in soup.find_all(["div", "li"]):
        children = container.find_all(["div", "span", "p"], recursive=False)
        if len(children) == 2:
            t1 = children[0].text.strip()
            t2 = children[1].text.strip()

            # Map known attributes safely, preventing flipped keys/values
            valid_keys = [
                "Architecture",
                "Parameters",
                "Size",
                "Context",
                "Quantization",
                "Family",
                "Usage",
                "Arch",
            ]
            if t1.title() in valid_keys:
                features[t1.title()] = t2
            elif t2.title() in valid_keys:
                features[t2.title()] = t1

    page_text = soup.get_text(separator=" ")

    # Extract Pulls and Updated Dates
    pulls_match = re.search(r"([\d\.]+[KMBTkmbt]?)\s+Pulls", page_text, re.IGNORECASE)
    if pulls_match:
        features["Pulls"] = pulls_match.group(1).upper()

    updated_match = re.search(r"Updated\s+(.*?ago)", page_text, re.IGNORECASE)
    if updated_match:
        features["Date / Updated"] = updated_match.group(1)

    # 2. Strict Metadata Classifier for Floating Badges
    capabilities = set()
    for span in soup.find_all("span"):
        text = span.get_text(strip=True)
        if not text:
            continue

        # Route Parameter Sizes (e.g., 05B, 8B, 104T) -> 'Parameters'
        if re.match(r"^[\d\.]+[bmtBMT]$", text):
            if "Parameters" not in features:
                features["Parameters"] = text.upper()
            continue

        # Route Context Windows (e.g., 128K, 32K) -> 'Context'
        if re.match(r"^[\d\.]+[kK]$", text):
            if "Context" not in features:
                features["Context"] = text.upper()
            continue

        # Route Quantization (e.g., q4_0, q8_k_m) -> 'Quantization'
        if re.match(r"^q\d_[A-Za-z0-9_]+$", text, re.IGNORECASE):
            if "Quantization" not in features:
                features["Quantization"] = text.lower()
            continue

        # Route Capabilities (e.g., Tools, Vision) -> 'Capabilities'
        if text.isalpha() and 2 < len(text) <= 15:
            lower_text = text.lower()
            ignore_list = [
                "new",
                "pulls",
                "tags",
                "models",
                "library",
                "download",
                "copy",
                "ago",
                "updated",
                "log",
                "in",
                "sign",
                "search",
                "blob",
                "size",
                "architecture",
            ]
            if lower_text not in ignore_list:
                capabilities.add(text.title())

    if capabilities:
        features["Capabilities"] = ", ".join(sorted(capabilities))

    return features


# ==========================================
# 2. AGGRESSIVE NETWORK TUNER
# ==========================================
class AdaptiveNetworkFetcher:
    def __init__(self, start_concurrency=50, max_concurrency=250):
        self.concurrency = start_concurrency
        self.max_concurrency = max_concurrency
        self.active_requests = 0
        self.lock = asyncio.Lock()

    async def wait_for_capacity(self):
        while self.active_requests >= self.concurrency:
            await asyncio.sleep(0.01)

    async def fetch(self, session, url, params=None, retries=3):
        for attempt in range(retries):
            await self.wait_for_capacity()
            async with self.lock:
                self.active_requests += 1

            status = 0
            html = None
            try:
                async with session.get(url, params=params, timeout=12) as response:
                    status = response.status
                    if status == 200:
                        html = await response.text()
            except Exception as e:
                status = 500
                logger.debug(f"Network error on {url}: {str(e)}")
            finally:
                async with self.lock:
                    self.active_requests -= 1
                    if status == 200:
                        self.concurrency = min(
                            self.max_concurrency, self.concurrency + 2
                        )
                    elif status == 429:
                        self.concurrency = max(10, self.concurrency // 2)
                        logger.warning(
                            f"Rate limited (429) on {url}. Reducing concurrency to {self.concurrency}."
                        )

            if html:
                return html
            elif status == 429 or status >= 500:
                await asyncio.sleep(1.5**attempt)
            else:
                break

        logger.error(f"Failed to fetch {url} after {retries} attempts.")
        return None


# ==========================================
# 3. CORE ORCHESTRATION LOGIC
# ==========================================
async def get_model_links(fetcher, session, page):
    html = await fetcher.fetch(
        session, "https://ollama.com/library", params={"page": page}
    )
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    return [
        link["href"]
        for link in soup.find_all("a", href=re.compile(r"^/library/[^/]+$"))
    ]


async def get_version_links(fetcher, session, model_href):
    html = await fetcher.fetch(session, f"https://ollama.com{model_href}/tags")
    if not html:
        return [model_href]
    soup = BeautifulSoup(html, "lxml")
    links = list(
        set(
            [
                t["href"]
                for t in soup.find_all("a", href=re.compile(rf"^{model_href}:[^/]+$"))
            ]
        )
    )
    return links if links else [model_href]


async def scrape_version(
    fetcher, session, process_pool, v_href, model_name, global_features, all_rows
):
    url = f"https://ollama.com{v_href}"
    html = await fetcher.fetch(session, url)
    if not html:
        return

    version = v_href.split(":")[-1] if ":" in v_href else "latest"
    loop = asyncio.get_running_loop()

    try:
        dynamic_features = await loop.run_in_executor(
            process_pool, extract_dynamic_features, html
        )
        row_data = {"Model Name": model_name, "Version": version, "URL": url}

        for key, val in dynamic_features.items():
            row_data[key] = val
            global_features.add(key)

        all_rows.append(row_data)
        logger.debug(f"Successfully processed: {model_name}:{version}")
    except Exception as e:
        logger.error(f"Parsing failed for {url}: {str(e)}")


# ==========================================
# 4. MAIN EXECUTION
# ==========================================
async def main():
    start_time = time.time()
    all_rows = []
    global_features = set()

    fetcher = AdaptiveNetworkFetcher(start_concurrency=50, max_concurrency=200)
    cpu_cores = max(1, multiprocessing.cpu_count() - 1)

    logger.info(f"Engine Active: {cpu_cores} CPU Workers")
    print(
        f"\n🚀 Engine Active: {cpu_cores} CPU Workers | Logs writing to: {log_filename}"
    )

    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_cores) as process_pool:
        connector = aiohttp.TCPConnector(limit=300)
        async with aiohttp.ClientSession(
            connector=connector, headers={"User-Agent": "Mozilla/5.0"}
        ) as session:

            # Phase 1
            logger.info("Phase 1: Discovering Base Models...")
            page_tasks = [get_model_links(fetcher, session, p) for p in range(1, 150)]
            page_results = await tqdm_asyncio.gather(
                *page_tasks, desc="Scanning Registry Pages", leave=True
            )

            model_urls = set([url for sublist in page_results for url in sublist])
            logger.info(f"Discovered {len(model_urls)} Base Models.")

            # Phase 2
            logger.info("Phase 2: Expanding Version Tags...")
            tag_tasks = [
                get_version_links(fetcher, session, href) for href in model_urls
            ]
            tags_results = await tqdm_asyncio.gather(
                *tag_tasks, desc="Fetching Version Tags", leave=True
            )

            version_tasks = []
            for i, versions in enumerate(tags_results):
                model_name = list(model_urls)[i].split("/")[-1]
                for v_href in versions:
                    version_tasks.append(
                        scrape_version(
                            fetcher,
                            session,
                            process_pool,
                            v_href,
                            model_name,
                            global_features,
                            all_rows,
                        )
                    )

            # Phase 3
            logger.info(f"Phase 3: Parallel Scraping {len(version_tasks)} models...")
            await tqdm_asyncio.gather(
                *version_tasks, desc="Parsing HTML Data", leave=True
            )

    # ==========================================
    # 5. DATA EXPORT
    # ==========================================
    if all_rows:
        # Standardize known columns to be at the front
        fixed_cols = [
            "Model Name",
            "Version",
            "Parameters",
            "Context",
            "Quantization",
            "Size",
            "Capabilities",
            "URL",
        ]
        dynamic_cols = sorted([f for f in global_features if f not in fixed_cols])
        final_columns = fixed_cols + dynamic_cols

        csv_filename = "ollama_master_db.csv"
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=final_columns)
            writer.writeheader()
            writer.writerows(all_rows)

        completion_msg = f"SUCCESS! Completed {len(all_rows)} records in {time.time() - start_time:.2f}s"
        logger.info(completion_msg)
        print(f"\n✅ {completion_msg}")
        print(f"💾 Saved data to {csv_filename}")
        print(f"📝 Logs saved to {log_filename}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    asyncio.run(main())
