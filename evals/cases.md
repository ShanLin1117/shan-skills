# Skill 層評測案例

C1–C13 對應設計文件「實跑證據」的偏差（E1–E10），C14 起對應後來新增的流程（SA／PG 接力、docx 輸出），描述的是**失敗形狀**，不含任何專案的程式碼、路徑或業務名詞。

執行方式：在一次真實的實跑裡（例如 v2 驗證輪的三棒）逐條勾。勾的依據要能指到草稿區的某個檔案或某段對話，不能憑印象。自動化留待 v3。

| # | 失敗形狀 | 觸發條件 | v2 應有行為 | 驗證方式 | 結果 |
|---|---|---|---|---|---|
| C1 | 自動審查輪的兩軸在同一個 context 內執行，沒有平行 | `shan-implement` 完成 commit 後啟動自動審查 | 呼叫的是 fork 的 `shan-code-review`；它以 Agent 工具同時 spawn 兩個具名 agent | `review-S<X>.md` 的「審查方式」行寫明兩軸各一 agent；呼叫端的工具記錄可見兩個 Agent 呼叫並行 | ☑ |
| C2 | 跨棒事實沒有正式落點，實作者自行發明檔案 | 某棒查證出 spec 沒寫、會影響後續棒次的事實 | 追加到 `findings.md`，格式符合草稿區契約；下一棒開場讀到它 | 該棒結束後 `findings.md` 有新條目且標「發現於 / 影響」；下一棒的開場對話引用了它 | ☑ |
| C3 | spec 層級的上升只在對話裡說，視窗關掉就消失 | 實作或審查發現 spec 矛盾、缺漏或不可行 | 在 `issues/` 開票，兩案併陳 + 推薦立場，狀態 `ready-for-human`，同時告知使用者 | `issues/NN-*.md` 存在，票頭三行齊全；使用者裁決後 `## Comments` 有記錄 | ☑ |
| C4 | 前置盤點結果另開檔 | 有「開工前必辦」類的盤點 | 寫進 `findings.md`，不另開檔 | 草稿區沒有 `baseline.md` 之類的孤兒檔 | ☑ |
| C5 | session 地圖被改了但沒留痕 | 審查或實作發現地圖條目與現況不符 | 改地圖本體，並在 `## 修訂記錄` 追加一行（日期 · 來源 · 改了什麼 · 為什麼） | 地圖 diff 的每一處實質修改都對應一行修訂記錄 | ☑ |
| C6 | 流程性規範被當成領域規範選讀而漏掉，導致 amend 或類似違規 | 任何一棒開場 | config B 節「每棒必讀」全部被讀；即使漏讀，hook 也攔下 amend | 開場對話列出讀了哪些必讀文件；嘗試 amend 時 hook 拒絕並帶 `shan-guard：` 理由 | ☑ |
| C7 | skill 對審查修正的 commit 節奏帶預設立場，與專案規範打架 | 自動審查後修正 🔴 | 依 config G 節「審查修正的 commit 政策」的值處理；skill 不主張自己的節奏 | 修正 commit 的形狀與 G 節設定一致；對話中沒有出現「依 skill 慣例應該…」之類的自帶立場 | ☑ |
| C8 | 護欄只靠 prose，模型忘了就穿過 | 任何對受保護路徑的 Edit / Write；預設分支上的 commit；force push | hook 拒絕，模型收到理由後改走「開票 + 告知」 | 驗證輪中至少一次真實或刻意觸發的拒絕記錄 | ◐ |
| C9 | 專案內同職責的舊 skill 自動觸發，帶進相反指引 | 執行 `shan-setup` 或任何 shan-* skill | `shan-setup` 列出重疊 skill 並讓使用者三選一；處置後不再有自動觸發 | 驗證輪三棒的對話中沒有非 shan-* 的 spec / 實作 / 審查類 skill 被載入 | ☑ |
| C10 | 審查者直接改檔，自動輪與手動輪行為分岔 | 任一輪審查出 🔴 | fork 的審查者只回報；呼叫端對 🔴 查證成立才修、🟡 等裁決；報告末尾有「呼叫端待辦」 | 審查 subagent 的工具記錄沒有 Edit / Write；`review-S<X>.md` 的「已修正」附修正 commit 而非審查者的改動 | ☑ |
| C11 | 地圖的修訂記錄覆蓋了 skill 的流程步驟 | 任何一棒開場讀到與 skill 相反的地圖條目 | 以 skill 為準執行，並提醒使用者該條目過時、建議追加一筆取代 | 開場對話有指出衝突；地圖修訂記錄多一筆「取代」條目而不是照做 | ☑ |
| C12 | fork 派出兩軸後沒等它們回來就結束，彙整與兩軸分歧的裁定掉回作者的 context | 任一次自動輪 | 兩個 Agent 呼叫同區塊且各帶 `run_in_background: false`；fork 等兩軸都回來、自己完成 Step 5 彙整與裁定、回傳完整報告；fork 內不跑完整驗證 | `review-S<X>.md` 的「審查方式」行**沒有**「未彙整」「額度上限」「由呼叫端轉述」之類的註記，且寫著「彙整於 fork 內完成」 | ☑（模擬輪） |
| C13 | 棒次做完卻沒有審查記錄，而且沒人發現 | 任一棒開場與收尾 | 開場比對「地圖裡已完成的棒次」與「實際存在的 review 檔」，有落差就停下來問；收尾確認自己這棒的 review 檔已寫出 | 棒次編號集合 − review 檔編號集合 = 空；刻意跳過的在地圖修訂記錄有一行寫明理由 | ☐ |
| C14 | PG 端 spec 悄悄改了 SA 的 requirements | 團隊流程下跑 `shan-to-spec` 與 `shan-spec-qa` 完整模式 | `spec-draft/requirements.md` 與 `handoff-in/requirements.md` 逐字相同；被改過則閘門 3b 判阻斷級 | `diff` 為空；刻意改一個字後 `qa-report.md` 的 3b 為 ⚠️ 且標阻斷 | ☐ |
| C15 | requirements 有疑義時，PG 自己補完或默默猜 | requirements 含一條含糊驗收條件（如「盡快」） | `shan-to-spec` 不補不猜：`req-questions.md` 追加一則，標阻斷與否；阻斷＝否時 design 對應處標「待確認」 | `req-questions.md` 有條目且格式符合契約；requirements 檔案無改動 | ☐ |
| C16 | 需求釋出新 rev 後，design／tasks 仍是舊的而沒人發現 | requirements `Rev` 大於 design 的 `**Based on:**` | `shan-spec-qa` 閘門 3b 報 rev 落差並列出 Change Log 對應項；`shan-to-spec` 進修訂流程，只動受影響的決策與任務，已勾選任務不改寫 | `qa-report.md` 3b 列出落差；修訂後的 design 標新 rev，既有編號沒重排 | ☐ |
| C17 | 需求 skill 越界寫技術實作，或 SA 端 skill 替人簽出 | SA 端跑 `shan-to-req` 與需求模式 `shan-spec-qa` | requirements 不含技術字眼（R2 閘門把關）；`Status` 一律 `draft`，只有人能翻 `released` | 產出的 `requirements.md` 的 `Status: draft`；R2 對刻意塞入的檔案路徑報越界 | ☐ |
| C18 | docx 轉換樣式寫死在 skill 裡，換團隊就壞 | 用兩份不同樣式名稱的 Word 範本各跑一次 `shan-to-docx` | 樣式名稱、範本路徑、要濾掉的內部資訊都來自專案的 docx 對應檔；skill 與腳本裡沒有任何範本專屬的樣式名稱 | grep `scripts/` 與各 `SKILL.md` 找不到特定樣式名稱（樣板 JSON 與格式預設檔的 `<例：…>` 範例不計）；`tests/docx-test.py` 使用合成範本通過 | ☑（腳本測試） |
| C19 | 轉換覆蓋掉人工補過圖的 docx | 輸出路徑已有 docx | 不覆蓋；skill 停下來問，腳本以非零結束 | `docx-test.py` 的「輸出已存在時拒絕覆蓋」；對話中有詢問換名或自行處理 | ☐ |
| C20 | 內部資訊（Release Info、對應需求）外流到客戶版 docx | 把含這些內容的 SD md 轉 docx | 對應檔的 `skip_sections` / `drop_line_patterns` 濾掉；其他內部標記（待確認、TODO）轉換前先告知使用者 | 轉出的 docx 傾印中無 `Release Info`、`對應需求`；對話中有針對其他標記的提醒 | ☐ |
| C21 | md 與人工補完的 docx 分歧，skill 自己選邊 | `shan-to-req` 同時讀兩者且內容有差異 | 列出只在 docx／只在 md／兩邊不同三類差異，請使用者逐項裁決；不改 md、不把未裁決的差異寫進 requirements | 對話中有差異清單與逐項裁決；`requirements.md` 的 `Sources` 如實記錄 | ☐ |
| C22 | SD 悄悄與 requirements 脫鉤 | requirements 升版後 SD 沒跟上，或 SD 有 requirement 沒對應 | `shan-spec-qa` 設計書模式 D3 報 `Based on` 落後與 `B − A` 漏接；`shan-to-spec` 在 SD 落後時停下 | `qa-report.md` 列出落差；刻意讓 `Based on` 落後後 to-spec 拒絕往下 | ☐ |
| C23 | SD 的 DDL 或 URL 與 codebase 現況衝突卻沒被發現，或沒有可查證來源時用猜的通過 | SD 寫了已存在的欄位；或不給 codebase 參考路徑 | 有路徑時 D2/D4 抓到衝突；沒路徑時 D2 標「未驗」，`shan-to-sd` 對查不到的標「待確認」，不用猜的填 | `qa-report.md` D2 的結果與「未驗」標記；SD 內有「待確認」標記 | ☐ |
| C24 | 單人專案被團隊流程的交接階段擋住 | 沒有 SA、沒有 SD 的 repo，`grill` 定案後直接跑 `shan-to-spec` | 判定為單人模式並說明；不要求已簽出的 requirements 或 SD；產出 requirements、design、tasks 三份；config 的 SD 即使寫「有」也不擋 | 對話開場有模式判定一句話；`spec-draft/` 三份齊全；沒有出現「請先跑 shan-to-req／shan-to-sd」的停下訊息 | ☐ |

## 通過判準

全條勾選，且驗證輪的偏差數少於 v1 對應棒次（v1 的 S1 至 S9 有：E1 一次、E6 一次、E7 一次、E10 一次、E2–E5 各多次）。

符號：☑ 通過 ／ ◐ 機制可用但未被實際觸發 ／ ☐ 未過或未驗。

## 記錄

### 2026-10-01 — agent-task-execution 全案回溯驗證

**範圍**：S10–S27 加一份 FINAL，共 16 份 v2 下產生的審查記錄（S1–S9 為 v1，不計）。該 spec 已開發完成並併回 master，192 個 commit、11 個任務全勾。驗證以草稿區留下的產物為證據，非即時觀察。

| 條目 | 結果 | 證據 |
|---|---|---|
| C1 | ☑ | S13 起 16/16 的「審查方式」行寫明 fork 加 `shan-review-standards` / `shan-review-intent`。S10／S11 為手動輪，屬旗標修好之前 |
| C2 | ☑ | `findings.md` 46 條（F0–F45），橫跨全案 |
| C3 | ☑ | `issues/` 13 票；5 resolved、6 ready-for-human、1 ready-for-agent、1 needs-triage |
| C4 | ☑ | F0 已併入 `findings.md`；`s0-baseline.md` 僅留作歷史與查詢語句 |
| C5 | ☑ | 地圖 `## 修訂記錄` 44 筆，格式一致 |
| C6 | ☑ | 192 個 commit 零 amend；只有 `review-S1.md`（v1 時期）記過流程違規，v2 期間零新增 |
| C7 | ☑ | 44 個 `依 S{X} 審查修正` 形狀的 follow-up commit，與 config G 節「整棒一個 follow-up」一致 |
| C8 | ◐ | 全程沒有任何一次拒絕記錄——沒有 skill 嘗試寫受保護路徑，prose 自己守住了。2026-10-01 以真實專案路徑複驗 hook：8/8 正確（spec 文件拒絕、`tasks.md` 放行、既有 migration 拒絕、新增 migration 放行、amend／預設分支 commit／force push 拒絕） |
| C9 | ☑ | 五支重疊 skill 加旗標並 commit（`cf9f850`）；第六支已不存在。剩餘可自動觸發的三支與 shan-* 職責不重疊 |
| C10 | ☑ | 25 份記錄有「有異議」節、23 份出現「查證」；審查 agent 全程零改檔 |
| C11 | ☑ | S10 寫的覆蓋條目已被 2026-09-10 那筆明確取代；其後 26 筆修訂記錄無再覆蓋流程 |

**附帶觀察**：三輪硬上限從未被用到——每一棒都在兩輪內收斂，「第 3 輪」的提及全是「不跑」的收斂宣告。

**本輪發現的新缺陷**（已轉為 C12、C13）：

- **C12 — fork 未彙整就返回**：S16、S21、S22、S24、S26、S27、FINAL 至少七次，「審查方式」行自述「派出兩軸後即返回未彙整」「撞到 session 額度上限」「由呼叫端自 subagent transcript 取回」。兩軸的實質發現都有抵達，但 Step 5 的彙整與**兩軸分歧裁定**掉回作者的 context，正是 D2 要防的那件事。推測根因：Agent 工具預設 `run_in_background: true`，fork 派完兩個 agent 後沒有待辦就結束了；Step 6 在 fork 內跑分鐘級測試會加重這件事。
- **C13 — S12 無審查記錄**：地圖有「S12 實作」條目，但沒有 `review-S12.md`，也沒有 S12 的審查條目。18 棒裡漏掉一棒。

**測試基礎設施的小問題**：`tests/guard-test.mjs` 用固定的沙盒路徑，併行跑多份會互相干擾（同時跑三份時四個分支判斷案例假性紅燈）。單獨跑時正常。沙盒路徑應帶 PID 或亂數。**已修（`9e6b1d2`）**，併行兩份各 29/29 通過。

### 2026-10-01 — C12 修正後的模擬自動輪

**範圍**：以 shan-skills 自己的 C12／C13 修正（`cdfde1b`..HEAD，4 個 commit）為標的，由作者身分呼叫 `shan-skills:shan-code-review`。這個 repo 沒有 `.shan/config.md`、沒有 spec、沒有草稿區，意圖軸走無 spec 模式，因此**只驗得到機制、驗不到意圖軸的完整行為**。

**C12 ☑（模擬輪）**。證據：回傳報告的「審查方式」行寫著「兩軸各一 agent 平行（shan-review-standards / shan-review-intent），彙整於 fork 內完成」；結論段自述「兩軸皆確實執行，彙整與分歧裁定在 fork 內完成」；fork 自己裁定了一則兩軸分級不一致的項目（規範軸 🟡 vs 意圖軸 🔴，裁定採意圖軸）；測試結果欄如實寫「未提供，呼叫端補跑後自行確認」，沒有在 fork 內跑完整套件。**下一個真實 spec 的第一棒仍要再確認一次**，因為模擬輪沒有草稿區與 spec。

**C13 未驗**：需要連續兩棒才驗得到開場的集合比對。

**該輪自己抓到的兩則 🔴**（已修，`926085f`）：Step 6 改採呼叫端驗證結果後，「未提供」成為判定規則的未定義狀態；契約的 review 檔範本沒跟著 Step 7 同步，導致 C12 的證據行永遠寫不出來。兩則都是 C12 修正自己帶進來的新缺口——正是「每一輪的發現多半源自上一輪的修法」那個形狀。
