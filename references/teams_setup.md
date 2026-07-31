# Microsoft Teams 通知設定（Power Automate Workflows webhook）

團隊只有 Teams。Teams 沒有可授權的 MCP connector，且舊版 Incoming Webhook 已退場
（Office 365 connectors 2025 底、延至 2026-04-30 停用），所以一律用 **Workflows webhook**。
一次設定，之後 `scripts/teams_notify.py` 就能把「知識庫更新」通知發到頻道。

## 一次性設定

1. 打開要收通知的 Teams **頻道** → 頻道名稱旁 **⋯（更多選項）→ Workflows（工作流程）**。
2. 選範本 **「Post to a channel when a webhook request is received」**（收到 webhook 請求時貼到頻道）。
3. 依指示選好 Team／Channel、建立流程 → 會給你一組 **webhook URL**（`https://prod-XX.westus.logic.azure.com/...` 之類）。
4. 複製這組 URL。這就是 `teams_notify.py` 要用的目標。

> 需要建立 Workflows 的權限；若被 IT 限制，請團隊管理員代建或開放。

## Webhook URL 放哪（資安）

⚠️ 這組 URL 等同「誰有誰就能往頻道貼文」，**不要放進會同步到 GitHub 的資料夾**。

- 執行時帶入：`TEAMS_WEBHOOK_URL=https://... python scripts/teams_notify.py ...`
- 或放同步夾以外的檔：
  ```bash
  echo 'https://prod-...' > ~/.aoccqa_teams_url   # 不在 repo/OneDrive 內
  python scripts/teams_notify.py --url-file ~/.aoccqa_teams_url ...
  ```

`.gitignore` 已排除 `*token*`/`*secret*`/`.env`；建議 URL 檔命名也避開 repo 目錄。

## 發送

```bash
# 先 dry-run 看 payload（不需 URL）
python scripts/teams_notify.py --title "[AOCCQA KB 更新] ME-6794" \
  --body "已 merge 到 main。新增 CB-627 Add to Cart 導向邏輯、CB-628 Success Banner。請 git pull 同步。" \
  --link https://github.com/Verna0519/AOCCQA_glossary --dry-run

# 正式送出
TEAMS_WEBHOOK_URL=https://prod-... python scripts/teams_notify.py --title "..." --body "..." --link "..."
```

## 自動化：GitHub → Teams（此路，repo 更新自動通知）

> 註：官方「GitHub for Teams」app（`@github subscribe`）在本租戶被擋，無法用。改走 **GitHub Actions → Teams Workflows webhook**。

已附 workflow：`.github/workflows/notify-teams.yml`——repo push 到 `main`（或手動 dispatch）時，自動把更新貼到 Teams 頻道。

啟用步驟（每個要通知的 repo 各做一次）：

1. 先照上面「一次性設定」建好頻道 Workflows webhook，拿到 URL。
2. 到 repo → **Settings → Secrets and variables → Actions → New repository secret**：
   - Name：`TEAMS_WEBHOOK_URL`
   - Value：貼上 webhook URL（存在 GitHub secret，不進程式碼）。
3. 把 `.github/workflows/notify-teams.yml` 放進該 repo（`AOCCQA_glossary`、`AOCCQA-Knowledge-Base` 這兩支才是知識庫本體，建議都放）。
4. 之後 merge 到 `main` → Actions 自動發卡片到頻道（訊息含 repo、pusher、commit message、「請 git pull」提示與查看連結）。

手動測試：repo → **Actions → Notify Teams on main update → Run workflow**。

## 常見錯誤

| HTTP | 意思 | 解法 |
|---|---|---|
| 401 / 403 | URL 失效 / 流程被停用 | 在頻道 Workflows 重新啟用或重建，取得新 URL |
| 400 | payload 格式不符 | 確認 Workflow 是「收到 webhook 就貼 Adaptive Card 到頻道」版型；本腳本送標準 Adaptive Card |

> 若你們用的是別的 Workflow 版型（例如只吃純文字），把 `teams_notify.py` 的 `build_card()` 改成對應格式即可。
