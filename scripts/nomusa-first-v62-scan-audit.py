#!/usr/bin/env python3
"""Independent automated reading of the 2020–2021 Q-Net answer grids."""
import argparse
from collections import Counter
import hashlib
from io import BytesIO
from itertools import groupby
import json
from pathlib import Path
import re
import subprocess

import fitz
import numpy as np
from PIL import Image, ImageOps

SUBJECTS = ("labor1", "labor2", "civil", "social", "economics", "management")


def bands(indices):
    return [int(np.median(list(group))) for _, group in
            groupby(enumerate(indices), lambda pair: pair[1] - pair[0])
            for group in [[value for _, value in group]]]


def read_grid(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), colorspace=fitz.csGRAY)
    raster = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
    ink = raster < 150
    rows = bands(np.where(ink.sum(1) > pix.width * .42)[0])
    if len(rows) != 36:
        raise ValueError(f"Expected six complete subject grids, found {len(rows)} row lines")
    cells = []
    for subject in range(6):
        boundaries = rows[subject * 6:subject * 6 + 6]
        block = ink[boundaries[0] + 4:boundaries[-1] - 4]
        columns = bands(np.where(block.sum(0) > block.shape[0] * .6)[0])
        if len(columns) != 11:
            raise ValueError(f"Expected 11 column lines, found {len(columns)}")
        for row in range(5):
            for col in range(5):
                cell = raster[boundaries[row] + 6:boundaries[row + 1] - 6,
                              columns[col * 2 + 1] + 6:columns[col * 2 + 2] - 6]
                cells.append(cell)
    return cells


def glyph(cell):
    mask = cell < 160
    y, x = np.where(mask)
    if len(x) < 8:
        return None
    cropped = mask[y.min():y.max() + 1, x.min():x.max() + 1]
    if cropped.shape[1] > cropped.shape[0] * 1.06:
        return None
    image = Image.fromarray(cropped.astype("uint8") * 255)
    return np.asarray(image.resize((24, 32), Image.Resampling.BILINEAR), dtype=np.float32) / 255


def read_cell(cell, templates):
    shape = glyph(cell)
    if shape is None:
        image = ImageOps.expand(Image.fromarray(cell), border=20, fill=255)
        buf = BytesIO()
        image.save(buf, format="PNG")
        result = subprocess.check_output(
            ["tesseract", "stdin", "stdout", "--psm", "7", "-l", "eng",
             "-c", "tessedit_char_whitelist=12345,"], input=buf.getvalue(), stderr=subprocess.DEVNULL,
        ).decode().strip()
        if re.fullmatch(r"[1-5](?:,[1-5])+", result):
            return result, None, "MULTI_OCR_CANDIDATE"
        return result, None, "OCR_HOLD"
    distances = sorted((round(float(np.mean(np.abs(shape - template))), 4), label)
                       for label, template in templates.items())
    error, answer = distances[0]
    margin = distances[1][0] - error
    status = "GLYPH_READ" if error < .23 and margin > .035 else "OCR_HOLD"
    return str(answer), {"error": error, "margin": round(margin, 4)}, status


def run(pdf_dir, root):
    sources, answers = json.loads(subprocess.check_output(["node", "-e", """
global.window=global;
for(const name of ['legacy-first-answer-review','legacy-first-v2-staged','legacy-first-v4-2014-2021-review','legacy-first-v5-correction','legacy-first-v61-sources']) require('./study-hub/'+name+'.js');
console.log(JSON.stringify([window.NOMUSA_FIRST_V61_SOURCES.answerDocuments,Object.fromEntries(window.NOMUSA_FIRST_LEGACY_V5.records.map(x=>[x.id,x.answers]))]));
"""], cwd=root))
    rows = []
    for year in (2020, 2021):
        source = sources[f"{year}-AB"]
        path = pdf_dir / f"{source['article']}-{source['attachment']}.pdf"
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Unexpected answer PDF hash: {path}")
        with fitz.open(path) as doc:
            grids = [read_grid(page) for page in doc]
            # First five cells of 2020 A and first ten cells of 2021 B read directly from the source images.
            anchors = ({1: 4, 2: 0, 3: 3, 4: 1, 5: 2} if year == 2020
                       else {1: 6, 2: 2, 3: 0, 4: 8, 5: 3})
            reference = grids[0 if year == 2020 else 1]
            templates = {label: glyph(reference[index]) for label, index in anchors.items()}
            if any(template is None for template in templates.values()):
                raise ValueError(f"Unable to extract the manually read anchors: {year}")
            for page, form in enumerate("AB"):
                for i in range(150):
                    subject, offset = divmod(i, 25)
                    number = min(subject, 4) * 25 + offset + 1
                    key = f"legacy1-{year}-{form}-{SUBJECTS[subject]}-{number:03}"
                    candidate, score, status = read_cell(grids[page][i], templates)
                    expected = ",".join(map(str, answers[key]))
                    if status == "GLYPH_READ":
                        status = "GLYPH_AGREES" if candidate == expected else "GLYPH_DISAGREES"
                    rows.append({"id": key, "answerPdfPage": page + 1, "stored": expected,
                                 "read": candidate, "score": score, "status": status})
    return {"method": "Grid segmentation and independently labeled digit templates on hash-verified Q-Net PDFs",
            "independentHumanApproval": "HOLD",
            "counts": Counter(row["status"] for row in rows), "rows": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_dir", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    print(json.dumps(run(args.pdf_dir, args.root), ensure_ascii=False, indent=2))
