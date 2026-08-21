# shan-skills

給 [Claude Code](https://claude.com/claude-code) 用的一套 AI 開發工作流 skill，從「還沒成形的想法」一路帶到「審查過的程式碼」。

大多數 AI coding skill 都會長進專案裡：寫死框架版本、目錄路徑、測試基底類別、commit 慣例。換一個專案就得整套重寫。**這套的做法相反——skill 本體一個專案字眼都沒有，所有 repo 專屬的事實住在該 repo 的 `.shan/config.md`。** 同一套 skill 因此可以跨專案帶著走，而每個專案仍然拿到符合自己慣例的行為。

## 工作流

```
shan-setup        新 repo 跑一次 ─────→ .shan/config.md（這個 repo 的事實）

shan-grill        對話 ──────────────→ 決策清單
     ↓
shan-to-spec      決策清單 ──────────→ spec 草稿
     ↓
shan-spec-qa      spec 品保 ─────────→ 四道閘門：格式 / 識別字 / 機械 / 對抗式語意
     ↓
shan-plan         spec ──────────────→ session 邊界地圖 + 每棒的開場 prompt
     ↓
shan-implement    一棒一個視窗 ──────→ 綠燈 + commit
     ↓
shan-code-review  規範軸 ∥ 意圖軸 ───→ 並排的審查報告
```

中間產物都落在專案的**草稿區**（由 config 指定，通常是 `.scratch/` 這類已被 gitignore 的目錄）。

## Skill 一覽

| Skill | 做什麼 | 什麼時候叫它 |
|---|---|---|
| `shan-setup` | 探索專案的技術棧、路徑、測試與 commit 慣例，寫出 `.shan/config.md` | 每個新 repo 跑一次 |
| `shan-grill` | 決策樹審訊：逐輪推進決策前沿，事實自己查、決策交你裁決 | 需求還沒成形，想先想清楚 |
| `shan-to-spec` | 把定案的決策綜合成 spec 草稿。不面談，只綜合 | 審訊完，要寫規格 |
| `shan-spec-qa` | 對 spec 文件本身做品保；語意審查強制由不共享脈絡的獨立審查者執行 | spec 初稿或修訂完，準備開工前 |
| `shan-plan` | 把任務清單切成 session 邊界，產出地圖與每棒的開場 prompt | 任務數超過 3，要開始實作 |
| `shan-implement` | 議定 seam → 紅綠迴圈 → 驗證閘門 → 收尾交棒。只做被指派的那一棒 | 動工一棒 |
| `shan-code-review` | 規範軸與意圖軸平行 subagent 審查，並排回報、不跨軸重排 | 一棒 commit 之後 |

## 安裝

實體檔案放這個 repo，用連結掛到 Claude Code 的全域 skill 目錄。

**Windows**（directory junction，免管理員權限）：

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills" -Target "<這個 repo 的絕對路徑>"
```

**Linux / macOS**：

```bash
ln -s "<這個 repo 的絕對路徑>" ~/.claude/skills
```

放全域而不是放進專案，有三個好處：跨專案通用、不污染客戶 repo、git worktree 裡也看得到。

## 完整走查

想看整條鏈怎麼運作，見 [WORKFLOW.md](./WORKFLOW.md)——一個功能從發想到審查走完七個階段，含審查回饋怎麼接、多輪怎麼收斂、可以從哪些階段中間切入。

## 開始使用

1. 在專案根目錄開 Claude Code，跑 `/shan-setup`。它會探索專案、把發現攤開、逐節問你，最後寫出 `.shan/config.md`。
2. 之後直接改那個檔就好；只有換技術棧或搬 spec 目錄才需要重跑 `shan-setup`。
3. 從 `/shan-grill` 開始第一個功能。

所有 skill 都掛 `disable-model-invocation: true`——**只能用 `/shan-xxx` 手動叫**，不會自動觸發。想讓某支自動觸發，把它 frontmatter 那一行拿掉即可。

## 設計原則

1. **skill 零專案知識。** 任何 repo 專屬的路徑、指令、慣例、護欄，一律從 `.shan/config.md` 讀。skill 檔案裡出現具體專案名、框架版本、目錄路徑就是 bug。
2. **config 是 cache，不是抄本。** 只記查不到、或查起來貴的東西；一個指令查得到的當下狀態（版號、檔案數）寫成查詢方式，不寫答案——寫死的答案會過期成錯誤的來源。
3. **格式契約住在專案裡，config 只指路。** 契約跟著 repo 走，不跟著 skill 走。同一支 skill 因此能服務格式完全不同的兩個專案。
4. **事實是 agent 的工作，決策是人的工作。** 能查的一律自己查，不拿去問人；該裁決的一律送到人面前等。
5. **審查者的 context 必須乾淨。** 作者沿著原本的思路再走一次，抓不到那條思路沒照到的東西。`shan-spec-qa` 的語意審查與 `shan-code-review` 都強制獨立 context。
6. **寫入 spec 目錄前一定經過人工核可。** skill 先寫草稿，你核可後才進正式位置。

## 狀態

七支 skill 皆已完成，**尚未經過完整的實跑驗證**。已知待辦：

- 整條鏈跑一次真實需求，驗證 config 的章節骨架與格式契約的銜接
- `shan-plan` 的 session 地圖是一次性快照，缺少「計畫過期」的更新機制
- `shan-to-spec` 的 expand–contract 缺收尾條款（共用 integration branch + 最終 integrate-and-verify）
