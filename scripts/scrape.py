"""Ollama model scraper — fully automatic column discovery.

Two data sources are merged per version:
  1. Tags page info blob  → Size, Context, Input, Updated (classified by value pattern)
  2. Detail page metadata → any key-value pair whose label is a lowercase word
                            (arch, parameters, quantization, …) plus Capabilities
                            and Downloads count from page text.

No hardcoded field names or allowlists. New Ollama metadata fields appear
automatically in the CSV.
"""

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
# 0. LOGGING
# ==========================================
os.makedirs("logs", exist_ok=True)
_LOG_FILE = f"logs/ollama_scraper_{time.strftime('%Y%m%d_%H%M%S')}.log"

logger = logging.getLogger("OllamaScraper")
logger.setLevel(logging.DEBUG)
_fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(_fh)

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info("uvloop enabled.")
except ImportError:
    logger.info("uvloop not found; using standard asyncio.")


# ==========================================
# 1. TAGS PAGE PARSING (CPU-BOUND)
# ==========================================


def _classify_blob_segment(segment: str) -> tuple[str, str] | None:
    """Return (field_name, value) for a bullet-separated blob segment, or None to skip.

    Classification is purely pattern-based so it adapts when Ollama changes
    the value format — no hardcoded column positions.
    """
    s = " ".join(segment.split())  # collapse whitespace
    if not s or len(s) < 2:
        return None
    # SHA hash (12-64 hex chars) — skip
    if re.match(r"^[0-9a-f]{8,}$", s):
        return None
    # Version identifier model:tag — skip
    if re.match(r"^[\w.-]+:[\w.-]+$", s):
        return None
    # File size: 2.0GB, 581MB, 1.3GB
    m = re.match(r"^([\d.]+\s*(?:GB|MB|KB|TB))$", s, re.IGNORECASE)
    if m:
        return ("Size", m.group(1).upper().replace(" ", ""))
    # Context window: "128K context window", "128K", "32k"
    m = re.match(r"^([\d.]+\s*[KMGkmg])\s*(?:context\s+window)?$", s, re.IGNORECASE)
    if m:
        return ("Context", m.group(1).upper().replace(" ", ""))
    # Relative date: "1 year ago", "3 months ago", "2 weeks ago"
    if re.match(r"^\d+\s+\w+\s+ago$", s, re.IGNORECASE):
        return ("Updated", s)
    # Input type: "Text input", "Text & images input", "Image input"
    m = re.match(r"^(.+?)\s+input$", s, re.IGNORECASE)
    if m:
        return ("Input", m.group(1).strip().title())
    # Unknown — log for forward-compatibility inspection but do not store
    if len(s) > 3 and not re.match(r"^[0-9a-f]+$", s):
        logger.debug("Unclassified tags-blob segment: %r", s)
    return None


def parse_tags_page(
    html_bytes: bytes, model_href: str
) -> tuple[list[str], dict[str, dict]]:
    """Parse a /tags page.

    Returns:
        ordered_hrefs: version hrefs in page order (deduplicated).
        version_data:  {href: {field: value, …}} from info blobs.

    The info blob inside each version link is identified by the presence of '•'
    and a file-size pattern — no CSS class dependency.
    """
    html = html_bytes.decode("utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")
    v_pattern = re.compile(rf"^{re.escape(model_href)}:[^/]+$")

    version_data: dict[str, dict] = {}

    for a in soup.find_all("a", href=v_pattern):
        href = a["href"]
        if href in version_data:
            continue
        # Find the first span inside this anchor that looks like an info blob
        blob_text = ""
        for span in a.find_all("span"):
            text = span.get_text(separator=" ", strip=True)
            if "•" in text and re.search(
                r"\d+\.?\d*\s*(?:GB|MB|KB)", text, re.IGNORECASE
            ):
                blob_text = text
                break
        if not blob_text:
            version_data[href] = {}
            continue
        fields: dict[str, str] = {}
        for seg in re.split(r"[•·]", blob_text):
            result = _classify_blob_segment(seg)
            if result:
                key, val = result
                fields.setdefault(key, val)
        version_data[href] = fields

    ordered_hrefs = list(
        dict.fromkeys(a["href"] for a in soup.find_all("a", href=v_pattern))
    )
    return ordered_hrefs, version_data


# ==========================================
# 2. DETAIL PAGE PARSING (CPU-BOUND)
# ==========================================


def extract_detail_metadata(html_bytes: bytes) -> dict[str, str]:
    """Dynamically extract all metadata from a version detail page.

    Three discovery strategies — no hardcoded field names:

    1. Two-span containers whose first span is a lowercase label word →
       metadata pairs (arch/llama, parameters/3.21B, quantization/Q4_K_M, …).
       Label text becomes the field name (title-cased). Any new pair Ollama
       adds is captured automatically.

    2. Multi-span badge containers → Capabilities. Spans that look like
       parameter-size badges (1b, 3b, 70b) and quantization strings are
       excluded; remaining short alphabetic tokens are capabilities.

    3. Full page-text regex → Downloads count and Updated date.
    """
    html = html_bytes.decode("utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")
    features: dict[str, str] = {}

    # Strategy 1 — two-span containers for metadata key-value pairs
    # Structure: <div><span class="hidden sm:block">label</span><span>value</span></div>
    # Ollama hides metadata labels on mobile with Tailwind 'hidden sm:block'.
    # Capability badges (tools, vision) share the same 2-span pattern when paired
    # with a single version-size badge, but their label span has 'bg-indigo-50'
    # (not 'hidden') — requiring 'hidden' in the label class excludes them.
    for container in soup.find_all(["div", "li", "tr"]):
        spans = container.find_all("span", recursive=False)
        if len(spans) != 2:
            continue
        label_span, value_span = spans
        label = label_span.get_text(strip=True)
        value = value_span.get_text(strip=True)
        if not label or not value or label == value:
            continue
        # Label span must carry 'hidden' (Tailwind 'hidden sm:block') — this is
        # the structural marker Ollama uses for all metadata column labels.
        if "hidden" not in " ".join(label_span.get("class", [])):
            continue
        # Label must be lowercase alphabetic
        if not re.match(r"^[a-z][a-z\s\-]{0,29}$", label):
            continue
        features[label.title()] = value

    # Strategy 2 — indigo-colored badge spans for capabilities
    # Ollama uses indigo CSS color classes ('bg-indigo-50', 'text-indigo-600') on
    # capability badges ('tools', 'vision', 'embedding', …) and blue color classes
    # for version-size badges ('1b', '3b').  Matching on 'indigo' in the class
    # string is more reliable than structural heuristics because it is a deliberate
    # UI design choice — the color conveys semantic meaning.
    caps: set[str] = set()
    for span in soup.find_all("span"):
        classes = " ".join(span.get("class", []))
        if "indigo" not in classes:
            continue
        text = span.get_text(strip=True)
        if text and re.match(r"^[a-z][a-z\s]{1,24}$", text):
            caps.add(text.title())
    if caps:
        features["Capabilities"] = ", ".join(sorted(caps))

    # Strategy 3 — page-text patterns for stats that are not in structured markup
    page_text = soup.get_text(separator=" ")

    if "Downloads" not in features:
        m = re.search(
            r"([\d,.]+\s*[KMBTkmbt]?)\s+(?:Downloads|Pulls)",
            page_text,
            re.IGNORECASE,
        )
        if m:
            features["Downloads"] = m.group(1).strip().replace(",", "").upper()

    if "Updated" not in features:
        m = re.search(
            r"Updated\s+(\d+\s+\w+\s+ago|\w+\s+ago)", page_text, re.IGNORECASE
        )
        if m:
            features["Updated"] = m.group(1)

    return features


# ==========================================
# 3. ADAPTIVE NETWORK FETCHER
# ==========================================


class AdaptiveNetworkFetcher:
    """Throttles concurrency and backs off on 429 / 5xx responses."""

    def __init__(self, start_concurrency: int = 15, max_concurrency: int = 80) -> None:
        self.concurrency = start_concurrency
        self.max_concurrency = max_concurrency
        self.active_requests = 0
        self.lock = asyncio.Lock()

    async def _wait_for_capacity(self) -> None:
        while self.active_requests >= self.concurrency:
            await asyncio.sleep(0.01)

    async def fetch(
        self,
        session: aiohttp.ClientSession,
        url: str,
        params: dict | None = None,
        retries: int = 4,
    ) -> bytes | None:
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
                        content = await response.read()
            except asyncio.TimeoutError:
                status = 504
                logger.debug("Timeout on %s (attempt %d)", url, attempt + 1)
            except Exception as exc:
                status = 500
                logger.debug("Network error on %s: %r", url, exc)
            finally:
                async with self.lock:
                    self.active_requests -= 1
                    if status == 200:
                        self.concurrency = min(
                            self.max_concurrency, self.concurrency + 2
                        )
                    elif status == 429:
                        self.concurrency = max(5, self.concurrency // 2)
                        logger.warning(
                            "Rate limited (429) on %s. concurrency → %d",
                            url,
                            self.concurrency,
                        )
            if content:
                return content
            if status == 429 or status >= 500:
                await asyncio.sleep(1.5**attempt)
            else:
                break
        logger.error("Failed to fetch %s after %d attempts.", url, retries)
        return None


# ==========================================
# 4. ORCHESTRATION
# ==========================================


async def get_model_links(
    fetcher: AdaptiveNetworkFetcher,
    session: aiohttp.ClientSession,
    page: int,
) -> list[str]:
    content = await fetcher.fetch(
        session, "https://ollama.com/library", params={"page": page}
    )
    if not content:
        return []
    soup = BeautifulSoup(content.decode("utf-8", errors="replace"), "lxml")
    return [
        link["href"]
        for link in soup.find_all("a", href=re.compile(r"^/library/[^/]+$"))
    ]


async def get_tags_and_metadata(
    fetcher: AdaptiveNetworkFetcher,
    session: aiohttp.ClientSession,
    model_href: str,
) -> tuple[list[str], dict[str, dict]]:
    """Fetch /tags page; return (ordered version hrefs, per-version blob metadata)."""
    content = await fetcher.fetch(session, f"https://ollama.com{model_href}/tags")
    if not content:
        return [model_href], {}
    hrefs, tags_meta = parse_tags_page(content, model_href)
    return (hrefs if hrefs else [model_href]), tags_meta


async def scrape_version(
    fetcher: AdaptiveNetworkFetcher,
    session: aiohttp.ClientSession,
    process_pool: concurrent.futures.ProcessPoolExecutor,
    v_href: str,
    model_name: str,
    tags_meta: dict[str, dict],
    global_features: set[str],
    all_rows: list[dict],
) -> None:
    url = f"https://ollama.com{v_href}"
    content = await fetcher.fetch(session, url)
    if not content:
        return

    version = v_href.split(":")[-1] if ":" in v_href else "latest"
    loop = asyncio.get_running_loop()
    try:
        detail = await loop.run_in_executor(
            process_pool, extract_detail_metadata, content
        )
        row: dict[str, str] = {"Model Name": model_name, "Version": version, "URL": url}
        # Tags page blob data first; detail page data overwrites on collision
        # (detail page is more authoritative for version-specific fields).
        for key, val in tags_meta.get(v_href, {}).items():
            row[key] = val
            global_features.add(key)
        for key, val in detail.items():
            row[key] = val
            global_features.add(key)
        all_rows.append(row)
        logger.debug("Processed: %s:%s", model_name, version)
    except Exception as exc:
        logger.error("Parsing failed for %s: %r", url, exc)


# ==========================================
# 5. MAIN
# ==========================================


async def main() -> None:
    start_time = time.time()
    all_rows: list[dict] = []
    global_features: set[str] = set()

    fetcher = AdaptiveNetworkFetcher(start_concurrency=15, max_concurrency=80)
    cpu_cores = max(1, multiprocessing.cpu_count() - 1)

    logger.info("Engine Active: %d CPU Workers", cpu_cores)
    print(f"\nEngine Active: {cpu_cores} CPU Workers | Logs → {_LOG_FILE}")

    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_cores) as process_pool:
        connector = aiohttp.TCPConnector(limit=150)
        async with aiohttp.ClientSession(
            connector=connector,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            },
        ) as session:

            # Phase 1 — discover base model hrefs
            logger.info("Phase 1: Discovering Base Models...")
            # Ollama currently has ~30 pages; 60 is a safe upper bound
            page_tasks = [get_model_links(fetcher, session, p) for p in range(1, 61)]
            page_results = await tqdm_asyncio.gather(
                *page_tasks, desc="Scanning Pages", leave=True
            )
            # dict.fromkeys: ordered deduplication
            model_href_list = list(
                dict.fromkeys(href for sublist in page_results for href in sublist)
            )
            logger.info("Discovered %d Base Models.", len(model_href_list))

            # Phase 2 — expand version tags AND collect tags-page blob metadata
            logger.info("Phase 2: Expanding Version Tags...")
            tag_tasks = [
                get_tags_and_metadata(fetcher, session, href)
                for href in model_href_list
            ]
            tags_results: list[tuple[list[str], dict]] = await tqdm_asyncio.gather(
                *tag_tasks, desc="Fetching Tags", leave=True
            )

            # Build version task list; zip ensures model_href_list[i] aligns with tags_results[i]
            version_tasks = []
            for href, (versions, tags_meta) in zip(model_href_list, tags_results):
                model_name = href.split("/")[-1]
                for v_href in versions:
                    version_tasks.append(
                        scrape_version(
                            fetcher,
                            session,
                            process_pool,
                            v_href,
                            model_name,
                            tags_meta,
                            global_features,
                            all_rows,
                        )
                    )

            # Phase 3 — scrape all version detail pages
            logger.info("Phase 3: Scraping %d versions...", len(version_tasks))
            await tqdm_asyncio.gather(*version_tasks, desc="Parsing HTML", leave=True)

    if not all_rows:
        logger.error("No records collected — CSV not written.")
        print("\nERROR: No records collected.")
        return

    # Priority columns appear first; all dynamically discovered columns follow.
    priority_cols = [
        "Model Name",
        "Version",
        "Parameters",
        "Context",
        "Quantization",
        "Size",
        "Input",
        "Downloads",
        "Updated",
        "Capabilities",
        "Arch",
        "URL",
    ]
    dynamic_cols = sorted(f for f in global_features if f not in priority_cols)
    final_columns = priority_cols + dynamic_cols

    csv_filename = "ollama_master_db.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=final_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    elapsed = time.time() - start_time
    msg = f"SUCCESS! {len(all_rows)} records in {elapsed:.1f}s"
    logger.info(msg)
    print(f"\n{msg}")
    print(f"CSV  → {csv_filename}")
    print(f"Logs → {_LOG_FILE}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    asyncio.run(main())
