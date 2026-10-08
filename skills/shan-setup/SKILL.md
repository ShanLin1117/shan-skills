---
name: shan-setup
description: 在一個 repo 裡跑一次，探索它的技術棧、路徑、測試與 commit 慣例（SA 的文件專案則探索文件目錄與需求格式），寫出 .shan/config.md 與 .shan/guard.yaml 供其餘 shan-* skill 與 hook 讀取。當使用者說「設定 shan skills」「這個專案要怎麼接」「shan-setup」，或在新 repo 第一次要用 shan-grill / shan-grill-sa / shan-to-req / shan-to-spec / shan-plan / shan-implement / shan-code-review 卻還沒有 .shan/config.md，或 config 版本過舊時使用。
disable-model-invocation: true
---

# Shan Setup — 專案設定

其餘 shan-* skill 一律**零專案知識**：所有跟這個 repo 有關的事實，都住在 `.shan/config.md`；由 hook 強制的護欄住在 `.shan/guard.yaml`。這支 skill 的工作就是把這兩份檔案生出來。

這是一支**對話驅動**的 skill，不是腳本。先探索、把發現攤開、跟使用者確認，最後才寫檔。

全程繁體中文（台灣用語）輸出。技術名詞、指令、路徑保留原文。

---

## Step 0：先問角色輪廓

第一個問題：**這個 repo 是哪一種？**

| 輪廓 | 是什麼 | 用到的 skill |
|---|---|---|
| `pg`（預設） | 程式專案：有 codebase、測試、commit 慣例 | grill、to-spec、spec-qa、plan、implement、code-review |
| `sa` | SA 的文件專案：存放需求分析書、需求規格書等文件，通常不是程式專案 | grill-sa、to-sa、to-docx、to-req、to-sd、spec-qa（需求模式與設計書模式） |

寫進 config A 節的「角色輪廓」。**單人從需求做到實作的專案選 `pg`**——它涵蓋全鏈。

`sa` 輪廓的差異，後面各步驟另有標示：只探索文件、只填 **A、B、C、H、I** 五節，**D、E、F、G 寫「不適用」**；不產 `guard.yaml` 的 git 區段（沒有 commit 慣例要護）。

`sa` 輪廓的 repo 不一定看得到程式碼，但 SA 做系統設計時要參考。C 節與 A 節的「codebase 參考路徑」記下**唯讀**的程式專案位置；沒有固定位置就寫「由 prompt 指定」，skill 會要求使用者在對話中指出。

---

## 核心原則：只寫查不到、或查起來貴的東西

`.shan/config.md` 是一份 **cache**。cache 一旦記了會過期的東西，就會變成錯誤的來源。

- ✅ **值得寫**：不成文慣例、決策的理由、踩過的坑、跨檔案才拼得出來的規則、要下三個指令才問得出來的答案
- ❌ **不要寫**：一個指令就查得到的當下狀態（下一個 migration 版號、目前版本號、檔案數量、目錄清單）

會過期的狀態一律寫成**查詢方式**而不是答案：

> 下一個 migration 版號：以 `ls db/migration/` 現況為準（**不要**在此寫死版號）

---

## Step 1：探索

讀，不要猜。目標是讓 Step 2 的每一節都能帶著推薦答案出場。

- **建置與依賴**：`package.json` / `pom.xml` / `build.gradle` / `pyproject.toml` / `Cargo.toml` / `go.mod` — 語言、框架、建置與測試指令、task runner
- **測試**：測試目錄、測試框架、既有的基底類別或共用 fixture、有沒有需要外部服務（容器、DB）才能跑的測試
- **既有 spec / 需求文件慣例**：`.kiro/specs/`、`docs/specs/`、`specs/`、`docs/adr/`、`CONTEXT.md` — 有沒有既成的格式契約可以沿用
- **護欄文件**：`CLAUDE.md`、`AGENTS.md`、`.kiro/steering/`、`CONTRIBUTING.md` — 有沒有 MUST / MUST NOT 層級的規範。**特別找流程性規範**（git 流程、審查節奏、commit 規則）——它們要進 B 節的「每棒必讀」，漏讀過一次就會出事
- **草稿區慣例**：`.scratch/`、`tmp/`、`.gitignore` 裡已被忽略的工作目錄
- **Commit 慣例**：`git log --oneline -30` 看實際格式；`.gitmessage`、`commitlint` 設定、`core.hooksPath` 下的 hook；**找 amend 與審查修正的規則**（往往寫在 steering 或 CONTRIBUTING 裡）
- **Remote**：`git remote -v` — 是公開平台還是客戶內網？這決定「發布」類動作預設要不要停下來問
- **重疊的 skill**：掃 `.claude/skills/*/SKILL.md` 的 description，凡職責與 shan-* 重疊（產 spec、切 session、實作、審查）且**未設** `disable-model-invocation: true` 者，記下來——它們會在 shan-* 執行途中自動觸發、帶進相反的指引

**`sa` 輪廓改探索這些**（取代上面的建置／測試／commit 等項目）：

- **文件目錄**：需求分析書、需求規格書、客戶問題單各放哪；有沒有編號或命名慣例
- **Word 範本**：有沒有需求分析書、系統設計書的 `.docx` 範本；有就進入下面的「docx 對應」流程
- **codebase 參考路徑**：使用者提到的程式專案位置（唯讀）
- **既有 requirements 的長相**：已有的 requirements.md 或等價文件，用什麼標題與句式；沒有就用預設格式（見 A 節）
- **詞彙來源**：有沒有 glossary、專有名詞表
- **Remote**：同上，決定對外動作的預設姿態

已經存在 `.shan/config.md` 時，讀它，並把這次探索當成**更新**而不是重寫——保留使用者手改過的內容。第一行不是 `<!-- shan-config: v2 -->` 就是舊版，升級時保留內容、補齊 v2 新欄位。

---

## Step 2：攤開發現，逐節確認

先用幾行講清楚「找到什麼、缺什麼」。然後一節一節走，**每節先給推薦答案**，讓使用者可以用一個字接受。

**探索已經定案的節就直接寫，不要問。** 只有真正分岔的才開口，並且只給一行說明。

| 節 | 何時需要問 |
|---|---|
| **A. 路徑與 spec 格式** | `sa` 輪廓時：「Spec 目錄」指 requirements 的輸出位置，「格式契約」只需涵蓋 requirements 與交接區塊。其餘：專案沒有既成 spec 慣例時，確認要用預設格式（見下）還是別的；**受保護路徑**一定要確認 |
| **B. 領域文件讀取順序** | 哪些是「每棒必讀」、哪些是「依主題選讀」——流程性規範一律必讀 |
| **C. 事實查核對照表** | 幾乎不用問，探索就能填 |
| **D. 技術棧與指令** | 有多套建置路徑（本機 vs 容器）時，確認預設走哪條 |
| **E. 測試慣例** | 測試要外部服務才能跑時，確認「服務不在」的處置（停下來問？降級？） |
| **F. 任務切法** | 一定要問，見下 |
| **G. Commit 慣例** | `git log` 格式不一致時；**三個政策欄位一定要問**，見下 |
| **H. 專案硬護欄** | 找到 MUST / MUST NOT 條款時，確認哪幾條要進 config |
| **I. 對外動作** | remote 是客戶或內網時確認預設姿態 |

### A — spec 格式的三種來源

1. **沿用專案既有契約**（找到 `.kiro/steering/spec-language.md` 之類的格式規範）→ config 只放**指標**，不複製內容
2. **沿用既有 spec 的實際長相**（有 spec 但沒有成文契約）→ 讀兩三份，把共同結構寫成契約，請使用者確認
3. **全新專案** → 用 [spec-format-default.md](./spec-format-default.md)，把它複製進專案（預設 `docs/specs/SPEC-FORMAT.md`），config 指向它

無論哪一種，**契約要住在專案裡**，config 只負責指路。這樣它跟著 repo 走，而不是跟著 skill 走。

### A — 交接物與 docx 對應（團隊流程）

問清楚這個團隊的流程有哪些交接物，**別預設有**：

1. **需求分析書**：有沒有？命名規則？格式契約——沿用專案既有的，或用 [sa-format-default.md](./sa-format-default.md) 複製進專案（預設 `docs/specs/SA-FORMAT.md`）
2. **系統設計書（SD）**：有沒有這個階段？有的話同樣處理格式契約，預設樣板 [sd-format-default.md](./sd-format-default.md)。**沒有 SD 階段的團隊寫「無」**，skill 會跳過整段
3. **docx 對應**：需求分析書、SD 各要輸出 docx 嗎？要的話，每種 docx 做一份對應檔（樣板 [docx-mapping-template.json](./docx-mapping-template.json)，複製進專案）：
   - 用 `python -X utf8 ${CLAUDE_SKILL_DIR}/../../scripts/docx/docx_dump.py <範本.docx>` 傾印範本，**看範本實際用了哪些樣式**（各層標題、內文）
   - 把 md 的 `#`～`####` 與範本樣式的對應攤給使用者確認，**樣式名稱以範本為準，不要憑印象**
   - 內部資訊（`Release Info`、`對應需求`）列進 `skip_sections` / `drop_line_patterns`，客戶版不該出現
   - 跑一次 `md_to_docx.py` 試轉，確認樣式都找得到（找不到它會報錯並列出範本現有樣式）

這幾項全部寫進 config A 節的「交接物」。單人流程、沒有 docx 需求的專案，整段寫「不適用」。

### A — SA 端的受保護路徑

`sa` 輪廓只保護**已釋出的 requirements**（`Status: released` 的檔所在位置）。改它要走新 rev 流程，不該被直接編輯。沒有 migration、steering 這類要護的東西。

### A — 受保護路徑（一定要確認）

這份清單同時寫進 config A 節（人讀）與 `guard.yaml`（hook 讀）。預設推薦：

- 已核可的 spec 文件（需求、設計）→ 保護
- 任務清單（要勾選）→ **開洞**放在 `allowed_paths`
- 已套用的 migration → 保護
- steering / 護欄文件本身 → 保護

跟使用者確認每一條。**保護太多會讓 skill 卡死在正常工作上**，例如把 `tasks.md` 也鎖住就沒人能勾任務。

### F — 任務切法（一定要問）

> 建議：**horizontal**

- **horizontal** — 同層聚焦（schema + entity + repository 一組）。session 短、context 乾淨、架構漂移少。後端服務、有 migration 的專案通常適合。
- **vertical** — 每個任務貫穿全層，完成即可獨立 demo。早期就曝光整合風險。前端、小服務、原型專案通常適合。

兩種都要求每個任務結束時**綠燈可 commit**，並在 spec 的依賴圖裡標明阻塞邊。

### G — 三個政策欄位（一定要問）

這三個欄位早期版本沒有，實跑時因此出過 amend 違規與兩套 follow-up 規則打架：

| 欄位 | 選項 | 推薦 |
|---|---|---|
| 審查的輸入 | `commit 後的 diff` / `工作目錄亦可` | commit 後的 diff——審查範圍才有清楚邊界 |
| 審查修正的 commit 政策 | `每輪一個 follow-up` / `整棒一個 follow-up` / `併入原 commit` | 專案既有規範為準；沒有就 `整棒一個 follow-up` |
| amend 政策 | `禁止` / `僅限未 push` / `不限` | `禁止`——與 `guard.yaml` 的 `deny_amend` 同步 |

---

## Step 3：寫檔

把草稿給使用者看過再寫。`sa` 輪廓的 `guard.yaml` 只填 `protected_paths`，`protected_existing_paths` 與 `git` 區段留空或省略。

1. **`.shan/config.md`**：用 [config-template.md](./config-template.md) 當骨架，第一行必須是 `<!-- shan-config: v2 -->`
2. **`.shan/guard.yaml`**：用 [guard-template.yaml](./guard-template.yaml) 當骨架，填 A 節的受保護路徑與 G 節的 git 政策。**寫完立刻生效**——hook 每次工具呼叫都會讀它，不需要重開 session

兩份都**要進版控**——它們是專案知識，對同事和未來的 session 都有用。已存在時就地更新，不要蓋掉使用者的手改。

寫完 `guard.yaml` 後做一次自我驗證：告訴使用者「接下來我會試著對受保護路徑做一次無害的 Edit，預期會被 hook 拒絕」，然後真的試一次。被拒 = 護欄在運作；沒被拒 = plugin 的 hook 沒載入，要提醒使用者檢查安裝。

---

## Step 4：收尾

告訴使用者：

1. `.shan/config.md` 與 `.shan/guard.yaml` 寫好了，其餘 shan-* skill 與 hook 會讀它們
2. 之後直接改那兩個檔就好，只有換技術棧或搬 spec 目錄才需要重跑這支 skill
3. **Step 1 找到的重疊 skill**：逐一列出，給三個選項——加 `disable-model-invocation: true`、搬到 `.claude/skills-reference/`、刪除——由使用者決定，**不要自作主張**。使用者選了才動手
4. 暫時停用護欄的方法：啟動 Claude Code 前設 `SHAN_GUARD_OFF=1`；或暫時改 `guard.yaml`

---

## 完成條件

- `.shan/config.md` 存在，首行為格式標記 `<!-- shan-config: v2 -->`，**A–I 每一節都有內容或明確標記「不適用」**——沒有一節是空的或含糊的
- B 節有「每棒必讀」段；G 節三個政策欄位都有值
- `.shan/guard.yaml` 存在，與 config A / G 節一致，且自我驗證時 hook 確實拒絕過一次
- config 裡沒有任何一個指令查得到的當下狀態
- 重疊 skill 的處置已由使用者裁決並執行
