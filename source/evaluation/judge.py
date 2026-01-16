"""
LLM-as-a-Judge 평가 시스템
답변 품질을 다차원으로 평가
"""
import json
import re
from typing import Dict, List, Any
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

from llm.llm import get_llm


JUDGE_PROMPT = PromptTemplate.from_template("""
당신은 보험 약관 Q&A 시스템의 답변 품질을 평가하는 전문가입니다.

[질문]
{question}

[생성된 답변]
{answer}

[참고 문서 (컨텍스트)]
{context}

다음 항목을 1-5점 척도로 평가하세요 (정수만):
1. 관련성 (Relevance): 답변이 질문과 얼마나 관련 있는가?
2. 정확도 (Accuracy): 답변이 사실적으로 정확한가? (제시된 컨텍스트 기반)
3. 유용성 (Helpfulness): 사용자에게 도움이 되는 답변인가?
4. 완전성 (Completeness): 질문에 충분히 답변했는가?
5. 근거 충실도 (Groundedness): 제시된 문서로 답변이 뒷받침되는가?

반드시 다음 JSON 형식으로만 반환하세요 (다른 텍스트 없이):
{{
    "relevance": 4,
    "accuracy": 5,
    "helpfulness": 4,
    "completeness": 3,
    "groundedness": 5,
    "explanation": "간단한 평가 이유 설명"
}}
""")


RAGAS_PROMPT = PromptTemplate.from_template("""
당신은 RAG 시스템 평가 전문가입니다.

[질문]
{question}

[생성된 답변]
{answer}

[검색된 문서들]
{context}

다음 RAGAS 메트릭을 0.0-1.0 사이의 실수로 평가하세요:

1. Faithfulness (신뢰성): 답변이 제공된 컨텍스트에 기반하는가? 컨텍스트에 없는 내용을 만들어내지 않았는가?
2. Answer Relevancy (답변 관련성): 답변이 질문에 대한 답이 되나? 질문을 제대로 해결하는가?
3. Context Precision (컨텍스트 정밀도): 검색된 문서 중에서 답변에 실제로 사용된 관련 문서의 비율은?
4. Context Recall (컨텍스트 재현율): 답변에 필요한 모든 정보가 검색된 문서에 포함되어 있는가?

반드시 다음 JSON 형식으로만 반환하세요:
{{
    "faithfulness": 0.9,
    "answer_relevancy": 0.85,
    "context_precision": 0.8,
    "context_recall": 0.75,
    "explanation": "평가 이유"
}}
""")


class LLMJudge:
    """LLM을 사용한 답변 품질 평가"""
    
    def __init__(self, llm=None):
        self.llm = llm or get_llm()
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        context: str,
        docs: List[Document] = None
    ) -> Dict[str, Any]:
        """
        답변을 다차원으로 평가
        
        Args:
            question: 사용자 질문
            answer: 생성된 답변
            context: 포맷팅된 컨텍스트
            docs: 검색된 문서 리스트 (선택)
            
        Returns:
            {
                'relevance': 4.5,
                'accuracy': 4.0,
                'helpfulness': 4.2,
                'completeness': 3.8,
                'groundedness': 4.5,
                'explanation': '...'
            }
        """
        try:
            prompt = JUDGE_PROMPT.format(
                question=question,
                answer=answer,
                context=context[:2000]  # 컨텍스트 길이 제한
            )
            
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # JSON 추출 (코드 블록 제거)
            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = content
            
            result = json.loads(json_str)
            
            # 평균 점수 계산
            scores = [
                result.get('relevance', 0),
                result.get('accuracy', 0),
                result.get('helpfulness', 0),
                result.get('completeness', 0),
                result.get('groundedness', 0),
            ]
            result['average_score'] = sum(scores) / len(scores) if scores else 0
            
            return result
            
        except Exception as e:
            print(f"[Judge 평가 실패] {e}")
            # 기본값 반환
            return {
                'relevance': 0,
                'accuracy': 0,
                'helpfulness': 0,
                'completeness': 0,
                'groundedness': 0,
                'average_score': 0,
                'explanation': f'평가 실패: {str(e)}',
                'error': str(e)
            }
    
    def evaluate_ragas_metrics(
        self,
        question: str,
        answer: str,
        context: str,
        docs: List[Document] = None
    ) -> Dict[str, float]:
        """
        RAGAS 기준 평가
        
        Returns:
            {
                'faithfulness': 0.9,
                'answer_relevancy': 0.85,
                'context_precision': 0.8,
                'context_recall': 0.75,
                'explanation': '...'
            }
        """
        try:
            # 문서 리스트를 텍스트로 변환
            if docs:
                docs_text = "\n\n".join([
                    f"[문서 {i+1}]\n{doc.page_content[:500]}"
                    for i, doc in enumerate(docs[:5])
                ])
            else:
                docs_text = context[:2000]
            
            prompt = RAGAS_PROMPT.format(
                question=question,
                answer=answer,
                context=docs_text
            )
            
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # JSON 추출
            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = content
            
            result = json.loads(json_str)
            
            # 평균 점수 계산
            scores = [
                result.get('faithfulness', 0),
                result.get('answer_relevancy', 0),
                result.get('context_precision', 0),
                result.get('context_recall', 0),
            ]
            result['average_score'] = sum(scores) / len(scores) if scores else 0
            
            return result
            
        except Exception as e:
            print(f"[RAGAS 평가 실패] {e}")
            return {
                'faithfulness': 0,
                'answer_relevancy': 0,
                'context_precision': 0,
                'context_recall': 0,
                'average_score': 0,
                'explanation': f'평가 실패: {str(e)}',
                'error': str(e)
            }
