"""
AI Research Pipeline V2
Class-based LangGraph research workflow.
"""

from datetime import datetime
from typing import TypedDict, List
import json
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

# ============================================================
# GLOBAL VARIABLES
# ============================================================

SEARCH_QUERY = "top ai agents for small business 2026"
MODEL_NAME = "qwen2.5-coder"
TEMPERATURE = 0.0
MAX_SEARCH_RESULTS = 5
HTTP_TIMEOUT = 15
REPORT_FILENAME = "research_report.md"
JOURNAL_FILENAME = "research_journal.json"

# ============================================================
# STATE
# ============================================================

class PipelineState(TypedDict):
    query: str
    urls: List[str]
    pages: List[dict]
    audited_pages: List[dict]
    summaries: List[dict]
    report: str

# ============================================================
# AGENTS
# ============================================================

class SearchAgent:
    """Find URLs related to a query."""

    def run(self, query: str):
        urls = []
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=MAX_SEARCH_RESULTS):
                href = item.get("href")
                if href:
                    urls.append(href)
        return list(dict.fromkeys(urls))

class ScraperAgent:
    """Download and clean webpage content."""

    def run(self, url: str):
        try:
            r = requests.get(url, timeout=HTTP_TIMEOUT)
            soup = BeautifulSoup(r.text, "html.parser")

            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            title = soup.title.text.strip() if soup.title else ""
            content = soup.get_text(" ", strip=True)

            return {
                "url": url,
                "title": title,
                "content": content[:10000]
            }
        except Exception as e:
            return {
                "url": url,
                "title": "",
                "content": "",
                "error": str(e)
            }

class AuditAgent:
    """Decide if content should be kept."""

    def __init__(self, llm):
        self.llm = llm

    def run(self, page):
        prompt = f"""
Return JSON only.

{{
 "status":"KEEP",
 "confidence_score":0.95,
 "reason":"why"
}}

TITLE:
{page['title']}

CONTENT:
{page['content'][:3000]}
"""
        try:
            response = self.llm.invoke(prompt).content
            start = response.find("{")
            end = response.rfind("}") + 1
            data = json.loads(response[start:end])

            score = float(data.get("confidence_score", 0.5))
            if score > 1:
                score = score / 100

            return {
                "status": data.get("status", "KEEP"),
                "confidence_score": score,
                "reason": data.get("reason", "")
            }
        except Exception:
            return {
                "status": "KEEP",
                "confidence_score": 0.5,
                "reason": "Fallback decision"
            }

class SummaryAgent:
    """Create article summaries."""

    def __init__(self, llm):
        self.llm = llm

    def run(self, page):
        prompt = f"Summarize:\n{page['content'][:4000]}"
        return self.llm.invoke(prompt).content

class ReportAgent:
    """Build markdown report."""

    def run(self, query, summaries):
        lines = [
            "# AI Research Report",
            f"Generated: {datetime.now()}",
            f"Query: {query}",
            ""
        ]

        for item in summaries:
            lines.extend([
                f"## {item['title']}",
                f"URL: {item['url']}",
                "",
                item['summary'],
                ""
            ])

        return "\n".join(lines)

# ============================================================
# PIPELINE
# ============================================================

class ResearchPipeline:

    def __init__(self):
        self.llm = ChatOllama(
            model=MODEL_NAME,
            temperature=TEMPERATURE
        )
        self.search_agent = SearchAgent()
        self.scraper_agent = ScraperAgent()
        self.audit_agent = AuditAgent(self.llm)
        self.summary_agent = SummaryAgent(self.llm)
        self.report_agent = ReportAgent()
        self.journal = []

    def search_node(self, state):
        urls = self.search_agent.run(state["query"])
        self.journal.append({"stage": "search", "urls": urls})
        return {"urls": urls}

    def scrape_node(self, state):
        pages = [self.scraper_agent.run(url) for url in state["urls"]]
        self.journal.append({"stage": "scrape", "count": len(pages)})
        return {"pages": pages}

    def audit_node(self, state):
        kept = []
        for page in state["pages"]:
            audit = self.audit_agent.run(page)
            if audit["status"] == "KEEP":
                kept.append(page)
        self.journal.append({"stage": "audit", "kept": len(kept)})
        return {"audited_pages": kept}

    def summary_node(self, state):
        summaries = []
        for page in state["audited_pages"]:
            summaries.append({
                "url": page["url"],
                "title": page["title"],
                "summary": self.summary_agent.run(page)
            })
        return {"summaries": summaries}

    def report_node(self, state):
        report = self.report_agent.run(
            state["query"],
            state["summaries"]
        )
        return {"report": report}

    def build(self):
        graph = StateGraph(PipelineState)
        graph.add_node("search", self.search_node)
        graph.add_node("scrape", self.scrape_node)
        graph.add_node("audit", self.audit_node)
        graph.add_node("summary", self.summary_node)
        graph.add_node("report", self.report_node)

        graph.add_edge(START, "search")
        graph.add_edge("search", "scrape")
        graph.add_edge("scrape", "audit")
        graph.add_edge("audit", "summary")
        graph.add_edge("summary", "report")
        graph.add_edge("report", END)

        return graph.compile()

if __name__ == "__main__":
    pipeline = ResearchPipeline()
    app = pipeline.build()

    result = app.invoke({"query": SEARCH_QUERY})

    with open(REPORT_FILENAME, "w", encoding="utf-8") as f:
        f.write(result["report"])

    with open(JOURNAL_FILENAME, "w", encoding="utf-8") as f:
        json.dump(pipeline.journal, f, indent=2)

    print(result["report"][:2000])
