def validate(state):
    docs = state["documents"]

    if not docs:
        return {"answer": "해당 내용은 약관에서 확인할 수 없습니다."}

    return state
