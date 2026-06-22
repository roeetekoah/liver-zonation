import markdown, pathlib
md = pathlib.Path("MANUSCRIPT.md").read_text(encoding="utf-8")
body = markdown.markdown(md, extensions=["tables","sane_lists","attr_list","md_in_html"])
css = """
@page { size: A4; margin: 20mm 22mm 18mm 22mm; }
* { box-sizing: border-box; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.6pt; line-height: 1.5;
       color: #1b1b1b; margin: 0; }
h1 { font-size: 22pt; line-height: 1.2; font-weight: 700; color: #14333a; margin: 0 0 4pt 0;
     letter-spacing: -0.2pt; }
/* the italic subtitle line right after the title */
body > p:first-of-type em { color: #5c6e73; font-size: 9.4pt; }
h2 { font-size: 14pt; font-weight: 700; color: #1B6E78; margin: 20pt 0 6pt 0;
     padding-bottom: 2pt; border-bottom: 0.6pt solid #d8d2c8; }
h3 { font-size: 11.6pt; font-weight: 700; color: #14333a; margin: 14pt 0 4pt 0; }
p { margin: 0 0 7pt 0; text-align: justify; }
strong { color: #14333a; }
em { color: #333; }
ul, ol { margin: 0 0 8pt 0; padding-left: 18pt; }
li { margin: 0 0 3pt 0; text-align: justify; }
code { font-family: Consolas, 'Courier New', monospace; font-size: 9pt; background: #f1efe9;
       padding: 0.5pt 3pt; border-radius: 2px; color: #8a3b12; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0 12pt 0; font-size: 9.3pt; }
th { background: #14333a; color: #fff; font-weight: 700; text-align: left; padding: 5pt 7pt;
     border: 0.5pt solid #14333a; }
td { padding: 4.5pt 7pt; border: 0.5pt solid #d8d2c8; vertical-align: top; }
tr:nth-child(even) td { background: #f7f5f1; }
hr { border: none; border-top: 0.6pt solid #d8d2c8; margin: 16pt 0; }
h2, h3 { page-break-after: avoid; }
table, tr { page-break-inside: avoid; }
"""
html = f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
pathlib.Path("manuscript.html").write_text(html, encoding="utf-8")
print("wrote manuscript.html")
