from llm.llm import get_llm
from llm.prompt import INSURANCE_PROMPT

def generate(state):
    llm = get_llm()

    context = "\n\n".join(
        doc.page_content for doc in state["documents"]
    )

    answer = llm.invoke(
        INSURANCE_PROMPT.format(
            context=context,
            question=state["question"],
        )
    )

    return {"answer": answer.content}
