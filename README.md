# shan-skills

給 [Claude Code](https://claude.com/claude-code) 用的一套 AI 開發工作流 plugin，從「還沒成形的想法」一路帶到「審查過的程式碼」。

大多數 AI coding skill 都會長進專案裡：寫死框架版本、目錄路徑、測試基底類別、commit 慣例。換一個專案就得整套重寫。**這套的做法相反——skill 本體一個專案字眼都沒有，所有 repo 專屬的事實住在該 repo 的 `.shan/config.md`。** 同一套 skill 因此可以跨專案帶著走，而每個專案仍然拿到符合自己慣例的行為。

v2 在此之上加了兩層：**草稿區契約**（跨 session 的狀態怎麼交接）與 **harness 層**（護欄由 hook 擋，不靠提示詞）。

## 工作流

```
shan-setup        新 repo 跑一次 ─────→ .shan/config.md + .shan/guard.yaml

shan-grill        對話 ──────────────→ 決策清單
     ↓
shan-to-spec      決策清單 ──────────→ spec 草稿
     ↓
shan-spec-qa      spec 品保 ─────────→ 四道閘門：格式 / 識別字 / 機械 / 對抗式語意
     ↓
shan-plan         spec ──────────────→ session 地圖 + 每棒的開場 prompt
     ↓
shan-implement    一棒一個視窗 ──────→ 綠燈 + commit + 自動審查
     ↓
shan-code-review  fork 的乾淨 context ─→ 規範軸 ∥ 意圖軸，並排回報
```

中間產物都落在專案的**草稿區**（由 config 指定，通常是 `.scratch/` 這類已被 gitignore 的目錄），檔案格式由 [docs/scratch-contract.md](./docs/scratch-contract.md) 定義。

## Skill 一覽

| Skill | 做什麼 | 什麼時候叫它 |
|---|---|---|
| `shan-setup` | 探索專案的技術棧、路徑、測試與 commit 慣例，寫出 `.shan/config.md` 與 `.shan/guard.yaml` | 每個新 repo 跑一次 |
| `shan-grill` | 決策樹審訊：逐輪推進決策前沿，事實自己查、決策交你裁決 | 需求還沒成形，想先想清楚 |
| `shan-to-spec` | 把定案的決策綜合成 spec 草稿。不面談，只綜合 | 審訊完，要寫規格 |
| `shan-spec-qa` | 對 spec 文件本身做品保；語意審查強制由不共享脈絡的獨立審查者執行 | spec 初稿或修訂完，準備開工前 |
| `shan-plan` | 把任務清單切成 session 邊界，產出地圖與每棒的開場 prompt | 任務數超過 3，要開始實作 |
| `shan-implement` | 議定 seam → 紅綠迴圈 → 驗證閘門 → 收尾交棒 → 自動審查。只做被指派的那一棒 | 動工一棒 |
| `shan-code-review` | 在 fork 出來的乾淨 context 平行 spawn 兩軸審查 agent，並排回報、不跨軸重排、**只回報不動手** | 一棒 commit 之後（自動），或另開視窗做第 2 輪／最終把關 |

除了 `shan-code-review`，其餘六支都掛 `disable-model-invocation: true`——**只能手動叫**，不會自動觸發。`shan-code-review` 不能掛這個旗標，因為它擋的是「模型的一切呼叫」而不只是自動觸發，掛了 `shan-implement` 就無法在 commit 後呼叫它；改以 description 明寫「只在自動輪或使用者明確呼叫時使用」來防誤觸發。呼叫名是 `/shan-skills:shan-grill`，短別名 `/shan-grill` 在沒有同名 skill 時也能用。

## 四層架構

```
harness 層   hooks/hooks.json + scripts/     受保護路徑、amend、force push、預設分支 commit 由 PreToolUse hook 拒絕
agent 層     agents/shan-review-*.md         兩個唯讀審查 agent，只由 shan-code-review spawn
skill 層     skills/shan-*/SKILL.md          流程與紀律
契約層       .shan/config.md（專案事實）、.shan/guard.yaml（機器可讀護欄）、docs/scratch-contract.md（跨 session 狀態）
```

hook 讀的是專案的 `.shan/guard.yaml`。沒有這個檔的專案，hook 靜默放行；啟動前設 `SHAN_GUARD_OFF=1` 可整體停用。

## 安裝

這是一個 skills-dir 型的 plugin：放在 `~/.claude/skills/<name>/` 底下、帶 `.claude-plugin/plugin.json`，Claude Code 下次啟動就會載入 skill、agent 與 hook。實體檔案放這個 repo，用連結掛過去。

**Windows**（directory junction，免管理員權限）：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\shan-skills" -Target "<這個 repo 的絕對路徑>"
```

**Linux / macOS**：

```bash
mkdir -p ~/.claude/skills
ln -s "<這個 repo 的絕對路徑>" ~/.claude/skills/shan-skills
```

hook 腳本以 bash 執行；Windows 需要 Git Bash（Claude Code 本身就要求）。改完 skill 不必重開 session，`/reload-plugins` 即可。

放全域而不是放進專案，有三個好處：跨專案通用、不污染客戶 repo、git worktree 裡也看得到。

## 開始使用

1. 在專案根目錄開 Claude Code，跑 `/shan-skills:shan-setup`。它會探索專案、把發現攤開、逐節問你，寫出 `.shan/config.md` 與 `.shan/guard.yaml`，並對受保護路徑做一次無害的寫入確認 hook 有攔。
2. 之後直接改那兩個檔就好；只有換技術棧或搬 spec 目錄才需要重跑 `shan-setup`。
3. 從 `/shan-skills:shan-grill` 開始第一個功能。

想看整條鏈怎麼運作，見 [WORKFLOW.md](./WORKFLOW.md)。

## 設計原則

1. **skill 零專案知識。** 任何 repo 專屬的路徑、指令、慣例、護欄，一律從 `.shan/config.md` 讀。skill 檔案裡出現具體專案名、框架版本、目錄路徑就是 bug。
2. **config 是 cache，不是抄本。** 只記查不到、或查起來貴的東西；一個指令查得到的當下狀態寫成查詢方式，不寫答案。
3. **格式契約住在專案裡，config 只指路。** 契約跟著 repo 走，不跟著 skill 走。
4. **事實是 agent 的工作，決策是人的工作。** 能查的一律自己查；該裁決的一律送到人面前等。
5. **審查者的 context 必須乾淨，而且是機制不是紀律。** `shan-code-review` 以 `context: fork` 執行，不論從哪裡呼叫都看不到呼叫端的對話；兩軸各一個 agent 平行跑。審查者只回報；呼叫端對 🔴 逐條查證成立就修，🟡 等使用者裁決，修正在提請 follow-up commit 時攤開。
6. **「絕不該做」的事由 hook 擋，不由 prose 擋。** 寫入已核可的 spec、amend、force push、在預設分支 commit——這些不靠模型記得，靠 `PreToolUse` 拒絕。需要判斷的事（未經同意不 commit）仍留在 prose。
7. **跨 session 的狀態只走草稿區契約。** `findings.md`、`issues/`、`review-S<X>.md`、地圖的修訂記錄——每個檔誰產、誰讀、追加還是覆寫，都有明文。skill 不各自發明檔案。
8. **寫入 spec 目錄前一定經過人工核可。** skill 先寫草稿，你核可後才進正式位置。

## 實跑記錄

| 版本 | 專案 | 規模 | 結果 |
|---|---|---|---|
| v1 | 一個 Java / Spring Boot 客戶專案（內網 GitLab，Kiro spec） | 一份 spec 16 棒走完；另一份 47 個任務切 28 棒，跑到 S9 | 骨架與審查紀律有效；暴露十條偏差，整理於 [docs/v2/design.md](./docs/v2/design.md) 的「實跑證據」 |
| v2 | 同一專案 | 接續 S10–S12 當驗證輪 | 進行中；通過條件見設計文件的 Testing Strategy |

v1 到 v2 的差異、每條決策的取捨與放棄的替代案，都在 [docs/v2/design.md](./docs/v2/design.md)。

## 測試

harness 層有自動化測試：

```bash
node tests/guard-test.mjs
```

它在暫存目錄建一個沙盒 repo，對兩支 guard 腳本餵 27 組 `PreToolUse` JSON，驗證拒絕與放行。skill 層的評測是手動清單，見 [evals/cases.md](./evals/cases.md)。

## Repo 結構

```
.claude-plugin/plugin.json      plugin manifest
skills/shan-*/                  七支 skill（shan-setup 含 config / guard / spec 格式三份樣板；shan-code-review 含兩軸檢查清單）
agents/                         shan-review-standards、shan-review-intent
hooks/hooks.json                PreToolUse 註冊
scripts/                        guard-protected-paths.sh、guard-git.sh、lib.sh
tests/guard-test.mjs            harness 層測試
docs/scratch-contract.md        草稿區契約
docs/v2/design.md               v2 設計文件
evals/cases.md                  skill 層的評測案例
```
