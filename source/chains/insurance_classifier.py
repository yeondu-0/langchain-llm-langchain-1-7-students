from langchain_core.prompts import PromptTemplate

from llm.llm import get_llm
from config.settings import ALLOWED_INSURANCE_TYPES

INSURANCE_CLASSIFY_PROMPT = PromptTemplate.from_template("""
다음 질문이 어떤 보험유형에 해당하는지 하나만 골라라.
반드시 아래 [보험유형 목록]에서 선택해야 한다.
여러 유형에 포함될 경우, 더 하위 범주로 선택하라.                                                         
                                                        

[보험유형 목록]
- 상해보험
- 손해보험
- 연금보험                                                         
- 자동차보험
- 질병보험
- 책임보험
- 화재보험

질문: {question}

보험유형:
""")


def classify_insurance_type(question: str) -> str:
    if not question or not question.strip():
        return "질병보험"  # 기본값 반환
    
    llm = get_llm()
    try:
        response = llm.invoke(
            INSURANCE_CLASSIFY_PROMPT.format(question=question)
        )
        raw = response.content.strip().splitlines()[0] if response.content else ""  # type: ignore
    except Exception as e:
        print(f"[WARN] LLM classification failed: {e}")
        raw = ""
    
    print(f"[DEBUG] raw classification: {raw}")

    q = question.replace(" ", "")

    # 1️⃣ LLM이 정확히 맞춘 경우
    if raw in ALLOWED_INSURANCE_TYPES:
        return raw

    # 2️⃣ 사고 / 상해
    if any(k in q for k in [
        "사고", "다쳤", "부상", "골절", "상해", "넘어", "충돌", "추락"
    ]):
        return "상해보험"

    # 3️⃣ 질병 / 진단 / 의료
    if any(k in q for k in [
        "질병", "진단", "암", "뇌출혈", "뇌경색",
        "입원", "수술", "치료", "병원", "의사"
    ]):
        return "질병보험"

    # 4️⃣ 자동차
    if any(k in q for k in [
        "자동차", "차량", "교통사고", "운전", "추돌", "렌트카"
    ]):
        return "자동차보험"

    # 5️⃣ 화재
    if any(k in q for k in [
        "화재", "불", "전소", "연기", "폭발", "누전"
    ]):
        return "화재보험"

    # 6️⃣ 책임보험 (손해배상 성격)
    if any(k in q for k in [
        "배상", "손해배상", "책임", "과실", "법적책임", "배상책임"
    ]):
        return "책임보험"

    # 7️⃣ 손해보험 (재산 피해)
    if any(k in q for k in [
        "도난", "침수", "파손", "망가", "훼손",
        "재산", "시설", "기계", "건물", "누수"
    ]):
        return "손해보험"

    # 8️⃣ 연금보험
    if any(k in q for k in [
        "연금", "노후", "은퇴", "퇴직", "연금수령",
        "연금개시", "연금액", "노령"
    ]):
        return "연금보험"

    # 9️⃣ 최후 기본값 (가장 많이 쓰이는 영역)
    return "질병보험"