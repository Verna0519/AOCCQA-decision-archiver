# 條目與頁面模板

## A. Notion 功能定義頁（人類可讀）— 對齊 AOCC SW PJT 現行 Notion 匯出結構

**此結構逐項對齊團隊實際的 Notion export（`[EU/PL/HU/CZ/RS] Add to Cart…` 匯出檔）**，
確保產出的 `.md` 用 Notion「Import → Markdown」匯入後、以及匯出回來都能對得上。發布前狀態標 `Draft，待 QA 確認`。

Notion 匯出的硬性慣例（務必照做）：

1. **屬性寫成 `名稱: 值` 純文字行**（緊接標題下方），**不是**表格。固定欄位：`分享人`、`更新日期`、`標籤`（逗號分隔）、`FSD`（連結）；有 Figma 才加 `Figma`。
2. **段落標題用 `#`（H1）**；次級規則用 `##`。
3. **重點提示用 callout**：`<aside>💡 … </aside>`。
4. **情境用表格**，慣例切成「Banner 顯示情境」與「Banner 不顯示情境」兩張（或依功能改成對應的兩面對照）。
5. **影片／截圖**用 `[說明文字](檔名.mp4)`，並在下一行重複說明文字。
6. 不放 HTML 註解 `<!-- -->`（Notion 會當文字顯示）。

```markdown
# [{市場標籤}] {Feature Name}

分享人: {Requester}
更新日期: {YYYY年M月D日}
標籤: {Tag1}, {Tag2}, {Tag3}
FSD: {ec-service.asus.com Confluence 連結}

# Purpose

{一段話：這個需求／機制在調整什麼、對使用者的影響}

# {核心邏輯段，標題可用 **粗體**，如 Add to Cart button 流程修改邏輯}

{舊行為 → 新行為，白話對比}

- {分支條件 1}：{結果}
- {分支條件 2}：{結果}
- {不受影響的路徑}：{維持原樣}

<aside>
💡

{一句話記法／重點總結}

</aside>

# {情境表 A，如 Banner 顯示情境}

| 操作位置／商品情境 | {條件欄} | 點擊按鈕後流程 | {結果欄，如 Banner} |
| --- | --- | --- | --- |
| {情境} | {條件} | {流程} | {結果} |

[{影片說明}](xxx.mp4)
{影片說明}

# {情境表 B，如 Banner 不顯示情境}

| 操作位置／商品情境 | {條件欄} | 點擊按鈕後流程 | {結果欄} |
| --- | --- | --- | --- |
| {情境} | {條件} | {流程} | **{結果，可加粗強調}** |

## 補充規則

- {邊界／例外規則 1，如 Freebie 不等同 Add-on}
- {邊界／例外規則 2}
```

> 適用時可保留原「功能定義」型段落（後台設定 / UI Info 多語系表 / Anatomy 欄位對來源 / 已確認來源 / 關聯知識庫條目），插在 Purpose 與情境表之間；純測試導向頁可只用上面骨架。
> 完整範例見 `references/example_energy_label.md`（功能定義型）與 `references/example_add_to_cart.md`（情境對照型，對齊實際 Notion export）。

---

## B. glossary term（New 範例）

```json
{
  "id": "CB-627",
  "category": "規則",
  "term": "{名詞原文}",
  "aliases": ["{別名1}", "{別名2}"],
  "definition_zh": "{一句話定義}",
  "detail": "{後台路徑/觸發/設定細節}",
  "sources": ["{來源檔名或 Jira 單號}"],
  "source_keys": ["{短碼，可省}"],
  "feature": ["Customized Bundle"]
}
```

## C. relations（New 範例）

```json
{
  "feature": "Customized Bundle",
  "backend": "{後台設定}",
  "backend_category": "{分類}",
  "frontend": "{前台呈現}",
  "frontend_category": "{分類}",
  "relation_zh": "{後台如何驅動前台}",
  "trigger": "{觸發/生效規則，保留字面值}",
  "sources": ["{來源}"],
  "id": "REL-###"
}
```

## D. system_relations（New 範例）

```json
{
  "from_layer": "Magento",
  "to_layer": "EC page",
  "from": "{來源物件}",
  "to": "{目的呈現}",
  "flow_zh": "{資料流說明}",
  "trigger": "{觸發}",
  "feature": "{機制名}",
  "sources": ["{來源}"],
  "id": "SYS-##"
}
```

## E. Update 指引（不整筆覆寫）

```markdown
### Update: glossary CB-012 "{term}"
- 目標檔：Definition_AOCCQA_glossary.json（兩支 repo 同步）
- 動作：detail 補一句「{新增內容}」；aliases 加 "{新別名}"
- 來源：{Jira 單號}
- 理由：既有定義未涵蓋 {新規則}
```

## F. quicklookup error_message（New 範例）

```json
{
  "term": "{錯誤情境名}",
  "definition_zh": "{何時出現}",
  "detail": "訊息：{錯誤訊息原文，一字不改}",
  "feature": "{功能}",
  "sources": ["{來源}"]
}
```
