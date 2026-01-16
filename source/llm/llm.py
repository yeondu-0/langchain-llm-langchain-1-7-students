from langchain_upstage import ChatUpstage
from config.settings import UPSTAGE_MODEL, TEMPERATURE

def get_llm():
    return ChatUpstage(
        model=UPSTAGE_MODEL,
        temperature=TEMPERATURE,
    )