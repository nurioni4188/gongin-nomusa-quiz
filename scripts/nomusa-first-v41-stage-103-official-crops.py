#!/usr/bin/env python3
"""V41: Copy ONLY 103 provisionally readable original Q-Net question crops.

These are source-image staging assets; they are NOT graded/approved quiz items.
The original V40 artifact preserves all 300 location candidates and 137 crops.
Four visually incomplete crops MUST NOT be promoted into the staged asset set.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
V40 = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "review-artifacts/NOMUSA_FIRST_V40_IMPORTED"
V41 = ROOT / "review/NOMUSA_FIRST_V41_107_SOURCE_IMAGE_TRIAGE_20261118.json"
DEST = ROOT / "review/first-v41-native-crops"
EVIDENCE = ROOT / "review/NOMUSA_FIRST_V41_103_CROP_SHA_20261118.json"
NAME = re.compile(r"^legacy1-202[01]-A-(?:labor1|labor2|civil|social|economics|management)-\d{3}$")
HOLD = {
    "legacy1-2020-A-social-098": "CROP_MISSING_FIVE_CHOICES",
    "legacy1-2020-A-management-101": "CROP_MISSING_FIVE_CHOICES",
    "legacy1-2021-A-labor2-043": "CROP_SPILLS_INTO_NEXT_QUESTION_044",
    "legacy1-2021-A-management-110": "CROP_MISSING_FIVE_CHOICES",
}


def sha256(buf):
    return hashlib.sha256(buf).hexdigest()


def main():
    manifest = json.loads(V41.read_text(encoding="utf-8"))
    v40 = json.loads((V40 / "NOMUSA_FIRST_V40_300_ANCHOR_REVIEW.json").read_text(encoding="utf-8"))
    source_lookup = {r["id"]: r for r in v40["rows"]}
    rows = manifest["rows"]
    assert len(rows) == 107 and len({r["id"] for r in rows}) == 107
    assert v40["totalCandidates"] == 300
    assert v40["v38PageCandidates"] == 274 and v40["v38UnlocatedHOLD"] == 26
    assert v40["sourcePDFSHAValidated"] == 4 and v40["sourceJPEG_SHAValidated"] == 88
    assert manifest["scoringApproved"] == 0 and manifest["newlyImportedQDATA"] == 0
    assert set(manifest["affectedIDs"]) == set(HOLD)
    DEST.mkdir(parents=True, exist_ok=True)
    records = []
    for item in rows:
        id = item["id"]
        assert NAME.fullmatch(id) and id in source_lookup, id
        source = source_lookup[id]
        crop = source["provisionalQuestionVisualCrop"]
        assert crop is not None
        assert source["originalPdfSHA256"] == item["officialPdfSHA256"]
        assert source["v38OcrCandidatePage"] == item["v38CandidatePDFPage"]
        assert item["completeQuestionTextProofread"] is False
        assert item["imageGraphicMathTranscriptionVerified"] is False
        assert item["officialAnswerChoiceIndependentMatch"] is False
        assert item["contentExplanationVerified"] is False
        assert item["readyForQDATAImport"] is False and item["scoringApproved"] is False
        if id in HOLD:
            assert item["cropIssue"] == HOLD[id]
            assert item["originalQuestionImageInspection"] == "VISUAL_CROP_HOLD"
            continue
        assert item["cropIssue"] is None
        assert item["originalQuestionImageInspection"] == "VISIBLE_STEM_AND_FIVE_OPTION_MARKERS_PRELIMINARY"
        assert crop["file"] == id + ".jpg"
        source_path = V40 / "source_question_location_previews" / crop["file"]
        raw = source_path.read_bytes()
        assert raw[:3] == b"\xff\xd8\xff", id + "_NOT_JPEG"
        assert sha256(raw) == crop["jpegSHA256"], id + "_V40_CROP_SHA_CHANGED"
        (DEST / crop["file"]).write_bytes(raw)
        records.append({
            "id": id, "image": "review/first-v41-native-crops/" + crop["file"],
            "jpegSHA256": sha256(raw), "bytes": len(raw),
            "officialPdfSHA256": item["officialPdfSHA256"],
            "officialPDFPageCandidate": item["v38CandidatePDFPage"],
            "cropRectPDFPoints": crop["cropPDFPoints"],
            "reviewStatus": "IMAGE_STRUCTURE_PRELIMINARY_ONLY",
            "approvedFullText": False,
            "approvedOfficialAnswer": False,
            "approvedFormulaOrGraphic": False,
            "approvedExplanation": False,
            "readyForQDATAImport": False,
            "scoringApproved": False,
        })
    assert len(records) == len({x["id"] for x in records}) == 103
    assert len(list(DEST.glob("*.jpg"))) == 103
    assert not any((DEST / (id + ".jpg")).exists() for id in HOLD)
    out = {
        "schema": "NOMUSA_FIRST_V41_103_STAGED_SOURCE_CROPS_SHA/1",
        "V40ActionRunID": 44235916434,
        "V40ArtifactID": 14397920969,
        "sourceOriginalPDFSHAValidated": 4,
        "sourceOriginalPageJPEG_SHAValidated": 88,
        "V40QuestionCrops": 137,
        "V41VisuallyInspectedSubset": 107,
        "sourceCropsStagedForFurtherIndependentReview": 103,
        "visualCropHOLD": 4,
        "actualQDATAItemsAdded": 0,
        "approvedOfficialAnswers": 0,
        "scoringApproved": 0,
        "files": records
    }
    EVIDENCE.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k != "files"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
