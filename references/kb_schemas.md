# 目標 JSON Schema 與分類路由（AOCCQA_glossary / AOCCQA-Knowledge-Base）

兩支 repo 底層資料相同；本檔定義「把已確認的功能定義轉譯成哪個檔、哪些欄位、什麼 id/category」。
所有欄位以既有庫（資料版本 2026-07-24）為準；轉譯時字面技術值一字不改照抄來源。

---

## 分類路由（Agent 自動指派用）

| 已確認內容型別 | 目的檔 | 主陣列 | id 前綴 |
|---|---|---|---|
| 名詞／欄位／狀態值／錯誤訊息／價格公式定義 | `Definition_AOCCQA_glossary.json` | `terms` | 全庫共用 `CB-###` 流水號（非 feature 前綴；目前至 `CB-626`，下一個 `CB-627`） |
| 後台設定 → 前台呈現的驅動關係 | `Definition_AOCCQA_relations.json` | `relations` | `REL-###` |
| 跨系統資料流（AOM ↔ Magento ↔ EC） | `Definition_AOCCQA_system_relations.json` | `relations` | `SYS-##` |
| 某 EC 頁面用途／區塊 | `Definition_AOCCQA_ecpages.json` | `pages` | `PAGE-##` |
| 某功能有哪些名詞/關係/頁面/FSD/QA 的對應 | `Definition_AOCCQA_traceability.json` | `rows` | （以 `feature` 為鍵，無獨立 id） |
| 縮寫 / 錯誤訊息原文 / API 來源 | `Reference_AOCCQA_quicklookup.json` | `acronyms`/`error_messages`/`apis` | （無 id，以 `abbr`/`term` 為鍵） |

> 一個新機制常同時命中多檔（例：新增一個後台開關 → glossary 名詞 + relations 前後台 + traceability 掛到 feature）。逐檔各產一條。
> `category`（glossary 用）取既有列舉：`核心概念`、`規則`、`欄位`、`後台`、`狀態`、`錯誤訊息`、`API`、`價格公式`、`頁面區塊`、`Buy Page`、`匯入欄位`、`顯示邏輯`、`購物車`、`通知信/Email`、`其他`。無合適者用 `其他` 並於 Summary 標 `Classification-Uncertain`。

---

## 各檔欄位（* = 必填）

### glossary → `terms[]`
```
id*            "CB-627"（全庫共用流水號，從既有最大號 +1；非 feature 前綴）
category*      見上列舉
term*          名詞（原文照抄）
aliases        別名陣列（中英、口語）
definition_zh* 中文定義（一句話講清是什麼）
detail         操作/設定細節（後台路徑、觸發條件）
sources*       來源檔名/單號陣列
source_keys    對應 metadata.source_files 的短碼
feature*       所屬功能陣列，如 ["Customized Bundle"]
```

### relations → `relations[]`
```
feature*            功能名
backend*            後台設定/機制
backend_category    後台設定的分類
frontend*           前台呈現
frontend_category   前台呈現的分類
relation_zh*        中文說明「後台如何驅動前台」
trigger             觸發條件/生效規則（保留字面值）
sources*            來源陣列
id*                 "REL-###"
```

### system_relations → `relations[]`
```
from_layer*  來源層（AOM / Magento / EC page）
to_layer*    目的層
from*        來源物件/設定
to*          目的物件/呈現
flow_zh*     中文資料流說明
trigger      觸發條件
feature*     機制名
sources*     來源陣列
id*          "SYS-##"
```

### ecpages → `pages[]`
```
page*          頁面名（含型別註記）
aliases        別名陣列
definition_zh* 頁面用途
key_sections   區塊名陣列（原文照抄）
features       涉及功能陣列
sources*       來源陣列
id*            "PAGE-##"
```

### traceability → `rows[]`（以 feature 為單位；多為 Update 而非 New）
```
feature*             功能名（需對得上既有庫寫法）
glossary_term_count  數字（合併時重算）
glossary_terms       名詞陣列
fe_be_relations      relations id/描述陣列
system_relations     system id 陣列
ec_pages             頁面陣列
fsd_chapter          章名
fsd_chapter_url      Confluence FSD 連結
qa_task_keys         Jira 單號陣列
```
> 新增名詞/關係後，通常是「更新既有 feature 的 traceability 列」而非新增列。用 Update 指引標明加了哪些。

### quicklookup
```
acronyms[]:       abbr*, meaning*
error_messages[]: term*, definition_zh*, detail（訊息原文照抄）, feature*, sources*
apis[]:           term*, definition_zh*, detail, feature*, sources*
```

---

## metadata / kb_manifest 計數（合併時同步）

- 各檔頂層 metadata 有 `*_count`（如 glossary `term_count`、`feature_index`）。新增條目後重算。
- `kb_manifest.json` 的 `files[]` 有各檔 size/筆數描述；glossary repo 另有人類可讀 `.md` 需同步。
- 本 skill 只**建議增量**（+N 筆、feature_index 某功能 +N），實際數字由合併時以工具重算，不手填猜測值。

---

## 直接寫入規則（`AOCCQA-Knowledge-Base` only；`scripts/merge_into_kb.py`）

Gate 5 確認後才寫；只寫 `AOCCQA-Knowledge-Base`，`AOCCQA_glossary` 一律輸出＋手動合併。

- **輸入格式**：沿用 `validate_entries.py` 的「依目的檔分組」，New 放 `items`、Update 放 `updates`：
  ```json
  {
    "Definition_AOCCQA_glossary.json": {
      "array": "terms",
      "items":   [ { "id": "CB-627", "...": "...新條目..." } ],
      "updates": [ { "id": "CB-100", "set": { "definition_zh": "改後定義" } } ]
    }
  }
  ```
  - id 為鍵的檔（glossary/relations/system_relations/ecpages）：`updates` 用 `{"id": …, "set": {…}}`。
  - `traceability`：以 `feature` 為鍵，用 `{"feature": …, "set": {…}}`（多為 Update）。
  - `quicklookup`：多陣列，用 `{"array": "error_messages", "term": …, "set": {…}}`。
- **New**：id/鍵撞既有庫 → **中止該檔報錯**（不覆寫）；否則追加進對應陣列。
- **Update**：依鍵定位既有條目，只改 `set` 內欄位；找不到鍵 → 報錯略過；不刪除、不整檔覆寫。
- **計數**：能重算的頂層 `metadata` 計數與 `kb_manifest.json` 既有數字欄位自動更新；結構非預期時印提醒，交人工確認。
- **安全**：預設 dry-run，`--write` 才落檔；UTF-8／`ensure_ascii=false`；**絕不執行 git**。寫後用 `git -C $AOCCQA_KB_PATH diff` 檢視再自行 push。
