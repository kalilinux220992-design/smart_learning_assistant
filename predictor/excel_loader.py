from functools import lru_cache
from pathlib import Path
import re
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from django.conf import settings


XML_NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
WORKBOOK_REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
CELL_REF_RE = re.compile(r"([A-Z]+)")


def _excel_path() -> Path:
    return settings.BASE_DIR / "predictor" / "data" / "GEC Bilaspur Placement details 2022, 2023 , 2024 & 2025.xlsx"


def _cell_column(cell_ref: str) -> str:
    match = CELL_REF_RE.match(cell_ref or "")
    return match.group(1) if match else ""


def _normalize_session_label(sheet_name: str) -> str:
    if sheet_name == "2021-22":
        return "2022"
    return sheet_name.split("-")[0]


def _normalize_package(package_value: str) -> str:
    return " ".join(str(package_value).split()) if package_value else "-"


def _normalize_row(sheet_name: str, row: dict[str, str]) -> dict[str, str] | None:
    if sheet_name == "2021-22":
        name = row.get("B", "").strip()
        branch = row.get("D", "").strip()
        company_name = row.get("E", "").strip()
        package = row.get("F", "").strip()
        campus_mode = row.get("G", "").strip()
        company_type = ""
    else:
        name = row.get("B", "").strip()
        company_name = row.get("C", "").strip()
        company_type = row.get("D", "").strip()
        branch = row.get("E", "").strip()
        campus_mode = row.get("F", "").strip()
        package = row.get("G", "").strip()

    if not name or not branch or not company_name:
        return None

    return {
        "name": name.title() if name.isupper() else name,
        "session": sheet_name,
        "year": _normalize_session_label(sheet_name),
        "company_name": company_name,
        "branch": branch,
        "package": _normalize_package(package),
        "campus_mode": campus_mode or "-",
        "company_type": company_type or "-",
        "status": "placed",
    }


def _load_shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []

    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for string_item in root.findall("a:si", XML_NS):
        strings.append("".join(text_node.text or "" for text_node in string_item.findall(".//a:t", XML_NS)))
    return strings


def _extract_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    value_node = cell.find("a:v", XML_NS)
    inline_node = cell.find("a:is", XML_NS)

    if cell_type == "s" and value_node is not None:
        return shared_strings[int(value_node.text)]

    if cell_type == "inlineStr" and inline_node is not None:
        return "".join(text_node.text or "" for text_node in inline_node.findall(".//a:t", XML_NS))

    if value_node is not None and value_node.text is not None:
        return value_node.text

    return ""


@lru_cache(maxsize=1)
def load_student_records() -> list[dict[str, str]]:
    workbook_path = _excel_path()
    records: list[dict[str, str]] = []

    with ZipFile(workbook_path) as archive:
        shared_strings = _load_shared_strings(archive)
        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels_root}

        for sheet in workbook_root.find("a:sheets", XML_NS):
            sheet_name = sheet.attrib["name"]
            target = "xl/" + rel_map[sheet.attrib[WORKBOOK_REL_NS]]
            sheet_root = ET.fromstring(archive.read(target))
            rows = sheet_root.findall(".//a:sheetData/a:row", XML_NS)

            for row in rows:
                cell_map: dict[str, str] = {}
                for cell in row.findall("a:c", XML_NS):
                    cell_ref = cell.attrib.get("r", "")
                    cell_map[_cell_column(cell_ref)] = _extract_cell_value(cell, shared_strings).strip()

                record = _normalize_row(sheet_name, cell_map)
                if record is not None:
                    records.append(record)

    return sorted(records, key=lambda item: (item["session"], item["name"]))
