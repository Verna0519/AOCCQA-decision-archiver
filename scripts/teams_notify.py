#!/usr/bin/env python3
"""
teams_notify.py — 把「知識庫更新」通知發到 Microsoft Teams 頻道。

用 Teams 的 Power Automate「Workflows」webhook（舊版 Incoming Webhook 已在退場，
2025 底 / 延至 2026-04-30 停用，一律改用 Workflows）。只用 Python 標準函式庫。

前置（見 references/teams_setup.md）：
  在目標頻道 ⋯ → Workflows → 「Post to a channel when a webhook request is received」
  建立後取得一組 webhook URL。

Webhook URL 來源（勿寫進會同步到 GitHub 的資料夾）：
  - 環境變數：  TEAMS_WEBHOOK_URL=https://... python teams_notify.py ...
  - URL 檔：    --url-file <只含 URL 的檔路徑，放在 repo/同步夾以外>

用法：
  python teams_notify.py --title "[AOCCQA KB 更新] ME-6794" \
     --body "已 merge 到 main。新增 CB-627/CB-628。請 git pull 同步。" \
     [--link https://github.com/...] [--url-file ~/.aoccqa_teams_url] [--dry-run]
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def get_url(args):
    if args.url_file:
        p = os.path.expanduser(args.url_file)
        try:
            u = open(p, encoding="utf-8").read().strip()
        except OSError as e:
            sys.exit(f"讀不到 webhook URL 檔 {p}：{e}")
        if not u:
            sys.exit(f"webhook URL 檔 {p} 是空的")
        return u
    u = os.environ.get("TEAMS_WEBHOOK_URL", "").strip()
    if not u:
        sys.exit("找不到 webhook URL：請設 TEAMS_WEBHOOK_URL 或用 --url-file")
    return u


def build_card(title, body, link, facts=None, status="🔴", details_header="📋 詳細異動內容："):
    """狀態標題 + FactSet（欄位區）+ 詳細異動內容（灰底等寬字塊）。"""
    heading = f"{status} {title}".strip() if status else title
    blocks = [
        {"type": "TextBlock", "text": heading, "weight": "Bolder", "size": "Large",
         "color": "Attention", "wrap": True},
    ]
    if facts:
        blocks.append({"type": "FactSet", "facts": [{"title": k, "value": v} for k, v in facts]})
    blocks.append({"type": "TextBlock", "text": details_header, "weight": "Bolder",
                   "spacing": "Medium", "wrap": True})
    blocks.append({"type": "Container", "style": "emphasis", "items": [
        {"type": "TextBlock", "text": body, "wrap": True, "fontType": "Monospace"}
    ]})
    card = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": blocks,
    }
    if link:
        card["actions"] = [{"type": "Action.OpenUrl", "title": "查看變更", "url": link}]
    return {
        "type": "message",
        "attachments": [
            {"contentType": "application/vnd.microsoft.card.adaptive", "content": card}
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--body", required=True, help="詳細異動內容（可多行）")
    ap.add_argument("--fact", action="append", default=[], metavar="標籤=值",
                    help="欄位區一列，如 --fact \"發起人=Cecilia Yu\"（可重複）")
    ap.add_argument("--status", default="🔴", help="標題前的狀態符號，預設 🔴")
    ap.add_argument("--link", default="")
    ap.add_argument("--url-file", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    facts = []
    for f in args.fact:
        if "=" in f:
            k, v = f.split("=", 1)
            facts.append((k.strip(), v.strip()))
    payload = build_card(args.title, args.body, args.link, facts=facts, status=args.status)

    if args.dry_run:
        print("=== DRY RUN：以下為將送出的 payload（未送出）===")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    url = get_url(args)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST", headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"✅ 已送出 Teams 通知（HTTP {resp.status}）")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        print(f"❌ Teams webhook 錯誤 HTTP {e.code}", file=sys.stderr)
        print(detail, file=sys.stderr)
        if e.code in (401, 403):
            print("提示：webhook URL 失效或流程被停用，請在頻道 Workflows 重新產生。", file=sys.stderr)
        elif e.code == 400:
            print("提示：payload 格式不符——確認你的 Workflow 是『收到 webhook 就貼到頻道』的 Adaptive Card 版型。", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        sys.exit(f"❌ 連線失敗：{e}")


if __name__ == "__main__":
    main()
