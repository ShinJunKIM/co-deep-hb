r"""Build the two IEIE 2026 fall submissions from the templates and the master draft (docs/paper/ieie2026f_plan_and_draft_ko.md).
Output: docs/paper/ieie2026f_proceedings_draft.docx (논문양식.docx), docs/paper/ieie2026f_blind_review_draft.docx (서면 심사용).
Figures are placeholders (English captions); tables are inserted as simple grid tables.
Usage: python src\tools\make_ieie_docx.py
"""
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

REPO = Path(__file__).resolve().parents[2]
MD = (REPO / "docs/paper/ieie2026f_plan_and_draft_ko.md").read_text(encoding="utf-8")
OUTDIR = REPO / "docs/paper"

FIGS = {   # placeholder captions (English), keyed by where they go (after the paragraph that starts with this text)
    "Fig1": ("Fig. 1. (a) Pad pair with recess r, thermo-elastic protrusion u and surface-diffusion bulge-out h_d; contact when "
             "m = u_t + u_b + h_d,t + h_d,b − (r_t + r_b) ≥ 0. (b) Pre-registered V&V workflow (verification → train → test → prediction)."),
    "Fig2": ("Fig. 2. Mechanism transition with pad size: top + bottom elastic protrusion at 400 °C (model, model × 0.69, imec measurement) "
             "versus the saturated diffusion bulge-out (checked for D ≤ 300 nm) and the IRPS 2026 recess sum of 5 nm; crossover ≈ 0.7 µm."),
    "Fig3": ("Fig. 3. Surface-diffusion term versus imec 2026 bulge-out distributions: (a) 400/500 nm pitch medians and IQR versus anneal "
             "T and time, (b) size dependence at 250 °C (200–500 nm pitch), (c) orientation factor f(ω) and the faceted fraction."),
    "Fig4": ("Fig. 4. 300 nm pads: contact-probability process window over anneal T × time for a clean surface (main) and an oxidised "
             "surface (sensitivity); hatched cells change within the uncertainty set b × τ₀ × Q."),
    "Fig5": ("Fig. 5. 300 nm pads: allowable CMP recess sum (top + bottom, nm) for P(contact) ≥ 0.99 returned by the model for each "
             "anneal T × time (σ = 0.5 nm per pad)."),
    "Fig6": ("Fig. 6. (a) Factor ranking: number of window cells changed when each factor is varied (0.54 and 0.30 µm). "
             "(b) Open-pair floor at 300 nm set by near-<111> pads (facet term) versus a fine-grained-Cu proxy without the tail."),
}


def md_section(start, end):
    i = MD.index(start); j = MD.index(end, i)
    return MD[i:j]


def clean(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s); s = re.sub(r"\*(.+?)\*", r"\1", s)
    return s.strip()


def parse_body():
    """Return list of (kind, text) from section 4 of the draft: title, etitle, abstract, h1, body, ref."""
    sec = md_section("## 4. 원고 초안", "## 5. 표 초안")
    items = []
    for line in sec.split("\n"):
        t = line.strip()
        if not t or t.startswith("## 4."):
            continue
        if t.startswith("**제목(국문):**"):
            items.append(("title", clean(t.split(":**", 1)[1])))
        elif t.startswith("**Title:**"):
            items.append(("etitle", clean(t.split(":**", 1)[1])))
        elif t.startswith("**요약.**"):
            items.append(("abstract", clean(t.replace("**요약.**", ""))))
        elif t.startswith("### References"):
            items.append(("h1", "References"))
        elif t.startswith("### "):
            items.append(("h1", clean(t[4:])))
        elif re.match(r"^\[\d+\]", t):
            items.append(("ref", clean(t)))
        elif t.startswith("h_d = ") or t.startswith("D는 패드 지름"):
            items.append(("eq" if t.startswith("h_d") else "body", clean(t)))
        else:
            items.append(("body", clean(t)))
    return items


def parse_tables():
    sec = md_section("## 5. 표 초안", "## 6. 서면")
    tables, cur, title = [], None, None
    for line in sec.split("\n"):
        t = line.strip()
        if t.startswith("**Table"):
            if cur: tables.append((title, cur))
            title, cur = clean(t), []
        elif t.startswith("|") and cur is not None:
            if set(t.replace("|", "").strip()) <= set("-: "):
                continue
            cur.append([clean(c) for c in t.strip("|").split("|")])
    if cur: tables.append((title, cur))
    return tables


def clear_body_keep_sections(doc):
    body = doc.element.body
    for p in list(body.iterchildren()):
        if p.tag == qn("w:p"):
            ppr = p.find(qn("w:pPr"))
            if ppr is not None and ppr.find(qn("w:sectPr")) is not None:
                for r in list(p):
                    if r.tag != qn("w:pPr"): p.remove(r)
                continue
            body.remove(p)


def add_par(doc, text, size=9, bold=False, align=None, style=None, font="HY신명조", italic=False):
    p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    r = p.add_run(text); r.font.size = Pt(size); r.bold = bold; r.italic = italic
    r.font.name = font; r._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    if align is not None: p.alignment = align
    return p


def add_table(doc, title, rows, size=7.5, font="HY신명조"):
    add_par(doc, title, size=8, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font=font)
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, c in enumerate(row):
            cell = t.cell(i, j); cell.text = ""
            r = cell.paragraphs[0].add_run(c); r.font.size = Pt(size); r.bold = (i == 0)
            r.font.name = font; r._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    doc.add_paragraph()


def placeholder(doc, key, style=None, font="HY신명조"):
    add_par(doc, f"[{key} placeholder — to be rendered]", size=8, align=WD_ALIGN_PARAGRAPH.CENTER, style=style, font=font, italic=True)
    add_par(doc, FIGS[key], size=8, align=WD_ALIGN_PARAGRAPH.CENTER, style=style, font=font)


# ------------------------------------------------------------------ proceedings
def build_proceedings(items, tables):
    doc = docx.Document(str(REPO / "논문양식.docx"))
    title = next(t for k, t in items if k == "title"); etitle = next(t for k, t in items if k == "etitle")
    tb0, tb1 = doc.tables[0], doc.tables[1]
    tb0.cell(0, 0).paragraphs[0].text = title
    for p in tb0.cell(0, 0).paragraphs[1:]: p.text = ""
    cell = tb1.cell(0, 0)
    for p in cell.paragraphs:
        if "Implementation of Improved" in p.text: p.text = etitle
        elif "Using Embedded" in p.text: p.text = ""
    clear_body_keep_sections(doc)
    add_par(doc, "요  약", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_par(doc, next(t for k, t in items if k == "abstract"), size=9)
    fig_after = {"I. 서론": None}
    for k, t in items:
        if k in ("title", "etitle", "abstract"): continue
        if k == "h1":
            add_par(doc, t, size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
            if t.startswith("II."):
                pass
        elif k == "eq":
            add_par(doc, t, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
        elif k == "ref":
            add_par(doc, t, size=9)
        else:
            add_par(doc, t, size=9)
            if t.startswith("본 연구는 (1)"): placeholder(doc, "Fig1")
            if t.startswith("2.4 검증 절차"): add_table(doc, tables[0][0], tables[0][1])
            if t.startswith("3.1 열탄성 모델"): add_table(doc, tables[1][0], tables[1][1]); placeholder(doc, "Fig2")
            if t.startswith("3.2 표면확산 항 테스트"): placeholder(doc, "Fig3")
            if t.startswith("3.4 300 nm 공정창"): placeholder(doc, "Fig4"); placeholder(doc, "Fig5"); placeholder(doc, "Fig6")
            if t.startswith("Table 3에 모델 부분별"): add_table(doc, tables[2][0], tables[2][1])
    doc.save(str(OUTDIR / "ieie2026f_proceedings_draft.docx"))


# ------------------------------------------------------------------ blind review (journal template, 4 pages, no authors)
BLIND_SKIP_PREFIX = ("웨이퍼 간(W2W) Cu/SiCN", )   # keep everything; the condensing is done by the user later if over 4 pages


def build_blind(items, tables):
    doc = docx.Document(str(REPO / "서면 심사용 논문 양식.docx"))
    title = next(t for k, t in items if k == "title"); etitle = next(t for k, t in items if k == "etitle")
    abstract = next(t for k, t in items if k == "abstract")
    cell = doc.tables[0].cell(0, 0)
    for p in cell.paragraphs:
        if "여기에 제목을 입력하세요" in p.text: p.text = title
        elif "Put English Title Here" in p.text: p.text = "(" + etitle + ")"
        elif "이곳에 한글 요약문" in p.text: p.text = abstract
        elif "투고용 논문" in p.text: p.text = "학부생 논문경진대회 서면 심사용 (저자·소속 비공개)"
    # remove the author table (second table) if present
    if len(doc.tables) > 1:
        tbl = doc.tables[1]._element; tbl.getparent().remove(tbl)
    clear_body_keep_sections(doc)
    for k, t in items:
        if k in ("title", "etitle", "abstract"): continue
        if k == "h1":
            add_par(doc, "REFERENCES" if t == "References" else t, style="각 장 제목", font="바탕", size=10, bold=True)
        elif k == "eq":
            add_par(doc, t, style="Body Text", font="바탕", size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
        elif k == "ref":
            add_par(doc, t, style="참고문헌내용", font="바탕", size=8)
        else:
            add_par(doc, t, style="Body Text", font="바탕", size=9)
            if t.startswith("3.1 열탄성 모델"): add_table(doc, tables[1][0], tables[1][1], font="바탕"); placeholder(doc, "Fig2", style="그림/표 제목", font="바탕")
            if t.startswith("3.2 표면확산 항 테스트"): placeholder(doc, "Fig3", style="그림/표 제목", font="바탕")
            if t.startswith("3.4 300 nm 공정창"): placeholder(doc, "Fig4", style="그림/표 제목", font="바탕")
            if t.startswith("Table 3에 모델 부분별"): add_table(doc, tables[2][0], tables[2][1], font="바탕")
    doc.save(str(OUTDIR / "ieie2026f_blind_review_draft.docx"))


def main():
    items, tables = parse_body(), parse_tables()
    build_proceedings(items, tables); build_blind(items, tables)
    n_chars = sum(len(t) for k, t in items if k in ("body", "abstract"))
    print(f"paragraph items {len(items)}, tables {len(tables)}, body chars {n_chars} (~{n_chars / 1900:.1f} double-column pages at 9 pt, rough)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
