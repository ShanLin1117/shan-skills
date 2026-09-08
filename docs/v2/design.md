# Design Document: shan-skills v2 重新設計

> 撰寫日期：2026-09-08
> 基準版本：tag `v1`（commit `059da3b`）
> 證據來源：nec-ai-platform 的 `document-lifecycle-management`（16 棒）與 `agent-task-execution`（S0–S9 / 28 棒）兩次實跑留下的草稿區產物

---

## Overview

### 目標

v1 的七支 skill 在「工作流骨架」與「審查紀律」兩層已被實跑驗證有效。v2 不重寫這兩層，只做三件事：

1. **把實跑中被迫發明的慣例正式化**——`findings.md`、`issues/`、session 地圖的修訂，全部收進一份明文的草稿區契約
2. **把靠文字約束的護欄搬進 harness**——spec 目錄保護、amend / force push 禁令、預設分支保護改由 hook 擋
3. **把冷 context 從「靠使用者記得另開視窗」變成機制**——審查 skill 以 `context: fork` 執行，雙軸平行由 skill 自己保證

### 量尺

「優化到最好」的判準只有一個：**下一次實跑（nec 的 S10–S12）的偏差數少於這一次。** 偏差的定義見「實跑證據」一節。文件變長、規則變多都不算改善。

### 不改的東西

以下內容在 nec 已證明有效，v2 逐字保留，只允許搬位置：

- `shan-grill` 的決策前沿式提問、事實／決策分工、兩案併陳 + 推薦立場
- `shan-spec-qa` 的四道閘門，特別是閘門 2（識別字存在性）與閘門 4 的三類必看問題
- `shan-code-review` 的審查者紀律（先形成預期再看 diff、追蹤被刪掉的東西、不為填欄位硬挑毛病）與多輪煞車（後續輪只報 🔴、縮小範圍、三輪上限、過度工程反向檢查）
- `shan-implement` 的紅綠迴圈三反模式、「spec 有問題就停」、「不自己審自己」
- 可追溯鏈：grill D 編號 → design D 編號 → Req X.Y → 測試前綴 → commit `Refs:`
- 三處人工閘門：spec 搬進正式目錄、commit、對外動作

---

## 實跑證據

每一條都有草稿區檔案可查，是 v2 設計的輸入。

| # | 偏差 | 證據 | 根因 | v2 對應 |
|---|---|---|---|---|
| E1 | 自動審查輪的兩軸在同一個 context 內執行，沒有平行 | `review-S6.md` 第 1 輪審查者自述「兩軸在同一個冷 context 內分開執行，未 spawn 平行 subagent」 | `shan-implement` 只要求 subagent「依 shan-code-review 回報」，沒要求它照 Step 3 再 spawn 兩軸。平台允許三層巢狀，是 prompt 問題 | D2 |
| E2 | 跨棒事實沒有正式落點 | `findings.md`（jsonb 鍵序正規化影響 S23 斷言寫法、測試容器 `ai_tool` 空表、跨分支版號衝突）是實作者自行發明的檔 | skill 只定義了 `review-S<X>.md` | D3 |
| E3 | spec 層級的上升沒有正式落點 | `issues/01`–`08`，狀態 `ready-for-human`，沿用專案另一套 skill 的 ticket 慣例 | skill 說「暫停並告知使用者」，但資訊要活過視窗邊界 | D3 |
| E4 | S0 盤點結果沒有正式落點 | `s0-baseline.md` | 同 E2 | D3 |
| E5 | session 地圖被審查輪回寫修正 | `review-S8.md` 第 2 輪更正地圖的 S26 條目；地圖內長出「已知的 spec 小問題」節 | 地圖是一次性快照，沒有修訂通道 | D3、D7 |
| E6 | `git commit --amend` 違規 | `review-S1.md`「流程違規」節 | config B 節「依主題選讀」漏了 `git-workflow.md`；config G 節沒有「審查修正不得 amend」 | D4、D5 |
| E7 | 審查修正的 commit 節奏兩套規則互相矛盾 | skill 寫「每輪一個獨立 follow-up commit」；專案 steering 寫「整棒一個 follow-up commit」；`review-S3.md` 第 2 輪審了未 commit 的異動再併進同一個 commit | skill 對本該由 config 決定的事帶了預設立場 | D4 |
| E8 | 護欄全靠文字 | 所有 MUST NOT 都只是 prose；nec 的 `docs/harness-engineering/improvement-candidates.md` 顯示需求存在 | v1 沒有 harness 層 | D5 |
| E9 | 專案內舊 skill 搶觸發 | nec `.claude/skills/kiro-spec-to-impl` 的 description 含自動觸發條件，且帶與 config E 節相反的測試指引 | `shan-setup` 只提醒不處理 | D9 |
| E10 | README 狀態過時 | README 寫「尚未經過完整實跑驗證」 | 沒有回寫機制 | D8 |

---

## Architecture

v2 分四層，由下往上：

```
┌─────────────────────────────────────────────────────────┐
│ 4. Harness 層   hooks/hooks.json + scripts/              │  工具擋，不靠 prose
├─────────────────────────────────────────────────────────┤
│ 3. Agent 層     agents/shan-reviewer-*.md                │  冷 context 的載體
├─────────────────────────────────────────────────────────┤
│ 2. Skill 層     skills/shan-*/SKILL.md + references/     │  流程與紀律（v1 內容）
├─────────────────────────────────────────────────────────┤
│ 1. 契約層       .shan/config.md（v2 樣板）                │  專案事實
│                 <草稿區>/<slug>/ 契約                     │  跨 session 狀態
└─────────────────────────────────────────────────────────┘
```

**打包形式改為 plugin**（D1）。目前 repo 整個 junction 到 `~/.claude/skills`，只能載 skill。plugin 可以同時載 `skills/`、`agents/`、`hooks/`，而且放在 `~/.claude/skills/<name>/` 加一個 `.claude-plugin/plugin.json` 就會自動載入，安裝方式不變。

### 依賴方向

- Skill 層讀契約層，**不得**把契約內容複製進 skill（v1 原則 1 不變）
- Agent 層只被 skill 層 spawn；agent 定義檔本身不含專案知識
- Harness 層讀 `.shan/guard.yaml`（契約層的機器可讀側車），不讀 `config.md`——hook 腳本不該解析 markdown

---

## Components and Interfaces

### Repo 結構（v2）

```
shan-skills/
├── .claude-plugin/plugin.json
├── skills/
│   ├── shan-setup/        SKILL.md, config-template.md, guard-template.yaml, spec-format-default.md
│   ├── shan-grill/        SKILL.md
│   ├── shan-to-spec/      SKILL.md
│   ├── shan-spec-qa/      SKILL.md
│   ├── shan-plan/         SKILL.md
│   ├── shan-implement/    SKILL.md
│   └── shan-code-review/  SKILL.md, references/standards-axis.md, references/intent-axis.md
├── agents/
│   ├── shan-review-standards.md
│   └── shan-review-intent.md
├── hooks/hooks.json
├── scripts/
│   ├── guard-protected-paths.sh
│   └── guard-git.sh
├── docs/
│   ├── scratch-contract.md      ← 草稿區契約（skill 與使用者共同的參考）
│   └── v2/design.md             ← 本檔
├── evals/cases.md
├── README.md
└── WORKFLOW.md
```

### 各 skill 的變更

| Skill | v2 變更 | 不變 |
|---|---|---|
| `shan-setup` | 樣板換 v2（D4）；多寫一份 `.shan/guard.yaml`（D5）；偵測並處理重疊 skill（D9）；config 首行加版本標記 | 探索與逐節確認流程 |
| `shan-grill` | 產出改依草稿區契約；無其他變更 | 全部 |
| `shan-to-spec` | 讀 `findings.md`（若存在）當事實來源之一；無其他變更 | 全部 |
| `shan-spec-qa` | 閘門 4 的獨立審查者改用 `context: fork` 的子 skill 或 agent（D2 的同一機制）；修訂建議可寫 `issues/` | 四道閘門內容 |
| `shan-plan` | 地圖加 `## 修訂記錄` 節（D7）；開場 prompt 固定要求讀 `findings.md` 與 open 的 `issues/` | 四維評估、切法、三個確認問句 |
| `shan-implement` | 自動審查改為呼叫 `/shan-code-review`（它自己是 fork）而不是手寫 subagent prompt（D2）；commit 政策全依 config G 節，移除「每輪獨立 follow-up commit」預設（D4）；新增 `findings.md` 與 `issues/` 的寫入責任（D3）；上升 spec 問題時開票而不是只「告知」 | 紅綠迴圈、範圍柵欄、驗證閘門 |
| `shan-code-review` | frontmatter 加 `context: fork`、`background: false`（D2）；Step 3 改 spawn 兩個具名 agent；Step 5 的「🔴 直接修」改為「回報，由呼叫端依裁決修」（D6）；記錄檔寫入責任移到呼叫端 | 紀律文字、多輪規則、報告格式 |

### Agent 定義

兩個 agent 都是唯讀審查者，各自預載一軸的檢查清單：

```yaml
---
name: shan-review-standards
description: 規範軸審查者。只由 shan-code-review 呼叫。
tools: Read, Grep, Glob, Bash
disallowedTools: Edit, Write, NotebookEdit, Agent
---
<共同前置紀律（v1 Step 3 引文）>
<references/standards-axis.md 的內容以 @ 引入或內聯>
```

`Bash` 保留是為了 `git diff` / `git log`。**不預載 skill**：`disable-model-invocation: true` 的 skill 不會被預載進 subagent，所以檢查清單維持 reference 檔。

---

## Data Models

### 草稿區契約（`docs/scratch-contract.md` 的內容摘要）

路徑：`<草稿區>/<feature-slug>/`。草稿區由 config A 節指定，必在 `.gitignore` 內。

| 檔案 | 產出者 | 讀取者 | 寫入模式 | 生命週期 |
|---|---|---|---|---|
| `grill.md` | shan-grill | shan-to-spec | 每輪追加 | 審訊定案後凍結 |
| `spec-draft/` | shan-to-spec | shan-spec-qa、使用者 | 覆寫 | 搬進正式目錄後留作歷史 |
| `qa-report.md` | shan-spec-qa | 使用者 | 每輪追加 | spec 定稿後凍結 |
| `session-map.md` | shan-plan | shan-implement、shan-code-review | 主體覆寫；`## 修訂記錄` 只追加 | 全案 |
| `findings.md` | shan-implement、shan-code-review | 所有後續棒次、shan-to-spec | 只追加，每則標「發現於 / 影響」 | 全案 |
| `issues/NN-<slug>.md` | shan-implement、shan-code-review、shan-spec-qa | 使用者、後續棒次 | 一票一檔；`Status:` 行可改；`## Comments` 只追加 | 至 `resolved` |
| `review-S<X>.md` | shan-code-review 的呼叫端 | 下一輪審查 | 每輪追加 | 該棒收斂後凍結 |

規則：

- **S0 類的前置盤點寫進 `findings.md`**，不另開檔（吸收 E4）
- `issues/` 的票頭固定三行：`Status:`（`open` / `ready-for-human` / `resolved`）、`Blocked by:`、`Spec 任務:`。這是 nec 已在用的形狀，沿用而不重新發明
- 每棒開場固定讀：地圖共通背景 + 本棒細節 + `findings.md` 全文 + `issues/` 中 `Status` 非 `resolved` 者
- 任何 skill 發現「spec 層級的問題」，動作是**開票**，不是只在對話裡說。「告知使用者」仍然要做，但票是持久化的那一份

### `.shan/config.md` v2 樣板的差異

章節字母 A–I **不變**，避免破壞 nec 現有 config。差異全在節內：

- **首行**：`<!-- shan-config: v2 -->`。skill 讀到沒有這行的 config，提示重跑 `shan-setup`，但仍以 v1 語意繼續
- **B 節**拆成兩段：「每棒必讀」（流程性規範：git 流程、審查節奏、測試策略）與「依主題選讀」（領域規範）。E6 的病因是流程規範被當成領域規範選讀
- **G 節**新增三個欄位：
  - `審查修正的 commit 政策`：`每輪一個 follow-up` | `整棒一個 follow-up` | `併入原 commit`
  - `amend 政策`：`禁止` | `僅限未 push` | `不限`
  - `審查的輸入`：`commit 後的 diff` | `工作目錄亦可`
- **A 節**新增 `受保護路徑` 清單（給 `guard.yaml` 用；config 是人讀的版本）

### `.shan/guard.yaml`

hook 腳本讀的機器可讀側車，由 `shan-setup` 產生，**進版控**：

```yaml
version: 2
protected_paths:          # PreToolUse 拒絕 Edit / Write / NotebookEdit
  - ".kiro/specs/**/*.md"
  - ".kiro/steering/**"
  - "src/main/resources/db/migration/V*.sql"
git:
  default_branch: master
  deny_commit_on_default_branch: true
  deny_amend: true
  deny_no_verify: true
  deny_force_push: true
```

---

## Resolved Decisions

### D1 — 打包為 plugin，安裝路徑改為 `~/.claude/skills/shan-skills/`

- **選了什麼**：repo 根加 `.claude-plugin/plugin.json`，skill 搬進 `skills/`，新增 `agents/`、`hooks/`、`scripts/`。junction 目標從 `~/.claude/skills` 改為 `~/.claude/skills/shan-skills`
- **為什麼**：agent 與 hook 沒有 plugin 就無處安放；文件明載 skills-dir plugin 會自動載入，安裝步驟數不變
- **放棄了什麼**：維持平鋪 skill 目錄 + 把 hook 寫進每個專案的 `.claude/settings.json`。後者讓 harness 變成每專案要重做的事，違反「skill 零專案知識」的對稱原則
- **待驗證**：plugin 內 skill 的呼叫名是否需要 `shan-skills:` 前綴。若需要，README 的所有 `/shan-xxx` 要改

### D2 — 冷 context 改由 `context: fork` 保證；雙軸由審查 skill 自己 spawn

- **選了什麼**：`shan-code-review` 加 `context: fork` + `background: false`，body 成為 fork 出來的 subagent 的 prompt。它在 Step 3 平行 spawn `shan-review-standards` 與 `shan-review-intent` 兩個 agent。`shan-implement` 的自動輪直接呼叫 `/shan-code-review <範圍>`，不再手寫 subagent prompt
- **為什麼**：E1 的根因是「委託 subagent 去跑 skill，但沒逼它照 Step 3 做」。fork 讓 skill body 本身成為 subagent 的指令，Step 3 不會被略過。fork 也天然隔離對話歷史，「另開視窗」從紀律變成機制
- **為什麼 `background: false`**：背景 subagent 會被拿掉 `Agent` 工具，無法 spawn 兩軸；而且呼叫端要等結果
- **放棄了什麼**：讓 `shan-implement` 自己平行 spawn 兩軸再彙整。彙整會落在作者的 context 裡，正是 v1 要避免的
- **保留的人工選項**：手動另開視窗跑 `/shan-code-review` 仍然成立，行為完全相同。「加強版審查」不再是不同機制，只是不同時機

### D3 — 草稿區契約成為一等文件

- **選了什麼**：`docs/scratch-contract.md` 定義所有檔案的產出者、讀取者、寫入模式（見 Data Models）。每支 skill 只引用契約，不各自描述檔案格式
- **為什麼**：E2–E5 四條偏差是同一個根因；四個補丁不如一份契約
- **放棄了什麼**：只補 `findings.md` 一個檔。那會讓 `issues/` 與地圖修訂繼續是隱性慣例

### D4 — skill 對 commit 節奏零預設立場，全由 config G 節決定

- **選了什麼**：G 節新增三欄位（見 Data Models）；`shan-implement` 與 `shan-code-review` 讀欄位行事，不再寫「獨立 follow-up commit」
- **為什麼**：E7 證明 skill 帶預設立場會與專案規範打架，而專案規範才是對的那一方
- **放棄了什麼**：把 nec 的「整棒一個 follow-up」寫成新預設。那只是換一個專案打架

### D5 — 三類護欄搬進 hook

- **選了什麼**：`hooks/hooks.json` 註冊兩個 `PreToolUse` hook：
  1. `matcher: "Edit|Write|NotebookEdit"` → `scripts/guard-protected-paths.sh`，讀 `.shan/guard.yaml` 的 `protected_paths`，命中即 `permissionDecision: deny`，理由字串引用 config H 節的條文
  2. `matcher: "Bash"` → `scripts/guard-git.sh`，攔 `git commit --amend`、`--no-verify`、`push --force` / `-f`、以及在 `default_branch` 上的 `git commit`
- **為什麼**：E6、E8。hook 不會忘記讀 steering；prose 會
- **放棄了什麼**：用 skill frontmatter 的 `disallowed-tools` 限制唯讀型 skill。實查後七支 skill 都要寫草稿區，沒有一支是純唯讀，此路不通
- **邊界**：hook 只擋「絕不該做」的事。「未經同意不 commit」無法由 hook 判斷同意，維持 prose
- **平台**：腳本用 bash（Claude Code 在 Windows 以 Git Bash 執行 hook）。`guard.yaml` 缺席時 hook 靜默放行，不影響未跑 `shan-setup` 的專案

### D6 — 審查者只回報，修正由呼叫端依裁決執行

- **選了什麼**：`shan-code-review` 的 Step 5 改為：分級與推薦立場照舊，但**不動手**。呼叫端收到報告後，🔴 由呼叫端在使用者確認後修，🟡 依使用者裁決
- **為什麼**：D2 讓審查者變成 fork 出來的 subagent，它修完的東西沒有人在主 session 看過；而且自動輪與手動輪的行為必須一致，否則 E1 那類「同一支 skill 兩種行為」會再發生
- **影響 WORKFLOW.md 第四節**：「在審查視窗改」的論證仍成立——手動輪的呼叫端就是乾淨視窗；自動輪的呼叫端是作者，所以維持 v1 的「原文轉述 + 使用者拍板」。兩者統一為「呼叫端修」
- **放棄了什麼**：讓 reviewer agent 有 Edit 權限。這會讓兩軸各自改檔，衝突無人仲裁

### D7 — session 地圖可修訂，修訂只追加

- **選了什麼**：地圖加 `## 修訂記錄`，格式 `- YYYY-MM-DD · 來源（review-S8 第 2 輪）· 改了什麼 · 為什麼`。`shan-implement` 與 `shan-code-review` 發現地圖與現況不符時，改地圖本體並在此追加一行。`shan-plan` 重跑時讀修訂記錄，不從零重切
- **為什麼**：E5。地圖已經在被改了，缺的是留痕
- **放棄了什麼**：地圖唯讀、問題全開票。地圖是給下一棒讀的工作文件，錯的內容留著比改掉更危險（review-S8 第 2 輪的 S26 條目就是一個會導向假守門的例子）

### D8 — README 與 WORKFLOW 隨 v2 重寫，狀態節改為「實跑記錄」

- **選了什麼**：README 的「狀態」節改為表列每次實跑的專案（不具名，只寫規模與偏差數）；已知待辦改為指向 `evals/cases.md`
- **為什麼**：E10

### D9 — `shan-setup` 偵測並處理重疊 skill

- **選了什麼**：Step 1 探索時掃 `.claude/skills/*/SKILL.md` 的 description，凡與 shan-* 職責重疊且**未設** `disable-model-invocation: true` 者，列出並建議三選一：加旗標、搬到 `skills-reference/`、刪除。由使用者決定，skill 不自作主張
- **為什麼**：E9
- **放棄了什麼**：只提醒（v1 做法），已證明沒有用

### D10 — 評測以「失敗形狀」為單位，不複製客戶專案內容

- **選了什麼**：`evals/cases.md` 每條記錄：失敗形狀（抽象描述）、觸發條件、v2 應有行為、驗證方式。內容從 E1–E10 抽出，**不含 nec 的程式碼、路徑、業務名詞**
- **為什麼**：nec 是客戶專案，其產物不得進入這個 repo；但失敗形狀是可攜的
- **放棄了什麼**：建一個合成的 sandbox 專案跑自動化 eval。投入與目前規模不成比例，列為 v3 候選

---

## Error Handling

- **config 版本不符**：skill 讀到無 `<!-- shan-config: v2 -->` 首行 → 提示一次「config 為 v1，建議重跑 `/shan-setup`」，然後以 v1 語意繼續（G 節缺的欄位視為「等使用者指示」）
- **`guard.yaml` 缺席或格式錯**：hook 靜默放行，並在第一次放行時輸出一行 stderr 提示。hook 絕不因自身錯誤擋住工作
- **fork 的審查 subagent 失敗**：呼叫端回報「本輪審查未完成」，不得自行補審。記錄檔寫一行「第 N 輪未完成：原因」
- **兩軸其中一軸無回報**：另一軸照常呈現，缺的那軸標「未執行」，判定為「待確認」，不得判「通過」
- **草稿區檔案格式不符契約**（例如舊版 `review-S<X>.md`）：讀取端寬鬆解析，寫入端一律用 v2 格式追加

---

## Testing Strategy

### 驗證輪

v2 寫完後，用 nec 的 **S10、S11、S12** 三棒當驗證輪。S10 與 S11 是 🔴 高風險棒次（Runner 迴圈、Approval Gate），最能暴露審查機制的問題。

驗證前先做 nec 的一致性核對：`config.md` 升 v2 樣板、產 `guard.yaml`、`session-map.md` 的開場 prompt 改為 v2 寫法、`s0-baseline.md` 內容併入 `findings.md`、`issues/` 票頭補齊三行。

### 通過條件

| 項目 | v1 實測 | v2 目標 |
|---|---|---|
| 自動審查輪有平行雙軸 | S6 沒有 | 三棒全部有 |
| 流程違規（amend、審未 commit 的 diff） | S1、S3 各一次 | 零，且 hook 有攔截記錄 |
| 跨棒事實與上升票有正式落點 | 自行發明 | 三棒的產出全在契約列表內 |
| 地圖修訂有留痕 | 無 | 每次修改對應一行修訂記錄 |
| 審查者未動手改檔 | S9 動手了 | 三棒的修正全由呼叫端執行 |

### `evals/cases.md`

從 E1–E10 各抽一條失敗形狀，格式：

```markdown
### C1 — 自動審查輪兩軸未平行
- 觸發：shan-implement 完成 commit 後啟動自動審查
- v2 應有行為：呼叫端記錄中可見兩個具名 agent 同時啟動
- 驗證：檢查 review-S<X>.md 首段的「審查方式」是否寫明兩軸各一 agent
```

手動跑，一條一條勾。自動化留待 v3。

---

## 遷移步驟

1. ~~打 `v1` tag~~（已完成）
2. 本設計文件經使用者核可
3. 重整 repo 結構為 plugin 佈局（搬檔案，內容不動），重建 junction，確認七支 skill 仍可呼叫，確認呼叫名是否需前綴
4. 寫 `docs/scratch-contract.md`、`guard-template.yaml`、兩個 agent、兩支 hook 腳本、`hooks.json`
5. 依「各 skill 的變更」表逐支修改 SKILL.md；`config-template.md` 升 v2
6. 重寫 README、WORKFLOW，寫 `evals/cases.md`
7. nec 一致性核對（見 Testing Strategy）
8. 跑 S10–S12 驗證輪，逐條對照通過條件
9. 通過後打 `v2` tag；未通過的項目回到步驟 5

步驟 3–6 在 shan-skills repo 內，每步一個 commit。步驟 7 在 nec repo，屬客戶專案，只動 `.shan/` 與草稿區。

---

## 使用者裁決記錄

以下四項於 2026-09-08 由使用者裁決，**全部採推薦方案**。表格保留替代案供日後追溯：

| # | 問題 | 推薦 | 替代 |
|---|---|---|---|
| Q1 | plugin 化後若呼叫名必須帶 `shan-skills:` 前綴，接受嗎？ | 接受，README 同步改；前綴反而避免與專案內同名 skill 撞名 | 保持平鋪目錄，hook 改寫進各專案 settings |
| Q2 | 審查者「只回報不動手」（D6）改變了 WORKFLOW 第四節的「在審查視窗改」。接受嗎？ | 接受；手動輪的呼叫端本來就是乾淨視窗，實質沒變 | 保留 reviewer 修 🔴，但自動輪與手動輪行為分岔 |
| Q3 | `issues/` 沿用 nec 目前的票頭格式（`Status:` / `Blocked by:` / `Spec 任務:`），還是另定？ | 沿用，已有八張票在用 | 另定更簡的格式 |
| Q4 | 評測投入到 D10 的手動清單為止，還是現在就做 sandbox 自動化？ | 手動清單；自動化等 v2 驗證輪之後 | 現在做 |
