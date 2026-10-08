#!/usr/bin/env python3
"""把 docx 依文件順序傾印成文字，供 skill 閱讀與比對。

用法：python -X utf8 docx_dump.py <檔案.docx>

每個段落一行，格式 [樣式名] 文字；表格以 <TABLE> 包起來、儲存格用 | 分隔；
含圖片的段落標 [IMAGE]。圖片內容本身不解析——需要看圖請另行開檔。
"""
import sys

try:
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph
except ImportError:
    sys.exit("缺少 python-docx。請在專案的虛擬環境執行：pip install python-docx")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    import os
    if not os.path.isfile(sys.argv[1]):
        sys.exit("錯誤：找不到檔案：" + sys.argv[1])
    try:
        d = docx.Document(sys.argv[1])
    except Exception as e:
        sys.exit("錯誤：無法讀取 docx（檔案損壞或不是 docx？）：%s" % e)
    out = []
    for el in d.element.body.iterchildren():
        if el.tag.endswith("}p"):
            p = Paragraph(el, d)
            has_img = bool(el.xpath(".//w:drawing")) or bool(el.xpath(".//w:pict"))
            text = p.text.strip()
            if text or has_img:
                out.append("[%s]%s %s" % (p.style.name, " [IMAGE]" if has_img else "", text))
        elif el.tag.endswith("}tbl"):
            t = Table(el, d)
            out.append("<TABLE>")
            for r in t.rows:
                seen, cells = [], []
                for c in r.cells:
                    if c._tc in seen:
                        continue
                    seen.append(c._tc)
                    cells.append(c.text.strip().replace("\n", " / "))
                out.append(" | ".join(cells))
            out.append("</TABLE>")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
