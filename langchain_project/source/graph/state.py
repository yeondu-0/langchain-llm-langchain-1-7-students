from typing import List, TypedDict
from langchain_core.documents import Document

class QAState(TypedDict):
    question: str
    documents: List[Document]
    answer: str
