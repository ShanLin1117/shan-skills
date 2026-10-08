#!/usr/bin/env python3
"""把 markdown 轉成 docx，以專案提供的 Word 範本為底，只替換內文。

用法：python -X utf8 md_to_docx.py --mapping <對應檔.json> --md <來源.md> --out <輸出.docx>

本腳本不含任何專案知識：樣式名稱、範本路徑、要略過的章節（skip_sections）、
要濾掉的內部追溯行（drop_line_patterns，regex）都來自對應檔。
支援的 markdown 子集：# 到 ###### 標題、純文字行、- / * / 1. 清單、``` 程式碼區塊、
| 表格 |、![說明](路徑) 圖片、行內 **粗體** 與 `程式碼`。每個非空白行就是一個段落。
"""
import argparse
import json
import os
import re
import sys

try:
    import docx
    from docx.oxml.ns import qn
    from docx.shared import Cm
except ImportError:
    sys.exit("缺少 python-docx。請在專案的虛擬環境執行：pip install python-docx")

REQUIRED_STYLES = ("h1", "h2", "h3", "h4", "body")
DEFAULTS = {"bullet": "List Paragraph", "code": "Normal", "table": "Table Grid"}


def load_mapping(path):
    with open(path, encoding="utf-8") as f:
        m = json.load(f)
    base = os.path.dirname(os.path.abspath(path))
    tpl = m.get("template")
    if not tpl:
        sys.exit("對應檔缺少 template（Word 範本路徑）")
    m["_template_path"] = tpl if os.path.isabs(tpl) else os.path.normpath(os.path.join(base, tpl))
    styles = dict(DEFAULTS)
    styles.update(m.get("styles", {}))
    missing = [k for k in REQUIRED_STYLES if k not in styles]
    if missing:
        sys.exit("對應檔 styles 缺少：" + ", ".join(missing))
    m["styles"] = styles
    m.setdefault("skip_sections", [])
    m["_drop"] = [re.compile(x) for x in m.get("drop_line_patterns", [])]
    m.setdefault("code_font", "Consolas")
    m.setdefault("image_placeholder", "【請貼上圖片：{alt}】")
    m.setdefault("image_width_cm", 15)
    return m


def check_styles(document, styles):
    have = {s.name for s in document.styles}
    bad = sorted({v for v in styles.values() if v not in have})
    if bad:
        sys.exit("範本裡找不到這些樣式（請檢查對應檔）：" + "、".join(bad)
                 + "\n範本現有樣式：" + "、".join(sorted(have)))


def clear_body(document):
    body = document.element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


INLINE = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`)")


def set_font(run, font):
    run.font.name = font
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font)


def add_runs(par, text, code_font):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            par.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            set_font(par.add_run(part[1:-1]), code_font)
        else:
            par.add_run(part)


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_sep(line):
    return bool(re.fullmatch(r"\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*", line))


def convert(md_text, document, m):
    st = m["styles"]
    lines = md_text.splitlines()
    i, n, skip_level = 0, len(lines), None
    while i < n:
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", line)
        if h:
            level, title = len(h.group(1)), h.group(2).strip()
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and title in m["skip_sections"]:
                skip_level = level
            if skip_level is None:
                document.add_paragraph(title, style=st["h%d" % min(level, 4)])
            i += 1
            continue
        if skip_level is not None or any(p.search(line) for p in m["_drop"]):
            i += 1
            continue
        if line.lstrip().startswith("```"):
            i += 1
            while i < n and not lines[i].lstrip().startswith("```"):
                p = document.add_paragraph(style=st["code"])
                set_font(p.add_run(lines[i]), m["code_font"])
                i += 1
            i += 1
            continue
        if line.lstrip().startswith("|") and i + 1 < n and is_sep(lines[i + 1]):
            rows = [split_row(line)]
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            cols = max(len(r) for r in rows)
            t = document.add_table(rows=len(rows), cols=cols)
            t.style = st["table"]
            for ri, row in enumerate(rows):
                for ci in range(cols):
                    par = t.cell(ri, ci).paragraphs[0]
                    add_runs(par, row[ci] if ci < len(row) else "", m["code_font"])
                    if ri == 0:
                        for r in par.runs:
                            r.bold = True
            continue
        img = re.match(r"^!\[([^\]]*)\]\(([^)]*)\)\s*$", line.strip())
        if img:
            alt, src = img.group(1), img.group(2).strip()
            if src and os.path.isfile(src):
                document.add_paragraph().add_run().add_picture(src, width=Cm(m["image_width_cm"]))
            else:
                document.add_paragraph(m["image_placeholder"].format(alt=alt or "圖片"), style=st["body"])
            i += 1
            continue
        b = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if b:
            depth = len(b.group(1).replace("\t", "  ")) // 2
            marker = "•" if b.group(2) in ("-", "*") else b.group(2)
            p = document.add_paragraph(style=st["bullet"])
            p.paragraph_format.left_indent = Cm(0.74 * (depth + 1))
            add_runs(p, "%s %s" % (marker, b.group(3)), m["code_font"])
            i += 1
            continue
        add_runs(document.add_paragraph(style=st["body"]), line.strip(), m["code_font"])
        i += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--md", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    m = load_mapping(a.mapping)
    if not os.path.isfile(m["_template_path"]):
        sys.exit("找不到 Word 範本：" + m["_template_path"])
    if os.path.abspath(a.out) == os.path.abspath(m["_template_path"]):
        sys.exit("輸出不可覆蓋範本")
    if os.path.exists(a.out):
        sys.exit("輸出檔已存在，不覆蓋（人工可能已編輯過）：" + a.out)
    document = docx.Document(m["_template_path"])
    check_styles(document, m["styles"])
    clear_body(document)
    with open(a.md, encoding="utf-8") as f:
        convert(f.read(), document, m)
    document.save(a.out)
    print("已產出：" + a.out)


if __name__ == "__main__":
    main()
