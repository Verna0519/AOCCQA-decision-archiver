#!/usr/bin/env python3
"""
merge_into_kb.py — 把 aoccqa-decision-archiver 產出、且經挑選+確認的條目
                   直接寫入本機 AOCCQA-Knowledge-Base repo 的對應 JSON 檔。

安全邊界（逐條遵守）：
  - 只寫 AOCCQA-Knowledge-Base；不碰 AOCCQA_glossary（另需 .md，走手動合併）。
  - 預設 dry-run；要帶 --write 才真的落檔。
  - New 追加（id 撞號則中止）；Update 依 id/鍵就地更新指定欄位，不刪除、不整檔覆寫。
  - 絕不執行 git（不 add/commit/push）。寫完提示用 `git -C <kb> diff` 檢視 → 自行 push。

用法：
  python merge_into_kb.py --entries selected.json [--kb <path>] [--write]

  --kb 省略時讀環境變數 AOCCQA_KB_PATH（指向 repo 根或其 references/）。

selected.json 格式（在 validate_entries.py 的分組格式上，New 用 items、Update 用 updates）：
{
  "Definition_AOCCQA_glossary.json": {
    "array": "terms",
    "items":   [ { ...完整新條目... } ],
    "updates": [ { "id": "CB-100", "set": { "definition_zh": "改後的定義" } } ]
  },
  "Definition_AOCCQA_traceability.json": {
    "array": "rows",
    "updates": [ { "feature": "Customized Bundle", "set": { "glossary_term_count": 12 } } ]
  }
}
  - id 為鍵的檔（glossary/relations/system_relations/ecpages）：update 用 {"id": ..., "set": {...}}。
  - traceability：以 feature 為鍵，update 用 {"feature": ..., "set": {...}}。
  - quicklookup：多陣列，update 用 {"array": "error_messages", "term": ..., "set": {...}}。
"""
import argparse
import json
import os
import sys
from pathlib import Path

# Windows 主控台常是 cp950(Big5)；避免印非 Big5 符號時 UnicodeEncodeError 直接崩潰。
try:
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
except Exception:
    pass

# 沿用 validate_entries.py 的目的檔規格（單一真相，避免兩處各寫一份）
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from validate_entries import REQUIRED
except Exception as e:  # pragma: no cover
    print(f"❌ 無法載入 validate_entries.REQUIRED：{e}")
    sys.exit(2)

# 各檔用來認出「同一筆」的鍵（New 查撞號、Update 定位用）
KEY_FIELD = {
    "Definition_AOCCQA_glossary.json": "id",
    "Definition_AOCCQA_relations.json": "id",
    "Definition_AOCCQA_system_relations.json": "id",
    "Definition_AOCCQA_ecpages.json": "id",
    "Definition_AOCCQA_traceability.json": "feature",
    # quicklookup 逐陣列，鍵在下方另處理
}
QUICKLOOKUP_KEY = {"acronyms": "abbr", "error_messages": "term", "apis": "term"}


def resolve_refs(kb_arg: str):
    """把 --kb / AOCCQA_KB_PATH 解析成放 Definition_*.json 的 references 目錄。"""
    raw = kb_arg or os.environ.get("AOCCQA_KB_PATH", "")
    if not raw:
        return None, "未提供 --kb 且環境變數 AOCCQA_KB_PATH 未設定"
    base = Path(raw).expanduser()
    if not base.exists():
        return None, f"路徑不存在：{base}"
    # 允許給 repo 根（找底下的 references/）或直接給 references/
    for cand in (base / "references", base):
        if (cand / "kb_manifest.json").exists() or any(cand.glob("Definition_AOCCQA_*.json")):
            return cand, ""
    return None, f"在 {base} 或 {base}/references 找不到 KB 檔（kb_manifest.json / Definition_AOCCQA_*.json）"


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def dump_json(p: Path, data):
    """indent=2、ensure_ascii=False、保尾端換行（KB 檔本就 pretty-print，降低無謂 diff）。"""
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ids_in(arr, key):
    return {it.get(key) for it in arr if isinstance(it, dict) and it.get(key) is not None}


def recount(data, array):
    """能重算的頂層 metadata 計數就重算；只動已存在的計數欄位，不新增猜測。"""
    changed = []
    meta = data.get("metadata")
    if isinstance(meta, dict):
        for ck in (f"{array}_count", "term_count" if array == "terms" else None):
            if ck and ck in meta and isinstance(meta[ck], int):
                new = len(data.get(array, []))
                if meta[ck] != new:
                    meta[ck] = new
                    changed.append(f"metadata.{ck}={new}")
    return changed


def apply_file(refs: Path, filename: str, block: dict, report: list):
    spec = REQUIRED.get(filename)
    if not spec:
        report.append((filename, "SKIP", f"不在已知目的檔清單，跳過"))
        return False
    fp = refs / filename
    if not fp.exists():
        report.append((filename, "ERROR", f"KB 內找不到 {filename}，不自動建檔"))
        return False

    data = load_json(fp)
    array = block.get("array") or spec.get("array")
    if not array or array not in data or not isinstance(data.get(array), list):
        report.append((filename, "ERROR", f"目標陣列 '{array}' 不存在或非陣列"))
        return False

    items = block.get("items", []) or []
    updates = block.get("updates", []) or []
    touched = False

    # ---- New：撞號檢查 → 追加 ----
    if filename == "Reference_AOCCQA_quicklookup.json":
        # 多陣列，逐 items 自帶 array（block['array'] 指定該批要進的陣列）
        key = QUICKLOOKUP_KEY.get(array, "term")
    else:
        key = KEY_FIELD.get(filename, spec.get("id_field") or "id")

    existing = ids_in(data[array], key) if key else set()
    for it in items:
        k = it.get(key) if key else None
        if key and k in existing:
            report.append((filename, "ERROR", f"New 撞既有 {key}={k}，中止該檔"))
            return False
        data[array].append(it)
        existing.add(k)
        touched = True
        report.append((filename, "NEW", f"追加 {key}={k}" if key else "追加 1 筆"))

    # ---- Update：依鍵定位 → 就地更新 set 欄位 ----
    for up in updates:
        ukey = "feature" if filename == "Definition_AOCCQA_traceability.json" else key
        kv = up.get(ukey)
        setobj = up.get("set", {})
        if kv is None or not setobj:
            report.append((filename, "ERROR", f"Update 缺 {ukey} 或 set，略過"))
            continue
        target = next((x for x in data[array] if isinstance(x, dict) and x.get(ukey) == kv), None)
        if target is None:
            report.append((filename, "ERROR", f"Update 找不到 {ukey}={kv}，略過"))
            continue
        fields = []
        for fk, fv in setobj.items():
            target[fk] = fv
            fields.append(fk)
        touched = True
        report.append((filename, "UPDATE", f"{ukey}={kv} 改 {', '.join(fields)}"))

    for c in recount(data, array):
        report.append((filename, "COUNT", c))

    return (data if touched else False)


def update_manifest(refs: Path, per_file_len: dict, report: list, write: bool):
    """best-effort：只更新 manifest 內既有的數字型計數欄位，不改結構。"""
    mp = refs / "kb_manifest.json"
    if not mp.exists():
        return None
    manifest = load_json(mp)
    files = manifest.get("files")
    if not isinstance(files, list):
        report.append(("kb_manifest.json", "NOTE", "結構非預期（files 非陣列），計數請手動確認"))
        return None
    changed = False
    for entry in files:
        if not isinstance(entry, dict):
            continue
        fn = entry.get("name") or entry.get("file") or entry.get("filename")
        if fn not in per_file_len:
            continue
        for ck in ("count", "entries", "records", "rows", "items"):
            if ck in entry and isinstance(entry[ck], int) and entry[ck] != per_file_len[fn]:
                entry[ck] = per_file_len[fn]
                changed = True
                report.append(("kb_manifest.json", "COUNT", f"{fn}.{ck}={per_file_len[fn]}"))
    if changed:
        return manifest
    report.append(("kb_manifest.json", "NOTE", "未找到可自動重算的計數欄位，請手動確認"))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entries", required=True, help="經挑選+確認的條目 JSON（分組格式）")
    ap.add_argument("--kb", default="", help="AOCCQA-Knowledge-Base repo 根或 references/（省略讀 AOCCQA_KB_PATH）")
    ap.add_argument("--write", action="store_true", help="真的寫檔（預設 dry-run 只印變更）")
    args = ap.parse_args()

    refs, err = resolve_refs(args.kb)
    if not refs:
        print(f"❌ 無法定位 KB：{err}")
        print("   設定範例：setx AOCCQA_KB_PATH C:\\path\\to\\AOCCQA-Knowledge-Base"
              "  或  export AOCCQA_KB_PATH=/path/to/AOCCQA-Knowledge-Base")
        sys.exit(2)

    entries = load_json(Path(args.entries))
    report, to_write, per_file_len = [], {}, {}
    fatal = False

    for filename, block in entries.items():
        result = apply_file(refs, filename, block, report)
        if any(r[0] == filename and r[1] == "ERROR" for r in report):
            fatal = True
        if isinstance(result, dict):
            to_write[filename] = result
            array = block.get("array") or REQUIRED.get(filename, {}).get("array")
            if array and array in result:
                per_file_len[filename] = len(result[array])

    manifest = update_manifest(refs, per_file_len, report, args.write) if to_write else None

    # ---- 報告 ----
    mode = "WRITE" if args.write else "DRY-RUN"
    print("=" * 60)
    print(f"AOCCQA merge_into_kb — {mode}   KB: {refs}")
    print("=" * 60)
    for fn, tag, msg in report:
        icon = {"NEW": "[+]", "UPDATE": "[~]", "COUNT": "[#]", "SKIP": "[>]",
                "NOTE": "[i]", "ERROR": "[X]"}.get(tag, "[ ]")
        print(f"  {icon} [{fn}] {msg}")
    if not report:
        print("  （沒有可套用的變更）")

    if fatal:
        print("\n[X] 有錯誤，未寫入任何檔（請修正後重跑）。")
        sys.exit(1)

    if not args.write:
        print(f"\n[i] 這是 dry-run。確認無誤後加 --write 才會落檔。將寫入 {len(to_write)} 個檔。")
        sys.exit(0)

    # ---- 實際寫檔（絕不 git）----
    for filename, data in to_write.items():
        dump_json(refs / filename, data)
    if manifest is not None:
        dump_json(refs / "kb_manifest.json", manifest)

    print(f"\n[OK] 已寫入 {len(to_write)} 個檔"
          + ("（含 kb_manifest.json）" if manifest is not None else "") + "。")
    print(f"   下一步（本 skill 不 commit）：")
    print(f"     git -C {refs.parent if refs.name == 'references' else refs} diff   # 檢視變更")
    print(f"     確認後自行 commit / push。")
    sys.exit(0)


if __name__ == "__main__":
    main()
