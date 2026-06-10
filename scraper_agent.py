import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def scrape_page(url: str) -> dict:

    print("[SCRAPER] Fetching:", url)

    try:

        r = requests.get(url, headers=HEADERS, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.text.strip() if soup.title else ""

        headings = [
            h.get_text(strip=True)
            for h in soup.find_all(["h1", "h2", "h3"])
        ]

        paragraphs = [
            p.get_text(strip=True)
            for p in soup.find_all("p")
            if len(p.get_text(strip=True)) > 40
        ]

        links = [
            a.get("href")
            for a in soup.find_all("a")
            if a.get("href") and a.get("href").startswith("http")
        ]

        return {
            "url": url,
            "title": title,
            "headings": headings[:15],
            "paragraphs": paragraphs[:20],
            "links": links[:20]
        }

    except Exception as e:

        print("[SCRAPER ERROR]", url, e)

        return {
            "url": url,
            "title": "",
            "headings": [],
            "paragraphs": [],
            "links": []
        }