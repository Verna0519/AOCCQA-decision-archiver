# 條目與頁面模板

## A. Notion 功能定義頁（人類可讀）

發布前狀態一律標 `Draft，待 QA 確認`。

```markdown
# {功能名稱}（{English Feature Name}）

> 狀態：Draft，待 QA 確認 ｜ 歸檔輪次：{Jira 單號 / 日期}

## 這是什麼
{一句話功能定義 — definition_zh}

## 規則與技術值
- {規則 1：保留字面技術值，如 country code、時區、公式、錯誤訊息原文}
- {規則 2 …}

## 前後台 / 跨系統關係
- 後台 {backend} → 前台 {frontend}：{relation_zh}
- 資料流 {from_layer} → {to_layer}：{flow_zh}

## 涉及頁面 / 區塊
{ec_pages 與 key_sections}

## 已確認來源
- Jira：{單號與連結}
- FSD：{Confluence 章節與連結}
- Test case：{檔名}
- 確認節點：{Gate 1 澄清 / reviewer 確認}

## 關聯知識庫條目
{對應寫進 glossary/KB 的 id：CB-069, REL-045 …}
```

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
