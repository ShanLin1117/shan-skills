---
name: shan-to-spec
description: PG 端把 SA 簽出的 requirements 加上技術決策，綜合成 design 與 tasks 草稿，寫進草稿區等使用者核可後才進 spec 目錄。也處理 requirements 釋出新 rev 後的修訂，以及發現需求疑義時的退回。當使用者說「產設計」「寫 design」「寫 tasks」「拆任務」「需求改版了」「shan-to-spec」，或 requirements 已到手、技術決策已定案要進入規格階段時使用。輸入是 SA 的 requirements，不是需求本身——需求沒成形請 SA 用 shan-grill-sa 與 shan-to-req；技術決策要先問用 shan-grill；產好的 spec 要品保用 shan-spec-qa；要排開發計畫用 shan-plan。
disable-model-invocation: true
---

# Shan To Spec — 需求 + 決策 → 設計與任務

把 SA 簽出的 `requirements.md` 與已定案的技術決策，綜合成 `design.md` 和 `tasks.md`。**不面談**，只綜合。

**requirements 是別人的契約，不是你的草稿。** 這支 skill 不改它一個字——有疑義退回 SA，不自己補、不默默猜。

全程繁體中文（台灣用語）輸出。文件標題依格式契約可能要求英文，見 Step 1。

---

## Step 1：載入

1. **`.shan/config.md`** —— 缺就告訴使用者跑 `/shan-skills:shan-setup`；首行不是 `<!-- shan-config: v2 -->` 就提示一次「config 是舊版」，以現有內容繼續
2. **格式契約** —— config **A 節**指向的那份，**只取 design 與 tasks 的部分**。標題、必要章節、生成標頭一律以它為準，本 skill 不重述任何模板
3. **requirements（輸入，唯讀）** —— `<草稿區>/<feature-slug>/handoff-in/requirements.md`。
   - 沒有這個檔，但 `spec-draft/requirements.md` 存在且已 `released`：單人流程（SA 與 PG 是同一人），改讀它，並在交付時註明
   - 都沒有：**停下來**，告訴使用者需求要先由 `shan-grill-sa` → `shan-to-req` 產出並簽出，或把 SA 交付的檔放進 `handoff-in/`
   - 讀 `## Release Info`：`Status` 不是 `released` 就**停下來**，要 SA 先簽出；記下 `Rev`
4. **決策來源** —— `<草稿區>/<feature-slug>/grill.md`（PG 端 `shan-grill` 產的技術決策）。沒有就從當前對話綜合，交付時說明「本次沒有 grill 記錄，決策來自對話」
5. **跨棒事實** —— `findings.md`（若存在；格式見草稿區契約）。前一輪實作查證出來、spec 該吸收的事實
6. **需求疑義** —— `req-questions.md`（若存在）。已 `answered` 的疑義，答覆已反映在 requirements 的新 rev 裡，不必再處理
7. **專案脈絡** —— 依 config **B 節**順序讀；詞彙用 config B 節指定的來源，不自創同義詞
8. **Codebase** —— 探索要動到的區域。事實查核走 config **C 節**，不憑記憶斷言任何 class / 欄位 / 設定鍵存在
9. **既有 design / tasks** —— spec 目錄裡這個 slug 已有 `design.md`（或 `tasks.md`）時，讀它的 `**Based on:**` rev，進入 Step 2 的修訂判斷

草稿區檔案格式一律依 `${CLAUDE_SKILL_DIR}/../../docs/scratch-contract.md`（下稱**草稿區契約**）。

### 份數與檔名由格式契約決定

Step 5–6 是兩個**角色**，不是固定檔名：

| 角色 | 承載什麼 |
|---|---|
| **設計**（how） | 架構、資料模型、介面契約、已定案決策 |
| **任務**（do） | 執行順序、依賴邊、回指標記 |

契約把兩個角色併在同一個檔，就寫進同一個檔；契約沒有某個角色，就跳過那一步。**MUST NOT 自行決定要產幾個檔**。需求角色由 SA 的 `requirements.md` 承擔，這裡**原樣複製**進 `spec-draft/` 讓三份成套，不加工。

---

## Step 2：新建或修訂

| 狀況 | 做法 |
|---|---|
| spec 目錄裡沒有這個 slug 的 design / tasks | **新建**，照 Step 3–7 |
| 有，且 `**Based on:**` rev **等於** requirements 的 `Rev` | 沒有需求面的變動，不需要這支 skill；告訴使用者 |
| 有，且 rev **落後** | **修訂**，照下面的流程 |

### 修訂流程（requirements 釋出新 rev）

1. 把正式目錄的 design / tasks 複製到 `spec-draft/`，**在複本上改**（正式目錄受 hook 保護）
2. 讀 requirements `Change Log` 中**落差 rev 之間的每一則**（例如 design 基於 rev 2、現在是 rev 4，就讀 rev 3 與 rev 4）。這是唯一的依據，不要比對兩版全文
3. 逐項處理，每個變動列出它影響的 **design 決策**、**元件／資料模型**、**任務**：
   - **新增 Req** → 補設計、**往後接號**新增任務
   - **修改 Req** → 找出受影響的決策與任務，改寫；改寫決策時保留編號，在決策內寫「rev N 修訂：<原因>」
   - **移除 Req** → 對應任務：**未勾選**的移除或改寫；**已勾選（已實作）**的不改寫，**另加新任務**處理拆除或調整，並開 `issues/` 票說明
   - Change Log 標「影響已實作行為」的項目，一律開票，不要悄悄當新功能處理
4. 編號永不重排、永不重用，與 requirements 的規則一致
5. 完成後 `**Based on:**` 更新到新 rev
6. 若已有 `session-map.md`，提醒使用者**重跑 `shan-plan`**（它會先讀修訂記錄、保留已完成棒次，不從零重切）

---

## Step 3：需求疑義檢查

讀 requirements 時，逐條問：**我能不能只靠這一條設計並寫出測試？**

出現下列任何一種，**不要猜、不要補**，寫進 `req-questions.md`（格式見草稿區契約）：

- 含糊（「適當」「盡快」）或無法觀察
- 兩條需求互相矛盾，或與 `findings.md` / codebase 查到的事實矛盾
- 少一個分支（錯誤路徑、權限差異、狀態轉換）
- 需求裡出現了技術實作字眼（那是不該出現的越界）

每則疑義標**阻斷**：

- **阻斷＝是**（沒有答覆就無法設計該條）：寫進 `req-questions.md` 後，**對該條相關的設計暫停**。其餘不相干的部分可以繼續，但交付時要明講哪些被卡住
- **阻斷＝否**：寫下「PG 的暫定理解」，design 以它繼續，並在 design 對應處標**待確認（req-questions Q<N>）**

交付時把疑義清單列給使用者，讓他帶給 SA。

---

## Step 4：議定 seam（唯一的 checkpoint）

動筆之前，先勾勒**要在哪些 seam 驗證這個功能**，把清單交給使用者確認。

**seam** = 你觀察行為的公開邊界；測試住在 seam 上，不伸進內部。挑選原則：

- **優先用既有 seam**，不要新增
- **用能到的最高 seam**——愈高，一個測試覆蓋愈多真實路徑
- **seam 愈少愈好**，理想是一個
- 真的需要新 seam，就提在你能提的最高點，並說明為什麼既有的不夠

一併對照 config **E 節**：這些 seam 落在哪種測試型態，有沒有既有的 prior art 可以照著寫。

**這是本 skill 唯一會停下來等回覆的地方。** seam 沒定就往下寫，等於整份 spec 的驗證面是猜的。修訂流程若 seam 沒變，直接沿用既有設計的測試策略，不必再問。

---

## Step 5：寫設計（how）

依格式契約產出。內容要求：

- **`**Based on:** requirements rev N`** 放在 `## Overview` 第一行（沒有 design 的小功能放 `tasks.md` 的 Overview）
- **決策編號要接續 `grill.md`。** 審訊的 `D1` 就是 design 的 `D1`。每條寫**選了什麼、為什麼、放棄了什麼**，審訊當時查到的支撐事實一併帶過來。沒有 `grill.md` 就從 `D1` 起編
- **每個設計決策回指它服務的 Requirement**（`serves Req 2.1`）。一個決策指不到任何需求，代表它在做沒人要求的事
- **測試策略直接寫 Step 4 議定的 seam**，附 config E 節對應的測試型態與 prior art
- **寫架構，不寫位置。** 模組／套件／類別職責／介面形狀／資料模型／API 契約要寫（那是決策）；**具體檔案路徑、行號、實作程式碼片段不要寫**（會過期）
  - 例外：prototype 產出的片段若比散文更精確地固定了一個決策（狀態機、schema、型別形狀），就內聯它，註明來自 prototype
- **牴觸既有決策就明講**，不靜默覆蓋（config B 節）
- **設計與需求打架**時，**不要用設計默默改寫需求**。需求有問題走 Step 3；設計上做不到就開 `issues/` 票，兩案併陳

---

## Step 6：寫任務（do）

依格式契約產出，切法看 config **F 節**：

- **`horizontal`** —— 同層聚焦（schema + 資料存取一組、業務邏輯一組、對外介面一組）。跨層太大的任務要拆。
- **`vertical`** —— 每個任務貫穿全層，完成即可獨立驗證。

**兩種切法的共同要求：**

- 每個任務結束時**綠燈可 commit**
- 每個任務標**依賴邊**，依格式契約的依賴圖章節呈現
- 每個任務都有**回指驗收條件**的標記——沒有回指的任務，代表它在做沒人要求的事，拿掉或補需求（補需求是 SA 的事，走 Step 3）
- 每個驗收條件**至少被一個任務涵蓋**——沒有孤兒需求。標為「已移除」的需求不需要、也不可以被任務回指
- 任務大小以「一個乾淨的 context window 做得完」為上限

**大範圍機械式重構是切法的例外。** 改用 **expand–contract**：先 expand（新舊並存）→ 分批遷移呼叫點（每批一個任務、都被 expand 擋住、批批綠燈）→ 最後 contract（沒有呼叫者了才刪舊的）。清單**必須以一個 integrate-and-verify 任務收尾**。

---

## Step 7：交付

產出寫進 `<草稿區>/<feature-slug>/spec-draft/`：`requirements.md`（原樣複製，**逐字相同**）、`design.md`、`tasks.md`（依格式契約）。然後：

1. 列出產出的檔案與各自規模（幾個決策、幾個任務）；修訂時列出**每則 Change Log 影響到的決策與任務**
2. 摘要 Step 4 議定的 seam
3. 列出 Step 3 寫進 `req-questions.md` 的疑義（阻斷與否），請使用者帶給 SA
4. 點出你在綜合過程中**自行補的假設**（`grill.md` 沒講、你依 codebase 現況推斷的），逐條列出讓使用者複核
5. 若吸收了 `findings.md` 的事實，列出哪幾條被寫進了哪些驗收條件或決策
6. 告訴使用者下一步：跑 `/shan-skills:shan-spec-qa` 品保，通過後再由**他自己**把三份搬進 config A 節的 spec 目錄

**MUST NOT 直接寫入 spec 目錄。** 那道搬遷動作是人工核可閘門，hook 也會擋。

---

## 完成條件

- `spec-draft/` 的份數與檔名符合格式契約，標題與必要章節**逐字相符**
- `spec-draft/requirements.md` 與來源**逐字相同**（`diff` 為空）
- design 標明 `**Based on:** requirements rev N`，N 等於 requirements 的 `Rev`
- 每個任務都有回指標記，每個（未移除的）驗收條件都被至少一個任務涵蓋
- 每個決策都有人拍過板（來自 `grill.md`，或使用者明確授權），且回指它服務的需求
- 需求疑義已寫進 `req-questions.md`，沒有被默默吸收
- 自行補的假設已逐條列給使用者
- spec 目錄**沒有被動過**

---

## 邊界

- **MUST NOT 修改 requirements 的內容**，包括錯字與格式。發現錯誤走 `req-questions.md`。
- **MUST NOT 面談。** 除了 Step 4 的 seam 確認，不要問問題。需要釐清技術決策就回 `shan-grill`，需求疑義就退回 SA。
- **MUST NOT 寫實作程式碼**，也不要為了「證明可行」順手改 codebase。
- **MUST NOT 修改 spec 目錄下的既有文件**。牴觸既有 spec 的，寫進 design 的決策段明講，由使用者決定怎麼處理。
