# 현재 코드에서 부족한 부분 및 개선 필요 사항

> **참고:** 본 문서는 현재 코드(v2.1.0) 기준으로 작성되었습니다.

## ✅ 완료된 항목

다음 항목들은 이미 구현되었거나 해결되었습니다:

- ✅ **Qdrant 필터 검색 문제 해결** - `metadata.insurance_type` 경로로 수정 완료
- ✅ **프롬프트 변수 일치** - 모든 필수 변수가 프롬프트에 전달됨
- ✅ **README.md 작성** - 프로젝트 문서화 완료
- ✅ **성능 평가 시스템 통합** - 정량적/정성적 평가 모두 구현
- ✅ **사용자 체감 응답 시간 측정** - 스피너 블록 내에서 정확히 측정
- ✅ **평가 UI/UX 개선** - 답변 유지, 평가 매핑, 버튼 표시 조건 개선

---

## 🟡 Important (프로덕션 배포 전 권장)

### 1. 테스트 코드 부재

**현재 상태:**
- 단위 테스트 없음
- 통합 테스트 없음
- E2E 테스트 없음

**추가 필요:**
```python
# tests/test_qa_chain.py
def test_classify_insurance_type():
    """보험유형 분류 테스트"""
    assert classify_insurance_type("자동차 사고 보험금") == "자동차보험"
    assert classify_insurance_type("병원 입원 보험") == "질병보험"

def test_filtered_retrieval():
    """필터 검색 테스트"""
    retriever = get_retriever("자동차보험")
    docs = retriever.invoke("자동차 보험금")
    assert len(docs) > 0
    assert all(doc.metadata.get("insurance_type") == "자동차보험" for doc in docs)

def test_fallback_mechanism():
    """Fallback 로직 테스트"""
    # 필터 검색 실패 시 전체 검색으로 전환되는지 확인
```

**우선순위:** 높음 (코드 안정성 확보)

---

### 2. 환경 변수 검증 및 .env.example

**현재 상태:**
- `.env.example` 파일 없음
- 환경 변수 검증 로직 없음
- 설정 오류 시 런타임에만 발견됨

**추가 필요:**
```
# .env.example
UPSTAGE_API_KEY=your_api_key_here
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

**설정 검증 로직:**
```python
# config/settings.py에 추가
import os
from dotenv import load_dotenv

load_dotenv()

UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
if not UPSTAGE_API_KEY:
    raise ValueError("UPSTAGE_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

if not (1 <= QDRANT_PORT <= 65535):
    raise ValueError(f"QDRANT_PORT는 1-65535 사이여야 합니다. 현재 값: {QDRANT_PORT}")
```

**우선순위:** 중간 (사용자 편의성 향상)

---

### 3. 로깅 시스템 개선

**현재 상태:**
- `print()` 문으로만 로깅
- 로그 레벨 구분 없음
- 파일 로깅 없음
- 프로덕션 환경에서 로그 관리 어려움

**개선 필요:**
```python
# utils/logger.py
import logging
from pathlib import Path
from datetime import datetime

def setup_logger(name: str, log_dir: Path = None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 기존 핸들러 제거
    logger.handlers.clear()
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 파일 핸들러 (선택)
    if log_dir:
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
```

**사용 예시:**
```python
# chains/qa_chain_with_metrics.py
from utils.logger import setup_logger

logger = setup_logger(__name__)

def retrieve_with_classification(inputs: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"질문 수신: {inputs.get('question', '')[:50]}...")
    # ... 기존 코드 ...
    logger.debug(f"검색된 문서 수: {len(docs)}")
```

**우선순위:** 중간 (운영 환경에서 중요)

---

### 4. 에러 핸들링 강화

**현재 상태:**
- 일부 try-except만 구현
- 사용자 친화적 에러 메시지 부족
- 재시도 로직 없음
- 일부 예외는 그냥 전파됨

**개선 필요:**

1. **커스텀 예외 클래스:**
```python
# exceptions.py
class QAChainError(Exception):
    """QA 체인 관련 기본 예외"""
    pass

class ClassificationError(QAChainError):
    """보험유형 분류 실패"""
    pass

class RetrievalError(QAChainError):
    """문서 검색 실패"""
    pass

class LLMGenerationError(QAChainError):
    """LLM 답변 생성 실패"""
    pass
```

2. **재시도 로직 (exponential backoff):**
```python
# utils/retry.py
import time
from functools import wraps

def retry_with_backoff(max_retries=3, initial_delay=1, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"{func.__name__} 실패 (시도 {attempt+1}/{max_retries}): {e}")
                    time.sleep(delay)
                    delay *= backoff_factor
            return None
        return wrapper
    return decorator

# 사용
@retry_with_backoff(max_retries=3)
def classify_insurance_type(question: str) -> str:
    # LLM 호출
```

3. **사용자 친화적 에러 메시지:**
```python
# app_streamlit_v2.py
except LLMGenerationError as e:
    st.error("❌ 답변 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
    logger.error(f"LLM 생성 오류: {e}", exc_info=True)
except RetrievalError as e:
    st.error("❌ 관련 문서를 찾는 중 오류가 발생했습니다.")
    logger.error(f"검색 오류: {e}", exc_info=True)
```

**우선순위:** 높음 (사용자 경험 개선)

---

### 5. 타입 힌팅 완성도

**현재 상태:**
- 일부 함수에 타입 힌팅 있음
- 반환 타입 일부 누락
- 타입 체크 도구 미사용

**개선 필요:**
```python
from typing import Dict, Any, Optional, List
from langchain_core.documents import Document

def get_retriever(insurance_type: Optional[str] = None) -> BaseRetriever:
    """검색기 반환"""
    pass

def format_insurance_docs(docs: List[Document]) -> str:
    """문서 포맷팅"""
    pass
```

**mypy 설정:**
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

**우선순위:** 낮음 (코드 품질 향상)

---

## 🟢 Nice to Have (장기적 개선)

### 6. 설정 검증 (Pydantic 활용)

**현재 상태:**
- 설정값 검증 로직 없음
- 잘못된 설정값으로 실행 시 런타임 에러 발생 가능

**개선 필요:**
```python
# config/settings.py
from pydantic import BaseSettings, validator
from typing import Set

class Settings(BaseSettings):
    UPSTAGE_API_KEY: str
    UPSTAGE_MODEL: str = "solar-1-mini-chat"
    TEMPERATURE: float = 0.0
    
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    COLLECTION_NAME: str = "insurance_docs"
    
    TOP_K: int = 20
    SCORE_THRESHOLD: float = 0.3
    
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    ALLOWED_INSURANCE_TYPES: Set[str] = {
        "상해보험", "손해보험", "연금보험",
        "자동차보험", "질병보험", "책임보험", "화재보험"
    }
    
    @validator('QDRANT_PORT')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('포트 번호는 1-65535 사이여야 합니다.')
        return v
    
    @validator('TEMPERATURE')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature는 0.0-2.0 사이여야 합니다.')
        return v
    
    @validator('TOP_K')
    def validate_top_k(cls, v):
        if v < 1:
            raise ValueError('TOP_K는 1 이상이어야 합니다.')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

**우선순위:** 낮음 (코드 품질 향상)

---

### 7. 문서화 (Docstring) 강화

**현재 상태:**
- 함수 docstring 대부분 부재
- 모듈 레벨 docstring 없음
- API 문서화 없음

**개선 필요:**
```python
def classify_insurance_type(question: str) -> str:
    """
    사용자 질문에서 보험유형을 자동으로 분류합니다.
    
    LLM 기반 분류를 시도하고, 실패 시 키워드 기반 fallback 로직을 사용합니다.
    
    Args:
        question: 사용자 입력 질문 문자열
        
    Returns:
        분류된 보험유형 문자열. 다음 중 하나:
        '상해보험', '손해보험', '연금보험', '자동차보험', 
        '질병보험', '책임보험', '화재보험'
        
        질문이 비어있거나 분류 실패 시 '질병보험'을 기본값으로 반환.
        
    Examples:
        >>> classify_insurance_type("자동차 사고 보험금 받고 싶어요")
        '자동차보험'
        >>> classify_insurance_type("병원 입원 보험")
        '질병보험'
    """
```

**우선순위:** 낮음 (코드 가독성 향상)

---

### 8. 성능 최적화

**현재 상태:**
- 캐싱 없음 (동일 질문도 매번 처리)
- 배치 처리 없음
- 평가 시스템 실행 시 추가 비용 발생

**개선 필요:**

1. **질문 캐싱:**
```python
from functools import lru_cache
from hashlib import md5

@lru_cache(maxsize=100)
def cached_qa_chain_invoke(question_hash: str):
    """질문 해시 기반 캐싱"""
    pass

def invoke_with_cache(question: str):
    q_hash = md5(question.encode()).hexdigest()
    return cached_qa_chain_invoke(q_hash)
```

2. **평가 시스템 선택적 실행:**
```python
# 이미 구현되어 있으나, 더 세밀한 제어 가능
if st.session_state.get("auto_evaluate", False):
    # 자동 평가 실행
```

**우선순위:** 중간 (비용 및 성능 개선)

---

### 9. 보안 강화

**현재 상태:**
- API 키는 환경 변수로 관리 (양호)
- 입력 검증 부분적으로만 구현
- Rate limiting 없음

**개선 필요:**
```python
# 입력 검증
def validate_question(question: str) -> str:
    """사용자 질문 검증"""
    if not question or not question.strip():
        raise ValueError("질문이 비어있습니다.")
    
    if len(question) > 1000:
        raise ValueError("질문이 너무 깁니다. (최대 1000자)")
    
    # SQL 인젝션 등 위험 문자 필터링
    dangerous_chars = ["<", ">", "script", "javascript:"]
    for char in dangerous_chars:
        if char.lower() in question.lower():
            raise ValueError("입력에 허용되지 않은 문자가 포함되어 있습니다.")
    
    return question.strip()

# Rate limiting (Streamlit 커뮤니티 컴포넌트 사용 가능)
```

**우선순위:** 중간 (보안 강화)

---

### 10. 모니터링 대시보드

**현재 상태:**
- 사이드바에 기본 통계만 표시
- 평가 결과 추이 분석 없음
- 실시간 대시보드 없음

**개선 필요:**
```python
# 별도 대시보드 페이지 추가
# app/dashboard.py
def show_evaluation_dashboard():
    """평가 결과 대시보드"""
    # 시간별 응답 시간 추이
    # 보험유형별 평균 점수
    # 토큰 사용량 추이
    # 필터 검색 성공률 추이
```

**우선순위:** 낮음 (운영 편의성)

---

### 11. 코드 중복 제거

**현재 상태:**
- `qa_chain.py`와 `qa_chain_with_metrics.py` 유사 구조
- 일부 유틸리티 함수 중복 가능성

**개선 필요:**
```python
# qa_chain.py를 base로 하고, metrics를 데코레이터 패턴으로 추가
def with_metrics(chain_func):
    """메트릭 수집 데코레이터"""
    def wrapper(*args, **kwargs):
        collector = MetricsCollector()
        # 메트릭 수집 로직
        return chain_func(*args, **kwargs)
    return wrapper
```

**우선순위:** 낮음 (코드 유지보수성)

---

## 📋 우선순위별 체크리스트

### 즉시 처리 (High Priority)
- [ ] 테스트 코드 작성 (단위, 통합, E2E)
- [ ] 에러 핸들링 강화 (커스텀 예외, 재시도 로직)
- [ ] 환경 변수 검증 및 .env.example 추가

### 단기 개선 (Medium Priority)
- [ ] 로깅 시스템 개선 (logging 모듈 사용)
- [ ] 성능 최적화 (캐싱, 배치 처리)
- [ ] 보안 강화 (입력 검증, Rate limiting)

### 장기 개선 (Low Priority)
- [ ] 타입 힌팅 완성도 (mypy 통합)
- [ ] 문서화 강화 (Docstring)
- [ ] 설정 검증 (Pydantic)
- [ ] 모니터링 대시보드
- [ ] 코드 중복 제거

---

**참고:** 위 항목들은 프로젝트의 완성도를 높이기 위한 권장사항입니다. 프로젝트의 목적과 제약사항에 따라 우선순위를 조정하여 진행하시면 됩니다.

**현재 버전:** v2.1.0  
**마지막 업데이트:** 2026년 1월 16일
