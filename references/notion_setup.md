# Notion 官方 API + Internal Integration Token 設定

不依賴 Claude 的 Notion connector，改用 Notion 官方 API 直接建頁。一次設定，之後 skill 用 `scripts/notion_publish.py` 發布。

---

## 一次性設定（約 5 分鐘）

### 步驟 1：建 Internal Integration，拿 token
1. 到 <https://www.notion.so/profile/integrations>（或 Settings → Connections → Develop or manage integrations）。
2. **New integration** → 選 **Internal** → 綁定你的 workspace → 命名（如 `AOCCQA Decision Archiver`）。
3. Capabilities 勾 **Insert content**（建頁必需）、需要更新頁再加 **Update content**。
4. 建立後複製 **Internal Integration Secret**（`ntn_...` 或舊格式 `secret_...`）。這就是 token。

### 步驟 2：把目標頁面／資料庫分享給 integration
Internal integration **預設看不到任何內容**，必須手動授權：
1. 在 Notion 開你要當「功能定義知識庫」的**父頁面**或**資料庫**。
2. 右上 **⋯ → Connections（連線）→ 搜尋你的 integration 名 → Confirm**。
3. 子頁面會繼承這個授權。

### 步驟 3：取得父物件 ID
- 開該頁面/資料庫，看網址：`https://www.notion.so/<workspace>/<名稱>-**32碼hex**?v=...`
- 結尾那段 32 碼 hex 就是 ID（帶不帶連字號都可）。
- 父為**一般頁面** → `--parent-type page`（推薦，最簡單）。
- 父為**資料庫** → `--parent-type data_source`，ID 用該資料庫的 **data source id**，並用 `--title-prop` 指定標題欄位名（預設 `Name`）。

---

## Token 放哪（重要，資安）

⚠️ **絕對不要**把 token 寫進 `AOCCQA-decision-archiver/` 這個資料夾——它會同步到 OneDrive，且這條產線的 JSON 最終要合併進**公開 GitHub repo**，token 一旦混進去就外洩。

建議擇一：

1. **執行時帶入（不落地，最安全）**
   ```bash
   NOTION_TOKEN=ntn_xxx python scripts/notion_publish.py --md draft.md ...
   ```
2. **放同步夾以外的 token 檔**（如家目錄）：
   ```bash
   echo 'ntn_xxx' > ~/.aoccqa_notion_token   # 不在 repo/OneDrive 內
   chmod 600 ~/.aoccqa_notion_token
   python scripts/notion_publish.py --token-file ~/.aoccqa_notion_token --md draft.md ...
   ```
3. **Windows 使用者**：放 `C:\Users\verna_chen\.aoccqa_notion_token`（在 OneDrive 同步夾之外），`--token-file` 指過去。

本資料夾附的 `.gitignore` 已把 `*token*`、`.env` 之類排除，作為第二層保險——但仍以「token 不進本資料夾」為第一原則。

---

## 發布（QA 確認內容後才做）

```bash
# 先 dry-run 確認 payload（不送出、不需 token）
python scripts/notion_publish.py --md draft.md \
  --title "Customized Bundle disable propagation" \
  --parent-type page --parent-id <32碼> --dry-run

# 正式送出
NOTION_TOKEN=ntn_xxx python scripts/notion_publish.py --md draft.md \
  --title "Customized Bundle disable propagation" \
  --parent-type page --parent-id <32碼>
```

成功會印出新頁的 `id` 與 `url`。

---

## 常見錯誤

| HTTP | 意思 | 解法 |
|---|---|---|
| 401 | token 無效/過期 | 重新複製 Internal Integration Secret |
| 403 | integration 沒權限 | 步驟 2 未做，或 Capabilities 沒勾 Insert content |
| 404 | 父 ID 找不到/未分享 | 確認 ID 正確且已 Connect 給 integration |
| 400 | payload 有誤 | data_source 父的 title 屬性名不符 → 用 `--title-prop` 指定實際名 |

---

## 備註

- `Notion-Version` 目前用 `2026-03-11`（撰寫時最新）。Notion 只在**破壞性變更**時發新版；未來若要升版，改 `notion_publish.py` 頂部的 `NOTION_VERSION` 常數即可。
- 建頁用官方新支援的 `markdown` body 參數，直接吃本 skill 產出的 Markdown 草稿，不需轉 Notion block。
- Internal integration 只能存取你手動 Connect 過的頁面/庫，權限範圍可控。
