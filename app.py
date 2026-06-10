from url_agent import get_urls
from audit_agent import audit_urls


query = """
Find sites with information about
LangGraph and Ollama
"""


urls = get_urls(query)

print("\nURL AGENT RESULTS")
print("=" * 50)

for url in urls:

    print(url)


audit_results = audit_urls(
    urls
)

print("\nAUDIT RESULTS")
print("=" * 50)

for item in audit_results:

    print(item)