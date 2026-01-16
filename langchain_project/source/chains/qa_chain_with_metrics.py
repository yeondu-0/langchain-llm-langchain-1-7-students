"""
메트릭 수집 기능이 통합된 QA Chain
기존 qa_chain.py를 기반으로 메트릭 수집 기능 추가
"""
from typing import Dict, Any, Optional
from langchain_core.runnables import RunnableLambda

from llm.llm import get_llm
from llm.prompt import INSURANCE_PROMPT
from vectorstore.retriever import get_retriever
from chains.insurance_classifier import classify_insurance_type
from chains.utils import format_insurance_docs
from evaluation.metrics import MetricsCollector


def get_qa_chain_with_metrics(enable_metrics: bool = True) -> RunnableLambda:
    """
    메트릭 수집 기능이 통합된 QA Chain
    
    Args:
        enable_metrics: 메트릭 수집 활성화 여부
        
    Returns:
        QA Chain with metrics in result dict
    """
    llm = get_llm()

    def retrieve_with_classification(inputs: Dict[str, Any]) -> Dict[str, Any]:
        question = inputs.get("question", "")
        enable_eval = inputs.get("enable_metrics", enable_metrics)
        
        # 메트릭 수집기 초기화
        collector = MetricsCollector() if enable_eval else None
        
        # total_time은 실제 사용자 체감 시간과 다를 수 있으므로
        # Streamlit 레벨에서 측정하는 것이 더 정확함
        # 여기서는 내부 처리 시간만 측정
        if collector:
            collector.start_timer("classification")
        
        # STEP 1: 보험유형 분류
        insurance_type = classify_insurance_type(question)
        
        if collector:
            collector.end_timer("classification")
            # 분류 응답 토큰 추정 (실제로는 LLM 호출 결과 필요하지만 추정)
            collector.record_classification_tokens(question, insurance_type)
            collector.record_search_stats(0, False, False, insurance_type)
        
        print(f"\n[STEP 1] 분류된 보험유형: {insurance_type}")

        # STEP 2: 보험유형 필터 검색
        print(f"[STEP 2] '{insurance_type}' 필터로 검색 시도...")
        
        if collector:
            collector.start_timer("retrieval")
        
        retriever = get_retriever(insurance_type)
        docs = retriever.invoke(question)
        
        if collector:
            collector.end_timer("retrieval")
        
        print(f"[STEP 2 결과] 필터 검색 결과: {len(docs)}개 문서 발견")

        # STEP 3: Fallback 검색
        fallback_activated = False
        if not docs:
            print(f"[STEP 3] 필터 검색 결과가 0개 → 필터 없이 전체 검색으로 fallback")
            fallback_activated = True
            
            if collector:
                collector.start_timer("retrieval")
            
            retriever = get_retriever(None)
            docs = retriever.invoke(question)
            
            if collector:
                collector.end_timer("retrieval")
            
            print(f"[STEP 3 결과] 전체 검색 결과: {len(docs)}개 문서 발견")
        else:
            print(f"[STEP 3] 건너뜀 (이미 {len(docs)}개 문서 찾음)")

        print(f"[최종 결과] 총 {len(docs)}개 문서를 사용합니다\n")

        # 메트릭 기록
        if collector:
            collector.record_search_stats(
                len(docs),
                insurance_type is not None,
                fallback_activated,
                insurance_type
            )

        # STEP 4: 컨텍스트 포맷팅
        context = format_insurance_docs(docs)
        first_doc = docs[0] if docs else None
        md = first_doc.metadata if first_doc else {}

        # 메타데이터 추출
        insurance_type_from_doc = md.get("insurance_type", insurance_type)
        level_1 = md.get("level_1", "")
        level_2 = md.get("level_2", "")
        level_3 = md.get("level_3", "")
        level_4 = md.get("level_4", "")

        # STEP 5: LLM 답변 생성
        if collector:
            collector.start_timer("generation")
        
        prompt_text = INSURANCE_PROMPT.format(
            question=question,
            context=context,
            insurance_type=insurance_type_from_doc,
            level_1=level_1,
            level_2=level_2,
            level_3=level_3,
            level_4=level_4
        )
        
        answer = llm.invoke(prompt_text).content
        
        if collector:
            collector.end_timer("generation")
            collector.record_generation_tokens(prompt_text, str(answer))
            # total_time 계산 (내부 처리 시간 합산)
            collector.metrics["total_time"] = (
                collector.metrics.get("classification_time", 0) +
                collector.metrics.get("retrieval_time", 0) +
                collector.metrics.get("generation_time", 0)
            )

        result = {
            "answer": answer,
            "question": question,
            "insurance_type": insurance_type_from_doc,
            "level_1": level_1,
            "level_2": level_2,
            "level_3": level_3,
            "level_4": level_4,
            "context": context,
            "docs": docs,
        }
        
        # 메트릭 추가
        if collector:
            result["metrics"] = collector.get_metrics()
        
        return result

    chain = RunnableLambda(retrieve_with_classification)
    
    return chain
