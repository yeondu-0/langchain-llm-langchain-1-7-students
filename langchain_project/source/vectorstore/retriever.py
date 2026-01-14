# source/vectorstore/retriever.py
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    TOP_K,
)

def get_retriever():
    client = QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
    )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )

    return vectorstore.as_retriever(
        search_kwargs={"k": TOP_K}
    )
