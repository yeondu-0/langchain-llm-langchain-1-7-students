import os

def format_insurance_docs(docs):
    if not docs:
        return "관련 약관 문서를 찾을 수 없습니다."
    
    blocks = []

    for d in docs:
        md = d.metadata

        clause_levels = []
        for k in ["level_1", "level_2", "level_3", "level_4"]:
            if md.get(k):
                clause_levels.append(md[k])

        clause_text = " > ".join(clause_levels) if clause_levels else "조항 정보 없음"

        blocks.append(f"""
[보험유형] {md.get("insurance_type", "UNKNOWN")}
[조항분류] {clause_text}
[약관본문]
{d.page_content}
""")

    return "\n\n".join(blocks)




# def format_insurance_docs(docs):
#     formatted = []

#     for doc in docs:
#         meta = doc.metadata

#         clauses = []
#         for key in ["level_1", "level_2", "level_3", "level_4"]:
#             value = meta.get(key)
#             if value:
#                 clauses.append(value)

#         source_file = os.path.basename(meta.get("source", ""))

#         formatted.append(
#             f"""
# [보험유형]
# {meta.get("insurance_type")}

# [조항]
# {" > ".join(clauses)}

# [약관 내용]
# {doc.page_content}

# [출처]
# {source_file}
# """
#         )

#     return "\n\n".join(formatted)
