from langgraph.graph import StateGraph
from graph.state import QAState

from graph.nodes.retrieve import retrieve
from graph.nodes.validate import validate
from graph.nodes.generate import generate

def build_graph():
    graph = StateGraph(QAState)

    graph.add_node("retrieve", retrieve)
    graph.add_node("validate", validate)
    graph.add_node("generate", generate)

    graph.set_entry_point("retrieve")

    graph.add_edge("retrieve", "validate")
    graph.add_conditional_edges(
        "validate",
        lambda s: "generate" if "documents" in s else "__end__"
    )

    graph.add_edge("generate", "__end__")

    return graph.compile()
