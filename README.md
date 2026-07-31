# AOCCQA Decision Archiver（知識歸檔決策員）

AOCCQA 測試案例產線的**終端歸檔 skill**。把一輪需求分析／審查中「已確認的功能定義與規則解釋」，
沉澱成未來 AI 可檢索的知識——不是流水帳，也不是測試案例清單。

## 這支 skill 做什麼

彙整上游已確認的素材（`aoccqa-fsd-parser` 六段報告 + Gate 1 澄清結論、
`aoccqa-quality-reviewer` 確認的行為定義、可選的 `aoccqa-rule-loader` Rule Context），
產出**兩條歸檔路徑**：

1. **Notion** — 人類可讀的功能定義頁（給 PM/RD/QA 看的功能定義知識庫）。
2. **AOCCQA_glossary + AOCCQA-Knowledge-Base** — 轉譯成兩支 repo 看得懂的 JSON 條目
   （`terms` / `relations` / `system_relations` / `ecpages` / `traceability` / `quicklookup`），
   **交你自行合併**進 repo（本 skill 不 commit）。

## 核心規範

- **內容要確認、分類自動**：完整草稿內容一律經 QA 人工確認後才發布／輸出；歸到哪一功能／哪個檔由 Agent 自動指派（QA 可覆寫）。
- **只歸檔已確認內容**：未確認、待釐清的一律不寫入知識庫。
- **不做**：重新解析 FSD（屬 fsd-parser）、產 Test Case/Steps（屬 tc-generator）、記錄 Keep/Cut 清單（屬 case-exporter）、直接 commit GitHub。

## 檔案結構

```
AOCCQA-decision-archiver/
├── SKILL.md                    # skill 進入點：職責、閘門、輸出契約
├── README.md                   # 本文件
├── .gitignore                  # 排除任何憑證檔（token 資安第二層保險）
├── references/
│   ├── kb_schemas.md           # 目標 JSON schema、分類路由、必填欄位、category 列舉
│   ├── templates.md            # Notion 頁模板 + 各檔 JSON 條目模板
│   └── notion_setup.md         # Notion 官方 API + Internal Integration Token 設定
└── scripts/
    ├── validate_entries.py     # 合併前檢查：schema 齊全、id 不撞號、算下一個 id
    └── notion_publish.py       # 用 Notion API + token 把 Markdown 草稿建成頁面
```

## 輸出契約（五段）

1. Archive Decision Summary（來源、archive-worthiness、自動分類、待確認）
2. Notion Draft（人類可讀頁草稿）
3. Glossary/KB JSON Entries（逐檔 New/Update 條目 + 計數增量）
4. QA Confirmation Gate（待確認內容項；分類已填可覆寫）
5. Merge & Publish Instructions（Notion 發布方式 + repo 手動合併步驟）

## 合併前檢查

```bash
python scripts/validate_entries.py --entries new_entries.json \
  --kb <aoccqa-knowledge-base>/references
```

檢查通過**不代表可合併**——仍須經 QA 內容確認（Gate 4）後，才手動合併進 repo／發布到 Notion。

## 相依

- `aoccqa-knowledge-base`：查重、抓現有 feature 名、算下一個 id（只查不載，Token 鐵則）。
- **Notion 發布**：預設走官方 API + Internal Integration Token（`scripts/notion_publish.py`，見 `references/notion_setup.md`，免 connector 授權）；也可改用已授權的 Notion connector，或退回手動貼上。
