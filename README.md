# shan-skills

個人的 AI 開發工作流 skill 組。設計目標是**可攜**：skill 本體零專案知識，所有 repo 專屬的事實住在該 repo 的 `.shan/config.md`。

## 安裝

實體檔案放這個 repo，用 directory junction 掛到 Claude Code 的全域 skill 目錄（Windows，免管理員權限）：

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills" -Target "<這個 repo 的絕對路徑>"
```

Linux / macOS 用 symlink：

```bash
ln -s "<這個 repo 的絕對路徑>" ~/.claude/skills
```

## 工作流

```
shan-setup        新 repo 跑一次 → 產出 .shan/config.md
     │
shan-grill        對話 ──────────→ <草稿區>/<slug>/grill.md（決策清單）
     ↓
shan-to-spec      決策清單 ──────→ spec 草稿（三份）
     ↓
shan-spec-qa      spec 品保 ─────→ 格式閘門 + 識別字查核 + 對抗式語意審查
     ↓
shan-plan         spec ──────────→ 開發計畫（session 邊界 + 每棒開場 prompt）
     ↓
shan-implement    一棒一 session ─→ 綠燈 + commit
     ↓
shan-code-review  雙軸平行審查 ──→ 審查報告
```

## 設計原則

1. **skill 零專案知識。** 任何 repo 專屬的路徑、指令、慣例、護欄，一律從 `.shan/config.md` 讀。skill 檔案裡出現具體專案名、框架版本、目錄路徑就是 bug。
2. **config 是 cache，不是抄本。** 只記查不到或查起來貴的東西；一個指令查得到的當下狀態（版號、檔案數）寫成查詢方式，不寫答案。
3. **格式契約住在專案裡。** config 只指路。契約跟著 repo 走，不跟著 skill 走。
4. **事實是 agent 的工作，決策是人的工作。** 能查的一律自己查；該裁決的一律送到人面前等。
5. **寫入 spec 目錄前一定經過人工核可。** skill 先寫草稿到草稿區，使用者核可後才進 spec 目錄。

## 開發狀態

| Skill | 狀態 |
|---|---|
| `shan-setup` | ✅ |
| `shan-grill` | ✅ |
| `shan-to-spec` | ✅ |
| `shan-spec-qa` | ✅ |
| `shan-plan` | ✅ |
| `shan-implement` | 待建 |
| `shan-code-review` | 待建 |

開發期間所有 skill 都掛 `disable-model-invocation: true`（只能手動 `/shan-xxx` 叫），避免全域生效時亂觸發。整套穩定後再逐支決定要不要開自動觸發。
