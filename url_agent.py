from ddgs import DDGS
from typing import List
from urllib.parse import urlparse


# ============================================================
# VALIDATION HELPERS
# ============================================================

def is_valid_url(url: str) -> bool:
    """
    Ensures only usable HTTP/HTTPS URLs are returned.
    """

    if not url:
        return False

    parsed = urlparse(url)

    return parsed.scheme in ("http", "https")


# ============================================================
# MAIN FUNCTION
# ============================================================

def get_urls(query: str) -> List[str]:
    """
    Input:
        query (str): user search query

    Process:
        - Runs DuckDuckGo search
        - Extracts URLs safely
        - Filters invalid or empty results
        - Removes duplicates

    Output:
        List[str]: clean working URLs
    """

    print("\n[URL AGENT] Searching query:", query)

    urls = []

    try:

        with DDGS() as ddgs:

            results = ddgs.text(query, max_results=10)

            for r in results:

                # ------------------------------------------------
                # SAFE EXTRACTION (handles API variations)
                # ------------------------------------------------
                url = r.get("href") or r.get("url")

                if not url:
                    continue

                if is_valid_url(url):
                    urls.append(url)

        # remove duplicates while preserving order
        seen = set()
        clean_urls = []

        for u in urls:
            if u not in seen:
                seen.add(u)
                clean_urls.append(u)

        print(f"[URL AGENT] Raw results: {len(urls)}")
        print(f"[URL AGENT] Clean URLs: {len(clean_urls)}")

        return clean_urls

    except Exception as e:

        print("[URL AGENT ERROR]", str(e))

        return []