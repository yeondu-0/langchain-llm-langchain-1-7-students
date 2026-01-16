from pathlib import Path
from .preprocessing import build_documents_from_xml
from source.ingest.vertorstore_ingest import get_vectorstore, get_embeddings

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data_selected"

# 🔥 Qdrant vectorstore 초기화
vectorstore = get_vectorstore(
    recreate=True  # 기존 데이터 싹 지우고 새로 만들기
)

total_docs = 0

for xml_file in DATA_DIR.glob("*.xml"):
    print("Processing:", xml_file.name)
    try:
        docs = build_documents_from_xml(str(xml_file))
        vectorstore.add_documents(docs)
        total_docs += len(docs)
        print(f"✅ {len(docs)} documents added for {xml_file.name}")
    except Exception as e:
        print(f"❌ Error processing {xml_file.name}: {e}")

print(f"\n총 {total_docs} documents Qdrant에 적재 완료")
