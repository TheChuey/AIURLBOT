import requests

from bs4 import BeautifulSoup

from pydantic import BaseModel
from typing import Literal

from langchain_ollama import ChatOllama


class AuditResult(BaseModel):

    url: str
    status: Literal["KEEP", "ELIMINATE"]
    confidence_score: float
    reason: str


llm = ChatOllama(
    #model="qwen2.5-coder",
    model="llama3.1",
    temperature=0
)

audit_llm = llm.with_structured_output(
    AuditResult
)


def scrape_url(url: str) -> dict:

    try:

        response = requests.get(
            url,
            timeout=10
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = ""

        if soup.title:
            title = soup.title.text

        content = soup.get_text(
            separator=" ",
            strip=True
        )

        return {
            "url": url,
            "title": title,
            "content": content[:10000]
        }

    except Exception:

        return {
            "url": url,
            "title": "",
            "content": ""
        }


def audit_url(url: str):

    page = scrape_url(url)

    prompt = f"""
You are an elite Content Audit Agent.

URL:
{page['url']}

TITLE:
{page['title']}

CONTENT:
{page['content']}

Return JSON only.
"""

    return audit_llm.invoke(prompt)


def audit_urls(urls: list[str]):

    results = []

    for url in urls:

        result = audit_url(url)

        results.append(
            result.model_dump()
        )

    return results