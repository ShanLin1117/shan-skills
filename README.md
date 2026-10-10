# shan-skills

給 [Claude Code](https://claude.com/claude-code) 用的一套 AI 開發工作流 plugin，從「還沒成形的想法」一路帶到「審查過的程式碼」。

大多數 AI coding skill 都會長進專案裡：寫死框架版本、目錄路徑、測試基底類別、commit 慣例。換一個專案就得整套重寫。**這套的做法相反——skill 本體一個專案字眼都沒有，所有 repo 專屬的事實住在該 repo 的 `.shan/config.md`。** 同一套 skill 因此可以跨專案帶著走，而每個專案仍然拿到符合自己慣例的行為。

2026 年 9 月的改版在此之上加了兩層：**草稿區契約**（跨 session 的狀態怎麼交接）與 **harness 層**（護欄由 hook 擋，不靠提示詞）。

## 工作流

```
shan-setup        新 repo 跑一次 ─────→ .shan/config.md + .shan/guard.yaml

shan-grill        對話 ──────────────→ 決策清單
     ↓
shan-to-spec      決策清單 ──────────→ spec 草稿
                  （團隊流程下上面兩步拆成 SA 與 PG 兩段，多出分析書、SD、docx，見下）
     ↓
shan-spec-qa      spec 品保 ─────────→ 四道閘門：格式 / 識別字 / 機械 / 對抗式語意
     ↓
shan-plan         spec ──────────────→ session 地圖 + 每棒的開場 prompt
     ↓
shan-implement    一棒一個視窗 ──────→ 綠燈 + commit + 自動審查
     ↓
shan-code-review  fork 的乾淨 context ─→ 規範軸 ∥ 意圖軸，並排回報
```

### 團隊流程：SA 與 PG 分段接力

一個專案若由不同角色接力（SA 收需求與做系統設計、PG 開發），工作流在交接物處切開。**交接物有哪些、命名、格式、要不要輸出 Word，都由各專案的 config 決定**，skill 不綁死：

```
SA（文件專案，setup 選 sa 輪廓；系統設計時唯讀參考 codebase）
 shan-grill-sa ──→ shan-to-sa ──→ shan-to-docx ──→ 人工補圖 ──┐
  業務決策         需求分析書.md     需求分析書.docx             │
                                                              ▼
                    shan-to-req ←── md + 人工補完的 docx（差異請你裁決）
                        │  requirements.md（user story + 驗收條件）
                        ▼
                  shan-spec-qa（需求模式）→ SA 手動簽出
                        │
 shan-grill（設計決策）──→ shan-to-sd ──→ shan-spec-qa（設計書模式）→ SA 手動簽出
                            系統設計書.md ──→ shan-to-docx ──→ 人工補圖 → 客戶版 SD.docx
                        │
                        └──── requirements.md + SD 交付 ────┐
                                                            ▼
PG（程式專案）                                      handoff-in/
 shan-grill（實作決策）→ shan-to-spec（design + tasks）→ shan-spec-qa（完整模式）→ shan-plan → …
        ▲                                                   │
        └──────── req-questions.md（疑義退回 SA）────────────┘
```

- **權威順序**：requirements（行為）> SD（DB、介面、流程契約）> design（SD 之下的實作決策）。衝突時 PG 不自行裁決，走 `req-questions.md`
- **簽出是人的動作**：`Status` 由 SA 手動改成 `released`，skill 不代簽
- **requirements 與 SD 各自有 `Rev`**：只改 SD 不讓需求升版；SD 以 `Based on` 綁住它依據的需求版次。PG 依各自的 `Change Log` 修訂 design 與 tasks，不比對全文
- **PG 不改上游**：`spec-qa` 逐字比對 PG 手上的副本，被動過就是阻斷級
- **docx 是輸出品，不是來源**：`shan-to-docx` 以專案的 Word 範本為底轉換（樣式對應檔由專案提供）；畫面截圖等複雜內容人工補。`shan-to-req` 同時讀 md 與補完的 docx，兩者有差異時由你裁決
- **團隊沒有的階段就跳過**：沒有系統設計書就在 config 寫「無」，整段不走
- **單人流程不需要任何交接階段**：沒有 SA、沒有 SD 的專案，`grill → to-spec` 一步就產出 requirements、design、tasks，與最初相同。`shan-to-spec` 看上游產物決定模式——有 `handoff-in/` 才進接力模式（唯讀、要求簽出）；否則由決策自己補上。團隊流程的階段只有真的存在才會被要求

細節見 [docs/scratch-contract.md](./docs/scratch-contract.md)。

中間產物都落在專案的**草稿區**（由 config 指定，通常是 `.scratch/` 這類已被 gitignore 的目錄），檔案格式由 [docs/scratch-contract.md](./docs/scratch-contract.md) 定義。

## Skill 一覽

| Skill | 做什麼 | 什麼時候叫它 |
|---|---|---|
| `shan-setup` | 探索專案的技術棧、路徑、測試與 commit 慣例，寫出 `.shan/config.md` 與 `.shan/guard.yaml` | 每個新 repo 跑一次 |
| `shan-grill-sa` | SA 端的需求審訊：只問業務規則，事實從 SA 專案文件查（現行系統行為可唯讀參考 codebase）；也處理 PG 退回的疑義 | 收到客戶需求或問題單，要釐清 |
| `shan-to-sa` | 把業務決策綜合成需求分析書 md | SA 審訊完，要寫分析書 |
| `shan-to-docx` | 以專案的 Word 範本把需求分析書／系統設計書 md 轉成 docx（只換內文，保留頁首頁尾與樣式），圖片留預留位置由人工補；不覆蓋既有檔 | 要交付客戶 Word 版 |
| `shan-to-req` | 把需求分析書（md + 人工補完的 docx）與業務決策綜合成 `requirements.md`（user story + 驗收條件 + Release Info），支援需求變更的新 rev | 分析書完成，要產給 PG 的需求 |
| `shan-to-sd` | 把簽出的 requirements 與設計決策綜合成系統設計書 md（畫面、資料流、欄位對照、DDL、URL 與流程），事實以 codebase 查證 | 需求簽出且設計決策定案，團隊有 SD 階段時 |
| `shan-grill` | 決策樹審訊：逐輪推進決策前沿，事實自己查、決策交你裁決。團隊流程下專問設計與實作決策（SA 產 SD 前、PG 做 design 前各一次）| 需求還沒成形，或 requirements／SD 到手後要定設計決策 |
| `shan-to-spec` | 把 SA 簽出的 requirements 與 SD 加上實作決策，綜合成 design + tasks。不改上游，疑義退回；上游釋出新 rev 時做修訂 | PG 收到 requirements 並審訊完，要寫設計與任務 |
| `shan-spec-qa` | 對 spec 文件本身做品保；語意審查強制由不共享脈絡的獨立審查者執行。**需求模式**審 requirements 能不能交給 PG，**設計書模式**審 SD 是否忠於需求且不與 codebase 衝突，**完整模式**審整份 spec 並比對是否忠於 requirements 與 SD | requirements 準備簽出前；spec 初稿或修訂完，準備開工前 |
| `shan-plan` | 把任務清單切成 session 邊界，產出地圖與每棒的開場 prompt | 任務數超過 3，要開始實作 |
| `shan-implement` | 議定 seam → 紅綠迴圈 → 驗證閘門 → 收尾交棒 → 自動審查。只做被指派的那一棒 | 動工一棒 |
| `shan-code-review` | 在 fork 出來的乾淨 context 平行 spawn 兩軸審查 agent，並排回報、不跨軸重排、**只回報不動手** | 一棒 commit 之後（自動），或另開視窗做第 2 輪／最終把關 |

除了 `shan-code-review`，其餘都掛 `disable-model-invocation: true`——**只能手動叫**，不會自動觸發。`shan-code-review` 不能掛這個旗標，因為它擋的是「模型的一切呼叫」而不只是自動觸發，掛了 `shan-implement` 就無法在 commit 後呼叫它；改以 description 明寫「只在自動輪或使用者明確呼叫時使用」來防誤觸發。呼叫名是 `/shan-skills:shan-grill`，短別名 `/shan-grill` 在沒有同名 skill 時也能用。

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
9. **每支 skill 都能單獨使用，階段都可以省略，缺上游時降級而不是擋下來。** 沒有 config 照樣跑（用預設與自行探索）；沒有格式契約用附的預設；沒有 spec 或 SD 就依手上有的做。**會停下來的只有三種**：待決事項要由人拍板、人工核可閘門（簽出、搬進 spec 目錄、commit 點頭）、會覆蓋人工編輯過的檔案。 skill 依上游產物存不存在決定行為，不依角色。「簽出」「版次比對」是交接機制，只有真的收到別人的交付件才適用；單人專案不該為了沒有的角色多跑步驟。skill 只是把你會做的步驟少打幾個字。

## 實跑記錄

| 階段 | 專案 | 規模 | 結果 |
|---|---|---|---|
| 改版前 | 一個 Java / Spring Boot 客戶專案（內網 GitLab，Kiro spec） | 一份 spec 16 棒走完；另一份 47 個任務切 28 棒，跑到 S9 | 骨架與審查紀律有效；暴露十條偏差，整理於 [docs/redesign-2026-09.md](./docs/redesign-2026-09.md) 的「實跑證據」 |
| 改版後 | 同一專案 | 同一份 spec 接續跑完 S10–S27 加一份全案把關 | 十一條評測案例逐條回溯驗過，結果見 [evals/cases.md](./evals/cases.md) |

改版前後的差異、每條決策的取捨與放棄的替代案，都在 [docs/redesign-2026-09.md](./docs/redesign-2026-09.md)。

## 測試

harness 層有自動化測試：

```bash
node tests/guard-test.mjs
```

它在暫存目錄建一個沙盒 repo，對兩支 guard 腳本餵 29 組 `PreToolUse` JSON，驗證拒絕與放行。docx 轉換腳本另有測試（需要 `python-docx`，請裝在專案虛擬環境）：

```bash
python -X utf8 tests/docx-test.py
```

skill 層的評測是手動清單，見 [evals/cases.md](./evals/cases.md)。

## Repo 結構

```
.claude-plugin/plugin.json      plugin manifest
skills/shan-*/                  十二支 skill（shan-setup 含 config / guard 樣板、spec / 需求分析書 / SD 格式預設與 docx 對應樣板；shan-code-review 含兩軸檢查清單）
agents/                         shan-review-standards、shan-review-intent
hooks/hooks.json                PreToolUse 註冊
scripts/                        guard-protected-paths.sh、guard-git.sh、lib.sh
scripts/docx/                   md_to_docx.py、docx_dump.py（通用，不含專案知識）
tests/guard-test.mjs            harness 層測試
tests/docx-test.py              docx 腳本測試
docs/scratch-contract.md        草稿區契約
docs/redesign-2026-09.md        2026 年 9 月改版的設計文件
evals/cases.md                  skill 層的評測案例
```
