---
name: shan-to-sd
description: 把已簽出的 requirements 與設計決策綜合成系統設計書（SD）md 草稿——畫面異動、資料流、資料表與欄位對照、DB 變更、URL 與流程規格，寫進草稿區的 doc-draft/，之後可轉 docx 交付客戶並交給 PG。需要查 codebase 以確保 DDL 與介面不與現況衝突。當使用者說「產系統設計書」「寫 SD」「系統程式規格書」「DB 要怎麼改」「shan-to-sd」，或需求已簽出、設計決策已定案要寫 SD 時使用。設計決策要先問用 shan-grill；轉 Word 用 shan-to-docx；品保用 shan-spec-qa。config 寫「系統設計書：無」的專案不使用這支。
disable-model-invocation: true
---

# Shan To SD — 需求 + 設計決策 → 系統設計書

把簽出的 `requirements.md` 與已定案的設計決策，綜合成系統設計書（`<名稱>_SD.md`）。**不面談**，只綜合。

SD 是 SA 交給 PG 的**設計契約**：DB 與介面的決定在這裡定案，PG 的 `design.md` 在它之下補實作層決策，不重寫、不推翻它。所以 SD 寫的每個 DDL、URL、欄位對照，都要經得起 codebase 現況的檢驗。

全程繁體中文（台灣用語）輸出。技術名詞、SQL、識別字保留原文。

---

## Step 1：載入

1. **`.shan/config.md`** —— 缺就告訴使用者跑 `/shan-skills:shan-setup`；首行不是 `<!-- shan-config: v2 -->` 就提示一次「config 是舊版」，以現有內容繼續。**A 節「系統設計書」若為「無」，告訴使用者這個專案沒有 SD 階段，停下**
2. **格式契約** —— config **A 節「交接物 → 系統設計書」**指向的那份。標題、章節、`對應需求` 行、`Release Info` 一律以它為準，本 skill 不重述模板
3. **命名** —— 同一節的命名規則（例：`<功能名稱>_SD`）
4. **requirements（輸入，唯讀）** —— `<草稿區>/<feature-slug>/spec-draft/requirements.md`（SA 端）或 `handoff-in/requirements.md`。讀 `## Release Info`：`Status` 不是 `released` 就**停下來**，SD 不能建在未簽出的需求上；記下 `Rev`
5. **需求分析書** —— `doc-draft/<名稱>_SA.md`，以及人工補過的 `.docx`（用 `python -X utf8 ${CLAUDE_SKILL_DIR}/../../scripts/docx/docx_dump.py <檔案>` 傾印，圖片只會標 `[IMAGE]`，內容不解析；畫面異動的細節向使用者確認）
6. **設計決策** —— `<草稿區>/<feature-slug>/grill.md` 中 `[設計]` 標籤的決策（`shan-grill` 產的）。沒有就從當前對話綜合，交付時說明；**但資料表、欄位、DDL、URL 這類難以逆轉的決策沒有人拍過板就停下來，建議回 `shan-grill`**
7. **codebase（唯讀）** —— 依 config **C 節 / A 節「codebase 參考路徑」**。這是 SD 的事實基礎：現有資料表結構、欄位型別、既有 URL、既有 service 與流程。config 寫「由 prompt 指定」而使用者沒給，就請他指出。**只查，不改**
8. **專案脈絡** —— 依 config **B 節**順序讀；詞彙用 config B 節指定的來源
9. **既有 SD** —— 目標檔已存在（修訂），讀它的 `Release Info`，走 Step 2 的修訂分支

草稿區檔案格式依 `${CLAUDE_SKILL_DIR}/../../docs/scratch-contract.md`（下稱**草稿區契約**）。

---

## Step 2：新建或修訂

| 狀況 | 做法 |
|---|---|
| `doc-draft/<名稱>_SD.md` 不存在 | **新建**，照 Step 3–5 |
| 已存在，requirements 的 `Rev` 比 SD 的 `Based on` 新 | **修訂**：讀 requirements `Change Log` 的落差 rev，逐項找受影響的 SD 段落；改寫後 `Based on` 更新、SD `Rev` +1、`Change Log` 追加 |
| 已存在，SD 本身要改（設計變更，requirements 沒動） | **修訂**：SD `Rev` +1、`Change Log` 追加，`Based on` 不動 |

修訂時：

- **不覆蓋既有檔**——它可能被人手動改過。複製為 `-v<Rev>` 後綴的新檔再改，或請使用者指示
- SD 的段落編號／標題不重用；移除的功能段落標 `（已移除，rev N）`，保留標題
- Change Log 以功能段落為粒度，動詞新增／修改／移除，每項附原因。**影響已實作行為的變動明寫**

---

## Step 3：事實查核

動筆前，把 SD 要引用的現況事實**逐一實際查證**，不憑記憶斷言：

| 要確認什麼 | 去哪查 |
|---|---|
| 資料表／欄位／型別／索引 | config C 節指向的 schema 或 migration |
| 既有 URL、service、流程 | config C 節指向的原始碼 |
| 要新增的欄位或表是否已存在、有沒有同義的既有物 | 同上 |

查證結果的處置：

- **與 SD 打算寫的衝突**（欄位已存在但型別不同、URL 已被占用）→ 不要默默改寫，回報使用者，必要時回 `shan-grill` 重議
- **查不到**（codebase 參考路徑沒給、或該部分不在可讀範圍）→ 在 SD 對應處標 **「待確認：<要確認什麼>」**，並在交付時列出。**不要用猜的填**

---

## Step 4：寫系統設計書

依格式契約產出。內容要求：

- **每個功能段落帶 `對應需求`**（契約固定項）：列出它落實的 `Req X.Y`。每條 requirement 至少被一個功能段落對應；確實不涉及設計變更的，明寫「不涉及設計變更」及理由——不要讓 requirement 默默沒有下落
- **設計決策的出處**：每個難以逆轉的決定（新欄位、新表、URL、交易邊界）要能回溯到 `grill.md` 的某個 `[設計]` 決策。沒有出處的不寫進 SD
- **DDL 與資料轉換可直接執行**：型別、預設值、NULL 性、前置清理（如改型別前先清空白）都寫全；有 comment 慣例的，依 config 寫
- **流程用 pseudocode 或條件清單**，把檢核、錯誤處理、交易與補償動作（失敗時回復什麼）寫出來。PG 照這份寫，漏寫的錯誤路徑到實作才發現
- **全院版／個人版這類「一套邏輯多個入口」的差異，用對照表列出**，不要散在文字裡
- **寫契約，不寫實作**：介面形狀、資料模型、流程規則是 SD 的事；具體檔案路徑、行號、程式碼片段不寫（會過期）。pseudocode 描述流程可以，Java／SQL 實作碼只在 DDL 與 SQL 設計這種「語法本身就是契約」的地方寫
- **截圖不由 AI 產生**：畫面異動需要圖的位置寫 `![說明](待補)`，由 SA 人工貼入

---

## Step 5：Release Info

檔尾 `## Release Info`（格式見草稿區契約「系統設計書的交接區塊」）：

- `Status: draft`、`Rev: 1`（新建）、`Based on: requirements rev N`（N 為 Step 1 記下的 requirements `Rev`）、`Change Log` 一則「初版」
- **一律 draft。簽出是人的動作**，與 requirements 相同

---

## Step 6：交付

產出寫進 `<草稿區>/<feature-slug>/doc-draft/<名稱>_SD.md`，然後：

1. 列出規模（幾個功能段落、幾項 DB 變更、幾個 URL）
2. 點出所有 **「待確認」** 項，與你**自行補的假設**，逐條列給使用者複核
3. 列出每條 requirement 對應到哪些 SD 段落，未對應的要說明
4. 列出放了 `待補` 的圖片位置
5. 告訴使用者下一步：
   - `/shan-skills:shan-spec-qa`（會走設計書模式，核對 SD 與 requirements、與 codebase 現況）
   - 通過後由 SA **手動**把 `Status` 改 `released`、填 `Released`
   - 要交客戶：`/shan-skills:shan-to-docx`，人工補圖
   - 把 `_SD.md`（與補完的 docx）連同 `requirements.md` 交給 PG

---

## 完成條件

- 產出符合格式契約的標題與章節，帶合規的 `Release Info`，`Status` 為 `draft`
- 每條 requirement 都有對應的功能段落，或明寫不涉及設計變更
- 每個 DDL、URL、欄位對照都經 codebase 查證，或標明待確認
- 難以逆轉的決定都有 `grill.md` 的出處
- 沒有覆蓋任何既有檔案；codebase 沒有被動過

---

## 邊界

- **MUST NOT 面談。** 設計決策要問回 `shan-grill`。
- **MUST NOT 修改 requirements。** SD 與 requirements 矛盾，或 requirements 有洞，寫進 `req-questions.md`（格式見草稿區契約），不要在 SD 裡默默補或改寫。
- **MUST NOT 修改 codebase**；參考路徑一律唯讀。
- **MUST NOT 把 `Status` 設為 `released`。**
- **MUST NOT 直接寫入正式文件目錄與 spec 目錄。**
