# `.shan/config.md` 樣板

寫進專案的 `.shan/config.md`。章節標題**固定不變**——其餘 shan-* skill 靠標題定位。
每節填不上就寫 `不適用`，不要留空。

<template>

# shan-skills 專案設定

> 本檔是給 AI agent 讀的專案事實。**只記查不到、或查起來貴的東西**；會過期的當下狀態一律寫成查詢方式。

## A. 路徑與 spec 格式

- **草稿區**：`<例：.scratch/>`（工作中的中間產物；已在 .gitignore 內）
- **Spec 目錄**：`<例：docs/specs/<feature-slug>/>`
- **Spec 檔案**：`<例：requirements.md / design.md / tasks.md>`
- **格式契約**：`<指向專案內的契約檔，例：docs/specs/SPEC-FORMAT.md>`
- **寫入方式**：skill 一律先寫草稿到草稿區，經使用者核可後才進 Spec 目錄

## B. 領域文件讀取順序

探索專案時依序讀（愈靠近要動的東西愈後讀）：

1. `<例：CLAUDE.md — 全域護欄>`
2. `<例：.kiro/steering/ — 跨 spec 規範，依主題選讀>`
3. `<例：<spec 目錄>/<feature>/ — 該功能的權威定義>`

缺漏時**靜默略過**，不要提示缺少、也不要主動建議建立。

**詞彙來源**：`<例：per-spec 的 ## Glossary；跨 spec 共用詞看 CLAUDE.md 模組架構段>`

## C. 事實查核對照表

agent 自己查，不要拿去問使用者。

| 要確認什麼 | 去哪查 |
|---|---|
| class / method 是否存在 | `<例：Grep src/main/java/>` |
| DB 欄位與表格名稱 | `<例：src/main/resources/db/migration/V*.sql>` |
| 設定鍵 | `<例：src/main/resources/application.yaml>` |
| 依賴與版本 | `<例：pom.xml>` |
| `<其他>` | `<路徑>` |

## D. 技術棧與指令

- **語言 / 框架**：`<例：Java 21 / Spring Boot 3.5 / Maven>`
- **建置**：`<例：./mvnw clean package -DskipTests>`
- **快速測試**：`<例：./mvnw test>`
- **完整驗證**：`<例：./mvnw verify>`
- **啟動**：`<例：./mvnw spring-boot:run -Dspring-boot.run.profiles=dev>`
- **外部前置**：`<例：Docker Desktop（整合測試用）、PostgreSQL 18>`

## E. 測試慣例

- **測試基底 / 共用 fixture**：`<例：BaseIntegrationTest（共用容器）、BasePropertyTest（獨立容器）>`
- **選擇原則**：`<例：能用切片測試就用；碰 DB 一律繼承 BaseIntegrationTest；不用 @DataJpaTest>`
- **測試命名**：`<例：@DisplayName("Req 2.3: WHEN ... THEN ...")，前綴回指驗收條件>`
- **外部服務不可用時**：`<例：Docker 失連即停下告知使用者，禁止跳過整合測試——本專案無 H2 fallback>`

## F. 任務切法

- **slicing**：`horizontal` | `vertical`
- **共同要求**：每個任務結束時綠燈可 commit；spec 的依賴圖要標明阻塞邊

## G. Commit 慣例

- **格式**：`<例：Conventional Commits，type/scope 英文、描述繁體中文>`
- **Footer**：`<例：Refs: <spec-folder>/REQ-N；無對應 spec 時省略>`
- **禁忌**：`<例：不得出現 AI / Claude / GPT / LLM / 🤖 等署名；有 commit-msg hook 把關，不得用 --no-verify 繞過>`
- **分支**：`<例：feat/<spec-folder-name>；bug 用 fix/、雜項用 chore/>`

## H. 專案硬護欄

skill 執行時最常踩到的幾條。完整清單見 `<指向 CLAUDE.md 或等價文件>`。

- `<例：MUST NOT 直接修改 <spec 目錄> 下的文件——需求或設計要改，暫停並告知使用者>`
- `<例：MUST 透過 RoutingChatModelClient 呼叫 LLM，不注入具體 provider>`
- `<例：MUST 在新增 @RequestParam / @PathVariable 時明確寫出 name=>`
- `<例：決策點一律兩案併陳 + 推薦立場，不得默默選最小 patch>`

## I. 對外動作

- **Remote**：`<例：客戶內網 GitLab／公司 GitLab／GitHub private／無 remote>`
- **預設姿態**：`<例：一切產出留在本機；push / 開 issue / 發 PR 一律需使用者明確同意>`

</template>

---

## 填寫檢查

- [ ] A–I 每節有內容或明確寫 `不適用`
- [ ] 沒有任何一行是「一個指令就查得到的當下狀態」（版號、檔案數、目錄清單）
- [ ] 格式契約指向**專案內**的檔案，不是把契約內容複製進來
- [ ] 護欄那節只放最常踩的幾條，不是把 CLAUDE.md 整份搬過來
