# source/vectorstore.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


COLLECTION_NAME = "insurance_docs"


def get_qdrant_client():
    return QdrantClient(url="http://localhost:6333")


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )  # type: ignore


def get_vectorstore(recreate: bool = False) -> QdrantVectorStore:
    client = get_qdrant_client()
    embeddings = get_embeddings()

    # 🔥 컬렉션 존재 여부 확인
    collections = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME not in collections or recreate:
        # 컬렉션 생성
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384, # 임베딩 차원 수
                distance=Distance.COSINE,
            ),
        )

    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )
