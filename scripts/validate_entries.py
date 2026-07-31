#!/usr/bin/env python3
"""
validate_entries.py — 檢查 aoccqa-decision-archiver 產出的知識庫 JSON 條目。

用途（只讀、不寫、不 commit、不連網）：
  1. 逐檔驗證產出條目的必填欄位是否齊全（依 references/kb_schemas.md）。
  2. 對照既有知識庫（AOCCQA-Knowledge-Base 的 references/）查 id 是否撞號。
  3. 為每個目的檔算出「下一個可用 id」建議。
  4. 印出可貼回對話的合併前檢查報告。

用法：
  python validate_entries.py --entries new_entries.json [--kb <KB references 路徑>]

new_entries.json 格式（把本輪要新增的條目依目的檔分組）：
{
  "Definition_AOCCQA_glossary.json":        {"array": "terms",     "items": [ {...term...} ]},
  "Definition_AOCCQA_relations.json":       {"array": "relations", "items": [ {...} ]},
  "Definition_AOCCQA_system_relations.json":{"array": "relations", "items": [ {...} ]},
  "Definition_AOCCQA_ecpages.json":         {"array": "pages",     "items": [ {...} ]},
  "Reference_AOCCQA_quicklookup.json":      {"array": "error_messages", "items": [ {...} ]}
}
"""
import argparse
import json
import re
import sys
from pathlib import Path

# 每個目的檔的必填欄位與 id 前綴規則
REQUIRED = {
    "Definition_AOCCQA_glossary.json": {
        "array": "terms",
        "required": ["id", "category", "term", "definition_zh", "sources", "feature"],
        "id_field": "id",
        "id_prefix": "CB-",  # 全庫共用流水號（非 feature 前綴）
    },
    "Definition_AOCCQA_relations.json": {
        "array": "relations",
        "required": ["feature", "backend", "frontend", "relation_zh", "sources", "id"],
        "id_field": "id",
        "id_prefix": "REL-",
    },
    "Definition_AOCCQA_system_relations.json": {
        "array": "relations",
        "required": ["from_layer", "to_layer", "from", "to", "flow_zh", "feature", "sources", "id"],
        "id_field": "id",
        "id_prefix": "SYS-",
    },
    "Definition_AOCCQA_ecpages.json": {
        "array": "pages",
        "required": ["page", "definition_zh", "sources", "id"],
        "id_field": "id",
        "id_prefix": "PAGE-",
    },
    "Reference_AOCCQA_quicklookup.json": {
        "array": None,  # 多陣列，逐 items 自帶 array
        "required_by_array": {
            "acronyms": ["abbr", "meaning"],
            "error_messages": ["term", "definition_zh", "feature", "sources"],
            "apis": ["term", "definition_zh", "feature", "sources"],
        },
    },
    "Definition_AOCCQA_traceability.json": {
        "array": "rows",
        "required": ["feature"],
        "id_field": None,  # 以 feature 為鍵
    },
}

GLOSSARY_CATEGORIES = {
    "核心概念", "規則", "欄位", "後台", "狀態", "錯誤訊息", "API", "價格公式",
    "頁面區塊", "Buy Page", "匯入欄位", "顯示邏輯", "購物車", "通知信/Email", "其他",
}


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def existing_ids(kb_dir: Path, filename: str, array: str, id_field: str):
    fp = kb_dir / filename
    if not fp.exists() or not id_field:
        return set()
    data = load_json(fp)
    return {i.get(id_field) for i in data.get(array, []) if i.get(id_field)}


def next_id(ids, prefix):
    """從既有 id 算下一個可用號；zero-pad 寬度沿用既有 id 的實際寬度。"""
    nums, widths = [], []
    for i in ids:
        if not i or (prefix and not str(i).startswith(prefix)):
            continue
        m = re.search(r"(\d+)$", str(i))
        if m:
            nums.append(int(m.group(1)))
            widths.append(len(m.group(1)))
    n = (max(nums) + 1) if nums else 1
    width = max(widths) if widths else 3
    return f"{prefix}{n:0{width}d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entries", required=True, help="本輪新增條目 JSON")
    ap.add_argument("--kb", default="", help="AOCCQA-Knowledge-Base 的 references/ 路徑（查重用，可省）")
    args = ap.parse_args()

    entries = load_json(Path(args.entries))
    kb_dir = Path(args.kb) if args.kb else None

    errors, warnings, notes = [], [], []

    for filename, block in entries.items():
        spec = REQUIRED.get(filename)
        if not spec:
            warnings.append(f"[{filename}] 不在已知目的檔清單，略過驗證。")
            continue
        items = block.get("items", [])
        array = block.get("array") or spec.get("array")

        # 查既有 id + 撞號 + 下一個可用 id
        idf = spec.get("id_field", "id")
        if kb_dir and idf and array:
            ex = existing_ids(kb_dir, filename, array, idf)
            seen = set()
            for it in items:
                iid = it.get(idf)
                if iid in ex:
                    errors.append(f"[{filename}] id 撞既有庫：{iid}")
                if iid in seen:
                    errors.append(f"[{filename}] 本輪 id 重複：{iid}")
                if iid == "TBD" or not iid:
                    notes.append(f"[{filename}] 有條目 id=TBD，合併時請指定。")
                seen.add(iid)
            prefix = spec.get("id_prefix", "")
            if prefix:
                notes.append(f"[{filename}] 下一個可用 id 建議：{next_id(ex, prefix)}")

        # 必填欄位
        for idx, it in enumerate(items):
            if filename == "Reference_AOCCQA_quicklookup.json":
                req = spec["required_by_array"].get(array, [])
            else:
                req = spec.get("required", [])
            missing = [f for f in req if not it.get(f)]
            if missing:
                errors.append(f"[{filename}] 第 {idx+1} 筆缺必填：{', '.join(missing)}")
            # glossary category 列舉
            if filename == "Definition_AOCCQA_glossary.json":
                cat = it.get("category")
                if cat and cat not in GLOSSARY_CATEGORIES:
                    warnings.append(f"[{filename}] 第 {idx+1} 筆 category '{cat}' 不在既有列舉，請確認。")

    print("=" * 56)
    print("AOCCQA Decision Archiver — 條目合併前檢查")
    print("=" * 56)
    total = sum(len(b.get("items", [])) for b in entries.values())
    print(f"目的檔 {len(entries)} 個，條目 {total} 筆\n")
    if errors:
        print(f"❌ 錯誤 {len(errors)}（合併前必須修）：")
        for e in errors:
            print("   -", e)
    if warnings:
        print(f"\n⚠️  提醒 {len(warnings)}：")
        for w in warnings:
            print("   -", w)
    if notes:
        print(f"\nℹ️  註記 {len(notes)}：")
        for n in notes:
            print("   -", n)
    if not errors:
        print("\n✅ Schema/id 檢查通過。仍須經 QA 內容確認（Gate 4）後才合併／發布。")
    print()
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
