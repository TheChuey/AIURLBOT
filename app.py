from url_agent import get_urls
from audit_agent import audit_urls
from scraper_agent import scrape_page
from summary_agent import summarize
from report_writer import build_markdown_report, save_markdown

# ============================================================
# INPUT
# ============================================================

query = "top ai agents for small business 2026"


# ============================================================
# STEP 1 - URL COLLECTION
# ============================================================

urls = get_urls(query)

print("\nURLS FOUND")
print("=" * 50)

for u in urls:
    print(u)


# ============================================================
# STEP 2 - AUDIT FILTERING
# ============================================================

audit_results = audit_urls(urls)

keep_urls = [
    r["url"]
    for r in audit_results
    if r["status"] == "KEEP"
]


print("\nKEEP URLS")
print("=" * 50)

for u in keep_urls:
    print(u)


# ============================================================
# STEP 3 - SCRAPE + SUMMARIZE
# ============================================================

final_output = []

for url in keep_urls:

    print("\n[PIPELINE] Processing URL:", url)

    page = scrape_page(url)

    print("[PIPELINE] Scraped OK")

    summary = summarize(page)

    print("[PIPELINE] Summary OK")

    final_output.append(summary)

# ============================================================
# STEP 4 - BUILD REPORT
# ============================================================

markdown_report = build_markdown_report(final_output)

print("\n\n===== PREVIEW REPORT =====\n")
print(markdown_report[:1000])  # preview only


# ============================================================
# SAVE PROMPT
# ============================================================

choice = input("\nWould you like to save this report? (y/n): ").strip().lower()

if choice == "y":

    filename = input("Enter filename (default: report.md): ").strip()

    if not filename:
        filename = "report.md"

    save_markdown(markdown_report, filename)

else:
    print("[REPORT] Not saved")
    
# ============================================================
# FINAL OUTPUT
# ============================================================

print("\nFINAL KNOWLEDGE BASE")
print("=" * 50)

for item in final_output:

    print("\nURL:", item["url"])
    print("TITLE:", item["title"])
    print("SUMMARY:\n", item["summary"])
    
print("\nDEBUG FINAL OUTPUT LENGTH:", len(final_output))

for i, item in enumerate(final_output):
    print("\nITEM", i)
    print(item)
keep_urls = [r["url"] for r in audit_results]

print("\n[DEBUG] BYPASS AUDIT MODE ACTIVE")
print("Using all URLs for scraping")