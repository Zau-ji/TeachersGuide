import json

from gemini_client import generate_text
from prompts import QUALITY_CHECK_PROMPT
from utils import clean_model_text


def quality_check(subject, grade, topic, approved_lesson, lecture):
    prompt = QUALITY_CHECK_PROMPT + f"""

SUBJECT: {subject}
GRADE: {grade}
TOPIC: {topic}

APPROVED LESSON:
{approved_lesson}

GENERATED LECTURE:
{lecture}
"""

    raw = generate_text(prompt, temperature=0.0, json_mode=True)
    raw = clean_model_text(raw)

    try:
        report = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "status": "NEEDS_REVISION",
            "summary": "The quality checker returned an unreadable result.",
            "issues": [{
                "severity": "HIGH",
                "category": "teachability",
                "location": "Quality check",
                "problem": "Quality-control output could not be parsed.",
                "recommended_fix": "Regenerate the lecture and quality check.",
            }],
        }

    report.setdefault("status", "NEEDS_REVISION")
    report.setdefault("summary", "")
    report.setdefault("issues", [])

    if report["status"] not in {"PASS", "NEEDS_REVISION"}:
        report["status"] = "NEEDS_REVISION"

    return report
