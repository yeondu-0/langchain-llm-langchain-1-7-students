import os
from pathlib import Path
import xml.etree.ElementTree as ET

# 원본 XML 파일 경로
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data_selected"
failed_files = []

# XML 파일 순회
for file_path in DATA_DIR.glob("*.xml"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            xml_text = f.read()
            # XML 파싱 시도
            ET.fromstring(xml_text)
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        failed_files.append(file_path)

# 실패한 파일 리스트 출력
print("\n=== Failed files ===")
for f in failed_files:
    print(f.name)
print(len(failed_files), "files failed to parse.")
# # 원하면 실패 파일 내용 일부 확인
# print("\n=== Sample contents ===")
# for f in failed_files:
#     with open(f, "r", encoding="utf-8") as file:
#         content = file.read()
#         print(f"--- {f.name} ---")
#         print(content[:500])  # 처음 500글자만 확인
#         print("...\n")
