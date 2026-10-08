---
name: shan-to-req
description: SA 端把定案的業務決策綜合成 requirements 草稿（user story 加可觀察的驗收條件），帶交接用的 Release Info，寫進草稿區等 SA 核可簽出後再交給 PG。也處理需求變更（新 rev）與 PG 退回疑義的答覆。當使用者說「產 requirements」「把需求寫成規格」「交給 PG 的需求」「需求變更」「shan-to-req」，或 shan-grill-sa 已定案要進入規格階段時使用。不面談——要問問題請先跑 shan-grill-sa；產好的 requirements 要品保用 shan-spec-qa；設計與任務是 PG 的 shan-to-spec，這裡不碰。
disable-model-invocation: true
---

# Shan To Req — 決策 → 需求規格

把已定案的業務決策綜合成 `requirements.md`。**不面談**，只綜合。**只產需求**——design 與 tasks 是 PG 的工作，這裡不寫、不暗示。

`requirements.md` 是 SA 與 PG 之間的契約。PG 拿到它之後，不會看到你的對話、你的 `grill.md`、你的 SA 文件。**它必須自己站得住。**

全程繁體中文（台灣用語）輸出。標題依格式契約可能要求英文，見 Step 1。

---

## Step 1：載入

1. **`.shan/config.md`** —— 缺就告訴使用者跑 `/shan-skills:shan-setup`；首行不是 `<!-- shan-config: v2 -->` 就提示一次「config 是舊版」，以現有內容繼續
2. **格式契約** —— config **A 節**指向的那份，**只取 requirements 的部分**。標題、必要章節、驗收條件句式一律以它為準，本 skill 不重述模板
3. **決策來源** —— `<草稿區>/<feature-slug>/grill.md`（`shan-grill-sa` 產的）。沒有就從當前對話綜合，並在交付時說明「本次沒有 grill 記錄，決策來自對話」
4. **`req-questions.md`**（存在才讀）—— PG 退回的疑義。見 Step 5
5. **既有 requirements.md**（spec 目錄或 `spec-draft/`，存在才讀）—— 有就是**需求變更**，走 Step 4 的修訂流程，不是重寫
6. **專案脈絡** —— 依 config **B 節**順序讀 SA 文件；詞彙用 config B 節指定的來源，不自創同義詞
7. 交接區塊的格式依 `${CLAUDE_SKILL_DIR}/../../docs/scratch-contract.md`（下稱**草稿區契約**）的「`requirements.md` 的交接區塊」

---

## Step 2：前置檢查

`grill.md` 的**「待決」還有項目**，就**停下來**，把未決清單攤給使用者，建議回 `shan-grill-sa` 補完。

**MUST NOT 自己替未決事項做決定再寫進 requirements。** requirements 裡每一條規則都應該有人拍過板。

使用者明說「那幾項先擱著、照現況寫」才繼續，並把它們原樣寫進格式契約指定的待確認位置，**標明 PG 不可依此設計**。

---

## Step 3：寫需求（新需求）

依格式契約產出。內容要求：

- **User story 要窮盡。** 角色、正常路徑、邊界、錯誤路徑、權限差異、跨既有功能的互動，全部各自成條。寧可長，不要漏——漏掉的需求在 PG 實作階段才發現，代價是退回重開。
- **驗收條件是可觀察行為**，一條一個，用格式契約指定的句式（通常是 EARS：WHEN / IF / WHERE / WHILE + SHALL）。
- **業務規則的理由**：不顯而易見的規則，在該 Requirement 的 User Story 下加一行 `**Rationale:** <為什麼>`。PG 看不到 `grill.md`，這一行是理由唯一的傳遞管道。
- **編號是後續一切的錨點**——設計決策、任務回指、測試前綴、commit footer 全靠它。編好就不要重排。
- **Glossary 只收本 spec 新引入或有歧義的詞**；已在 config B 節詞彙來源定義過的，不複製。

### 不要寫什麼

**技術實作不屬於需求。** 檔案路徑、class 名、資料表欄位、API 路徑、程式碼片段、「用快取」之類的做法——一律不寫。需求描述**系統可被觀察到的行為**；怎麼做到是 PG 的設計。客戶指定的技術限制（「必須用 SSO」）可以寫，但寫成**限制**並註明來源，不是設計。

### 交接可用性自檢

寫完逐條問自己：**一個沒看過這場審訊的 PG，能不能只靠這一條寫出測試？**

| 不合格形狀 | 改成 |
|---|---|
| 「適當」「盡快」「必要時」「合理範圍」 | 具體數字或條件 |
| 「同現行行為」卻沒說現行行為是什麼 | 把行為寫出來，或引用 Glossary 的定義 |
| 一條裡有兩個 SHALL | 拆成兩條 |
| 「系統應支援 X」 | X 發生時系統做什麼、看到什麼 |
| 角色只寫「使用者」 | 指明是哪個角色，或「所有角色」 |

不合格的修好再交付；修不好是因為業務決策不在手上，那是待決，回 `shan-grill-sa`。

---

## Step 4：Release Info 與需求變更

每份 `requirements.md` 檔尾帶 `## Release Info`，格式見草稿區契約。

### 新需求

`Status: draft`、`Rev: 1`、`Change Log` 一則「初版」。**一律 draft**——簽出是人的動作，見 Step 6。

### 需求變更（既有 requirements.md 已存在）

1. **在 `spec-draft/` 的複本上改**（正式目錄受 hook 保護）。複本的來源是 spec 目錄或上一輪的 `spec-draft/`
2. `Rev` +1、`Status` 回 `draft`、`Released` 日期清掉
3. `Change Log` **追加**一則，以 Req／驗收條件為粒度，動詞只用新增／修改／移除，**每項附原因**。這則是 PG 修訂 design 與 tasks 的唯一依據，所以要寫到「PG 不必比對兩版全文就知道動了哪裡」的程度
4. **編號永不重用、永不重排**：
   - 新增 → 往後接號
   - 修改 → 原號不動，內容改
   - 移除 → 保留 Requirement 標題並標 `（已移除，rev N）`，驗收條件刪除。**不要讓後面的編號往前補**
5. 修改的項目若會讓**已完成的實作**失效（例如把已上線的規則反過來），在 Change Log 該項明寫「影響已實作行為」。PG 會據此把它當遷移而不是新功能

---

## Step 5：答覆 PG 的疑義

`req-questions.md` 有 `Status: open` 的疑義時：

- 每則疑義的答覆來自 `grill.md` 的對應決策（`shan-grill-sa` 處理過），沒有對應決策的，回去補審訊，**不要自己答**
- 答覆在「**SA 答覆**」小節寫結論與對應的 requirements rev，`Status` 改 `answered`
- 答覆若造成 requirements 內容變動，同步走 Step 4 的變更流程；答覆是「維持原需求」的，說明理由，Rev 不動
- 疑義本身、PG 的暫定理解不改一個字

---

## Step 6：交付

產出寫進 `<草稿區>/<feature-slug>/spec-draft/requirements.md`（覆寫），然後：

1. 列出規模（幾條 Requirement、幾條驗收條件）；變更時列出本次 Change Log
2. 點出你在綜合過程中**自行補的假設**（`grill.md` 沒講、你依 SA 文件推斷的），逐條列出讓使用者複核
3. 變更時列出本次已答覆的 `req-questions.md` 條目
4. 告訴使用者下一步，**三步，順序固定**：
   1. 跑 `/shan-skills:shan-spec-qa`（會自動走需求模式）
   2. 通過後**由 SA 手動**把 `Status` 改成 `released`、填 `Released` 日期——這是簽出，skill 不代做
   3. **由 SA** 把 `requirements.md` 搬進 config A 節的 spec 目錄，並把同一份檔案交給 PG（PG 放進自己草稿區的 `handoff-in/`）

**MUST NOT 直接寫入 spec 目錄。** 那道搬遷動作是人工核可閘門，hook 也會擋。

---

## 完成條件

- `spec-draft/requirements.md` 標題與必要章節**逐字相符**格式契約，檔尾有合規的 `## Release Info`，`Status` 為 `draft`
- 每條規則都有人拍過板；`grill.md` 沒有待決
- 沒有任何技術實作字眼；每條驗收條件通過「交接可用性自檢」
- 變更時：編號沒有重排或重用，Change Log 每項附原因
- 自行補的假設已逐條列給使用者
- spec 目錄**沒有被動過**

---

## 邊界

- **MUST NOT 面談。** 需要釐清就回 `shan-grill-sa`。
- **MUST NOT 寫 design 或 tasks**，也不在 requirements 裡暗示實作做法。
- **MUST NOT 把 `Status` 設為 `released`。** 簽出是人的動作。
- **MUST NOT 修改 spec 目錄下的既有文件。**
- 交付客戶的 SA 文件（docx）不在這支的範圍；它是 requirements 的衍生輸出，另案處理。
