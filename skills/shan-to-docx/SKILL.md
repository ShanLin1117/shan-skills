---
name: shan-to-docx
description: 把需求分析書或系統設計書的 md 草稿，以專案的 Word 範本為底轉成 docx（套用範本樣式、保留頁首頁尾，只換內文）。AI 只負責產出基本 docx；畫面截圖與其他複雜內容由人工補。當使用者說「轉成 Word」「產 docx」「交付客戶的文件」「shan-to-docx」，或 shan-to-sa / shan-to-sd 產完 md 要交付時使用。需要先有 md 草稿——寫 md 用 shan-to-sa 或 shan-to-sd。
disable-model-invocation: true
---

# Shan To Docx — md → Word

把 `doc-draft/` 裡的 md 轉成 docx，交給 SA 人工補完後交付客戶。這支 skill 只做**確定性的轉換**——樣式、表格、程式碼區塊、清單、圖片預留位置；複雜內容（畫面截圖、版面微調）本來就由人工處理。

全程繁體中文（台灣用語）輸出。

---

## Step 1：載入

1. **`.shan/config.md`** —— 缺就告訴使用者跑 `/shan-skills:shan-setup`
2. **對應檔** —— config **A 節「交接物」**裡，這種文件（需求分析書或系統設計書）的「docx 對應檔」。寫「不適用」或沒有，就告訴使用者這個專案沒設定 docx 輸出，建議跑 `shan-setup` 的「docx 對應」流程
3. **來源 md** —— 使用者指定，或 `doc-draft/` 下依命名規則找到的 `<名稱>_SA.md` / `<名稱>_SD.md`。有多個候選就問
4. **Python 與 python-docx** —— 腳本需要 `python-docx`。先試 `python -X utf8 ${CLAUDE_SKILL_DIR}/../../scripts/docx/docx_dump.py` 看會不會報「缺少 python-docx」。缺的話**告訴使用者在專案虛擬環境裝**（`pip install python-docx`），**不要自己安裝**

---

## Step 2：轉換前確認

- 輸出檔 = `doc-draft/` 下與 md 同名的 `.docx`。**已存在就不覆蓋**（人工可能已補過圖）。停下來問：換名（如加 `-v2`）、還是使用者自己處理舊檔。腳本本身也會拒絕覆蓋
- 讀一次來源 md，確認沒有不該外流的內部資訊會進 docx：`Release Info`、`對應需求` 這類內部追溯內容應已被對應檔的 `skip_sections` / `drop_line_patterns` 濾掉。若來源有**別的**內部標記（如「待確認」「TODO」），**在轉換前告訴使用者**，不要靜默送進客戶版

---

## Step 3：轉換

```bash
python -X utf8 ${CLAUDE_SKILL_DIR}/../../scripts/docx/md_to_docx.py \
  --mapping <對應檔.json> --md <來源.md> --out <輸出.docx>
```

- 樣式找不到會報錯並列出範本現有樣式——代表對應檔與範本不一致，回報使用者，**不要自己改對應檔湊合**
- 轉完用 `docx_dump.py <輸出.docx>` 傾印，與 md 對照：標題層級、表格列數、程式碼區塊、`待補` 圖片的預留文字是否都在

---

## Step 4：交付

告訴使用者：

1. 輸出檔路徑
2. **需要人工處理的清單**，逐項列出（這是這支 skill 最重要的輸出）：
   - 每個 `待補` 圖片的位置（轉出後是「【請貼上圖片：…】」預留文字）
   - **頁首文字來自範本**，通常含專案名稱或年度採購案名，不會自動更新，請手動修改
   - 版面微調、封面／簽核欄等範本以外的內容
3. 補完後的 docx 由使用者自行保管；之後若 md 再改，**重新轉換會產生新檔**，人工補的內容不會自動帶過去，需要手動合併。這是刻意的：docx 是下游的輸出品，不是來源
4. 要產給 PG 的 requirements 時，`shan-to-req` 會同時讀這份 md 與補完的 docx

---

## 完成條件

- 輸出的 docx 存在，樣式與範本一致，頁首頁尾保留
- 沒有覆蓋任何既有檔案
- 內部資訊沒有進客戶版，或已事先告知使用者
- 人工處理清單已列給使用者

---

## 邊界

- **MUST NOT 覆蓋既有 docx。**
- **MUST NOT 自行產生或插入圖片內容**；沒有圖就是預留文字。
- **MUST NOT 自行修改對應檔或 Word 範本。**
- **MUST NOT 自行安裝套件。**
- 這支 skill 不改 md；md 要改回 `shan-to-sa` / `shan-to-sd`。
