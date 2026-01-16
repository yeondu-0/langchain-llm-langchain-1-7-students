# preprocessing.py
import re
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional
from pathlib import Path
from langchain_core.documents import Document
import unicodedata

BASE_DIR = Path(__file__).resolve().parent


# ---------- Insurance Type Extraction ----------
def extract_insurance_type(xml_path: str) -> str:
    filename = Path(xml_path).name
    # 001_상해보험_가공.xml → 상해보험
    filename = unicodedata.normalize("NFC", filename)
    match = re.search(r"_(.+?)_가공", filename)
    if not match:
        raise ValueError(f"보험유형 추출 실패: {filename}")
    return match.group(1)


def resolve_structure_type(insurance_type: str) -> str:
    """
    보험 유형 → 구조 타입 결정
    """
    if "자동차" in insurance_type:
        return "automobile"
    return "default"

# ---------- Load ----------
def load_xml_text(xml_path: str) -> str:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    texts = []
    for cn in root.iter("cn"):
        if cn.text:
            texts.append(cn.text)

    return "\n".join(texts)


# ---------- Normalize ----------
def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


# ---------- Level Patterns ----------
LEVEL_PATTERNS = {
    "automobile": {
        "level_1": re.compile(r"(제\s*\d+\s*편[^\n]*)"),
        "level_2": re.compile(r"(제\s*\d+\s*장[^\n]*)"),
        "level_3": re.compile(r"(제\s*\d+\s*절[^\n]*)"),
        "level_4": re.compile(r"(제\s*\d+\s*조\s*\([^)]+\))"),
    },
    "default": {
        "level_1": re.compile(r"(제\s*\d+\s*관[^\n]*)"),
        "level_2": re.compile(r"(제\s*\d+\s*조\s*\([^)]+\))"),
    },
}


# ---------- Split Helper ----------
def split_with_pattern(
    text: str, pattern: re.Pattern
) -> List[Tuple[Optional[str], str]]:
    """
    pattern 기준 분리
    반환: [(title, body)]
    """
    parts = pattern.split(text)
    if len(parts) == 1:
        return [(None, text)]

    result = []
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i + 1]
        result.append((title, body))

    return result

# =========================================================
# 5. Document Builder
# =========================================================
def build_documents_from_xml(xml_path: str) -> List[Document]:
    raw_text = load_xml_text(xml_path)
    text = normalize_text(raw_text)

    insurance_type = extract_insurance_type(xml_path)
    structure_type = resolve_structure_type(insurance_type)
    patterns = LEVEL_PATTERNS[structure_type]

    documents: List[Document] = []

    # -----------------------------------------------------
    # 🚗 자동차보험: 편 / 장 / 절 / 조
    # -----------------------------------------------------
    if structure_type == "automobile":
        for l1_title, l1_body in split_with_pattern(text, patterns["level_1"]):
            for l2_title, l2_body in split_with_pattern(l1_body, patterns["level_2"]):
                for l3_title, l3_body in split_with_pattern(l2_body, patterns["level_3"]):
                    jo_parts = patterns["level_4"].split(l3_body)

                    if len(jo_parts) > 1:
                        for i in range(1, len(jo_parts), 2):
                            l4_title = jo_parts[i].strip()
                            l4_body = jo_parts[i + 1].strip()

                            documents.append(
                                Document(
                                    page_content=l4_body,
                                    metadata={
                                        "insurance_type": insurance_type,
                                        "level_1": l1_title,
                                        "level_2": l2_title,
                                        "level_3": l3_title,
                                        "level_4": l4_title,
                                        "source": xml_path,
                                    },
                                )
                            )
                    else:
                        content = l3_body.strip()
                        if content:
                            documents.append(
                                Document(
                                    page_content=content,
                                    metadata={
                                        "insurance_type": insurance_type,
                                        "level_1": l1_title,
                                        "level_2": l2_title,
                                        "level_3": l3_title,
                                        "level_4": None,
                                        "source": xml_path,
                                    },
                                )
                            )

    # -----------------------------------------------------
    # 📘 일반 보험: 관 / 조
    # -----------------------------------------------------
    else:
        for l1_title, l1_body in split_with_pattern(text, patterns["level_1"]):
            jo_parts = patterns["level_2"].split(l1_body)

            if len(jo_parts) > 1:
                for i in range(1, len(jo_parts), 2):
                    l2_title = jo_parts[i].strip()
                    l2_body = jo_parts[i + 1].strip()

                    documents.append(
                        Document(
                            page_content=l2_body,
                            metadata={
                                "insurance_type": insurance_type,
                                "level_1": l1_title,
                                "level_2": l2_title,
                                "level_3": None,
                                "level_4": None,
                                "source": xml_path,
                            },
                        )
                    )
            else:
                content = l1_body.strip()
                if content:
                    documents.append(
                        Document(
                            page_content=content,
                            metadata={
                                "insurance_type": insurance_type,
                                "level_1": l1_title,
                                "level_2": None,
                                "level_3": None,
                                "level_4": None,
                                "source": xml_path,
                            },
                        )
                    )

    # -----------------------------------------------------
    # ❗ 최후 방어
    # -----------------------------------------------------
    if not documents:
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "insurance_type": insurance_type,
                    "level_1": None,
                    "level_2": None,
                    "level_3": None,
                    "level_4": None,
                    "source": xml_path,
                },
            )
        )

    return documents