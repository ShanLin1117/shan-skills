# 草稿區契約

所有 shan-* skill 之間跨 session 傳遞狀態的唯一通道。skill 只引用本契約，**不得**在自己的 SKILL.md 裡另行描述這些檔案的格式。

路徑：`<草稿區>/<feature-slug>/`。草稿區由 `.shan/config.md` A 節指定，**必須**已在 `.gitignore` 內；沒有 config 時預設 `.scratch/`。

---

## 檔案總表

| 檔案 | 產出者 | 讀取者 | 寫入模式 | 生命週期 |
|---|---|---|---|---|
| `grill.md` | shan-grill | shan-to-spec | 每輪追加 | 審訊定案後凍結 |
| `spec-draft/` | shan-to-spec | shan-spec-qa、使用者 | 覆寫 | 搬進正式目錄後留作歷史 |
| `qa-report.md` | shan-spec-qa | 使用者、shan-plan | 每輪追加 | spec 定稿後凍結 |
| `session-map.md` | shan-plan | shan-implement、shan-code-review | 主體覆寫；`## 修訂記錄` 只追加 | 全案 |
| `findings.md` | shan-implement、shan-code-review、shan-spec-qa | 所有後續棒次、shan-to-spec | 只追加 | 全案 |
| `issues/NN-<slug>.md` | shan-implement、shan-code-review、shan-spec-qa | 使用者、後續棒次 | 一票一檔；`Status:` 可改；`## Comments` 只追加 | 至 `resolved` |
| `review-S<X>.md` | shan-code-review 的**呼叫端** | 下一輪審查 | 每輪追加 | 該棒收斂後凍結 |

三條通則：

1. **只追加的檔案不得重排、不得刪除既有內容。** 要更正就追加一則「更正」，指明更正的是哪一則。
2. **日期一律用 `date +%F` 取得**，不憑記憶填。
3. **每棒開場固定讀**：`session-map.md` 的共通背景與本棒細節、`findings.md` 全文、`issues/` 中 `Status` 非 `resolved` 的票。這三份是上一棒留給你的全部脈絡。

---

## `grill.md`

格式由 `shan-grill` 定義，摘要：`## 已敲定決策`（D1、D2…，每條含問題／決定／理由／依據事實）、`## 待決`、`## 明確排除`。決策編號一經寫定不得重排，`shan-to-spec` 的設計文件直接接續同一組編號。

## `spec-draft/`

份數與檔名由 config A 節指向的格式契約決定。`shan-to-spec` 每次執行整目錄覆寫。使用者核可後**由使用者**搬進正式 spec 目錄，skill 不代做。

## `qa-report.md`

```markdown
## 第 N 輪 — YYYY-MM-DD

### 閘門結果
| 閘門 | 結果 | 數字 |
|---|---|---|
| 1 格式 | ✅ / ⚠️ | |
| 2 識別字 | ✅ / ⚠️ | 可疑 N 個 |
| 3 機械 | ✅ / ⚠️ | 需求 N、驗收 N、涵蓋率 N% |
| 4 語意 | 執行 / 略過 | 阻斷級 N、文字層 N |

### 實質發現
### 文字層發現
### 不同意審查之處
### 未解決的開放決策
```

閘門 4 每跑一輪追加一節。**問題從結構性轉為文字層就是可以停的訊號**，這個判斷要寫在該輪結尾。

## `session-map.md`

主體格式由 `shan-plan` 定義。v2 新增必要章節 `## 修訂記錄`，放在檔尾：

```markdown
## 修訂記錄

- YYYY-MM-DD · review-S8 第 2 輪 · S26 條目「以 ArchUnit 類別依賴斷言守門」改為「方法層級且排除第二呼叫點」 · 原寫法會產生恆綠的假守門
```

規則：

- 任何 skill 發現地圖與現況不符，**改地圖本體，並在此追加一行**。錯的地圖留著比改掉更危險。
- 每行固定四段：日期 · 來源 · 改了什麼 · 為什麼。
- `shan-plan` 重跑時先讀修訂記錄，不從零重切。

## `findings.md`

跨棒事實：實作或審查過程中查證出來、spec 沒寫、且會影響後續棒次的東西。**S0 類的前置盤點也寫在這裡**，不另開檔。

```markdown
# 跨棒發現 — <feature-slug>

> 只追加。每則標明「發現於」與「影響」。

## F1 — <一句話標題>

- **發現於**：S1（任務 1.1）
- **影響**：S23、S24、S12
- **日期**：YYYY-MM-DD

### 事實
<查證到什麼，附檔案路徑或指令輸出>

### 對後續棒次的意思
<具體到「某棒的某個斷言要怎麼寫」的程度>
```

判準：「下一棒的人如果不知道這件事，會做錯什麼？」講不出來的不是 finding，不要寫。

## `issues/NN-<slug>.md`

spec 層級的上升票。skill 說「暫停並告知使用者」時，**同時開票**——對話會消失，票不會。

編號自 `01` 起，依相依順序（blocker 在前）。票頭固定三行：

```markdown
# NN — <一句話標題>

Status: open | ready-for-human | resolved
Blocked by: —
Spec 任務: 任務 1.3（S2）

> ⚠ 本票是 <spec 文字問題 / 設計矛盾 / 需求缺漏>，不是程式碼缺陷。
> **不得由 agent 直接修改 spec 目錄。**

## 矛盾在哪 / 缺口在哪
<引用 spec 原文，附行號>

## 已採取的實作（若有）
<使用者裁決了什麼、程式碼現在怎麼做>

## 需要人做的事
<兩案併陳 + 推薦立場>

## Comments

- YYYY-MM-DD：<誰、說了什麼>
```

狀態字串：**config A 節若指向專案自己的 triage 標籤檔，以那份為準**；沒有就用下面三種：

- `open`：發現了，還沒整理成可裁決的形式
- `ready-for-human`：兩案併陳完成，等使用者拍板
- `resolved`：使用者裁決並落地（spec 已改，或明確決定不改）。在 `## Comments` 記錄裁決

不論哪一套，skill 讀票時把「非 `resolved`」一律視為未結。

## `review-S<X>.md`

由 **呼叫 `shan-code-review` 的那個 session** 寫，不是審查 subagent 寫。每輪追加：

```markdown
## 第 N 輪 — YYYY-MM-DD — 範圍 <定點>...<HEAD>

**審查方式**：fork 的 shan-code-review，兩軸各一 agent 平行（shan-review-standards / shan-review-intent）
**判定**：通過 / 有問題已修正 / 待確認

### 已修正（修正 commit: <sha>）
- 🔴 <問題> → <怎麼修的>

### 已裁決不修（使用者決定）
- 🟡 <問題> — 理由：<使用者給的理由>

### 有異議
- <審查者的判斷與呼叫端查證後的結論不同之處>

### 交接
- <留給下一棒或下一輪的事；跨棒的請同時寫進 findings.md>
```

**第 1 輪也要寫**。「審查方式」那一行是 v2 驗證輪的證據，不可省。

---

## 誰可以寫什麼

| Skill | 可寫 | 不可寫 |
|---|---|---|
| shan-grill | `grill.md` | 其餘 |
| shan-to-spec | `spec-draft/` | 其餘（讀 `grill.md`、`findings.md`） |
| shan-spec-qa | `qa-report.md`、`spec-draft/`（修訂）、`issues/`、`findings.md` | `session-map.md`、`review-*` |
| shan-plan | `session-map.md` | 其餘（讀 `qa-report.md`、`findings.md`、`issues/`） |
| shan-implement | `findings.md`、`issues/`、`session-map.md` 的修訂記錄、`review-S<X>.md` | `grill.md`、`spec-draft/` |
| shan-code-review（fork 內） | **無**——只回報 | 全部 |
| shan-code-review 的呼叫端 | `review-S<X>.md`、`findings.md`、`issues/`、`session-map.md` 的修訂記錄 | `grill.md`、`spec-draft/` |

正式 spec 目錄不在此表內：**沒有任何 skill 可以寫**。由 harness 層的 hook 強制（見 `.shan/guard.yaml`）。
