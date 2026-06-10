from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen2.5-coder",
    temperature=0
)


def summarize(page: dict) -> dict:

    print("[SUMMARY] Processing:", page["url"])

    try:

        prompt = f"""
You are a research summarizer.

Extract key insights from this page.

URL:
{page["url"]}

TITLE:
{page["title"]}

HEADINGS:
{page["headings"]}

CONTENT:
{page["paragraphs"]}

Return a clear structured summary.
"""

        response = llm.invoke(prompt)

        result = {
            "url": page["url"],
            "title": page["title"],
            "summary": response.content.strip()
        }

        # 🔥 CRITICAL DEBUG
        print("[SUMMARY] Output length:", len(result["summary"]))

        return result

    except Exception as e:

        print("[SUMMARY ERROR]", e)

        return {
            "url": page["url"],
            "title": page["title"],
            "summary": "ERROR_GENERATING_SUMMARY"
        }