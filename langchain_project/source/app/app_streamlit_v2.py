import streamlit as st
import sys
from pathlib import Path
import time

# 프로젝트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from chains.qa_chain_with_metrics import get_qa_chain_with_metrics
from vectorstore.retriever import get_retriever
from evaluation.judge import LLMJudge
from evaluation.store import EvaluationStore

# Streamlit 페이지 설정
st.set_page_config(
    page_title="보험 약관 Q&A 챗봇",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .answer-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .source-box {
        background-color: #fff9e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
        margin-top: 1rem;
    }
    .error-box {
        background-color: #ffe6e6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff6b6b;
        margin-top: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
        margin-top: 1rem;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2196F3;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .metrics-box {
        background-color: #f0f8f0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #4CAF50;
        margin-top: 1rem;
    }
    .score-box {
        background-color: #fff5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #e91e63;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
    st.session_state.conversation_history = []
    st.session_state.qdrant_ready = False
    st.session_state.init_attempted = False
    st.session_state.enable_evaluation = True  # 평가 모드 기본값
    st.session_state.evaluation_store = EvaluationStore()
    st.session_state.judge = LLMJudge()
    # 최근 답변 유지용
    st.session_state.current_result = None
    st.session_state.current_question = None
    # 사용자 체감 시간 측정용
    st.session_state.question_start_time = None
    st.session_state.last_processed_question = None
    # 평가 결과를 현재 질문과 매핑
    st.session_state.current_judge_scores = None
    st.session_state.evaluated_question = None

# 헤더
st.markdown('<h1 class="main-header">🏠 보험 약관 Q&A 챗봇</h1>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #666; margin-bottom: 1rem;">
    <p style="font-size: 1.1rem; font-weight: 500; margin-bottom: 0.5rem;">Upstage Solar 모델 기반의 지능형 보험 상담 시스템</p>
    <p style="margin-bottom: 1rem;">정확한 약관 조항을 근거로 답변해드립니다</p>
</div>
""", unsafe_allow_html=True)

# 기능 및 기술 설명 (접기 가능)
with st.expander("ℹ️ 시스템 안내", expanded=False):
    st.markdown("""
    ### 💡 기능
    
    본 시스템은 **RAG(Retrieval-Augmented Generation)** 기술을 활용하여 사용자의 질문을 분석하고, 
    8만여 개의 보험 약관 문서 중에서 관련 조항을 자동으로 검색합니다.
    
    - 📋 **보험유형 자동 분류**: 질문 내용을 분석하여 7가지 보험유형 중 적절한 유형을 자동으로 분류
    - 🔍 **필터링 검색**: 분류된 보험유형으로 관련 문서만 선별하여 검색 정확도 향상
    - 📚 **계층적 조항 참조**: 약관의 level_1~level_4 구조를 활용하여 정확한 조항 정보 제공
    - 🤖 **AI 기반 답변 생성**: 검색된 약관 조항을 근거로 LLM이 구조화된 답변 생성
    
    ⚠️ **중요 안내**
    - 본 시스템은 약관상 보장 가능성을 **참고용**으로 제공합니다
    - 실제 보험금 지급 여부는 보험사 심사 및 개별 사안에 따라 달라질 수 있습니다
    - 완벽한 보장 여부를 판단하지 않으며, 약관 조항을 근거로 한 정보 제공에 그칩니다
    
    ---
    
    ### ⚡ 기술 스택
    
    **핵심 기술**
    - **LangChain**: RAG 파이프라인 구축 및 체인 관리
    - **Upstage Solar LLM**: 한국어 최적화된 대규모 언어 모델
    - **Qdrant Vector DB**: 벡터 유사도 검색 및 메타데이터 필터링
    - **Sentence Transformers**: 다국어 임베딩 모델
    
    **검색 방식**
    - **하이브리드 검색**: 보험유형 필터링 + 벡터 유사도 검색
    - **Fallback 메커니즘**: 필터 검색 실패 시 전체 검색으로 자동 전환
    - **Top-K 검색**: 유사도 기반 상위 20개 문서 검색
    
    **품질 보장**
    - **LLM-as-a-Judge**: 답변 품질을 다차원으로 자동 평가
    - **성능 모니터링**: 응답 시간, 토큰 사용량 등 실시간 메트릭 수집
    """)

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    st.markdown("---")
    
    st.subheader("📊 대화 통계")
    st.metric("질문 수", len(st.session_state.conversation_history))
    
    # 평가 모드 토글
    st.markdown("---")
    st.subheader("🔬 평가 설정")
    st.session_state.enable_evaluation = st.checkbox(
        "메트릭 수집 활성화",
        value=st.session_state.enable_evaluation,
        help="성능 메트릭을 수집합니다 (응답 시간, 토큰 사용량 등)"
    )
    
    # 자동 평가 옵션 (기본값: OFF)
    if "auto_evaluate" not in st.session_state:
        st.session_state.auto_evaluate = False
    
    st.session_state.auto_evaluate = st.checkbox(
        "자동 평가 (추가 비용 발생)",
        value=st.session_state.auto_evaluate,
        help="답변 시 자동으로 품질 평가를 수행합니다. OFF면 수동 버튼으로만 평가 가능",
        disabled=not st.session_state.enable_evaluation
    )
    
    st.markdown("---")
    
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.conversation_history = []
        st.rerun()
    
    st.markdown("---")
    
    # 성능 메트릭 (최근 답변)
    if st.session_state.enable_evaluation and st.session_state.get("last_metrics"):
        st.subheader("⚡ 성능 메트릭")
        metrics = st.session_state.last_metrics
        
        # 사용자 체감 시간 우선 표시 (있으면), 없으면 total_time
        user_perceived_time = metrics.get('user_perceived_time')
        if user_perceived_time:
            response_time = user_perceived_time
            response_time_label = "응답 시간 (체감)"
        else:
            response_time = metrics.get('total_time', 0)
            response_time_label = "응답 시간"
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(response_time_label, f"{response_time:.2f}초")
            st.caption(f"검색: {metrics.get('retrieval_time', 0):.2f}초 | 생성: {metrics.get('generation_time', 0):.2f}초")
        with col2:
            st.metric("토큰 사용", f"{metrics.get('total_tokens', 0):,}")
            st.caption(f"검색 문서: {metrics.get('retrieved_docs_count', 0)}개")
        
        if metrics.get('fallback_activated'):
            st.warning("⚠️ 필터 실패 → 전체 검색")
        
        st.markdown("---")
    
    # 답변 품질 평가
    if st.session_state.enable_evaluation:
        st.subheader("🎯 답변 품질 평가")
        
        # 평가 실행 함수
        def run_evaluation():
            """평가 실행 헬퍼 함수"""
            if not st.session_state.get("last_question"):
                return False
            
            try:
                judge_scores = st.session_state.judge.evaluate_answer(
                    question=st.session_state.last_question,
                    answer=st.session_state.last_answer,
                    context=st.session_state.last_context,
                    docs=st.session_state.last_docs
                )
                
                # 세션에 저장 (현재 질문과 함께)
                st.session_state.current_judge_scores = judge_scores
                st.session_state.last_judge_scores = judge_scores
                st.session_state.evaluated_question = st.session_state.last_question
                
                # 히스토리 업데이트
                if st.session_state.conversation_history:
                    st.session_state.conversation_history[-1]["judge_scores"] = judge_scores
                
                # 결과 저장
                st.session_state.evaluation_store.save_evaluation(
                    question=st.session_state.last_question,
                    answer=st.session_state.last_answer,
                    metrics=st.session_state.get("last_metrics", {}),
                    judge_scores=judge_scores,
                    metadata={
                        "insurance_type": st.session_state.last_insurance_type,
                        "docs_count": len(st.session_state.last_docs),
                    }
                )
                return True
            except Exception as e:
                st.error(f"❌ 평가 실패: {str(e)}")
                return False
        
        # 평가 버튼 (수동 평가) - 현재 질문이 있으면 항상 표시 (재평가 가능)
        current_question = st.session_state.get("last_question")
        
        # 현재 질문이 있으면 항상 버튼 표시 (평가 완료 여부와 관계없이)
        if current_question is not None:
            # 버튼 텍스트: 평가 완료 여부에 따라 다르게 표시
            evaluated_question = st.session_state.get("evaluated_question")
            has_evaluation = (
                st.session_state.get("current_judge_scores") is not None 
                and evaluated_question == current_question
            )
            
            button_text = "🔄 답변 재평가하기" if has_evaluation else "🔬 현재 답변 평가하기"
            
            if st.button(button_text, use_container_width=True):
                with st.spinner("평가 중..."):
                    if run_evaluation():
                        st.rerun()
        
        # 평가 결과 표시 (현재 질문과 일치하는 평가만 표시)
        current_scores = st.session_state.get("current_judge_scores")
        evaluated_q = st.session_state.get("evaluated_question")
        last_q = st.session_state.get("last_question")
        
        if (current_scores is not None 
            and evaluated_q is not None 
            and last_q is not None
            and evaluated_q == last_q):
            scores = current_scores
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("관련성", f"{scores.get('relevance', 0)}/5")
            with col2:
                st.metric("정확도", f"{scores.get('accuracy', 0)}/5")
            with col3:
                st.metric("유용성", f"{scores.get('helpfulness', 0)}/5")
            with col4:
                st.metric("완전성", f"{scores.get('completeness', 0)}/5")
            with col5:
                st.metric("근거 충실도", f"{scores.get('groundedness', 0)}/5")
            
            avg_score = scores.get('average_score', 0)
            st.progress(avg_score / 5.0)
            st.caption(f"평균 점수: {avg_score:.2f}/5.0")
            
            if scores.get('explanation'):
                with st.expander("📝 평가 설명"):
                    st.write(scores['explanation'])
        
        st.markdown("---")
    
    # 평가 통계
    if st.session_state.enable_evaluation:
        st.subheader("📈 평가 통계")
        
        stats = st.session_state.evaluation_store.get_statistics()
        if stats["total_evaluations"] > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("총 평가 수", stats["total_evaluations"])
                st.metric("평균 응답 시간", f"{stats['avg_response_time']:.2f}초")
                st.metric("평균 토큰 사용", f"{stats['avg_token_usage']:.0f}")
            with col2:
                if stats['avg_relevance_score'] > 0:
                    st.metric("평균 관련성", f"{stats['avg_relevance_score']:.2f}/5.0")
                st.metric("필터 성공률", f"{stats['filter_success_rate']*100:.1f}%")
                st.metric("Fallback 비율", f"{stats['fallback_rate']*100:.1f}%")
            
            if st.button("📥 평가 결과 다운로드", use_container_width=True):
                export_file = st.session_state.evaluation_store.export_to_json()
                st.success(f"✅ 저장 완료: {export_file.name}")
        else:
            st.info("아직 평가 데이터가 없습니다.")
        
        st.markdown("---")
    
    st.markdown("---")
    
    st.subheader("💡 사용 팁")
    st.info("""
    **질문 예시:**
    - "대중교통 이용 중 다쳤는데 보험 보장받을 수 있나요?"
    - "음주운전 사고 시 보험 적용 가능한가요?"
    - "뇌출혈로 진단 확정되면 어떤 보험금이 지급되나요? 청구 요건은 무엇인가요?"
    """)
    
    st.markdown("---")
    
    st.subheader("🔗 보험 상품")
    insurance_types = [
        "상해보험",
        "손해보험",
        "연금보험",
        "자동차보험",
        "질병보험",
        "책임보험",
        "화재보험",
    ]
    for ins in insurance_types:
        st.caption(f"✓ {ins}")

# 메인 콘텐츠
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.subheader("💬 질문 입력")
    
    # Qdrant 연결 상태 확인
    if not st.session_state.init_attempted:
        st.session_state.init_attempted = True
        with st.spinner("🔄 시스템 초기화 중..."):
            try:
                # Qdrant 연결 테스트
                retriever = get_retriever()
                st.session_state.qdrant_ready = True
                st.session_state.qa_chain = get_qa_chain_with_metrics(enable_metrics=True)
            except ConnectionRefusedError as e:
                st.session_state.qdrant_ready = False
                st.markdown(f"""
<div class="error-box">
<h3>❌ Qdrant 서버 연결 실패</h3>
<p><b>오류:</b> Qdrant 서버에 연결할 수 없습니다.</p>
<p><b>해결 방법:</b></p>
<ol>
<li><b>Docker 시작:</b>
<pre>docker run -p 6333:6333 qdrant/qdrant</pre>
또는 Docker Desktop 애플리케이션을 실행하세요.</li>
<li>위 명령 후 이 페이지를 새로고침하세요 (F5)</li>
<li>계속해서 오류가 발생하면 터미널에서 다음을 확인하세요:
<pre>docker ps</pre></li>
</ol>
<p><b>상세 오류:</b> {str(e)}</p>
</div>
""", unsafe_allow_html=True)
            except Exception as e:
                st.session_state.qdrant_ready = False
                st.markdown(f"""
<div class="error-box">
<h3>❌ 시스템 초기화 오류</h3>
<p><b>오류 메시지:</b> {str(e)}</p>
<p><b>해결 방법:</b></p>
<ol>
<li>Docker가 실행 중인지 확인하세요: <code>docker ps</code></li>
<li>Qdrant 서버가 실행 중인지 확인하세요: <code>docker run -p 6333:6333 qdrant/qdrant</code></li>
<li>.env 파일의 UPSTAGE_API_KEY가 설정되어 있는지 확인하세요</li>
<li>페이지를 새로고침하세요 (F5)</li>
</ol>
</div>
""", unsafe_allow_html=True)
    
    # Qdrant 준비됨 - 질문 입력 허용
    if st.session_state.qdrant_ready and st.session_state.qa_chain is not None:
        question = st.text_input(
            "보험에 대해 궁금한 점을 물어보세요:",
            placeholder="예: 대중교통 이용 중 다쳤는데 보험 보장받을 수 있나요?",
            label_visibility="collapsed"
        )
        
        # 질문 처리
        if question:
            import time
            
            # 새 질문인지 확인 (질문이 변경되었거나 처음 질문)
            is_new_question = (
                st.session_state.last_processed_question != question or
                st.session_state.last_processed_question is None
            )
            
            with st.spinner("🔍 약관을 검색하고 답변을 생성 중입니다..."):
                # 스피너 블록 시작 직후 시간 측정 (실제 사용자가 보기 시작하는 시점)
                user_start_time = time.time()
                
                try:
                    # 답변 생성 (메트릭 포함)
                    result = st.session_state.qa_chain.invoke({
                        "question": question,
                        "enable_metrics": st.session_state.enable_evaluation
                    })
                    
                    # 작업 완료 직후 시간 측정 (답변 생성 완료 시점)
                    user_end_time = time.time()
                    user_perceived_time = user_end_time - user_start_time
                    
                    # 사용자 체감 시간을 메트릭에 추가
                    if result.get("metrics"):
                        result["metrics"]["user_perceived_time"] = user_perceived_time
                    
                    # 새 질문 처리 완료 표시
                    if is_new_question:
                        st.session_state.last_processed_question = question
                    
                    # 대화 히스토리 추가
                    st.session_state.conversation_history.append({
                        "question": question,
                        "answer": result.get("answer", ""),
                        "metrics": result.get("metrics"),
                        "judge_scores": None,  # 나중에 채워짐
                    })
                    
                    # 현재 답변을 세션에 저장 (rerun 후에도 유지)
                    st.session_state.current_result = result
                    st.session_state.current_question = question
                    
                    # 메트릭을 세션에 저장 (사이드바에서 표시용)
                    if result.get("metrics") and st.session_state.enable_evaluation:
                        st.session_state.last_metrics = result["metrics"]
                    else:
                        st.session_state.last_metrics = None
                    
                    # 평가용 데이터 저장
                    st.session_state.last_question = question
                    st.session_state.last_answer = result.get("answer", "")
                    st.session_state.last_context = result.get("context", "")
                    st.session_state.last_docs = result.get("docs", [])
                    st.session_state.last_insurance_type = result.get("insurance_type")
                    
                    # 평가 결과 초기화 (새 답변 생성 시 현재 질문과 불일치하는 평가 제거)
                    # 현재 질문과 일치하지 않으면 평가 결과를 None으로 설정
                    evaluated_q = st.session_state.get("evaluated_question")
                    if evaluated_q is None or evaluated_q != question:
                        st.session_state.current_judge_scores = None
                        st.session_state.last_judge_scores = None
                    
                    # 자동 평가 실행 (옵션이 켜져 있는 경우, 새 질문이면 바로 실행)
                    if (st.session_state.enable_evaluation 
                        and st.session_state.get("auto_evaluate", False)
                        and is_new_question):
                        st.session_state.pending_evaluation = True
                    
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                    result = None
        
        # 답변 표시 (새 답변 또는 저장된 답변)
        current_result = st.session_state.get("current_result")
        if current_result:
            # 답변 표시
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown("### 📋 답변")
            st.write(current_result.get("answer", "약관에서 명확한 근거를 찾을 수 없습니다"))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 보험유형, 적용 조항 표시
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            insurance_type = current_result.get("insurance_type")
            if insurance_type:
                st.markdown(f"**보험유형:** {insurance_type}")

            levels = ["level_1", "level_2", "level_3", "level_4"]
            level_texts = [f"- {current_result.get(l, '')}" for l in levels if current_result.get(l)]
            if level_texts:
                st.markdown("**적용 조항:**")
                st.markdown("\n".join(level_texts))
            st.markdown('</div>', unsafe_allow_html=True)

            # 참고 약관 표시
            docs = current_result.get("docs", [])
            if docs:
                st.markdown('<div class="source-box">', unsafe_allow_html=True)
                st.markdown("### 📚 참고 약관")
                
                for i, doc in enumerate(docs[:2], 1):
                    source_path = doc.metadata.get("source", "")
                    source_name = Path(source_path).name if source_path else "Unknown"
                    with st.expander(f"📄 {source_name} - 문서 {i}"):
                        st.write(doc.page_content)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 자동 평가 실행 (답변 표시 후)
        if (st.session_state.enable_evaluation 
            and st.session_state.get("auto_evaluate", False)
            and st.session_state.get("pending_evaluation", False)
            and st.session_state.get("last_question")
            and st.session_state.evaluated_question != st.session_state.last_question):
            
            st.session_state.pending_evaluation = False  # 플래그 제거
            
            with st.spinner("🔬 답변 품질 평가 중..."):
                try:
                    judge_scores = st.session_state.judge.evaluate_answer(
                        question=st.session_state.last_question,
                        answer=st.session_state.last_answer,
                        context=st.session_state.last_context,
                        docs=st.session_state.last_docs
                    )
                    
                    # 세션에 저장 (현재 질문과 함께)
                    st.session_state.current_judge_scores = judge_scores
                    st.session_state.last_judge_scores = judge_scores
                    st.session_state.evaluated_question = st.session_state.last_question
                    
                    # 히스토리 업데이트
                    if st.session_state.conversation_history:
                        st.session_state.conversation_history[-1]["judge_scores"] = judge_scores
                    
                    # 결과 저장
                    st.session_state.evaluation_store.save_evaluation(
                        question=st.session_state.last_question,
                        answer=st.session_state.last_answer,
                        metrics=st.session_state.get("last_metrics", {}),
                        judge_scores=judge_scores,
                        metadata={
                            "insurance_type": st.session_state.last_insurance_type,
                            "docs_count": len(st.session_state.last_docs),
                        }
                    )
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 평가 실패: {str(e)}")
                    st.session_state.pending_evaluation = False
    
    elif not st.session_state.qdrant_ready:
        st.markdown("""
<div class="warning-box">
<h3>⚠️ 시스템 준비 중</h3>
<p>Qdrant 서버를 실행한 후 페이지를 새로고침하세요 (F5)</p>
<p><b>터미널에서 다음을 실행하세요:</b></p>
<pre>docker run -p 6333:6333 qdrant/qdrant</pre>
</div>
""", unsafe_allow_html=True)

# 대화 히스토리 표시
with col2:
    st.subheader("📝 대화 히스토리")
    
    if st.session_state.conversation_history:
        for i, conv in enumerate(reversed(st.session_state.conversation_history), 1):
            idx = len(st.session_state.conversation_history) - i + 1
            with st.expander(f"질문 {idx}"):
                st.markdown("**Q:** " + conv["question"])
                st.markdown("---")
                answer_preview = conv["answer"][:200] + "..." if len(conv["answer"]) > 200 else conv["answer"]
                st.markdown("**A:** " + answer_preview)
                
                # 간단한 요약만 표시 (자세한 내용은 expander 내부에서)
                if conv.get("metrics"):
                    m = conv["metrics"]
                    st.caption(f"⏱️ {m.get('total_time', 0):.1f}초")
                
                if conv.get("judge_scores"):
                    js = conv["judge_scores"]
                    avg = js.get('average_score', 0)
                    st.caption(f"⭐ {avg:.1f}/5.0")
    else:
        st.info("아직 질문이 없습니다. 왼쪽에서 질문을 입력해보세요! 👈")

# 하단 정보
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.85rem; padding: 1rem 0;">
    <p style="margin-bottom: 0.5rem;">🔐 <b>보안:</b> 모든 데이터는 로컬에서 처리되며, 외부로 전송되지 않습니다.</p>
    <p style="margin-bottom: 0.5rem;">⚡ <b>기술:</b> LangChain + Upstage Solar + Qdrant Vector DB | RAG 기반 검색을 통해 관련 약관 조항을 참조하여 답변 생성</p>
    <p style="margin-bottom: 0.5rem;">📊 <b>평가:</b> LLM-as-a-Judge 기반 자동 품질 평가 시스템</p>
    <p style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #ddd;">
        📜 <b>버전:</b> v2.1.0 (평가 기능 사이드바 통합) | 마지막 업데이트: 2026년 1월 15일
    </p>
</div>
""", unsafe_allow_html=True)
