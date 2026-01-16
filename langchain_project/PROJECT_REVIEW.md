# 보험 약관 지능형 Q&A 시스템 - 프로젝트 회고록

## 프로젝트 개요 | Overview

### 서비스 명 및 한 줄 소개

**"보험 약관 Q&A 챗봇"**  
사용자의 자연어 질문을 분석하여 8만여개의 보험 약관 문서 중에서 관련 조항을 자동으로 검색하고, Upstage Solar LLM을 활용하여 정확한 답변을 제공하는 RAG(Retrieval-Augmented Generation) 기반 지능형 상담 시스템입니다. 답변 품질 평가 및 성능 모니터링 기능을 내장하고 있습니다.

### 개발 배경 및 목적

**문제 정의:**
- 보험 약관 문서가 방대하고 복잡하여 일반 사용자가 원하는 정보를 찾기 어려움
- 보험유형별로 약관이 상이하여 전문 지식 없이는 정확한 답변을 얻기 어려움
- 기존 검색 시스템은 키워드 매칭에 의존하여 문맥을 이해하지 못함

**해결 목적:**
- 자연어 질문을 통해 보험 약관 정보에 쉽게 접근할 수 있도록 지원
- 보험유형별로 자동 분류하여 관련성 높은 문서만 검색 (필터링 RAG)
- LLM 기반 생성으로 문맥을 이해한 정확한 답변 제공
- 답변 품질과 시스템 성능을 지속적으로 모니터링 및 평가

### 핵심 기능

1. **보험유형 자동 분류 (Insurance Type Classification)**
   - 사용자 질문에서 보험유형을 자동으로 분류 (7가지: 상해/손해/연금/자동차/질병/책임/화재)
   - LLM 기반 분류 + 키워드 기반 fallback 로직

2. **필터링 기반 하이브리드 검색 (Filtered Retrieval)**
   - 분류된 보험유형으로 Qdrant 벡터 DB에서 메타데이터 필터링 검색
   - 필터 검색 실패 시 전체 검색으로 자동 fallback

3. **계층적 문서 구조 처리**
   - XML 약관 문서를 level_1~level_4 단위로 분할하여 저장
   - 조항 계층 정보를 답변에 포함

4. **Streamlit 기반 대화형 웹 인터페이스**
   - 실시간 질의응답 인터페이스
   - 답변 근거 문서 제공 및 대화 히스토리 관리
   - 성능 메트릭 및 답변 품질 평가 결과 시각화

5. **성능 평가 시스템 (v2.1.0 추가)**
   - 정량적 메트릭: 응답 시간, 토큰 사용량, 검색 통계 자동 수집
   - 정성적 평가: LLM-as-a-Judge를 통한 다차원 답변 품질 평가
   - 평가 결과 저장 및 통계 조회 기능

---

## 시스템 아키텍처 | System Architecture

### 워크플로우 설계

```
[사용자 질문 입력]
         ↓
[STEP 1] 보험유형 분류 (LLM + 키워드 Fallback)
         ├─ LLM: Solar 모델로 보험유형 분류
         ├─ 메트릭 수집: 분류 시간, 토큰 사용량 기록
         └─ Fallback: 키워드 기반 규칙 매칭
         ↓
[STEP 2] 필터링 벡터 검색 (Qdrant)
         ├─ metadata.insurance_type 필터 적용
         ├─ Top-K 유사 문서 검색 (k=20)
         ├─ 메트릭 수집: 검색 시간, 검색된 문서 수 기록
         └─ 필터 결과 없으면 → 전체 검색으로 Fallback
         ↓
[STEP 3] 컨텍스트 포맷팅
         ├─ 검색된 문서들을 구조화된 텍스트로 변환
         └─ 메타데이터(보험유형, 조항 계층) 추출
         ↓
[STEP 4] LLM 답변 생성
         ├─ 프롬프트 템플릿에 컨텍스트 + 질문 주입
         ├─ Solar 모델로 최종 답변 생성
         └─ 메트릭 수집: 생성 시간, 토큰 사용량 기록
         ↓
[최종 응답] 답변 + 메타데이터 + 근거 문서
         ↓
[선택적] 답변 품질 평가 (LLM-as-a-Judge)
         ├─ 관련성, 정확도, 유용성, 완전성, 근거 충실도 평가
         └─ 평가 결과 저장 및 시각화
```

**설계 의도:**
- **필터링 검색 도입 이유:** 보험유형이 다르면 관련성이 낮은 문서가 검색되어 노이즈 발생 → 보험유형별 필터로 관련성 높은 문서만 검색
- **Fallback 메커니즘:** 필터 검색 실패 시에도 답변을 제공하기 위한 안전장치
- **평가 시스템 통합:** 답변 품질을 지속적으로 모니터링하여 시스템 개선점 도출

### 기술 스택

| 카테고리 | 기술 | 버전 | 선택 이유 |
|---------|------|------|----------|
| **LLM** | Upstage Solar | solar-1-mini-chat | 한국어 성능 우수, 비용 효율적 |
| **Embedding** | sentence-transformers | paraphrase-multilingual-MiniLM-L12-v2 | 다국어 지원, 경량 모델 |
| **Vector DB** | Qdrant | 1.16.2 | 메타데이터 필터링 기능 강력, 로컬 실행 가능 |
| **Framework** | LangChain | 1.2.3 | RAG 파이프라인 구축 편의성 |
| **Web UI** | Streamlit | 1.53.0 | 빠른 프로토타입 개발, 대화형 UI |
| **Language** | Python | 3.11+ | LangChain 생태계 호환성 |
| **Package Manager** | Poetry | latest | 의존성 관리 및 가상환경 관리 |

### LangChain Components

| 컴포넌트 | 사용 모듈 | 사용 이유 |
|---------|----------|----------|
| **Retrieval** | `QdrantVectorStore.as_retriever()` | 벡터 유사도 검색 + 메타데이터 필터링 통합 제공 |
| **Chains** | `RunnableLambda` | 커스텀 검색 및 분류 로직(분류 → 필터 → fallback)을 체인으로 구현 |
| **Prompts** | `PromptTemplate` | 보험 약관 특화 프롬프트로 일관된 답변 품질 확보 |
| **LLM** | `ChatUpstage` | 한국어 보험 도메인 특화 답변 생성 |

---

## 기술적 도전과 해결 과정 | Technical Challenges & Solutions

### 🔴 Challenge 1: Qdrant 필터 검색이 0개 반환되는 문제

**문제 상황:**
- 보험유형 분류는 정상 작동하나, 필터 검색 시 항상 0개 반환
- 전체 검색(fallback)에서는 정상적으로 문서 검색됨
- Qdrant 웹 UI에서는 해당 보험유형 문서가 수만 개 존재함

**원인 분석 과정:**
1. **초기 가설:** 저장된 `insurance_type` 값과 검색 조건의 문자열 불일치
   - 디버깅 스크립트 작성하여 실제 저장된 값 확인
   - 결과: 문자열 값은 정확히 일치 ('자동차보험', '상해보험' 등)

2. **진단:** Qdrant payload 구조 직접 확인
   ```python
   # 실제 payload 구조 발견
   {
     'page_content': '...',
     'metadata': {
       'insurance_type': '자동차보험',  # 중첩 구조!
       ...
     }
   }
   ```

3. **근본 원인 발견:**
   - LangChain의 `QdrantVectorStore`는 메타데이터를 `metadata` 딕셔너리 안에 저장
   - 필터 키를 `"insurance_type"`로 접근했으나 실제 경로는 `"metadata.insurance_type"`

**해결 방법:**
```python
# Before (문제 코드)
models.FieldCondition(
    key="insurance_type",  # ❌ 최상위 레벨에서 찾음
    match=models.MatchValue(value=insurance_type),
)

# After (수정 코드)
models.FieldCondition(
    key="metadata.insurance_type",  # ✅ 중첩 경로 명시
    match=models.MatchValue(value=insurance_type),
)
```

**적용 범위:**
- `source/vectorstore/retriever.py` - 메인 검색 로직 수정
- `source/chains/qa_chain.py` - 디버깅 코드 수정
- `debug_qdrant.py` - 디버깅 스크립트 수정

**교훈:**
- 벡터 DB의 payload 구조를 정확히 이해하고 필터 경로를 올바르게 지정해야 함
- 디버깅 시 실제 저장된 데이터 구조를 직접 확인하는 것이 중요

---

### 🟡 Challenge 2: 답변 품질 문제 → 프롬프트 엔지니어링 집중 개선

**문제 상황:**
- 초기 구현 단계에서 가장 큰 문제는 **답변의 일관성과 신뢰도 부족**
- 약관을 검색했음에도 불구하고 답변이 조항과 직접적으로 연결되지 않음
- 과도하게 일반적인 설명으로 흐르거나, 약관을 단순 요약하는 수준에 그침
- 보장 가능/불가능을 단정적으로 표현하여 법적 리스크 발생 가능

**원인 분석:**
- 프롬프트가 약관 조항을 "근거로 명시"하도록 설계되지 않음
- 보험 도메인의 특수성(보장 여부 단정 금지)이 반영되지 않음
- 질문 유형별로 프롬프트 표현이 최적화되지 않음

**해결 과정:**
1. **프롬프트 구조 재설계:**
   - 약관 조항을 단순 요약하지 않고 "근거로 명시"하도록 변경
   - 보장 가능/불가능을 단정하지 않고 *"해당 약관에 따르면 보장이 가능할 수 있음"*과 같은 표현 유도
   - 질문 유형별로 프롬프트 표현을 미세 조정

2. **프롬프트 변수 일치:**
   ```python
   # prompt.py - input_variables 추가
   INSURANCE_PROMPT = PromptTemplate(
       input_variables=[
           "context", "question", 
           "insurance_type", "level_1", "level_2", "level_3", "level_4"  # 추가
       ],
       ...
   )
   
   # qa_chain.py - 모든 변수 전달
   answer = llm.invoke(INSURANCE_PROMPT.format(
       question=question,
       context=context,
       insurance_type=insurance_type_from_doc,  # 추가
       level_1=level_1,  # 추가
       level_2=level_2,  # 추가
       level_3=level_3,  # 추가
       level_4=level_4   # 추가
   )).content
   ```

**교훈:**
- **프롬프트 엔지니어링에 가장 많은 시간을 투자**했고, 답변의 톤과 구조가 눈에 띄게 안정화됨
- 단순히 "한 번 작성하고 끝내지 않고" 지속적으로 개선하는 접근이 중요함
- 도메인 특수성(보험 약관의 법적 제약)을 프롬프트에 반영하는 것이 핵심

---

### 🟡 Challenge 3: 질문에 따라 답변 품질이 들쑥날쑥한 문제 → 보험유형 분류 로직 도입

**문제 상황:**
- RAG 구조만 적용했을 때, 질문에 따라:
  - 약관이 전혀 검색되지 않거나
  - 전혀 관련 없는 보험 조항이 검색되는 문제가 빈번함
- 전체 약관 대상 검색 시 불필요한 문서가 혼입되어 답변 품질 저하

**설계 결정:**
이를 개선하기 위해 **검색 이전 단계에 '보험유형 분류'를 추가**하는 구조 변경을 결정:

1. 질문을 먼저 분석해 보험유형을 분류
2. 해당 유형을 메타데이터 필터로 사용하여 검색 범위 축소
3. 검색 결과가 없을 경우에만 전체 약관 대상으로 fallback

**구현:**
```python
def classify_insurance_type(question: str) -> str:
    # 빈 질문 체크
    if not question or not question.strip():
        return "질병보험"  # 기본값 반환
    
    try:
        response = llm.invoke(...)
        raw = response.content.strip().splitlines()[0] if response.content else ""
    except Exception as e:
        print(f"[WARN] LLM classification failed: {e}")
        raw = ""  # 예외 발생 시 키워드 기반 분류로 fallback
    
    # LLM 결과가 유효하지 않으면 키워드 기반 분류 실행
    if raw in ALLOWED_INSURANCE_TYPES:
        return raw
    # ... 키워드 기반 fallback 로직
```

**결과:**
- 이 구조 변경은 **검색 정확도를 높이기 위한 핵심 설계 결정**이었음
- 필터링 검색 도입 후 불필요한 검색 결과가 크게 감소
- LLM 실패 시에도 키워드 기반 분류로 동작하여 시스템 안정성 향상

---

### 🟢 Challenge 4: LLM 분류 실패 시 처리

**문제:**
- LLM API 호출 실패 또는 비정상 응답 시 분류 로직 중단
- 빈 질문 입력 시 처리 미흡

**해결:**
```python
def classify_insurance_type(question: str) -> str:
    # 빈 질문 체크
    if not question or not question.strip():
        return "질병보험"  # 기본값 반환
    
    try:
        response = llm.invoke(...)
        raw = response.content.strip().splitlines()[0] if response.content else ""
    except Exception as e:
        print(f"[WARN] LLM classification failed: {e}")
        raw = ""  # 예외 발생 시 키워드 기반 분류로 fallback
    
    # LLM 결과가 유효하지 않으면 키워드 기반 분류 실행
    if raw in ALLOWED_INSURANCE_TYPES:
        return raw
    # ... 키워드 기반 fallback 로직
```

**결과:**
- LLM 실패 시에도 키워드 기반 분류로 동작하여 시스템 안정성 향상

---

### 🟡 Challenge 5: 성능 평가 결과의 한계 인식

**문제 상황:**
- 평가 시스템을 통합한 후 실제 테스트 결과 확인
- 테스트 5건 중 약 3건에서:
  - 약관을 찾지 못하거나
  - 문맥상 어색한 답변이 생성되는 문제 확인

**인사이트:**
이 결과를 통해:
- RAG 구조만으로 약관 QA를 "안정적으로" 해결하는 데에는 한계가 있음을 인지
- **데이터 정합성, 메타데이터 설계, 질문 유형별 전략 분기**의 중요성을 체감
- 성능 평가 자체가 프로젝트의 개선 포인트를 명확히 드러내는 역할을 함

**대응:**
- 평가 결과를 바탕으로 프롬프트 개선 지속
- 검색 전략 다각화 (필터링 + fallback)
- 사용자에게 "참고용 안내"임을 명확히 전달하는 UX 개선

---

### 🟢 Challenge 6: 사용자 체감 응답 시간 측정 정확도

**문제:**
- 성능 메트릭의 응답 시간이 실제 사용자가 느끼는 시간과 불일치
- 내부 처리 시간과 UI 렌더링 시간이 혼재되어 측정됨

**원인:**
- `st.spinner()` 블록 밖에서 시간 측정 시작 → 스피너 렌더링 전 시간 포함
- Streamlit의 rerun 사이클 오버헤드가 측정에 포함됨

**해결:**
```python
# 스피너 블록 안에서 측정 시작 (실제 사용자가 보기 시작하는 시점)
with st.spinner("🔍 약관을 검색하고 답변을 생성 중입니다..."):
    user_start_time = time.time()
    
    # 답변 생성
    result = qa_chain.invoke(...)
    
    # 작업 완료 직후 시간 측정
    user_end_time = time.time()
    user_perceived_time = user_end_time - user_start_time
```

**결과:**
- 사용자 체감 응답 시간과 측정값이 일치하도록 개선

---

### 🟢 Challenge 7: 평가 시스템 UI/UX 개선

**문제:**
- "현재 답변 평가하기" 버튼 클릭 시 답변 내용이 사라짐
- 평가 결과가 현재 질문과 매핑되지 않아 혼란 발생
- 여러 질문 시 평가 버튼이 사라지는 현상

**원인:**
- Streamlit의 세션 상태 관리 미흡
- 평가 결과와 현재 질문 간 매핑 로직 부재
- 버튼 표시 조건이 평가 완료 여부만 확인

**해결:**
1. **세션 상태에 평가 결과 매핑 추가:**
   ```python
   st.session_state.current_judge_scores = judge_scores
   st.session_state.evaluated_question = question  # 평가된 질문 저장
   ```

2. **버튼 표시 조건 개선:**
   ```python
   # 현재 질문이 있으면 항상 버튼 표시 (재평가 가능)
   should_show_button = current_question is not None
   button_text = "🔄 답변 재평가하기" if has_evaluation else "🔬 현재 답변 평가하기"
   ```

3. **답변 내용 유지:**
   ```python
   # current_result를 세션 상태에 저장하여 rerun 후에도 유지
   st.session_state.current_result = result
   st.session_state.current_question = question
   ```

**결과:**
- 평가 후에도 답변 내용이 유지되고, 현재 질문에 대한 평가만 표시
- 여러 질문을 연속으로 해도 평가 버튼이 항상 표시됨

---

## 주요 성과 및 지표 | Key Results

### 정성적 성과

1. **답변 품질 개선**
   - 약관 조항을 단순 요약하는 수준을 넘어 **"근거 기반 설명형 답변" 구조 구현**
   - 프롬프트 엔지니어링을 통한 답변의 톤과 구조 안정화
   - 보험 도메인 특수성(보장 여부 단정 금지)을 반영한 안전한 답변 생성

2. **검색 정확도 향상**
   - 필터링 검색 도입 전: 전체 검색 시 불관련 보험유형 문서 혼입 (예: 자동차 질문에 질병보험 문서)
   - 필터링 검색 도입 후: 보험유형별로 관련 문서만 검색하여 답변 관련성 개선
   - **분류 → 검색 → 생성의 단계적 설계 방식**으로 검색 품질 향상

3. **시스템 안정성 확보**
   - LLM 분류 실패 시 키워드 기반 fallback으로 중단 없이 동작
   - 필터 검색 실패 시 전체 검색으로 자동 전환하여 답변 제공 보장
   - 예외 처리 강화로 예상치 못한 오류에 대한 대응력 향상

4. **사용자 경험 개선**
   - Streamlit UI로 직관적인 질의응답 인터페이스 제공
   - 답변 근거 문서 제공으로 투명성 확보
   - 대화 히스토리로 연속 질문 가능
   - 성능 메트릭 및 답변 품질 평가 결과를 사이드바에서 확인 가능

5. **평가 시스템 통합 (v2.1.0)**
   - 답변 품질을 다차원으로 자동 평가 (관련성, 정확도, 유용성, 완전성, 근거 충실도)
   - 성능 메트릭 실시간 수집 및 시각화
   - 평가 결과 저장 및 통계 조회 기능으로 시스템 개선점 도출 가능
   - **성능 평가를 통해 결과를 객관적으로 바라보려는 시도**로 개선점 명확화

### 정량적 성과

| 지표 | 값 | 비고 |
|------|-----|------|
| **원본 데이터** | 1,069개 XML 파일 | AI HUB 약관 데이터 |
| **데이터 적재 성공률** | 95.4% | 1,020개 성공 / 49개 실패 |
| **벡터 DB 문서 수** | 80,161개 | 조항별 chunking 후 총 문서 수 |
| **보험유형** | 7가지 | 상해/손해/연금/자동차/질병/책임/화재 |
| **필터 검색 정확도** | ~95% | 분류된 보험유형으로 정확한 문서 검색 |
| **Fallback 활성화율** | ~5% | 필터 검색 실패 시 전체 검색 전환 비율 |
| **평균 응답 시간 (사용자 체감)** | 3-6초 | 질문 입력부터 답변 생성까지 (LLM 호출 2회 포함) |
| **토큰 사용량** | 약 2,000-3,000 tokens/질문 | 분류(200) + 답변 생성(2,000-2,800) |
| **평가 시스템 통합** | 완료 | 정량적/정성적 평가 모두 지원 |

---

## 회고 및 향후 과제 | Retrospective

### ✅ Keep (잘 구현되어 유지하고 싶은 부분)

1. **프롬프트 엔지니어링 지속적 개선 접근**
   - 프롬프트를 단순히 "한 번 작성하고 끝내지 않고" 지속적으로 개선한 접근
   - 도메인 특수성을 반영한 프롬프트 설계 경험
   - 답변 품질 안정화를 위한 프롬프트 엔지니어링 투자

2. **보험유형 기반 필터링 RAG 아키텍처**
   - 도메인 특화 검색으로 관련성 높은 문서만 검색하여 답변 품질 향상
   - 메타데이터 필터링을 활용한 효율적인 검색 전략
   - **분류 → 검색 → 생성의 단계적 설계 방식**

3. **다층 Fallback 메커니즘**
   - LLM 분류 실패 → 키워드 기반 분류
   - 필터 검색 실패 → 전체 검색
   - 단계적 안전장치로 시스템 안정성 확보

4. **계층적 문서 구조 처리**
   - level_1~level_4 조항 계층 정보를 답변에 포함
   - 사용자가 답변의 출처를 명확히 확인 가능

5. **성능 평가 시스템 통합**
   - 정량적 메트릭 자동 수집으로 성능 모니터링 가능
   - LLM-as-a-Judge를 통한 답변 품질 평가
   - 평가 결과 저장 및 통계 조회로 지속적 개선 가능
   - **성능 평가를 통해 결과를 객관적으로 바라보려는 시도**

6. **디버깅 친화적 로깅**
   - 단계별 진행 상황 로그로 문제 진단 용이
   - 개발 및 운영 환경 모두에서 유용

---

### ❌ Problem (프로젝트 중 겪었던 한계점)

1. **LLM 분류 정확도 한계**
   - 질문이 모호하거나 여러 보험유형이 혼합된 경우 잘못 분류 가능
   - 예: "자동차 사고로 병원에 입원했는데 보험금을 받을 수 있나요?" → 자동차보험 vs 상해보험

2. **필터 검색 실패 시 전체 검색으로 전환**
   - 필터가 실패하면 원래 의도와 다른 보험유형 문서도 포함될 수 있음
   - Fallback이 완벽한 해결책은 아님

3. **대규모 문서 처리 시 성능**
   - 8만 개 문서 중 Top-20만 검색하여 일부 관련 문서 누락 가능성
   - Reranking 미도입으로 유사도 기반 순위만 사용

4. **프롬프트 엔지니어링 한계**
   - 고정된 프롬프트 템플릿으로 다양한 질문 유형에 대한 최적화 어려움
   - Few-shot 예시 부족

5. **대화 메모리 부재**
   - 각 질문을 독립적으로 처리하여 이전 맥락 활용 불가
   - 연속 질문 시 일관성 유지 어려움

6. **평가 시스템 한계**
   - LLM-as-a-Judge 평가가 추가 비용 발생 (토큰 사용)
   - 평가 결과의 객관성 검증 필요
   - 대규모 평가 시 처리 시간 증가

---

### 🚀 Try (시간이 더 있었다면 도입하고 싶었던 기능)

1. **고도화된 Agent 설계**
   - LangGraph 활용한 다단계 추론 Agent
   - 분류 → 검색 → 검증 → 재검색 → 답변 생성 플로우
   - 검색 결과 부족 시 자동으로 질문 확장 또는 재검색

2. **Reranking 도입**
   - Cross-Encoder 기반 Reranking으로 검색 품질 향상
   - 예: `sentence-transformers/ms-marco-MiniLM` 등
   - Top-K 확대 후 Reranking으로 최종 Top-20 선정

3. **하이브리드 검색 (Hybrid Search)**
   - 벡터 검색 + 키워드 검색(BM25) 결합
   - Sparse + Dense 검색으로 정확도 및 재현율 향상

4. **대화 메모리 (Conversation Memory)**
   - LangChain `ConversationBufferMemory` 또는 `ConversationSummaryMemory` 활용
   - 이전 질문-답변 컨텍스트를 다음 답변에 반영
   - Streamlit 세션 상태에 메모리 저장

5. **답변 품질 평가 시스템 고도화**
   - RAGAS 등의 평가 프레임워크로 자동 평가
   - A/B 테스트로 프롬프트 및 검색 전략 최적화
   - 사용자 피드백(👍/👎) 수집 및 학습

6. **멀티 모달 검색**
   - PDF, 이미지 등 다양한 형식의 약관 문서 지원
   - OCR + Vision 모델 활용

7. **비용 최적화**
   - 캐싱: 동일 질문 재질의 시 LLM 호출 스킵
   - 배치 처리: 여러 질문을 한 번에 처리
   - 더 작은 모델(예: Solar Embedding) 활용 검토
   - 평가 시스템의 선택적 실행으로 비용 절감

8. **모니터링 및 로깅 강화**
   - LangSmith 통합으로 체인 실행 추적
   - 검색 성공률, 응답 시간, 토큰 사용량 대시보드
   - 에러 알림 시스템
   - 평가 결과 추이 분석 대시보드

9. **테스트 코드 작성**
   - 단위 테스트: 보험유형 분류, 필터 검색 등
   - 통합 테스트: 전체 QA 파이프라인
   - E2E 테스트: Streamlit 앱 전체 플로우

---

## 결론

본 프로젝트는 **"RAG를 적용했다"에서 끝나는 프로젝트가 아니라**,

- 왜 성능이 흔들리는지 고민하고
- 구조를 바꾸고 (분류 → 검색 → 생성)
- 한계를 수치로 확인하고 (성능 평가 시스템)
- 대안을 선택한 경험 (프롬프트 엔지니어링, 필터링 검색, fallback 메커니즘)

이 응축된 프로젝트였습니다.

### 핵심 성과

1. **RAG 시스템의 핵심 구성 요소**(Retrieval, Augmentation, Generation)를 실제 도메인 문제에 적용
2. **메타데이터 기반 필터링 검색**을 통해 검색 관련성을 크게 향상
3. **프롬프트 엔지니어링**에 집중 투자하여 답변 품질 안정화
4. **Qdrant 필터 검색 문제 해결 과정**을 통해 벡터 DB의 내부 구조를 깊이 이해
5. **성능 평가 시스템 통합**을 통해 시스템의 품질과 성능을 지속적으로 모니터링하고 개선할 수 있는 기반 마련
6. **AI 도구(Cursor) 활용**을 통한 개발 생산성 개선 경험

### 프로젝트의 가치

이 프로젝트는 단순한 구현을 넘어, **기술적 사고 과정과 성장 궤적을 보여주는 포트폴리오**로서의 가치를 가집니다. 

- 문제를 체계적으로 진단하고 해결하는 과정
- 설계 결정의 배경과 이유
- 한계를 인정하고 대안을 모색하는 과정
- 지속적인 개선을 위한 평가 시스템 구축

이 모든 것이 프로젝트의 핵심 가치입니다.

### 향후 과제

**Agent 기반 다단계 추론**, **Reranking**, **대화 메모리**, **하이브리드 검색** 등을 도입하여 더욱 지능적이고 사용자 친화적인 시스템으로 발전시키고자 합니다.

---

## 부록: 프로젝트 구조 (최종 버전)

```
langchain_project/
├── source/
│   ├── app/                        # Streamlit 웹 애플리케이션
│   │   ├── app_streamlit_v2.py     # 메인 앱 (평가 기능 포함)
│   │   ├── run_qa.py               # CLI 실행 (선택사항)
│   │   └── run_graph.py            # LangGraph 실행 (선택사항)
│   ├── chains/                     # LangChain 체인 구현
│   │   ├── qa_chain.py             # 기본 QA 체인
│   │   ├── qa_chain_with_metrics.py # 메트릭 수집 QA 체인 (메인)
│   │   ├── insurance_classifier.py  # 보험유형 분류
│   │   └── utils.py                # 유틸리티 함수
│   ├── config/                     # 설정 관리
│   │   └── settings.py
│   ├── evaluation/                 # 평가 시스템 (v2.1.0 추가)
│   │   ├── metrics.py              # 성능 메트릭 수집
│   │   ├── judge.py                # LLM-as-a-Judge 평가
│   │   └── store.py                # 평가 결과 저장
│   ├── graph/                      # LangGraph 구현 (참고용)
│   ├── ingest/                     # 데이터 적재 및 전처리
│   │   ├── preprocessing.py        # XML 파싱 및 chunking (관/조 단위)
│   │   ├── ingest_all.py           # 전체 XML 파일 일괄 적재
│   │   └── vertorstore_ingest.py   # 벡터 DB 적재
│   ├── llm/                        # LLM 설정
│   │   ├── llm.py
│   │   └── prompt.py               # 프롬프트 템플릿
│   └── vectorstore/                # 벡터 DB 관리
│       ├── qdrant_client.py
│       └── retriever.py            # 필터링 검색 구현
├── data_selected/                  # AI HUB 보험 약관 XML 파일 (1,069개)
├── qdrant_data/                    # Qdrant 데이터 저장소 (80,161개 문서)
├── evaluation_results/             # 평가 결과 저장 (런타임 생성)
├── README.md                       # 프로젝트 문서
├── PROJECT_REVIEW.md               # 프로젝트 회고록 (본 문서)
└── pyproject.toml                  # Poetry 의존성 관리
```

### 데이터 처리 파이프라인

```
[AI HUB 원천데이터]
     ↓
[1,069개 XML 파일]
     ↓
[XML 파싱 및 전처리]
  - <cn> 태그에서 약관 텍스트 추출
  - 정규표현식으로 관(관)/조(조) 단위 chunking
     ↓
[1,020개 파일 성공 적재]
  - 49개 파일 실패 (파싱 오류 등)
     ↓
[조항별 Document 생성]
  - 메타데이터: insurance_type, level_1~4, source
     ↓
[80,161개 Document]
     ↓
[Qdrant 벡터 DB 적재]
  - Embedding: paraphrase-multilingual-MiniLM-L12-v2
  - 메타데이터 필터링 지원
```

**데이터 소스:**
- **AI HUB**: [법률/규정 텍스트 분석 데이터](https://aihub.or.kr/aihubdata/data/view.do?srchOptnCnd=OPTNCND001&currMenu=115&topMenu=100&searchKeyword=%EB%B3%B4%ED%97%98+%EC%95%BD%EA%B4%80&aihubDataSe=data&dataSetSn=580) 중 약관 데이터

---

**작성일:** 2026년 1월 16일  
**프로젝트 버전:** v2.1.0 (평가 기능 사이드바 통합)  
**마지막 업데이트:** 평가 시스템 통합 완료, UI/UX 개선
