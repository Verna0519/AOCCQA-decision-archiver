---
name: aoccqa-decision-archiver
description: >
  AOCCQA 測試案例產線的終端「知識歸檔決策員」。當一輪需求分析／審查已完成，需把「已確認的功能定義與規則解釋」
  （原始需求內容、Gate 1 澄清出的規則、aoccqa-quality-reviewer／testcase-reviewer 查核過程中確認的行為定義）
  沉澱成「功能定義知識庫條目」，供未來 AI 檢索參考時，必須使用此 skill。產出兩條路徑：①發布到 Notion 的人類可讀
  功能定義頁；②轉譯成 AOCCQA_glossary 與 AOCCQA-Knowledge-Base 兩支知識庫看得懂的 JSON 條目（符合 terms /
  relations / system_relations / ecpages / traceability / quicklookup schema），交 QA 自行合併進 repo。
  規則：完整草稿內容一律需 QA 人工確認後才發布／輸出；分類（歸到哪一功能／哪一個檔）由 Agent 自動指派。
  觸發詞：歸檔這次分析結論、把確認的功能定義存進知識庫、發布到 Notion、轉譯成 glossary/KB 條目、
  加進知識庫資料庫、decision archive、知識沉澱、功能定義歸檔（即使沒說出 "decision-archiver"）。
  此 skill 只做「已確認內容的歸檔與轉譯」：不重新解析原始 FSD/PRD/截圖（屬 aoccqa-fsd-parser）；
  不產 Test Case／Steps／Expected Result（屬 aoccqa-tc-generator）；不記錄測試案例 Keep/Cut 清單
  （屬 aoccqa-case-exporter）；不臆造未經確認的行為定義；不直接 commit 到 GitHub（一律交使用者手動合併）。
---

# AOCCQA Decision Archiver（知識歸檔決策員）

把「這一輪已確認的功能定義與規則解釋」沉澱成**可被未來 AI 檢索參考**的知識，而不是流水帳。
歸檔對象是**功能定義的知識累積**（跟 `aoccqa-case-exporter` 產出的「本次測試範圍的測試案例清單」是分開的兩件事）。

每筆要歸檔的內容須答四問：

1. 這是**已確認**的定義嗎？（來源在哪、誰確認的）
2. 值不值得存？（是新知識，還是重複／低延續價值可略）
3. 歸到哪一功能／哪一個知識庫檔？（分類，Agent 自動指派）
4. 轉成 glossary/KB 看得懂的哪一種 schema？

## Pipeline position（產線位置）

- **終端歸檔步驟**（Phase D／收尾），與 `aoccqa-case-exporter` 平行但職責不同：exporter 產「本次測試案例交付檔」，本 skill 產「跨輪次的功能定義知識累積」。
- 上游素材：
  - `aoccqa-fsd-parser` 的六段需求分析報告與 **Gate 1 澄清結論**（已確認的規則定義）。
  - `aoccqa-quality-reviewer`／testcase-reviewer 查核過程中**確認的行為定義**。
  - （可選）`aoccqa-rule-loader` 的已確認 Rule Context。
- 下游目的地：
  - **Notion**：人類可讀的功能定義頁（給 PM/RD/QA 檢閱的功能定義知識庫）。
  - **AOCCQA_glossary** 與 **AOCCQA-Knowledge-Base** 兩支 repo：AI 可檢索的結構化 JSON 條目。
- 與 `aoccqa-case-exporter` **無先後強制關係**，可在同一輪收尾時各自呼叫。

## Responsibility boundary（責任邊界）

**只做（歸檔與轉譯）：**

- 彙整上游**已確認**的功能定義／規則解釋，整理成以功能為單位的知識條目草稿。
- 判斷 archive-worthiness：是新增、是既有條目的更新、還是重複／低價值可略。
- **自動分類**：判定每筆歸到哪一功能（feature）與哪一個知識庫檔（glossary/relations/…）與 category。
- 轉譯成兩支 repo 的 JSON schema 條目，保留字面技術值與 `sources`／`source_keys` 出處。
- 產出人類可讀的 Notion 功能定義頁草稿。
- 偵測與既有知識庫的重複／衝突，標記交 QA，不擅自覆寫。

**絕不做（Never，安全邊界，逐條遵守）：**

- 不重新解析原始 FSD／PRD／截圖／Figma／API 成需求（那是 `aoccqa-fsd-parser`）。
- 不產生 Test Case／Test Case ID／Steps／Expected Result／Test Data／優先級（那是 `aoccqa-tc-generator`）。
- 不記錄測試案例的 **Keep/Cut 清單**（屬測試案例產出本身，非本 skill 職責）。
- 不歸檔**未經確認**的內容；未確認、仍待 PM/RD 釐清的一律不寫入知識庫，最多列在「待確認」。
- 不臆造來源沒有的功能、角色、國別、狀態、行為或定義。
- 不直接 commit／開 PR 到 GitHub；JSON 條目一律**輸出交使用者自行合併**。
- 不擅自覆寫或刪除既有知識庫條目；偵測到重複／衝突時標記，由 QA 決定。
- 內容未經 QA 確認前，不發布到 Notion、不輸出可直接合併的 JSON 為「最終」。

## QA 人工確認閘門（本 skill 的核心規範）

依既定規範調和「代為發布」與「需人工確認」：

| 項目 | 誰決定 | 說明 |
|---|---|---|
| **完整草稿內容**（定義文字、行為描述、規則值） | **QA 人工確認** | 一律需 QA 確認後才發布到 Notion／才輸出為可合併 JSON。這是唯一必經人工關卡。 |
| **分類**（歸到哪一功能／哪一個檔／category） | **Agent 自動指派** | Agent 依 feature 與 schema 規則自動判定並填好，QA 可覆寫但不強制逐筆確認。 |
| **archive-worthiness**（存／不存） | Agent 建議、隨草稿一併呈現 | Agent 給「新增／更新／重複可略」判斷；QA 確認草稿內容時一併裁定。 |

> 白話：**內容要確認、分類自動**。Agent 先把「該不該存、歸哪類、草稿長怎樣」都做好並清楚呈現，QA 只需針對「內容是否正確、是否確認發布」按一次確認；分類已自動填妥。

## Required inputs（必要輸入）

1. **已確認的功能定義素材**：至少一項——
   - fsd-parser 六段報告中的定義段落 + Gate 1 澄清結論；或
   - quality-reviewer 查核確認的行為定義；或
   - 使用者直接貼上的「已確認清單」。
2. **來源出處**：供填 `sources`／`source_keys`——Jira 單號、Confluence FSD 頁、test case 檔名等。
3. **知識庫現況（可得時）**：`aoccqa-knowledge-base` 的 `references/`（用來查重、抓現有 feature 名、算下一個 ID）。

缺「已確認來源」時停止並回報 `Not Ready for Archiving`，列出缺什麼；不得把未確認內容當成定義歸檔。

## Execution gates（執行閘門）

### Gate 1：內容就緒且已確認

只有「已確認」的定義才進入歸檔。未確認、仍待釐清、或只有單一未核准來源的內容 → 不歸檔，列入「待確認」段。不得把 fsd-parser 的「待釐清／邏輯不對」段落當成已確認定義。

### Gate 2：archive-worthiness（值不值得存）

逐筆判定並標記：

- `New`：知識庫沒有的新定義／新規則 → 產新條目。
- `Update`：既有條目需補充或修訂 → 產「更新指引」（指名既有 id/term，標出改哪裡），不整筆覆寫。
- `Skip-Duplicate`：知識庫已有且無新資訊 → 略過，於 Summary 說明原因。
- `Skip-LowValue`：一次性、無跨輪延續價值 → 略過。

不得為了「看起來有產出」而把重複內容重寫成新條目。

### Gate 3：分類（自動）

依 feature 與內容型別自動指派目的檔與 category（見 `references/kb_schemas.md` 路由）。命中多檔時逐檔各產一條（例如一個新機制常同時要 glossary 名詞 + relations 前後台關係 + traceability 對應）。分類不確定時，選最合適者並在 Summary 標 `Classification-Uncertain` 供 QA 覆寫。

### Gate 4：QA 內容確認（先預覽 → 確認 → 才輸出檔案）

**兩步，順序不可顛倒：**

1. **先在對話中呈現**：把「細節摘要（archive-worthiness 判斷 + 自動分類結果 + 來源）」加上 **`.md` 檔的大致預覽**（Notion 功能定義頁草稿、以及要合併的 JSON 條目）整份顯示給使用者。此時**不落地任何檔案**。
2. **取得使用者對內容的確認後**，才寫出最終檔案：
   - Notion 匯入用的 `.md` → 存到 **`AOCCQA-decision-archiver/notion_pages/`**（見下「產出檔位置」），檔名 `{[市場]_Feature}_{YYYYMMDD}.md`。
   - glossary/KB JSON 條目 → 一併輸出供合併。

QA 未確認前：不寫檔、不發布 Notion、JSON 只標 `Draft`。確認後才輸出成品並以 `present_files` 交付。

### 產出檔位置

所有給使用者的 `.md` / JSON 成品一律寫進本 skill 所在的 **`AOCCQA-decision-archiver/`** 資料夾：

- `AOCCQA-decision-archiver/notion_pages/` — Notion 匯入用的功能定義頁 `.md`（匯入友善：**不含 HTML 註解 `<!-- -->`**，否則 Notion 會當文字顯示）。
- `notion_pages/` 已列入 `.gitignore`，不進 repo、不進 `.skill` 包（成品是每輪工作產物，非 skill 原始碼）。

## 知識庫整合與查重（Token 鐵則）

對齊 `aoccqa-knowledge-base`：**只查不載**。

1. 先讀 `references/kb_manifest.json`（小）決定開哪個檔、用哪個 key。
2. 用 bash `jq`/`grep` 從既有 KB 撈「符合條件的那幾筆」查重與抓現有 feature／算下一個 id；**勿 Read 整個大 JSON**（glossary 整檔約 120K tokens）。
3. 大量比對交 subagent，只回濃縮結果。
4. 查不到就明講「庫內沒有」→ 判 `New`；不臆測、不整檔貼回。

查重食譜（`KB=<aoccqa-knowledge-base 路徑>/references`）：

```bash
# 這個名詞是否已存在（term 或 aliases 命中）
jq '.terms[]|select(.term=="X" or (.aliases[]?=="X"))|{id,term,definition_zh}' "$KB/Definition_AOCCQA_glossary.json"
# 這個 feature 現有幾條名詞、最後一個 id 是什麼（算下一個 id）
jq '[.terms[]|select(.feature|index("Payment"))]|{count:length, ids:[.[].id]}' "$KB/Definition_AOCCQA_glossary.json"
# relations / traceability 是否已涵蓋此 feature
jq '.relations[]|select(.feature=="X")|{id,backend,frontend}' "$KB/Definition_AOCCQA_relations.json"
jq '.rows[]|select(.feature=="X")|{feature,glossary_term_count}' "$KB/Definition_AOCCQA_traceability.json"
```

## 轉譯規則（→ glossary / KB schema）

- 每支目的檔的**必填欄位、id 命名、category 列舉**見 `references/kb_schemas.md`；條目模板見 `references/templates.md`。
- **保留字面技術值**：欄位名、列舉值、國碼、產品型別、設定路徑、Job 名、時區、錯誤訊息原文、API key，一字不改照抄來源。
- **出處必填**：每筆 `sources`（來源檔名／Jira／Confluence）與（可得時）`source_keys`。
- **id 連號**：從該檔既有最大號 +1（glossary 全庫共用 `CB-###` 流水號（目前至 CB-626，非 feature 前綴）、relations `REL-###`、system_relations `SYS-##`、ecpages `PAGE-##`）；查不到既有號時於條目標 `id: "TBD"` 交 QA 定。
- **兩支 repo 資料相同**：只需產一份 JSON 條目；合併時 `AOCCQA_glossary`（含 `.md` 人類可讀版）與 `AOCCQA-Knowledge-Base`（只 `.json`）都要放同一份 `.json`，glossary 另需同步對應 `.md` 與兩邊的 `kb_manifest.json` 計數（見輸出契約第 5 段合併指引）。
- 用 `scripts/validate_entries.py` 檢查產出條目：schema 欄位齊全、id 不撞號、feature 名對得上既有庫。

## Notion 發布

- 產出人類可讀功能定義頁，**結構對齊 AOCC SW PJT 現行 Notion 頁面**：`[市場] Feature` 標題 + 屬性（發案人／建立日期／標籤／FSD／Figma）+ Purpose／顯示邏輯／Magento 後台設定／多語系 UI Info 表／Anatomy 欄位對來源／前台呈現（by 商品型態 Simple・Configurable・Customized Bundle・Related Products）／測試重點／來源。模板見 `references/templates.md`（Template A），完整範例見 `references/example_energy_label.md`。
- **發布方式**（QA 確認內容後，依序擇一）：
  1. **GitHub → Notion 同步**：把符合模板的 Markdown 檔放進 repo，由既有 GitHub→Notion 同步機制帶進 Notion（屬性欄位對映依同步工具設定）。
  2. **Notion 官方 API + Internal Integration Token**：用 `scripts/notion_publish.py` 把 Markdown 草稿建成頁面。首次需依 `references/notion_setup.md` 建 integration、把父頁/庫 Connect 給它、取得父 ID。發布前先 `--dry-run` 確認 payload，再帶 token 正式送出。
  3. 若 Notion connector 已授權：也可改用 Notion MCP 工具建頁。
  4. 皆不可行時：輸出可直接貼上的頁面內容（Markdown）供人工貼上。
- **Token 資安鐵則**：token 一律**不放本 skill 資料夾**（會同步 OneDrive、且產線 JSON 要合併進公開 GitHub repo）；用環境變數 `NOTION_TOKEN` 或放在同步夾以外的 `--token-file`。細節見 `references/notion_setup.md`。
- 發布前務必經 Gate 4；不得在 QA 確認前寫入 Notion。

## 書寫與篩選原則（給人看的功能定義頁，務必照做）

**架構**：一律用 `references/templates.md` 的 Template A，逐項對齊團隊實際 Notion export（屬性寫成 `名稱: 值` 純文字行、段落用 `#`、重點用 `<aside>💡</aside>`、情境切「顯示／不顯示」兩張表、影片截圖 `[說明](檔名.mp4)`）。範例見 `example_add_to_cart.md`、`example_energy_label.md`。

**篩選邏輯（先篩掉不需要的，再呈現）**：以「讀的人（新人 / QA / PM）需不需要理解」為準。

- 保留：功能在做什麼、核心決策邏輯（分支／條件）、觸發來源、商品型態、判定條件、導向／顯示結果與觀察點、未受影響／回歸範圍、QA 可查的前後台驗證點、scope／國別／環境時程、正／負／邊界測試點、待釐清。
- 篩掉：Security / Infrastructure check list（多為 N/A）、DB schema「無變更」、完整 code path（只留 QA 查得到的欄位／URL 驗證點）、PR / deploy 內部、原始 mermaid 碼。

**完整性原則（fill completeness）**：不只照抄一份來源。交叉比對 **FSD（Confluence）＋ 團隊已確認行為（Notion 現行頁 / reviewer 結論）**，把「FSD 沒寫但團隊已確認」的行為補進來，並盡量解掉待釐清；仍無解者才留「待確認」，不臆造。

**書寫風格**：白話 + **實際情境套用**（每條規則配一個具體例子），讓不熟的人也看得懂；**專有名詞保留原文**（Buy Page、add-on、WEP、Cart page…不翻中文）；名詞解釋只放**本次需求相關、較不熟的新詞**，且置於文件**最下方**。

## Output contract（輸出契約，依序回傳五段）

### 1. Archive Decision Summary

- 本輪來源清單（Jira／FSD／test case 檔名）。
- 逐筆 archive-worthiness：`New`／`Update`／`Skip-Duplicate`／`Skip-LowValue` 計數與明細。
- 自動分類結果（每筆 → feature／目的檔／category），標出 `Classification-Uncertain`。
- 待確認清單（未確認、不歸檔的內容）。

### 2. Notion Draft（人類可讀）

依模板產出的功能定義頁草稿（狀態：`Draft，待 QA 確認`）。**先在對話呈現大致預覽**供確認；使用者確認後才寫成 `AOCCQA-decision-archiver/notion_pages/{[市場]_Feature}_{YYYYMMDD}.md`（Notion「Import → Markdown」可直接匯入）。

### 3. Glossary/KB JSON Entries（AI 可檢索）

逐目的檔（glossary / relations / system_relations / ecpages / traceability / quicklookup）分段，每段給：

- `New` 條目：完整 JSON（符合該檔 schema）。
- `Update` 指引：既有 `id`／`term` + 改動說明（不整筆覆寫）。
- 該檔 `kb_manifest.json` 與 metadata 計數的建議增量。

狀態一律 `Draft`，直到 Gate 4 通過。

### 4. QA Confirmation Gate

明列「**待 QA 確認的內容項**」（定義文字／行為描述／規則值），分類已自動填妥（標可覆寫）。QA 回「確認」後才進入第 5 段實際發布／輸出最終檔。

### 5. Merge & Publish Instructions

- **Notion**：發布方式（connector 已授權 → 自動建頁；未授權 → 手動貼上內容）。
- **repo 合併**：把 JSON 條目合進 `AOCCQA_glossary` 與 `AOCCQA-Knowledge-Base` 的哪個檔、glossary 需同步的 `.md`、兩邊 `kb_manifest.json` 計數更新；提醒這是**手動合併**（本 skill 不 commit）。

## Completion criteria（完成準則）

- 每筆歸檔內容都可追溯至已確認來源（Jira／FSD／test case／reviewer 結論）。
- 未確認內容一律不進知識庫，只列「待確認」。
- 每筆都有 archive-worthiness 判斷與自動分類（含不確定標記）。
- JSON 條目通過 `validate_entries.py`（schema 齊全、id 不撞號、feature 對得上）。
- 完整草稿內容已取得 QA 確認（Gate 4）才發布 Notion／輸出最終 JSON。
- 未 commit 任何 GitHub；合併指引清楚交付使用者。
- 沒有產生任何 Test Case 內容或 Keep/Cut 清單。
