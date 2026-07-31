#!/usr/bin/env python3
"""
notion_publish.py — 用 Notion 官方 API + Internal Integration Token 建頁。

只用 Python 標準函式庫（urllib），不需安裝套件；沙盒/本機皆可跑。
把本 skill 產出的「功能定義頁 Markdown 草稿」發布成一個 Notion 頁面。

前置（見 references/notion_setup.md）：
  1. 在 Notion 建 internal integration，取得 token（ntn_... 或 secret_...）。
  2. 把目標父頁面／資料庫「Connect」給該 integration。
  3. 取得父物件 ID（Notion URL 結尾 32 碼 hex）。

Token 來源（擇一，勿把 token 寫進會同步到 GitHub 的 skill 資料夾）：
  - 環境變數：  NOTION_TOKEN=ntn_xxx python notion_publish.py ...
  - Token 檔：  --token-file <只含 token 的檔路徑，放在 repo/同步夾以外>

用法：
  python notion_publish.py \
     --md draft.md --title "Customized Bundle disable propagation" \
     --parent-type page --parent-id 1a2b3c...（32 碼） \
     [--token-file ~/.aoccqa_notion_token] [--dry-run]

parent-type：
  page         父為一般頁面（推薦；title 為唯一屬性，body 用 markdown）
  data_source  父為資料庫的 data source（title 屬性名用 --title-prop 指定，預設 "Name"）
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2026-03-11"  # 撰寫時最新；見 references/notion_setup.md


def get_token(args):
    if args.token_file:
        p = os.path.expanduser(args.token_file)
        try:
            tok = open(p, encoding="utf-8").read().strip()
        except OSError as e:
            sys.exit(f"讀不到 token 檔 {p}：{e}")
        if not tok:
            sys.exit(f"token 檔 {p} 是空的")
        return tok
    tok = os.environ.get("NOTION_TOKEN", "").strip()
    if not tok:
        sys.exit("找不到 token：請設環境變數 NOTION_TOKEN 或用 --token-file")
    return tok


def build_payload(args, md_text):
    if args.parent_type == "page":
        parent = {"page_id": args.parent_id}
        props = {"title": {"title": [{"text": {"content": args.title}}]}}
    else:  # data_source
        parent = {"data_source_id": args.parent_id}
        props = {args.title_prop: {"title": [{"text": {"content": args.title}}]}}
    # create-page 支援 markdown body 參數（與 content/children 互斥）；換行由 json 自動轉 \n
    return {"parent": parent, "properties": props, "markdown": md_text}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True, help="Markdown 草稿檔")
    ap.add_argument("--title", required=True, help="頁面標題")
    ap.add_argument("--parent-type", choices=["page", "data_source"], default="page")
    ap.add_argument("--parent-id", required=True, help="父頁面/data source ID（32 碼 hex）")
    ap.add_argument("--title-prop", default="Name", help="data_source 父的 title 屬性名")
    ap.add_argument("--token-file", default="", help="只含 token 的檔路徑")
    ap.add_argument("--dry-run", action="store_true", help="只印 payload 不送出")
    args = ap.parse_args()

    try:
        md_text = open(os.path.expanduser(args.md), encoding="utf-8").read()
    except OSError as e:
        sys.exit(f"讀不到 Markdown 檔：{e}")

    payload = build_payload(args, md_text)

    if args.dry_run:
        print("=== DRY RUN：以下為將送出的 payload（未送出）===")
        redacted = dict(payload)
        redacted["markdown"] = md_text[:200] + ("…" if len(md_text) > 200 else "")
        print(json.dumps(redacted, ensure_ascii=False, indent=2))
        print(f"\nendpoint: POST {API_URL}")
        print(f"Notion-Version: {NOTION_VERSION}")
        return

    token = get_token(args)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=data, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        print("✅ 已建立 Notion 頁面")
        print("   id :", body.get("id"))
        print("   url:", body.get("url"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        print(f"❌ Notion API 錯誤 HTTP {e.code}", file=sys.stderr)
        print(detail, file=sys.stderr)
        hint = {
            401: "token 無效或過期。",
            403: "integration 沒有此父物件權限——請在 Notion 該頁/庫的 ⋯ → Connections 加入你的 integration，並確認有 Insert content 能力。",
            404: "父物件 ID 找不到或未分享給 integration。",
            400: "payload 有誤（常見：data_source 父的 title 屬性名不符，用 --title-prop 指定）。",
        }.get(e.code)
        if hint:
            print("提示：", hint, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        sys.exit(f"❌ 連線失敗：{e}")


if __name__ == "__main__":
    main()
