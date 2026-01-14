# test_search.py
from langchain_qdrant import QdrantVectorStore
from .vertorstore_ingest import get_embeddings, get_qdrant_client


def test_similarity_search():
    vectorstore = QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name="insurance_docs",
        embedding=get_embeddings(),
    )

    query = "교통사고가 났는데 보험 보장받을 수 있어?"

    docs = vectorstore.similarity_search(query, k=3)

    for i, doc in enumerate(docs, 1):
        print(f"\n--- RESULT {i} ---")
        print(doc.metadata)
        print(doc.page_content[:300])


if __name__ == "__main__":
    test_similarity_search()
