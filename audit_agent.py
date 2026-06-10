from typing import Literal
from pydantic import BaseModel
from langchain_ollama import ChatOllama


# ============================================================
# STRUCTURED OUTPUT MODEL
# ============================================================

class AuditResult(BaseModel):
    url: str
    status: Literal["KEEP", "ELIMINATE"]
    confidence_score: float
    reason: str


# ============================================================
# LLM
# ============================================================

llm = ChatOllama(
    model="qwen2.5-coder",
    temperature=0
)

audit_llm = llm.with_structured_output(AuditResult)


# ============================================================
# SINGLE URL AUDIT
# ============================================================

def audit_url(url: str) -> dict:

    print("[AUDIT] Processing:", url)
    prompt = f"""
You are a content classifier.

Return KEEP for MOST technical articles about AI, LangGraph, Ollama, agents.

Only eliminate:
- login pages
- ads
- empty pages

URL:
{url}
"""

    result = audit_llm.invoke(prompt)

    return result.model_dump()


# ============================================================
# MAIN FUNCTION (PRESERVED NAME ✔)
# ============================================================

def audit_urls(urls: list[str]) -> list[dict]:

    print("\n[AUDIT AGENT] Starting batch audit")

    results = []

    for url in urls:

        results.append(audit_url(url))

    print("[AUDIT AGENT] Completed:", len(results))

    return results