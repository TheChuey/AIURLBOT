"""
AI RESEARCH PIPELINE
============================================================

Educational LangGraph Research Agent

Pipeline:

Search Agent
    ↓
Scraper Agent
    ↓
Content Audit Agent
    ↓
Summary Agent
    ↓
Report Agent

This example demonstrates:

1. LangGraph state management
2. Ollama integration
3. DDGS search
4. BeautifulSoup scraping
5. Structured content auditing
6. Automated report generation

Author Notes:

- Keep all editable settings in GLOBAL VARIABLES.
- Each node has one responsibility.
- Designed to be easy to extend later.
"""

# ============================================================
# IMPORTS
# ============================================================

from datetime import datetime
from typing import TypedDict, List, Literal

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from pydantic import BaseModel, Field

from langchain_ollama import ChatOllama

from langgraph.graph import (
    StateGraph,
    START,
    END
)

# ============================================================
# GLOBAL VARIABLES
# ============================================================

SEARCH_QUERY = "top ai agents small project for small business 2026"

MAX_SEARCH_RESULTS = 5

MODEL_NAME = "qwen2.5-coder"

TEMPERATURE = 0.0

HTTP_TIMEOUT = 15

SAVE_REPORT = True

REPORT_FILENAME = "research_report.md"

REQUEST_HEADERS = {
    "User-Agent":
    "Mozilla/5.0"
}

# ============================================================
# LLM
# ============================================================

llm = ChatOllama(
    model=MODEL_NAME,
    temperature=TEMPERATURE
)

# ============================================================
# AUDIT MODEL
# ============================================================

class AuditResult(BaseModel):

    url: str

    status: Literal[
        "KEEP",
        "ELIMINATE"
    ]

    confidence_score: float = Field(
        ge=0.0,
        le=1.0
    )

    reason: str


audit_llm = llm.with_structured_output(
    AuditResult
)

# ============================================================
# STATE
# ============================================================

class PipelineState(TypedDict):
    query: str
    discovered_urls: List[str]
    scraped_pages: List[dict]
    audited_pages: List[dict]
    summaries: List[dict]
    final_report: str

# ============================================================
# HELPERS
# ============================================================

def clean_text(text: str) -> str:
    """
    Basic cleanup.
    """

    return " ".join(
        text.split()
    )


def scrape_url(url: str):

    try:
        response = requests.get(
            url,
            headers=REQUEST_HEADERS,
            timeout=HTTP_TIMEOUT
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove noisy elements

        for tag in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside"
            ]
        ):
            tag.decompose()

        title = ""

        if soup.title:
            title = soup.title.text.strip()

        text = clean_text(
            soup.get_text(
                separator=" ",
                strip=True
            )
        )

        return {
            "url": url,
            "title": title,
            "content": text[:12000]
        }

    except Exception as e:

        print(
            f"[SCRAPER ERROR] {url}"
        )

        print(e)

        return {
            "url": url,
            "title": "",
            "content": ""
        }

# ============================================================
# NODE 1
# URL SEARCH AGENT
# ============================================================

def search_node(
    state: PipelineState
):

    print(
        "\n[SEARCH AGENT]"
    )

    urls = []

    try:

        with DDGS() as ddgs:

            results = ddgs.text(
                state["query"],
                max_results=MAX_SEARCH_RESULTS
            )

            for item in results:

                href = item.get(
                    "href"
                )

                if href:

                    urls.append(
                        href
                    )

    except Exception as e:

        print(
            f"Search Error: {e}"
        )

    urls = list(
        dict.fromkeys(urls)
    )

    print(
        f"Found {len(urls)} URLs"
    )

    return {
        "discovered_urls": urls
    }

# ============================================================
# NODE 2
# SCRAPER AGENT
# ============================================================

def scraper_node(
    state: PipelineState
):

    print(
        "\n[SCRAPER AGENT]"
    )

    pages = []

    for url in state[
        "discovered_urls"
    ]:

        print(
            f"Scraping: {url}"
        )

        page = scrape_url(
            url
        )

        pages.append(
            page
        )

    return {
        "scraped_pages": pages
    }

# ============================================================
# NODE 3
# CONTENT AUDIT AGENT
# ============================================================

def audit_node(
    state: PipelineState
):

    print(
        "\n[AUDIT AGENT]"
    )

    approved_pages = []

    for page in state[
        "scraped_pages"
    ]:

        prompt = f"""
You are an elite Content Audit Agent.

KEEP:
- Documentation
- Tutorials
- Technical guides
- Research articles
- Educational content

ELIMINATE:
- Login pages
- Cookie pages
- Privacy policies
- Terms of service
- Error pages
- Thin marketing pages

URL:
{page["url"]}

TITLE:
{page["title"]}

CONTENT:
{page["content"][:5000]}
"""

        try:

            result = audit_llm.invoke(
                prompt
            )

            print(
                f"{result.status} -> {page['url']}"
            )

            if result.status == "KEEP":

                approved_pages.append(
                    page
                )

        except Exception as e:

            print(
                f"Audit Error: {e}"
            )

            approved_pages.append(
                page
            )

    return {
        "audited_pages":
        approved_pages
    }

# ============================================================
# NODE 4
# SUMMARY AGENT
# ============================================================

def summarize_node(
    state: PipelineState
):

    print(
        "\n[SUMMARY AGENT]"
    )

    summaries = []

    for page in state[
        "audited_pages"
    ]:

        prompt = f"""
Summarize the following article.

Requirements:

- Focus on facts
- Focus on practical value
- Ignore marketing language
- Maximum 300 words

TITLE:
{page["title"]}

CONTENT:
{page["content"][:6000]}
"""

        try:

            response = llm.invoke(
                prompt
            )

            summaries.append(
                {
                    "url":
                    page["url"],

                    "title":
                    page["title"],

                    "summary":
                    response.content
                }
            )

        except Exception as e:

            print(
                f"Summary Error: {e}"
            )

    return {
        "summaries":
        summaries
    }

# ============================================================
# NODE 5
# REPORT AGENT
# ============================================================

def report_node(
    state: PipelineState
):

    print(
        "\n[REPORT AGENT]"
    )

    report = []

    report.append(
        "# AI Research Report\n"
    )

    report.append(
        f"Generated: {datetime.now()}\n"
    )

    report.append(
        f"Query: {state['query']}\n"
    )

    report.append(
        "\n---\n"
    )

    for item in state[
        "summaries"
    ]:

        report.append(
            f"## {item['title']}\n"
        )

        report.append(
            f"URL: {item['url']}\n"
        )

        report.append(
            "\nSummary:\n"
        )

        report.append(
            item["summary"]
        )

        report.append(
            "\n\n---\n"
        )

    final_report = "\n".join(
        report
    )

    return {
        "final_report":
        final_report
    }

# ============================================================
# GRAPH
# ============================================================

def build_graph():

    graph = StateGraph(
        PipelineState
    )

    graph.add_node(
        "search",
        search_node
    )

    graph.add_node(
        "scrape",
        scraper_node
    )

    graph.add_node(
        "audit",
        audit_node
    )

    graph.add_node(
        "summarize",
        summarize_node
    )

    graph.add_node(
        "report",
        report_node
    )

    graph.add_edge(
        START,
        "search"
    )

    graph.add_edge(
        "search",
        "scrape"
    )

    graph.add_edge(
        "scrape",
        "audit"
    )

    graph.add_edge(
        "audit",
        "summarize"
    )

    graph.add_edge(
        "summarize",
        "report"
    )

    graph.add_edge(
        "report",
        END
    )

    return graph.compile()

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n" +
        "=" * 60
    )

    print(
        "AI RESEARCH PIPELINE"
    )

    print(
        "=" * 60
    )

    app = build_graph()

    result = app.invoke(
        {
            "query":
            SEARCH_QUERY
        }
    )

    report = result[
        "final_report"
    ]

    print(
        "\n===== PREVIEW REPORT =====\n"
    )

    print(
        report[:3000]
    )

    if SAVE_REPORT:

        with open(
            REPORT_FILENAME,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                report
            )

        print(
            f"\nReport saved to: {REPORT_FILENAME}"
        )