# Spec 格式契約（預設）

專案還沒有既成 spec 慣例時用這份。`shan-setup` 會把它複製進專案（預設 `docs/specs/SPEC-FORMAT.md`），之後就是**專案的資產**——要改直接改專案裡那份，不要改 skill 裡的樣板。

## 為什麼是三份

三份文件的存活週期不同，混在一起長期會爛：

| 檔案 | 性質 | 讀取時機 |
|---|---|---|
| `requirements.md` | **資產**，功能上線後仍有效 | 寫測試、review、日後回歸 |
| `design.md` | **資產**，跨功能被引用 | 實作時、下個功能碰到同區域時 |
| `tasks.md` | **耗材**，全打勾後只剩歷史 | 切 session、實作打勾 |

小功能可以只寫 `requirements.md` + `tasks.md`，跳過 `design.md`——但別把設計決策塞進 requirements。

---

## 標題契約

標題**必須逐字相符**（可在後面加冒號 + 中文副標題）。QA 與消費端 skill 靠它定位。

### `requirements.md`

```markdown
# Requirements Document: <中文副標題>

## Introduction
<一到兩段：這個功能解決什麼問題、對誰>

## Glossary
<本 spec 引入的領域詞彙；一詞一行，附「不要說成 X」的反向詞條>

## Requirements

### Requirement 1 — <標題>

**User Story:** 身為 <角色>，我想要 <功能>，以便 <效益>

#### Acceptance Criteria

1. WHEN <觸發條件> THEN <系統> SHALL <可觀察行為>
2. IF <前置狀態> THEN <系統> SHALL <可觀察行為>
3. WHERE <適用範圍> THE <系統> SHALL <可觀察行為>
```

驗收條件用 **EARS** 句式（WHEN / IF / WHERE / WHILE + SHALL），一條一個可觀察行為。編號 `<需求編號>.<條件編號>` 是後續一切回指的錨點：測試名稱、commit footer、審查對照。

**不要寫**：檔案路徑、class 名、程式碼片段。那些屬於 `design.md`，而且會過期。

### `design.md`

```markdown
# Design Document: <中文副標題>

## Overview
## Architecture
## Components and Interfaces
## Data Models
## Resolved Decisions
## Error Handling
## Testing Strategy
```

- **Resolved Decisions** 是本專案的 ADR 等價物。一條一個決策，編號 `D1` / `D2`，寫下**選了什麼、為什麼、放棄了什麼**。只記三者皆成立的決策：難以逆轉、沒有脈絡會讓人困惑、真的有取捨。
- `Overview` / `Architecture` / `Components and Interfaces` / `Data Models` 必要；其餘視功能取捨。

### `tasks.md`

```markdown
# Implementation Plan: <中文副標題>

## Overview
<這份計畫共幾個任務、採哪種切法（horizontal / vertical）>

## Tasks

- [ ] 1. <任務標題>
  - <子項：具體要做的事>
  - <子項>
  - _Requirements: 1.1, 1.3_

- [ ] 2. <任務標題>
  - _Requirements: 2.1_

## Task Dependency Graph
<哪些任務阻塞哪些；無阻塞者標明可立即開始>

## Notes
```

- 每個任務結尾**必須**有 `_Requirements: X.Y_` 回指——沒有回指的任務，代表它在做沒人要求的事。
- `## Task Dependency Graph` 是必要章節，別漏。
- 一個任務 = 一次聚焦改動 = 一個 commit。

---

## 三份之間的一致性

這三條是 `shan-spec-qa` 的機械檢查項：

1. `tasks.md` 每個 `_Requirements:` 引用的編號，在 `requirements.md` 裡真的存在
2. `requirements.md` 每個驗收條件，至少被一個任務涵蓋（沒有孤兒需求）
3. `design.md` 提到的元件，在 `tasks.md` 裡有對應任務（沒有畫了不做的設計）
