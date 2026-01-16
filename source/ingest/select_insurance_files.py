# select_insurance_files.py
from pathlib import Path
import shutil
import re
import unicodedata

# 원본 XML 폴더
RAW_DIR = Path("/Users/kim-yein/workspace/raw_insurance_xml")
# 선택된 파일 저장 폴더
TARGET_DIR = Path(__file__).resolve().parent.parent / "data_selected"

# 우리가 가져올 보험 유형
TARGET_INSURANCE_TYPES = [
    "상해보험",
    "손해보험",
    "연금보험",
    "자동차보험",
    "질병보험",
    "책임보험",
    "화재보험",
]

def extract_insurance_type_raw(filename: str) -> str | None:
    """
    파일명에서 보험 유형 추출
    예: 001_상해보험_가공.xml -> 상해보험
    """
    # Unicode 정규화(NFC)
    filename = unicodedata.normalize("NFC", filename)
    match = re.search(r"_(.+?)_가공", filename)
    if match:
        return match.group(1)
    return None

def select_files():
    TARGET_DIR.mkdir(exist_ok=True)
    copied = 0

    print(f"RAW_DIR: {RAW_DIR}")
    print(f"TARGET_DIR: {TARGET_DIR}")
    print("---- 복사 시작 ----")

    for xml_file in RAW_DIR.glob("*.xml"):
        insurance_type = extract_insurance_type_raw(xml_file.name)
        if insurance_type in TARGET_INSURANCE_TYPES:
            shutil.copy(xml_file, TARGET_DIR / xml_file.name)
            copied += 1
            print(f"✅ 복사: {xml_file.name} -> {insurance_type}")
        else:
            print(f"❌ 스킵: {xml_file.name} -> {insurance_type}")

    print("---- 완료 ----")
    print(f"총 {copied}개 파일 복사 완료")

if __name__ == "__main__":
    select_files()
