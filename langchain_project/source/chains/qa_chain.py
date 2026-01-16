# source/chains/qa_chain.py
from typing import Dict, Any, Optional
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from llm.llm import get_llm
from llm.prompt import INSURANCE_PROMPT
from vectorstore.retriever import get_retriever
from chains.insurance_classifier import classify_insurance_type
from chains.utils import format_insurance_docs


def get_qa_chain() -> RunnableLambda:
    llm = get_llm()

    def retrieve_with_classification(inputs: Dict[str, Any]) -> Dict[str, Any]:
        question = inputs.get("question", "")
        insurance_type = classify_insurance_type(question)
        print(f"\n[STEP 1] 분류된 보험유형: {insurance_type}")

        # 보험유형 필터 검색
        print(f"[STEP 2] '{insurance_type}' 필터로 검색 시도...")
        retriever = get_retriever(insurance_type)
        docs = retriever.invoke(question)
        print(f"[STEP 2 결과] 필터 검색 결과: {len(docs)}개 문서 발견")
        
        # 디버깅: 실제 저장된 insurance_type 값 확인
        if not docs:
            print(f"[디버깅] 필터 검색 실패 - 실제 DB에 저장된 insurance_type 값 확인 중...")
            debug_retriever = get_retriever(None)  # 필터 없이 전체 검색
            debug_docs = debug_retriever.invoke(question)
            if debug_docs:
                unique_types = set(doc.metadata.get("insurance_type") for doc in debug_docs[:20])
                print(f"[디버깅] 전체 검색 상위 20개 문서의 insurance_type 값들: {unique_types}")
                print(f"[디버깅] 찾고 있는 값: '{insurance_type}' (repr: {repr(insurance_type)})")
                print(f"[디버깅] 값 일치 여부: {insurance_type in unique_types}")
                
                # 각 insurance_type별로 실제 몇 개가 있는지 확인
                from qdrant_client import QdrantClient
                from qdrant_client.http import models
                from config.settings import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME
                
                try:
                    debug_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
                    filter_condition = models.Filter(
                        must=[
                            models.FieldCondition(
                                key="metadata.insurance_type",  # 수정: metadata. 경로 추가
                                match=models.MatchValue(value=insurance_type),
                            )
                        ]
                    )
                    # count를 사용하여 필터 조건에 맞는 포인트 개수만 확인
                    result = debug_client.count(
                        collection_name=COLLECTION_NAME,
                        count_filter=filter_condition
                    )
                    print(f"[디버깅] Qdrant count API로 확인한 '{insurance_type}' 문서 수: {result.count:,}개")
                except Exception as e:
                    print(f"[디버깅] Qdrant count 확인 실패: {e}")

        # fallback 검색
        if not docs:
            print(f"[STEP 3] 필터 검색 결과가 0개 → 필터 없이 전체 검색으로 fallback")
            retriever = get_retriever(None)  # None = 필터 없음
            docs = retriever.invoke(question)
            print(f"[STEP 3 결과] 전체 검색 결과: {len(docs)}개 문서 발견")
        else:
            print(f"[STEP 3] 건너뜀 (이미 {len(docs)}개 문서 찾음)")

        print(f"[최종 결과] 총 {len(docs)}개 문서를 사용합니다\n")

        # format context
        context = format_insurance_docs(docs)
        first_doc = docs[0] if docs else None
        md = first_doc.metadata if first_doc else {}

        # 메타데이터 추출
        insurance_type_from_doc = md.get("insurance_type", insurance_type)
        level_1 = md.get("level_1", "")
        level_2 = md.get("level_2", "")
        level_3 = md.get("level_3", "")
        level_4 = md.get("level_4", "")

        # LLM 호출
        answer = llm.invoke(INSURANCE_PROMPT.format(
            question=question,
            context=context,
            insurance_type=insurance_type_from_doc,
            level_1=level_1,
            level_2=level_2,
            level_3=level_3,
            level_4=level_4
        )).content

        return {
            "answer": answer,
            "question": question,
            "insurance_type": insurance_type_from_doc,
            "level_1": level_1,
            "level_2": level_2,
            "level_3": level_3,
            "level_4": level_4,
            "context": context,
            "docs": docs,  # Streamlit 참고용
        }

    chain = RunnableLambda(retrieve_with_classification)
    
    return chain

# # source/chains/qa_chain.py
# # LCEL chain
# from langchain_core.runnables import RunnableMap,RunnableLambda, RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser
# from typing import Dict, Any

# from llm.llm import get_llm
# from llm.prompt import INSURANCE_PROMPT
# from vectorstore.retriever import get_retriever
# from chains.insurance_classifier import classify_insurance_type
# from chains.utils import format_insurance_docs


# def get_qa_chain():
#     llm = get_llm()

#     def retrieve_with_classification(question: str):
#         insurance_type = classify_insurance_type(question)
#         print(f"[DEBUG] Classifiedinsurance_type: {insurance_type}")

#         # 1️⃣ 보험유형 필터 검색
#         retriever = get_retriever(insurance_type)
#         docs = retriever.invoke(question)

#         print(f"[DEBUG] insurance_type: {insurance_type}")
#         print(f"[DEBUG] docs with filter: {len(docs)}")

#         # 2️⃣ fallback 검색
#         if not docs:
#             print("[WARN] fallback to no-filter search")
#             retriever = get_retriever(None)
#             docs = retriever.invoke(question)

#         # 3️⃣ 문서 최종 개수
#         print(f"[DEBUG] final docs: {len(docs)}")
#         for i, d in enumerate(docs[:2]):
#             print(f"[DOC {i}] type:", d.metadata.get("insurance_type"))
#             print(f"[DOC {i}] source:", d.metadata.get("source"))

#         # return {
#         #     "context": format_insurance_docs(docs),
#         #     "insurance_type": insurance_type,
#         #     "question": question,
#         # }
    
#         d = docs[0]  # 1개만 써도 됨 (지금 단계에서는)
#         md = d.metadata

#         context = format_insurance_docs(docs)
#         return {
#             "context": context, #d.page_content,
#             "docs": docs,
#             "insurance_type": md.get("insurance_type", insurance_type),
#             "level_1": md.get("level_1", ""),
#             "level_2": md.get("level_2", ""),
#             "level_3": md.get("level_3", ""),
#             "level_4": md.get("level_4", ""),
#             "question": question,
#         }


#     retrieve_runnable = RunnableLambda(retrieve_with_classification)
#     llm_runnable = RunnableLambda(lambda inputs:  {
#         **inputs, #type: ignore
#         "answer": llm.invoke(INSURANCE_PROMPT.format(**inputs)).content
#     })
#     chain = retrieve_runnable | llm_runnable | StrOutputParser()



#     return chain


#     # def debug_formatter(docs):
#     #     print("\n[DEBUG] 검색된 문서 수:", len(docs))
#     #     for i, d in enumerate(docs[:2]):
#     #         print(f"\n[DOC {i}] metadata:", d.metadata)
#     #         print(f"[DOC {i}] content preview:", d.page_content[:200])
#     #     return format_insurance_docs(docs)

#     # chain = (
#     #     {
#     #         "context": retriever | debug_formatter,
#     #         "question": RunnablePassthrough(),
#     #     }
#     #     | INSURANCE_PROMPT
#     #     | llm
#     # )

