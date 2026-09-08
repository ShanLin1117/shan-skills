---
name: shan-setup
description: 在一個 repo 裡跑一次，探索它的技術棧、路徑、測試與 commit 慣例，寫出 .shan/config.md 供其餘 shan-* skill 讀取。當使用者說「設定 shan skills」「這個專案要怎麼接」「shan-setup」，或在新 repo 第一次要用 shan-grill / shan-to-spec / shan-plan / shan-implement / shan-code-review 卻還沒有 .shan/config.md 時使用。
disable-model-invocation: true
---

# Shan Setup — 專案設定

其餘 shan-* skill 一律**零專案知識**：所有跟這個 repo 有關的事實，都住在 `.shan/config.md`。這支 skill 的工作就是把那份檔案生出來。

這是一支**對話驅動**的 skill，不是腳本。先探索、把發現攤開、跟使用者確認，最後才寫檔。

全程繁體中文（台灣用語）輸出。技術名詞、指令、路徑保留原文。

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
- **護欄文件**：`CLAUDE.md`、`AGENTS.md`、`.kiro/steering/`、`CONTRIBUTING.md` — 有沒有 MUST / MUST NOT 層級的規範
- **草稿區慣例**：`.scratch/`、`tmp/`、`.gitignore` 裡已被忽略的工作目錄
- **Commit 慣例**：`git log --oneline -30` 看實際格式；`.gitmessage`、`commitlint` 設定、`core.hooksPath` 下的 hook
- **Remote**：`git remote -v` — 是公開平台還是客戶內網？這決定「發布」類動作預設要不要停下來問

已經存在 `.shan/config.md` 時，讀它，並把這次探索當成**更新**而不是重寫——保留使用者手改過的內容。

---

## Step 2：攤開發現，逐節確認

先用幾行講清楚「找到什麼、缺什麼」。然後一節一節走，**每節先給推薦答案**，讓使用者可以用一個字接受。

**探索已經定案的節就直接寫，不要問。** 只有真正分岔的才開口，並且只給一行說明。

| 節 | 何時需要問 |
|---|---|
| **A. 路徑與 spec 格式** | 專案沒有既成 spec 慣例時，確認要用預設格式（見下）還是別的 |
| **B. 領域文件讀取順序** | 找到多份護欄文件、順序不明顯時 |
| **C. 事實查核對照表** | 幾乎不用問，探索就能填 |
| **D. 技術棧與指令** | 有多套建置路徑（本機 vs 容器）時，確認預設走哪條 |
| **E. 測試慣例** | 測試要外部服務才能跑時，確認「服務不在」的處置（停下來問？降級？） |
| **F. 任務切法** | 一定要問，見下 |
| **G. Commit 慣例** | `git log` 格式不一致時 |
| **H. 專案硬護欄** | 找到 MUST / MUST NOT 條款時，確認哪幾條要進 config |

### A — spec 格式的三種來源

1. **沿用專案既有契約**（找到 `.kiro/steering/spec-language.md` 之類的格式規範）→ config 只放**指標**，不複製內容
2. **沿用既有 spec 的實際長相**（有 spec 但沒有成文契約）→ 讀兩三份，把共同結構寫成契約，請使用者確認
3. **全新專案** → 用 [spec-format-default.md](./spec-format-default.md)，把它複製進專案（預設 `docs/specs/SPEC-FORMAT.md`），config 指向它

無論哪一種，**契約要住在專案裡**，config 只負責指路。這樣它跟著 repo 走，而不是跟著 skill 走。

### F — 任務切法（一定要問）

> 建議：**horizontal**

- **horizontal** — 同層聚焦（schema + entity + repository 一組）。session 短、context 乾淨、架構漂移少。後端服務、有 migration 的專案通常適合。
- **vertical** — 每個任務貫穿全層，完成即可獨立 demo。早期就曝光整合風險。前端、小服務、原型專案通常適合。

兩種都要求每個任務結束時**綠燈可 commit**，並在 spec 的依賴圖裡標明阻塞邊。

---

## Step 3：寫檔

把草稿給使用者看過再寫。用 [config-template.md](./config-template.md) 當骨架。

- 寫到 `.shan/config.md`
- `.shan/` **要進版控**——它是專案知識，對同事和未來的 session 都有用
- 已存在時就地更新，不要蓋掉使用者的手改

---

## Step 4：收尾

告訴使用者：

1. `.shan/config.md` 寫好了，`shan-grill` / `shan-to-spec` / `shan-spec-qa` / `shan-plan` / `shan-implement` / `shan-code-review` 會讀它
2. 之後直接改那個檔就好，只有換技術棧或搬 spec 目錄才需要重跑這支 skill
3. 若專案裡還有跟 shan-* 描述重疊的舊 skill，提醒他們會搶觸發

---

## 完成條件

`.shan/config.md` 存在，且 **A–H 每一節都有內容或明確標記「不適用」**——沒有一節是空的或含糊的。config 裡沒有任何一個指令查得到的當下狀態。
