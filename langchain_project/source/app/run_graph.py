from graph.graph import build_graph

def main():
    graph = build_graph()

    while True:
        q = input("\n질문: ")
        result = graph.invoke({"question": q}) # type: ignore
        print("\n📌 답변:")
        print(result["answer"])
