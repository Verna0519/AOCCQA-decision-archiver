# [EU/PL/HU/CZ/RS] Add to Cart button action go to Cart Page process (not stay on Buy Page)

分享人: Verna Chen
更新日期: 2026年7月17日
標籤: Buy Page, Cart page, EU10
FSD: https://ec-service.asus.com/confluence/spaces/EP/pages/172665400/DV2IN1-44888+MCC1+Add+to+Cart+button+action+go+to+Cart+Page+process+not+stay+on+Buy+Page

# Purpose

此專案主要調整 MCC1 全國家的 Buy Page「Add to Cart / Pre Order」流程。

# **Add to Cart button 流程修改邏輯**

原本使用者加入商品後，即使商品沒有可購買的 Add-on Product，頁面仍可能停留在 Buy Page，只顯示「加入購物車成功」Banner，使用者還要自己前往 Cart Page。

調整後，系統會先檢查商品是否有符合條件的 Add-on Product：

- 有符合條件的 Add-on Product：維持原流程，前往 Add-on Page（Plus Sales）
- 沒有符合條件的 Add-on Product：不顯示成功 Banner，直接前往 Cart Page
- Related Product Card：不受本次調整影響，加入後仍停留在原頁面並顯示成功 Banner

<aside>
💡

簡單說，就是「有 Add-on 才進 Add-on Page；沒有就直接送進 Cart」，不再讓使用者看完成功訊息後自己點去購物車。

</aside>

# Banner 顯示情境

此處 Banner 是指加入購物車後，頁面上方顯示的「Add to Cart Success Notification」。

| 操作位置／商品情境 | Add-on Product 狀態 | 點擊按鈕後流程 | Banner on Product Card or Buy Page |
| --- | --- | --- | --- |
| Buy Page－Main Product | 有可購買的 Physical Add-on，且有庫存 | 前往 Add-on Page（Plus Sales） | Product Card 上仍會顯示 |
| Buy Page－Main Product | 有關聯的 WEP Add-on | 前往 Add-on Page（Plus Sales） | Product Card 上仍會顯示 |
| Buy Page－Main Product | 同時有 Physical Add-on 與 WEP Add-on | 前往 Add-on Page（Plus Sales） | Product Card 上仍會顯示 |
| Buy Page－Customized Bundle | 有可購買的 Physical Add-on | 前往 Add-on Page（Plus Sales） | Product Card 上仍會顯示 |
| Related Product Card－Simple Product | 不受 Add-on 判斷影響 | 加入購物車後停留在原頁面 | 導頁至 Buy Page 仍會顯示 |
| Cross-sell Product Card | 維持既有流程 | 加入購物車後維持原流程 | 導頁至 Buy Page 仍會顯示 |

[Related Product Card 產品點選並加入購物車後，會顯示加入購物車成功 Banner](bandicam_2026-07-17_09-25-52-942.mp4)
Related Product Card 產品點選並加入購物車後，會顯示加入購物車成功 Banner

[Add-on Page (Product Card) + Cross-sell Product Card 產品點選並加入購物車後，均會顯示加入購物車成功 Banner](bandicam_2026-07-17_09-28-19-128.mp4)
Add-on Page (Product Card) + Cross-sell Product Card 產品點選並加入購物車後，均會顯示加入購物車成功 Banner

# Banner 不顯示情境

| 操作位置／商品情境 | Add-on Product 狀態 | 點擊按鈕後流程 | Banner |
| --- | --- | --- | --- |
| Buy Page－Simple／Virtual／Configurable Product | 沒有任何 Add-on Product | 直接前往 Cart Page | **不顯示** |
| Buy Page－Pre Order Product | 沒有任何 Add-on Product | 直接前往 Cart Page | **不顯示** |
| Buy Page－Main Product | Physical Add-on 無法購買或沒有庫存，且沒有 WEP Add-on | 直接前往 Cart Page | **不顯示** |
| Buy Page－Customized Bundle | 沒有可購買的 Physical Add-on | 直接前往 Cart Page | **不顯示** |
| Buy Page－Main Product with Freebie | 僅有 Freebie，沒有符合條件的 Add-on Product | 直接前往 Cart Page | **不顯示** |

[bandicam 2026-07-17 09-23-54-696.mp4](bandicam_2026-07-17_09-23-54-696.mp4)

## 補充規則

- Freebie 不等同於 Add-on Product，因此只有 Freebie 時，仍視為「沒有 Add-on」
- Physical Add-on 必須可購買且有庫存，才符合進入 Add-on Page 的條件
- WEP Add-on 只要有建立關聯，即符合進入 Add-on Page 的條件
- 從 Buy Page 直接前往 Cart Page 後，可使用 Browser Back Button 返回原 Product Page
- Related Product Card 的行為在 FSD 中有明確說明；Cross-sell Product Card 則依測試清單維持既有流程，FSD 沒有另外修改其規則

# QA 驗證重點（本 skill 加註，可留可刪）

- 正向：Simple／Virtual／Configurable／Pre Order 且無 Add-on → 直接進 Cart Page，且不顯示 Banner
- 維持原樣：有 Physical（有貨）或 WEP Add-on → 進 Add-on Page；Related Product Card / Cross-sell → 留原頁 + Banner
- 邊界：Physical Add-on 缺貨 / 僅 Freebie / Customized Bundle 無可購買 Add-on → 直接進 Cart Page；Configurable 未選規格 → 應報錯
- 回歸：Add-on Page 進入條件、Browser Back 回原頁、購物車數量與內容正確
