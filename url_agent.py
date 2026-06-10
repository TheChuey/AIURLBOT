from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain.tools import tool
from ddgs import DDGS


llm = ChatOllama(
    model="qwen2.5-coder",
    temperature=0
)


@tool
def duckduckgo_search(query: str) -> str:
    """Search DuckDuckGo and return URLs."""

    with DDGS() as ddgs:

        results = ddgs.text(
            query,
            max_results=10
        )

        return "\n".join(
            r["href"]
            for r in results
            if "href" in r
        )


class State(TypedDict):

    input: str
    tool_result: str


def search_node(state: State):

    result = duckduckgo_search.invoke(
        state["input"]
    )

    return {
        "tool_result": result
    }


def llm_node(state: State):

    prompt = f"""
You are a URL filtering agent.

User Request:
{state["input"]}

Search Results:
{state["tool_result"]}

Return ONLY relevant URLs.
"""

    response = llm.invoke(prompt)

    return {
        "tool_result": response.content
    }


def final_node(state: State):

    return {
        "tool_result": state["tool_result"]
    }


graph = StateGraph(State)

graph.add_node("search", search_node)
graph.add_node("llm", llm_node)
graph.add_node("final", final_node)

graph.set_entry_point("search")

graph.add_edge("search", "llm")
graph.add_edge("llm", "final")
graph.add_edge("final", END)

app = graph.compile()


def get_urls(query: str) -> list[str]:

    result = app.invoke(
        {
            "input": query
        }
    )

    urls = []

    for line in result["tool_result"].splitlines():

        line = line.strip()

        if line.startswith("http"):

            urls.append(line)

    return urls