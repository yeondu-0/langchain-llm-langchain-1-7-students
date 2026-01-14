# source/vectorstore/formatter.py

from typing import List
from langchain_core.documents import Document


def format_insurance_docs(docs: List[Document]) -> str:
    """
    Qdrant에서 검색된 Document들을
    보험 약관 '조문 인용용 텍스트'로 변환
    """

    formatted_blocks = []

    for doc in docs:
        meta = doc.metadata
        header_lines = []

        # 보험 종류
        if meta.get("insurance_type"):
            header_lines.append(f"[보험종류] {meta['insurance_type']}")

        # 약관 계층 구조
        if meta.get("level_1"):
            header_lines.append(f"[상위구조] {meta['level_1']}")
        if meta.get("level_2"):
            header_lines.append(f"[조] {meta['level_2']}")
        if meta.get("level_3"):
            header_lines.append(f"[하위구조] {meta['level_3']}")
        if meta.get("level_4"):
            header_lines.append(f"[세부조항] {meta['level_4']}")

        formatted_blocks.append(
            "\n".join(header_lines)
            + "\n[조문 내용]\n"
            + doc.page_content
        )

    return "\n\n---\n\n".join(formatted_blocks)
