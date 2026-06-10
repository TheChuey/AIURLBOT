from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain.tools import tool
from ddgs import DDGS   # ✅ FIXED IMPORT


# ============================================================
# MODEL
# ============================================================

llm = ChatOllama(
    model="qwen2.5-coder",
    temperature=0
)


# ============================================================
# TOOL
# ============================================================

@tool
def duckduckgo_search(query: str) -> str:
    """Search DuckDuckGo and return URLs."""

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5)

        return "\n".join(
            r["href"] for r in results if "href" in r
        )


TOOLS = {
    "duckduckgo_search": duckduckgo_search
}


# ============================================================
# STATE
# ============================================================

class State(TypedDict):
    input: str
    tool_result: str


# ============================================================
# NODES
# ============================================================

def search_node(state: State):
    query = state["input"]
    result = duckduckgo_search.invoke(query)
    return {"tool_result": result}


def llm_node(state: State):
    prompt = f"""
    You are a research assistant.
    User request:
    {state['input']}
    Search results:
    {state['tool_result']}
    Return ONLY final URLs.
    """
    response = llm.invoke(prompt)
    return {"tool_result": response.content}


def final_node(state: State):
    return {"tool_result": state["tool_result"]}


# ============================================================
# GRAPH
# ============================================================

graph = StateGraph(State)

graph.add_node("search", search_node)
graph.add_node("llm", llm_node)
graph.add_node("final", final_node)

graph.set_entry_point("search")

graph.add_edge("search", "llm")
graph.add_edge("llm", "final")
graph.add_edge("final", END)

app = graph.compile()


# ============================================================
# RUN
# ============================================================

result = app.invoke(
    {
        "input": "Find list of sites with information about LangGraph library and ollama"
    }
)

print("\nFINAL RESULT")
print("=" * 40)
print(result["tool_result"])