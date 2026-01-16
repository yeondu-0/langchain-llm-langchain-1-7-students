"""
평가 결과 저장 및 조회
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class EvaluationStore:
    """평가 결과 저장 및 조회"""
    
    def __init__(self, storage_dir: Path = None):
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "evaluation_results"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # 결과 파일 경로
        self.results_file = self.storage_dir / "evaluation_results.jsonl"
    
    def save_evaluation(
        self,
        question: str,
        answer: str,
        metrics: Dict[str, Any],
        judge_scores: Optional[Dict[str, Any]] = None,
        ragas_scores: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        평가 결과 저장 (JSONL 형식)
        
        Args:
            question: 질문
            answer: 답변
            metrics: 정량적 메트릭
            judge_scores: Judge 평가 점수
            ragas_scores: RAGAS 평가 점수
            metadata: 추가 메타데이터
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer[:500],  # 답변 일부만 저장
            "metrics": metrics,
            "judge_scores": judge_scores or {},
            "ragas_scores": ragas_scores or {},
            "metadata": metadata or {}
        }
        
        # JSONL 형식으로 추가
        with open(self.results_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    
    def load_all_results(self) -> List[Dict[str, Any]]:
        """모든 평가 결과 로드"""
        if not self.results_file.exists():
            return []
        
        results = []
        with open(self.results_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))
        
        return results
    
    def get_statistics(
        self, 
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        기간별 통계 조회
        
        Args:
            date_from: 시작 날짜 (ISO 형식)
            date_to: 종료 날짜 (ISO 형식)
            
        Returns:
            통계 딕셔너리
        """
        results = self.load_all_results()
        
        # 날짜 필터링
        if date_from:
            results = [r for r in results if r["timestamp"] >= date_from]
        if date_to:
            results = [r for r in results if r["timestamp"] <= date_to]
        
        if not results:
            return {
                "total_evaluations": 0,
                "avg_response_time": 0,
                "avg_token_usage": 0,
                "avg_relevance_score": 0,
                "filter_success_rate": 0,
            }
        
        # 메트릭 통계
        total_time = [r["metrics"].get("total_time", 0) for r in results]
        total_tokens = [r["metrics"].get("total_tokens", 0) for r in results]
        
        # Judge 점수 통계
        relevance_scores = []
        accuracy_scores = []
        helpfulness_scores = []
        for r in results:
            if r.get("judge_scores"):
                js = r["judge_scores"]
                if "relevance" in js:
                    relevance_scores.append(js["relevance"])
                if "accuracy" in js:
                    accuracy_scores.append(js["accuracy"])
                if "helpfulness" in js:
                    helpfulness_scores.append(js["helpfulness"])
        
        # 필터 성공률
        filter_success = sum(
            1 for r in results 
            if r["metrics"].get("used_filter") and not r["metrics"].get("fallback_activated", False)
        )
        
        return {
            "total_evaluations": len(results),
            "avg_response_time": sum(total_time) / len(total_time) if total_time else 0,
            "avg_token_usage": sum(total_tokens) / len(total_tokens) if total_tokens else 0,
            "avg_relevance_score": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0,
            "avg_accuracy_score": sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0,
            "avg_helpfulness_score": sum(helpfulness_scores) / len(helpfulness_scores) if helpfulness_scores else 0,
            "filter_success_rate": filter_success / len(results) if results else 0,
            "fallback_rate": sum(1 for r in results if r["metrics"].get("fallback_activated", False)) / len(results) if results else 0,
        }
    
    def export_to_json(self, output_file: Path = None) -> Path:
        """모든 결과를 JSON 파일로 내보내기"""
        if output_file is None:
            output_file = self.storage_dir / f"evaluation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        results = self.load_all_results()
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return output_file
