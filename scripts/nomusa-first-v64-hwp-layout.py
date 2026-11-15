#!/usr/bin/env python3
"""Reconstruct question layout from pyhwp XHTML with a narrow HTML allowlist."""
import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
import re
from lxml import etree

MARKERS = "①②③④⑤"
NUMBER = re.compile(r"^(\d{1,3})\.\s")
GROUP = re.compile(r"^\[\s*(\d+)\s*[-~～]\s*(\d+)\s*\]")
SUBJECT_HEADER = re.compile(r"^제\s*\d+\s*과목")


def string(node):
    return "".join(node.itertext()).strip()


def name(node):
    return etree.QName(node).localname


def markup(node, underlines):
    tag = name(node)
    if tag not in {"p", "span", "div", "table", "tbody", "thead", "tfoot", "tr", "td", "th", "br"}:
        raise ValueError(f"Unrecognized layout element: {tag}")
    if tag == "br":
        return "<br>"
    # A table can be nested in a pyhwp paragraph. Use a div in that case.
    if tag == "p" and node.xpath(".//*[local-name()='table']"):
        tag = "div"
    if tag == "span" and node.xpath(".//*[local-name()='table']"):
        tag = "div"
    if tag == "span" and set(node.get("class", "").split()) & underlines:
        tag = "u"
    attrs = ""
    if tag in ("td", "th"):
        for key in ("rowspan", "colspan"):
            value = node.get(key, "")
            if value.isdecimal() and 1 < int(value) <= 20:
                attrs += f' {key}="{int(value)}"'
    children = escape(node.text or "") + "".join(
        markup(child, underlines) + escape(child.tail or "") for child in node
    )
    return f"<{tag}{attrs}>{children}</{tag}>"


def blocks(document):
    sections = document.xpath('//*[@class="Page"]')
    elements = [p for section in sections for p in section if string(p)]
    starts = [(i, int(m[1])) for i, element in enumerate(elements)
              if name(element) == "p" and (m := NUMBER.match(string(element)))]
    if [number for _, number in starts] not in (list(range(1, 26)) * 5, list(range(1, 126))):
        raise ValueError("Unexpected HWP question numbering")
    context = {}
    boundaries = [i for i, _ in starts]
    for pos, element in enumerate(elements):
        found = GROUP.match(string(element))
        if found is None:
            continue
        following = next((i for i, j in enumerate(boundaries) if j > pos), None)
        if following is None or starts[following][1] != int(found[1]):
            continue
        lead = elements[pos:boundaries[following]]
        for offset in range(int(found[2]) - int(found[1]) + 1):
            context[following + offset] = lead

    for index, (begin, number) in enumerate(starts):
        end = boundaries[index + 1] if index + 1 < len(starts) else len(elements)
        raw = elements[begin:end]
        body = []
        for element in raw:
            text = string(element)
            if GROUP.match(text) or SUBJECT_HEADER.match(text):
                break
            if re.fullmatch(r"A\s*-\s*\d+\s*-\s*\d+", text):
                continue
            body.append(element)
        yield number, context.get(index, []), body


def generate(xhtml, baseline, report, year, elective="management"):
    subjects = ("노동법(1)", "노동법(2)", "경제학원론", "민법", "영어")
    codes = ("labor1", "labor2", "economics", "civil", "english")
    if year >= 2010:
        subjects = ("노동법(1)", "노동법(2)", "민법", "사회보험법", "경영학개론")
        codes = ("labor1", "labor2", "civil", "social", "management")
        if elective == "economics":
            subjects = (*subjects[:-1], "경제학원론")
            codes = (*codes[:-1], "economics")
    css = xhtml.with_name("styles.css").read_text()
    underlines = set(re.findall(r"\.(charshape-\d+)\s*\{[^}]*text-decoration:\s*underline", css))
    existing = {q["k"]: q for q in baseline}
    held = {}
    output = []
    doc = etree.parse(str(xhtml), etree.XMLParser(resolve_entities=False, no_network=True))
    for index, (number, lead, body) in enumerate(blocks(doc)):
        group = index // 25
        if elective == "economics" and group != 4:
            continue
        key = f"legacy1-{year}-A-{codes[group]}-{number:03}"
        if key in existing:
            output.append(existing[key])
            continue
        text = "\n".join(string(x) for x in body)
        selected = re.split(f"([{MARKERS}])", text)
        if selected[1::2] != list(MARKERS) or any(not part.strip() for part in selected[2::2]):
            held[key] = "CHOICE_SEQUENCE_REVIEW"
            continue
        try:
            html = "".join(markup(node, underlines) for node in [*lead, *body])
        except ValueError:
            held[key] = "UNRENDERED_DRAWING_OR_SYMBOL"
            continue
        row = report["verifiedAnswers"][key]
        output.append({"k": key, "y": year, "r": year - 1991, "form": "A", "s": subjects[group],
                       "n": number, "q": NUMBER.sub("", selected[0]).strip(), "t": True,
                       "o": [part.strip() for part in selected[2::2]], "a": row,
                       "sourceUrl": report.get("officialQuestionNotice"), "answerSourceUrl": report.get("answerSourceUrl"),
                       "paperHtml": html})
    return output, held


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("xhtml", type=Path)
    p.add_argument("baseline", type=Path)
    p.add_argument("answer_report", type=Path)
    p.add_argument("--year", type=int, choices=(2008, 2009, 2010, 2011, 2012, 2015), default=2008)
    p.add_argument("--elective", choices=("management", "economics"), default="management")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    bank = json.loads(args.baseline.read_text().split(" = ", 1)[1].strip().removesuffix(";"))
    rows, held = generate(args.xhtml, bank, json.loads(args.answer_report.read_text()), args.year, args.elective)
    args.output.write_text(f"window.NOMUSA_FIRST_{args.year} = " +
                           json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(json.dumps({"questions": len(rows), "layoutRestored": sum("paperHtml" in r for r in rows),
                      "bySubject": Counter(q["s"] for q in rows), "held": held}, ensure_ascii=False, indent=2))
