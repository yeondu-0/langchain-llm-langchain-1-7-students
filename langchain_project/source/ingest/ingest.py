# ingest.py
from typing import List
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore

from .preprocessing import build_documents_from_xml
from source.ingest.vertorstore_ingest import get_qdrant_client, get_embeddings


def ingest_xml_to_qdrant(
    xml_path: str,
    collection_name: str = "insurance_docs"
) -> int:
    """
    XML 약관 파일을 파싱 → level 단위 Document 생성 → Qdrant 적재
    """
    # 1. 문서 생성
    documents: List[Document] = build_documents_from_xml(xml_path)

    if not documents:
        raise ValueError("❌ 생성된 Document가 없습니다.")

    # 2. VectorStore 생성 + 적재 (🔥 핵심)
    QdrantVectorStore.from_documents(
        documents=documents,
        embedding=get_embeddings(),
        url="http://localhost:6333",
        collection_name=collection_name,
    )
    return len(documents)
