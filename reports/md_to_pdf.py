"""
Clean Markdown -> PDF for the supplementary reports.
Pipeline: python-markdown -> styled HTML (academic CSS) -> Chrome headless print-to-pdf.
Usage:  python reports/md_to_pdf.py reports/REPORT_relaxed.md
Output: same path with .pdf. Image src paths are rewritten to absolute file:/// so figures embed.
"""
import sys, os, re, subprocess, pathlib, urllib.parse

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CSS = """
@page { size: A4; margin: 20mm 18mm; }
html { -webkit-print-color-adjust: exact; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.7pt; line-height: 1.5;
       color: #1a1a1a; max-width: 100%; text-align: justify; }
h1 { font-size: 19pt; line-height: 1.25; margin: 0 0 2pt; color: #0f172a; text-align: left; }
h2 { font-size: 13.5pt; margin: 18pt 0 4pt; color: #0f172a; border-bottom: 1px solid #cbd5e1;
     padding-bottom: 2pt; text-align: left; }
h3 { font-size: 11.5pt; margin: 12pt 0 3pt; color: #1e293b; text-align: left; }
p { margin: 0 0 7pt; }
em { color: #334155; }
strong { color: #0f172a; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f1f5f9; padding: 0 3px; border-radius: 3px; }
pre { background: #f1f5f9; padding: 8px 10px; border-radius: 5px; font-size: 8.6pt; overflow-x: auto;
      white-space: pre-wrap; }
blockquote { margin: 8pt 0; padding: 4pt 12pt; border-left: 3px solid #94a3b8; color: #334155; background:#f8fafc; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 8pt 0; }
th, td { border: 1px solid #cbd5e1; padding: 3px 7px; text-align: left; vertical-align: top; }
th { background: #f1f5f9; color: #0f172a; }
img { max-width: 92%; display: block; margin: 8pt auto 2pt; }
hr { border: none; border-top: 1px solid #cbd5e1; margin: 14pt 0; }
ul, ol { margin: 0 0 7pt; padding-left: 20px; }
li { margin: 1pt 0; }
"""

def main(md_path):
    md_path = pathlib.Path(md_path).resolve()
    base = md_path.parent
    text = md_path.read_text(encoding="utf-8")
    import markdown
    html_body = markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list", "sane_lists", "smarty"])
    # rewrite image src to absolute file:/// URLs so Chrome embeds them
    def absimg(m):
        src = m.group(1)
        if src.startswith(("http", "data:", "file:")):
            return m.group(0)
        p = (base / src).resolve()
        return 'src="' + p.as_uri() + '"'
    html_body = re.sub(r'src="([^"]+)"', absimg, html_body)
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    html_path = md_path.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    pdf_path = md_path.with_suffix(".pdf")
    if pdf_path.exists():
        pdf_path.unlink()
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf_path}", html_path.as_uri()]
    subprocess.run(cmd, check=True, timeout=120,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok = pdf_path.exists() and pdf_path.stat().st_size > 5000
    print(f"{'OK' if ok else 'FAIL'}: {pdf_path}  ({pdf_path.stat().st_size if pdf_path.exists() else 0} bytes)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
