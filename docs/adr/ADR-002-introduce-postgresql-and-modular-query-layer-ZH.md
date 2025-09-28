ADR-002: 引入 PostgreSQL 與查詢模組化
狀態：Accepted
日期：2025-09-28

1. 背景
原本專案只用 wedding_data.json 儲存資料，但隨著需求增加出現幾個問題：
- JSON 難以維護與更新。
- 無法方便查詢或處理模糊搜尋。
- 把整包 JSON 丟給 GPT 會浪費 Token。

2. 決策
- 資料層改為 PostgreSQL。
- 建立 db/ 資料夾，拆出 db_connection、queries、formatters。
- 在意圖判斷先用硬邏輯與正則清洗，減少 API 成本。

3. 考慮過的替代方案
- 繼續用 JSON：簡單，但不適合長期維護。
- 全部交給 GPT：彈性高，但成本與輸出不穩定。

4. 後果
- 專案結構更清楚，可以成長。
- 我需要額外學 SQL，但換來擴展性與穩定性。
