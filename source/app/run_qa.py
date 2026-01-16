from chains.qa_chain import get_qa_chain

def safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except UnicodeDecodeError:
        print("⚠️ 입력 인코딩 오류가 발생했습니다. 다시 입력해주세요.")
        return ""
    
def main():
    chain = get_qa_chain()

    while True:
        q = input("\n질문 (exit 입력 시 종료): ")
        if q == "exit":
            break

        answer = chain.invoke(q)
        print("\n📌 답변:")
        print(answer)

if __name__ == "__main__":
    main()
