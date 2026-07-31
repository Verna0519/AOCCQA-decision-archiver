# [EU10/PL/HU/CZ] Energy Efficiency Logo / Label image auto sync up to Buy Page

| 屬性 | 值 |
|---|---|
| 發案人 | Verna Chen |
| 建立日期 | 2026/07/14 |
| 標籤 | EU · Buy Page · Energy Logo |
| FSD | ec-service.asus.com（Confluence，Buy Page 章節連結） |
| Figma | figma.com/…（node 2960:1） |

> 狀態：Draft，待 QA 確認 ｜ 歸檔輪次：{Jira 單號待補}

> ⚠️ 這是依參考頁面結構產出的**示範草稿**。可清楚辨識的內容已填入；看不清或需 PM 版本確認之處以 `{…}` 占位，未臆造技術值。

## Purpose（需求說明）
讓符合條件的商品在 Buy Page 顯示能源效率標章（Energy Label），並讓使用者可由此連結到對應的能效資訊與產品資訊文件（Product Information Sheet）。

> 📎 詳細規格（PM 提供，異動時以 PM 版本為準）：https://docs.google.com/spreadsheets/d/{sheet-id}/edit?usp=sharing

## 顯示 / 觸發邏輯（Display Logic）
系統只在符合下列條件時顯示 Energy Label：
- 商品資料具備 Energy Label 的 **Simple product & Configurable product & Customized Bundle**。
- **Freebie**（贈品）不適用／排除。
- Related Products（Products Card）中符合條件的商品一併呈現。
- 依後台設定與生效條件決定是否顯示（見下方 Magento Configuration）。
- 標章依型式顯示對應元素（icon、文字連結、PDF 連結）。

> 邏輯細節依 Buy Page 模組相關文件；上列為可辨識之條件，其餘 `{依 FSD 補}`。

## 後台設定（MCC1 Magento Configuration）
`Stores → Settings → Configuration → Catalog → Catalog → Display The Energy Label Section On Buy Page`

## Energy labels UI Info（多語系欄位對照）
「Product Information Sheet」各語系顯示字串：

| Locale | 顯示字串 |
|---|---|
| EN | Product Information Sheet |
| FR | Fiche d'information produit |
| DE | Produktinformationsblatt |
| IT | {Scheda informativa del prodotto，依 FSD 核對} |
| FI | Tuoteseloste |
| DK | Produktinformationsblad |
| SE | Produktinformationsblad |
| PL | {依 FSD 補} |
| CZ | Specifikace / {依 FSD 補} |
| PT | Ficha de informação do produto |

> 上表語系與字串以參考頁面可辨識者為準；模糊處標 `{依 FSD 補}`，合併前請對照 PM 規格表核實。

## Anatomy（欄位 → 來源對應）
標章元件：**Icon**（能效等級 A–G 圖示）＋ **Text link**（Product Information Sheet）。各顯示元素對應來源：
- Energy Label → Energy Label image URL
- Energy Label Name → Energy Label Level（等級 A–G）
- File Path → Energy Label PDF URL
- Energy Link → Product Information Sheet URL

## 前台呈現（by 商品型態）
- **Simple product & Configurable product**：Buy Page 規格區顯示 Energy Label icon 與 Product Information Sheet 連結。截圖：{附圖}
- **Customized Bundle**：主商品／組合內符合條件之商品顯示標章。截圖：{附圖}
- **Related Products（Products Card）**：卡片上顯示標章（示例商品：ROG Ally Gaming Console 2023 $584.99、ROG Ally Premium Hard Case $44.99、ROG Ally Gaming Console 2024 Out of Stock、ROG Ally Travel Case $35.99）。截圖：{附圖}
- **With File / Hyperlink**：點擊 Energy Label icon 開啟能效標章圖／PDF；點擊 Product Information Sheet 文字連結開啟產品資訊文件。截圖：{附圖}

## 已確認來源
- Jira：{單號與連結待補}
- FSD：ec-service.asus.com（Buy Page 章節）
- Figma：figma.com/…（node 2960:1）
- 確認節點：{Gate 1 澄清 / reviewer 確認}

## 關聯知識庫條目（建議）
- glossary：`Energy Label`、`Product Information Sheet`、`Display The Energy Label Section On Buy Page`（category：後台／頁面區塊）
- relations：後台 `Display The Energy Label Section On Buy Page` → 前台 `Buy Page Energy Label 區塊`
- ecpages：`Buy Page` key_sections 增列 `Energy Label Section`
- traceability：`EU 30天最低價 / Energy Label` feature 對應更新
