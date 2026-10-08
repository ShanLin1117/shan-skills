# 草稿區契約

所有 shan-* skill 之間跨 session 傳遞狀態的唯一通道。skill 只引用本契約，**不得**在自己的 SKILL.md 裡另行描述這些檔案的格式。

路徑：`<草稿區>/<feature-slug>/`。草稿區由 `.shan/config.md` A 節指定，**必須**已在 `.gitignore` 內；沒有 config 時預設 `.scratch/`。

---

## 檔案總表

| 檔案 | 產出者 | 讀取者 | 寫入模式 | 生命週期 |
|---|---|---|---|---|
| `grill.md` | shan-grill、shan-grill-sa | shan-to-spec、shan-to-req | 每輪追加 | 審訊定案後凍結 |
| `spec-draft/` | shan-to-req（僅 `requirements.md`）、shan-to-spec（`requirements.md` 副本、`design.md`、`tasks.md`） | shan-spec-qa、使用者 | 覆寫 | 搬進正式目錄後留作歷史 |
| `requirements-in/requirements.md` | **使用者**（PG 端，把 SA 交付的檔放進來） | shan-grill、shan-to-spec、shan-spec-qa | 整檔替換（人工） | 每次 SA 釋出新 rev 就替換 |
| `req-questions.md` | shan-to-spec、shan-spec-qa、shan-grill（PG 端提問）；shan-to-req（SA 端答覆） | 使用者、shan-grill-sa、shan-to-req | 只追加；`Status:` 可改 | 至所有問題 `answered` 或 `withdrawn` |
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

格式由 `shan-grill` 定義（`shan-grill-sa` 沿用同一格式，差別只在「依據事實」指向 SA 文件而非 codebase），摘要：`## 已敲定決策`（D1、D2…，每條含問題／決定／理由／依據事實）、`## 待決`、`## 明確排除`。決策編號一經寫定不得重排，`shan-to-spec` 的設計文件直接接續同一組編號。

## `spec-draft/`

份數與檔名由 config A 節指向的格式契約決定。SA 端 `shan-to-req` 只產 `requirements.md`；PG 端 `shan-to-spec` 產 `design.md`、`tasks.md`，並把 `requirements.md` **原樣複製**進來讓三份成套。每次執行覆寫自己負責的檔。使用者核可後**由使用者**搬進正式 spec 目錄，skill 不代做。

## `requirements.md` 的交接區塊

SA 與 PG 之間的契約是 `requirements.md`。不論專案的格式契約長怎樣，團隊流程下的 `requirements.md` **檔尾一律帶 `## Release Info`**（專案契約沒有這一節時照加，spec-qa 閘門 1 不視為違規）：

```markdown
## Release Info

- **Status**: draft | released
- **Rev**: 2
- **Released**: YYYY-MM-DD

### Change Log

- **rev 2** (YYYY-MM-DD)：新增 Req 2.4；修改 Req 1.2（<原因>）；移除 Req 3.1（<原因>）
- **rev 1** (YYYY-MM-DD)：初版
```

規則：

- **Status 由人翻**。`shan-to-req` 一律產出 `draft`；`shan-spec-qa`（需求模式）通過後，由 SA **手動**改成 `released` 並填 `Released` 日期。skill 不替人簽出
- **釋出後再改一個字，就是新 rev**：`Rev` +1、`Status` 回到 `draft`、`Change Log` 追加一則，再走一次 QA 與簽出
- **Change Log 以 Req / 驗收條件為粒度**（`Req 2.4`、`Req 1.2`），三種動詞固定：新增／修改／移除，每則附原因。它是 PG 修訂 design 與 tasks 的唯一依據
- **編號永不重用、永不重排**：被移除的需求保留標題，並標 `（已移除，rev N）`，驗收條件刪除。這個墓碑讓 `B − A` 涵蓋率比對與既有 commit 的 `Refs:` 回指不失效
- PG 端的 `design.md`（沒有 design 的小功能則 `tasks.md`）在 `## Overview` 第一行記 `**Based on:** requirements rev N`，供 spec-qa 比對

## `qa-report.md`

```markdown
## 第 N 輪 — YYYY-MM-DD — 模式：需求 | 完整

### 閘門結果
| 閘門 | 結果 | 數字 |
|---|---|---|
| 1 格式 | ✅ / ⚠️ | |
| 2 識別字 | ✅ / ⚠️ | 可疑 N 個 |
| 3 機械 | ✅ / ⚠️ | 需求 N、驗收 N、涵蓋率 N% |
| 3b 交接 | ✅ / ⚠️ / 不適用 | 完整模式才有：Status、rev 比對、requirements 是否被動過 |
| 4 語意 | 執行 / 略過 | 阻斷級 N、文字層 N |

### 實質發現
### 文字層發現
### 不同意審查之處
### 未解決的開放決策
```

閘門 4 每跑一輪追加一節。**問題從結構性轉為文字層就是可以停的訊號**，這個判斷要寫在該輪結尾。

## `req-questions.md`

PG 端發現 requirements 有疑義時的**回流通道**，對應 `findings.md` 之於實作。**PG 不得自己改 requirements、也不得默默猜**——疑義寫在這裡，由使用者把檔案帶給 SA（兩個 repo 之間靠人搬）。SA 端把它放進自己的草稿區同名位置，由 `shan-grill-sa` 當前沿處理、`shan-to-req` 寫答覆。

```markdown
# 需求疑義 — <feature-slug>

> 只追加。PG 端提問，SA 端答覆。檔案由人在兩個 repo 之間搬運。

## Q1 — <一句話標題>

Status: open | answered | withdrawn
針對: Req 2.3
提問於: design 階段，基於 requirements rev 2
阻斷: 是 | 否
日期: YYYY-MM-DD

### 疑義
<哪裡含糊、矛盾、無法觀察或遺漏，引用 requirements 原文>

### PG 的暫定理解
<阻斷=否時必填：在答覆前 design 採用的解讀，design 的對應處標「待確認」>

### SA 答覆
<SA 端填：結論，與對應的 requirements rev>
```

- **阻斷=是**：沒有答覆就無法設計，`shan-to-spec` 停下來
- **阻斷=否**：以暫定理解繼續；SA 答覆與暫定理解不同時，走 requirements 的新 rev，PG 端依 Change Log 修訂
- 判準同 `findings.md`：「不問的話，PG 會做錯什麼？」講不出來的不是疑義

## `session-map.md`

主體格式由 `shan-plan` 定義。必要章節 `## 修訂記錄` 放在檔尾：

```markdown
## 修訂記錄

- YYYY-MM-DD · review-S8 第 2 輪 · S26 條目「以 ArchUnit 類別依賴斷言守門」改為「方法層級且排除第二呼叫點」 · 原寫法會產生恆綠的假守門
```

規則：

- 任何 skill 發現地圖與現況不符，**改地圖本體，並在此追加一行**。錯的地圖留著比改掉更危險。
- **修訂記錄不得改寫 skill 的流程步驟。** 地圖只管範圍、護欄、檢查點、專案參數；流程以 skill 為準。實跑曾發生一棒把「審查改由使用者手動跑」寫進修訂記錄，之後五棒全部照做——讀到這種條目要追加一筆取代它，不是遵守它。
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

**審查方式**：fork 的 shan-code-review，第 N 輪，兩軸各一 agent 平行（shan-review-standards / shan-review-intent），彙整於 fork 內完成
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

**第 1 輪也要寫**。「審查方式」那一行是審查機制有沒有失效的證據，不可省——它**必須如實描述實際發生的事**：

- 有任何一軸未執行 → 改寫成「<某軸> 未執行：<原因>」，判定降為待確認
- 彙整不是在 fork 內完成（報告是空的或只有半邊，由呼叫端拼起來）→ 如實寫出來，**不要照抄範本那句**

這一行是日後檢查審查機制有沒有失效的唯一證據，寫得漂亮而不屬實，等於把缺陷藏起來。

**不變量：每一個已完成的棒次都要有一份 `review-S<X>.md`。**

```
地圖裡標為已完成的棒次  −  草稿區實際存在的 review 檔  =  空集合
```

`shan-implement` 在**開場**與**收尾**各驗一次這條（開場驗前面所有棒次、收尾驗自己這棒）。刻意不審的棒次，要在地圖的 `## 修訂記錄` 留一行寫明哪一棒、為什麼——**沒有記錄的缺口等於沒發生過**，下一棒會再攔一次。

這條存在的理由：漏審的那一棒自己不會知道（中途斷線、或自動審查失敗而沒人注意），只有下一棒的開場看得到全局。實跑曾漏掉一整棒，直到全案做完回頭盤點才發現。

---

## 誰可以寫什麼

| Skill | 可寫 | 不可寫 |
|---|---|---|
| shan-grill | `grill.md`、`req-questions.md`（只追加新疑義） | 其餘（讀 `requirements-in/`） |
| shan-grill-sa | `grill.md` | 其餘（讀 `req-questions.md`） |
| shan-to-req | `spec-draft/requirements.md`、`req-questions.md`（只填「SA 答覆」與 `Status`） | 其餘（讀 `grill.md`） |
| shan-to-spec | `spec-draft/`、`req-questions.md`（只追加新疑義） | 其餘（讀 `requirements-in/`、`grill.md`、`findings.md`）；**不得改動 `requirements.md` 內容** |
| shan-spec-qa | `qa-report.md`、`spec-draft/`（修訂 design / tasks；需求模式下修訂 requirements）、`issues/`、`findings.md`、`req-questions.md`（只追加新疑義） | `session-map.md`、`review-*`；完整模式下不得改 `requirements.md` |
| shan-plan | `session-map.md` | 其餘（讀 `qa-report.md`、`findings.md`、`issues/`） |
| shan-implement | `findings.md`、`issues/`、`session-map.md` 的修訂記錄、`review-S<X>.md` | `grill.md`、`spec-draft/` |
| shan-code-review（fork 內） | **無**——只回報 | 全部 |
| shan-code-review 的呼叫端 | `review-S<X>.md`、`findings.md`、`issues/`、`session-map.md` 的修訂記錄 | `grill.md`、`spec-draft/` |

正式 spec 目錄不在此表內：**沒有任何 skill 可以寫**。由 harness 層的 hook 強制（見 `.shan/guard.yaml`）。
