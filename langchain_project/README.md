# 🏠 보험 약관 Q&A 챗봇

> Upstage Solar 모델 기반의 지능형 보험 상담 시스템  
> RAG(Retrieval-Augmented Generation) 기술을 활용한 보험 약관 질의응답 시스템

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [프로젝트 구조](#-프로젝트-구조)
- [설치 및 실행](#-설치-및-실행)
- [설정](#-설정)
- [평가 시스템](#-평가-시스템)
- [사용 예시](#-사용-예시)
- [문제 해결](#-문제-해결)

## 🎯 프로젝트 개요

본 프로젝트는 **AI HUB의 보험 약관 원천데이터**를 벡터 데이터베이스에 저장하고, 사용자의 자연어 질문에 대해 관련 약관 조항을 검색하여 정확한 답변을 제공하는 RAG 기반 질의응답 시스템입니다.

### 데이터 소스

- **원천데이터**: [AI HUB - 법률/규정 텍스트 분석 데이터](https://aihub.or.kr/aihubdata/data/view.do?srchOptnCnd=OPTNCND001&currMenu=115&topMenu=100&searchKeyword=%EB%B3%B4%ED%97%98+%EC%95%BD%EA%B4%80&aihubDataSe=data&dataSetSn=580) 중 약관 데이터
- **원본 파일**: 총 1,069개 XML 파일
- **적재 결과**: 1,020개 파일 성공 (49개 파일 실패)
- **최종 문서 수**: 80,161개 문서 (조항별 전처리 후)
- **데이터 형식**: XML 파일 내 전체 텍스트 형태의 약관 문서
- **전처리 방식**: 정규표현식을 사용하여 관(관)/조(조) 단위로 chunking

**XML 구조 예시:**
- `<category>`: 보험유형 (예: "12. 상해보험")
- `<name>`: 파일명 (예: "001_상해보험_가공.xml")
- `<cn>`: 실제 약관 내용 (CDATA 섹션)

**Chunking 규칙:**
- 일반 보험: `제X관` → `제Y조` 단위로 분할
- 자동차보험: `제X편` → `제Y장` → `제Z절` → `제W조` 단위로 분할

### 핵심 가치

- 🔍 **정확한 검색**: 보험유형 자동 분류를 통한 필터링 검색으로 관련성 높은 문서만 검색
- 📚 **구조화된 답변**: 계층적 약관 구조(level_1~level_4)를 활용한 명확한 조항 참조
- ⚡ **실시간 성능 모니터링**: 응답 시간, 토큰 사용량, 답변 품질 평가 기능 내장
- 🤖 **LLM 기반 지능형 분류**: Upstage Solar 모델을 활용한 보험유형 자동 분류

### 해결하는 문제

- 보험 약관 문서가 방대하고 복잡하여 일반 사용자가 원하는 정보를 찾기 어려움
- 보험유형별로 약관이 상이하여 전문 지식 없이는 정확한 답변을 얻기 어려움
- 기존 검색 시스템은 키워드 매칭에 의존하여 문맥을 이해하지 못함

## ✨ 주요 기능

### 1. 보험유형 자동 분류 (Insurance Type Classification)
- 사용자 질문을 분석하여 7가지 보험유형 중 적절한 유형을 자동으로 분류
- **지원 보험유형**: 상해보험, 손해보험, 연금보험, 자동차보험, 질병보험, 책임보험, 화재보험
- LLM 기반 분류 + 키워드 기반 Fallback 로직

### 2. 필터링 기반 하이브리드 검색 (Filtered Retrieval)
- 분류된 보험유형으로 Qdrant 벡터 DB에서 메타데이터 필터링 검색
- 필터 검색 실패 시 전체 검색으로 자동 Fallback
- Top-K 유사도 기반 검색 (기본값: 20개 문서)

### 3. 계층적 문서 구조 처리
- XML 약관 문서를 level_1~level_4 단위로 분할하여 저장
- 조항 계층 정보를 답변에 포함하여 정확한 조항 위치 제공

### 4. Streamlit 기반 대화형 웹 인터페이스
- 실시간 질의응답 인터페이스
- 답변 근거 문서 제공 및 대화 히스토리 관리
- 답변 품질 평가 및 성능 메트릭 시각화

### 5. 성능 평가 시스템
- **정량적 메트릭**: 응답 시간, 토큰 사용량, 검색 통계
- **정성적 평가**: LLM-as-a-Judge를 통한 답변 품질 평가 (관련성, 정확도, 유용성, 완전성, 근거 충실도)
- 평가 결과 저장 및 통계 조회 기능

## 🛠 기술 스택

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
| **Chains** | `RunnableLambda` | 커스텀 검색 및 분류 로직을 체인으로 구성 |
| **LLM** | `ChatUpstage` | Upstage Solar 모델 통합 |
| **Embeddings** | `HuggingFaceEmbeddings` | 다국어 임베딩 모델 지원 |

## 📁 프로젝트 구조

```
langchain_project/
├── source/
│   ├── app/
│   │   ├── app_streamlit_v2.py      # 메인 Streamlit 앱 (평가 기능 포함)
│   │   ├── run_qa.py                # CLI 기반 QA 실행
│   │   └── run_graph.py             # LangGraph 기반 실행
│   ├── chains/
│   │   ├── insurance_classifier.py  # 보험유형 분류 로직
│   │   ├── qa_chain.py              # 기본 QA 체인
│   │   ├── qa_chain_with_metrics.py # 메트릭 수집 기능 포함 QA 체인
│   │   └── utils.py                 # 유틸리티 함수
│   ├── config/
│   │   └── settings.py              # 설정 관리
│   ├── evaluation/
│   │   ├── metrics.py               # 성능 메트릭 수집
│   │   ├── judge.py                 # LLM-as-a-Judge 평가
│   │   └── store.py                 # 평가 결과 저장
│   ├── graph/
│   │   ├── graph.py                 # LangGraph 정의
│   │   ├── nodes/                   # 그래프 노드
│   │   └── state.py                 # 그래프 상태 정의
│   ├── ingest/
│   │   ├── ingest.py                # 문서 수집 및 전처리
│   │   ├── preprocessing.py         # XML 전처리
│   │   └── vertorstore_ingest.py    # 벡터 DB 적재
│   ├── llm/
│   │   ├── llm.py                   # LLM 초기화
│   │   └── prompt.py                # 프롬프트 템플릿
│   └── vectorstore/
│       ├── qdrant_client.py         # Qdrant 클라이언트
│       └── retriever.py             # 검색기 정의
├── data_selected/                   # 선택된 보험 문서 (XML)
├── qdrant_data/                     # Qdrant 벡터 DB 데이터
├── evaluation_results/              # 평가 결과 저장 디렉토리
├── pyproject.toml                   # Poetry 의존성 관리
└── README.md                        # 본 문서
```

## 🚀 설치 및 실행

### 사전 요구사항

- Python 3.11 이상
- Docker (Qdrant 실행용)
- Poetry (패키지 관리)
- Upstage API Key

### 1. 저장소 클론 및 의존성 설치

```bash
# 저장소 클론
git clone <repository-url>
cd langchain_project

# Poetry로 의존성 설치
poetry install
```

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가합니다:

```env
UPSTAGE_API_KEY=your_upstage_api_key_here
```

### 3. Qdrant 벡터 DB 실행

Docker를 사용하여 Qdrant를 실행합니다:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Qdrant가 정상적으로 실행되었는지 확인:

```bash
curl http://localhost:6333/health
```

### 4. 문서 수집 및 벡터 DB 적재 (최초 1회)

벡터 DB에 보험 약관 문서를 적재합니다:

```bash
# Poetry 환경에서 실행
poetry run python -m source.ingest.ingest_all
```

또는 개별 모듈 실행:

```bash
poetry run python -m source.ingest.ingest
poetry run python -m source.ingest.vertorstore_ingest
```

### 5. Streamlit 앱 실행

메인 애플리케이션 실행:

```bash
poetry run streamlit run source/app/app_streamlit_v2.py
```

브라우저에서 자동으로 열리며, 기본 URL은 `http://localhost:8501`입니다.

### CLI 기반 실행 (선택사항)

Streamlit 없이 터미널에서 질의응답:

```bash
poetry run python -m source.app.run_qa
```

## ⚙️ 설정

주요 설정은 `source/config/settings.py`에서 관리됩니다:

```python
# LLM 설정
UPSTAGE_MODEL = "solar-1-mini-chat"
TEMPERATURE = 0.0

# Embedding 모델
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Qdrant 설정
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "insurance_docs"

# 검색 설정
TOP_K = 20  # 검색할 문서 수
SCORE_THRESHOLD = 0.3  # 유사도 임계값

# 지원 보험유형
ALLOWED_INSURANCE_TYPES = {
    "상해보험", "손해보험", "연금보험",
    "자동차보험", "질병보험", "책임보험", "화재보험"
}
```

## 📊 평가 시스템

본 시스템은 답변 품질과 성능을 평가하기 위한 내장 평가 시스템을 제공합니다.

### 평가 메트릭

#### 정량적 메트릭
- **응답 시간**: 사용자 체감 응답 시간 (검색 + 생성 시간)
- **토큰 사용량**: 분류 및 생성에 사용된 토큰 수
- **검색 통계**: 검색된 문서 수, 필터 사용 여부, Fallback 발생 여부

#### 정성적 평가 (LLM-as-a-Judge)
- **관련성 (Relevance)**: 답변이 질문과 얼마나 관련 있는지
- **정확도 (Accuracy)**: 답변의 사실적 정확성
- **유용성 (Helpfulness)**: 답변이 사용자에게 얼마나 도움이 되는지
- **완전성 (Completeness)**: 답변이 질문에 완전히 답하는지
- **근거 충실도 (Groundedness)**: 답변이 검색된 문서에 얼마나 근거를 두고 있는지

### 평가 기능 사용

1. **자동 평가**: 사이드바에서 "자동 평가 활성화" 옵션을 체크하면 새 답변 생성 시 자동으로 평가합니다.
2. **수동 평가**: "현재 답변 평가하기" 버튼을 클릭하여 원하는 시점에 평가할 수 있습니다.
3. **평가 통계**: 사이드바에서 평가 통계를 확인하고 결과를 다운로드할 수 있습니다.

평가 결과는 `evaluation_results/evaluation_results.jsonl`에 저장됩니다.

자세한 내용은 다음 문서를 참고하세요:
- [평가 시스템 개요](EVALUATION_SYSTEM_OVERVIEW.md)
- [평가 사용 가이드](EVALUATION_USAGE.md)
- [빠른 시작 가이드](QUICK_START_EVALUATION.md)

## 💡 사용 예시

### 질문 예시

- "대중교통 이용 중 다쳤는데 보험 보장받을 수 있나요?"
- "음주운전 사고 시 보험 적용 가능한가요?"
- "뇌출혈로 진단 확정되면 어떤 보험금이 지급되나요? 청구 요건은 무엇인가요?"

### 워크플로우

```
[사용자 질문 입력]
         ↓
[STEP 1] 보험유형 분류 (LLM + 키워드 Fallback)
         ↓
[STEP 2] 필터링 벡터 검색 (Qdrant)
         ├─ metadata.insurance_type 필터 적용
         ├─ Top-K 유사 문서 검색
         └─ 필터 결과 없으면 → 전체 검색으로 Fallback
         ↓
[STEP 3] 컨텍스트 포맷팅
         ├─ 검색된 문서들을 구조화된 텍스트로 변환
         └─ 메타데이터(보험유형, 조항 계층) 추출
         ↓
[STEP 4] LLM 답변 생성
         ├─ 프롬프트 템플릿에 컨텍스트 + 질문 주입
         └─ Solar 모델로 최종 답변 생성
         ↓
[최종 응답] 답변 + 메타데이터 + 근거 문서
```

## 🔧 문제 해결

### Qdrant 연결 오류

**증상**: "Qdrant 서버 연결 실패" 오류

**해결 방법**:
1. Docker가 실행 중인지 확인: `docker ps`
2. Qdrant 컨테이너 실행: `docker run -p 6333:6333 qdrant/qdrant`
3. 페이지 새로고침 (F5)

### Upstage API Key 오류

**증상**: LLM 호출 실패

**해결 방법**:
1. `.env` 파일에 `UPSTAGE_API_KEY`가 올바르게 설정되어 있는지 확인
2. API Key가 유효한지 확인
3. Poetry 환경에서 실행 중인지 확인

### 벡터 DB에 문서가 없는 경우

**증상**: 검색 결과가 항상 0개

**해결 방법**:
1. 문서 수집 및 적재 스크립트 실행:
   ```bash
   poetry run python -m source.ingest.ingest_all
   ```
2. Qdrant 웹 UI에서 컬렉션 확인: `http://localhost:6333/dashboard`

### 평가 데이터 초기화

평가 결과를 초기화하려면:

```bash
# 평가 결과 파일 삭제
rm evaluation_results/evaluation_results.jsonl
```

## 📝 주요 파일 설명

- **`app_streamlit_v2.py`**: 평가 기능이 통합된 메인 Streamlit 애플리케이션
- **`qa_chain_with_metrics.py`**: 성능 메트릭 수집 기능이 포함된 QA 체인
- **`insurance_classifier.py`**: 보험유형 자동 분류 로직
- **`retriever.py`**: Qdrant 벡터 검색기 정의 및 필터링 로직

## ⚠️ 주의사항

- 본 시스템은 약관상 보장 가능성을 **참고용**으로 제공합니다.
- 실제 보험금 지급 여부는 보험사 심사 및 개별 사안에 따라 달라질 수 있습니다.
- 완벽한 보장 여부를 판단하지 않으며, 약관 조항을 근거로 한 정보 제공에 그칩니다.

## 📚 추가 문서

프로젝트 개발 과정 및 기술적 도전과 해결 과정에 대한 상세 내용은 다음 문서를 참고하세요:

- [프로젝트 회고록](PROJECT_REVIEW.md): 프로젝트 개발 배경, 기술적 도전과 해결 과정, KPT 회고

## 📄 라이선스

본 프로젝트는 교육 및 연구 목적으로 개발되었습니다.

## 👥 기여

이슈 및 개선 사항은 Issue 탭에서 제안해주세요.

---

**문의**: 프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.
