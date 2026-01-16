"""
정량적 메트릭 수집기
응답 시간, 토큰 사용량, 검색 통계 등을 자동으로 측정
"""
import time
from typing import Dict, Any, Optional
from datetime import datetime


class MetricsCollector:
    """QA 체인 실행 중 메트릭 자동 수집"""
    
    def __init__(self):
        self.start_times: Dict[str, float] = {}
        self.metrics: Dict[str, Any] = {
            "total_time": 0.0,
            "classification_time": 0.0,
            "retrieval_time": 0.0,
            "generation_time": 0.0,
            "classification_tokens": 0,
            "generation_input_tokens": 0,
            "generation_output_tokens": 0,
            "total_tokens": 0,
            "retrieved_docs_count": 0,
            "used_filter": False,
            "fallback_activated": False,
            "classified_insurance_type": None,
            "timestamp": None,
        }
    
    def start_timer(self, stage: str):
        """단계별 시간 측정 시작"""
        self.start_times[stage] = time.time()
    
    def end_timer(self, stage: str) -> float:
        """단계별 시간 측정 종료 및 경과 시간 반환"""
        if stage not in self.start_times:
            return 0.0
        
        elapsed = time.time() - self.start_times[stage]
        del self.start_times[stage]
        
        # 메트릭에 저장
        if stage == "total":
            self.metrics["total_time"] = elapsed
        elif stage == "classification":
            self.metrics["classification_time"] = elapsed
        elif stage == "retrieval":
            self.metrics["retrieval_time"] = elapsed
        elif stage == "generation":
            self.metrics["generation_time"] = elapsed
        
        return elapsed
    
    def count_tokens(self, text: str, model: str = "default") -> int:
        """
        토큰 수 계산 (대략적 추정)
        실제 토큰화 대신 문자 수 기반으로 추정
        한국어: 약 1.5자/토큰, 영문: 약 4자/토큰
        """
        if not text:
            return 0
        
        # 간단한 추정: 한국어 중심
        korean_chars = sum(1 for c in text if ord(c) >= 0xAC00 and ord(c) <= 0xD7A3)
        other_chars = len(text) - korean_chars
        
        # 한국어 1.5자/토큰, 영문/기타 4자/토큰 추정
        estimated_tokens = int(korean_chars / 1.5 + other_chars / 4)
        
        return estimated_tokens
    
    def record_classification_tokens(self, question: str, response: str):
        """분류 단계 토큰 기록"""
        input_tokens = self.count_tokens(question)
        output_tokens = self.count_tokens(response)
        total = input_tokens + output_tokens
        
        self.metrics["classification_tokens"] = total
        self.metrics["total_tokens"] += total
    
    def record_generation_tokens(self, prompt: str, answer: str):
        """생성 단계 토큰 기록"""
        input_tokens = self.count_tokens(prompt)
        output_tokens = self.count_tokens(answer)
        
        self.metrics["generation_input_tokens"] = input_tokens
        self.metrics["generation_output_tokens"] = output_tokens
        self.metrics["total_tokens"] += (input_tokens + output_tokens)
    
    def record_search_stats(
        self, 
        docs_count: int, 
        used_filter: bool,
        fallback_activated: bool = False,
        insurance_type: Optional[str] = None
    ):
        """검색 통계 기록"""
        self.metrics["retrieved_docs_count"] = docs_count
        self.metrics["used_filter"] = used_filter
        self.metrics["fallback_activated"] = fallback_activated
        if insurance_type:
            self.metrics["classified_insurance_type"] = insurance_type
    
    def get_metrics(self) -> Dict[str, Any]:
        """수집된 메트릭 반환"""
        self.metrics["timestamp"] = datetime.now().isoformat()
        return self.metrics.copy()
    
    def reset(self):
        """메트릭 초기화"""
        self.__init__()
