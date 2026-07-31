# AOCCQA 維護規範（Conventions）

團隊共用規範。改動知識庫 / 功能定義頁時一律照這份走。放在 repo 上作為單一真相。

## 0. Onboarding（第一次接手 / 首次設定，照順序做一次）

> 首次載入 `aoccqa-decision-archiver` 或新人接手時，照這份做一次即可。

1. **安裝 skill**：Claude → Customize → Skills → Add，上傳 `aoccqa-decision-archiver.skill`。
2. **連接器**：授權 Confluence（AOCCPM_confluence-mcp）與 Jira（AOCCPM_jira-mcp）——抓 FSD / 單用；要抓 Figma 設計截圖再另授權 Figma。
3. **建 Teams 通知（GitHub Actions → Teams Workflows webhook）**：
   1. 目標頻道 **⋯ → Workflows → 「Post to a channel when a webhook request is received」** → 建立 → 複製 webhook URL（詳見 `references/teams_setup.md`）。
   2. 每個 repo（`AOCCQA_glossary`、`AOCCQA-Knowledge-Base`、`AOCCQA-decision-archiver`）→ **Settings → Secrets and variables → Actions → New repository secret**：名稱 `TEAMS_WEBHOOK_URL`、值 = 該 webhook URL。
   3. 把 `.github/workflows/notify-teams.yml` 放進該 repo（本 repo 已內含，複製到另兩支）。
   4. **測試**：repo → **Actions → Notify Teams on main update → Run workflow**（手動觸發）→ 頻道應出現卡片。之後 push / merge 到 `main` 會自動發。
4. **Watch 三個 repo**（GitHub 內建通知，當備援）。
5. 之後的知識庫更新照第 2 節 SOP、第 3 節同步通知走。

## 1. 文件書寫與篩選規範

**架構**：用 `references/templates.md` Template A，逐項對齊團隊 Notion export——屬性寫成 `名稱: 值` 純文字行（分享人 / 更新日期 / 標籤 / FSD）、段落用 `#`（次級 `##`）、重點用 `<aside>💡 …</aside>`、情境切「顯示／不顯示」兩張表、影片截圖 `[說明](檔名.mp4)`、不放 HTML 註解。範例：`references/example_add_to_cart.md`、`example_energy_label.md`。

**篩選邏輯**（先篩掉不需要的再呈現，以「讀的人需不需要理解」為準）：

- 保留：功能在做什麼、核心決策邏輯（分支／條件）、觸發來源、商品型態、判定條件、導向／顯示結果與觀察點、未受影響／回歸、QA 可查的前後台驗證點、scope／國別／環境時程、正／負／邊界測試點、待釐清。
- 篩掉：Security / Infra check list、DB「無變更」、完整 code path（只留 QA 查得到的欄位/URL）、PR/deploy 內部、mermaid 原始碼。

**完整性**：交叉比對 FSD（Confluence）＋ 團隊已確認行為（Notion 現行頁 / reviewer 結論），補上「FSD 沒寫但已確認」的、解掉待釐清；仍無解才留「待確認」，不臆造。

**書寫風格**：白話 + 每條規則配實際情境例子；專有名詞保留原文不翻中文（Buy Page、add-on、WEP、Cart page…）；新名詞解釋只放本次相關、較不熟的，且置於文件最下方。

## 2. 知識庫維護 SOP

知識庫更新**不會自動同步**。Git 是「拉」的：push 只更新 repo，隊友要自己 `git pull`（或重裝 `.skill`）才會拿到。

- **GitHub repo** = 單一真相；**本機安裝的 skill** = Claude 實際查的副本。直接改本機快取無效且會被覆蓋——一律改在 repo。
- 流程：archiver 產 JSON 條目 → `validate_entries.py` 驗過 → 開 branch → PR → review → **maintainer** merge 到 `main`。
- 合併後同步兩支 repo（`AOCCQA_glossary` 另更 `.md` 與兩邊 `kb_manifest.json` 的 `term_count`）。
- 只有 maintainer 能 merge 到 `main`；個人不各自本機亂改。

## 3. 同步與通知規範（每次改動後必做）

每次 archiver 產出 KB 條目 / 功能頁後，最後一定要做這三步：

1. **commit + push（或開 PR）** 到對應 repo。
2. **merge 到 `main`**（maintainer）。
3. **通知團隊 pull / 重裝**。

通知方式（擇一）：

- **GitHub 內建**：push / PR 會通知有 Watch 該 repo 的成員——請團隊先 Watch `AOCCQA_glossary`、`AOCCQA-Knowledge-Base`、`AOCCQA-decision-archiver`。
- **Microsoft Teams（團隊用這個，自動）**：`.github/workflows/notify-teams.yml`——repo push 到 `main` 時，GitHub Actions 自動把更新貼到頻道（GitHub for Teams app 被租戶擋，改走 Actions → Teams Workflows webhook）。每個 repo 設 secret `TEAMS_WEBHOOK_URL` 即可。設定見 `references/teams_setup.md`。手動客製訊息可另用 `scripts/teams_notify.py`。
- **手動**：用下方範本貼到群組。

通知範本：

```
[AOCCQA KB 更新] {功能 / Jira 單號} 已 merge 到 main（{commit 或 PR 連結}）。
新增／更新：{條目摘要，如 CB-627 Add to Cart 導向邏輯、CB-628 Success Banner}。
請 git pull main（或重裝更新後的 .skill）同步知識庫。
```
