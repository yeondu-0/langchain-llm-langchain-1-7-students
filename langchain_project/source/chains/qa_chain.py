# source/chains/qa_chain.py
# LCEL chain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from llm.llm import get_llm
from llm.prompt import INSURANCE_PROMPT
from vectorstore.retriever import get_retriever
from vectorstore.formatter import format_insurance_docs

def get_qa_chain():
    retriever = get_retriever()
    llm = get_llm()

    chain = (
        {
            "context": retriever | format_insurance_docs,
            "question": RunnablePassthrough(),
        }
        | INSURANCE_PROMPT
        | llm
        | StrOutputParser()
    )
    # def debug_formatter(docs):
    #     print("\n[DEBUG] 검색된 문서 수:", len(docs))
    #     for i, d in enumerate(docs[:2]):
    #         print(f"\n[DOC {i}] metadata:", d.metadata)
    #         print(f"[DOC {i}] content preview:", d.page_content[:200])
    #     return format_insurance_docs(docs)

    # chain = (
    #     {
    #         "context": retriever | debug_formatter,
    #         "question": RunnablePassthrough(),
    #     }
    #     | INSURANCE_PROMPT
    #     | llm
    # )

    return chain
