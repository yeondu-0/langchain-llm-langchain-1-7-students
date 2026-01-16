from vectorstore.retriever import get_retriever

def retrieve(state):
    retriever = get_retriever()
    docs = retriever.get_relevant_documents(state["question"]) # type: ignore
    return {"documents": docs}
