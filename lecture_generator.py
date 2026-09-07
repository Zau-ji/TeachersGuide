import json

from gemini_client import generate_text
from prompts import LECTURE_GENERATION_PROMPT, LECTURE_REVISION_PROMPT, LECTURE_TRANSLATION_PROMPT
from utils import clean_model_text


def generate_final_lecture(
    subject,
    grade,
    topic,
    duration,
    approved_lesson,
    teacher_instructions="",
    lecture_recommendations="",
    max_quality_revisions=2,
):
    from quality_checker import quality_check

    base_prompt = LECTURE_GENERATION_PROMPT + f"""

SUBJECT: {subject}
GRADE: {grade}
TOPIC: {topic}
DURATION CONTEXT: {duration}
ORIGINAL TEACHER INSTRUCTIONS: {teacher_instructions or "None"}

TEACHER RECOMMENDATIONS FOR THE LECTURE:
{lecture_recommendations or "None"}

APPROVED LESSON REVIEW:
{approved_lesson}
"""

    lecture = clean_model_text(generate_text(base_prompt, temperature=0.2))

    for _ in range(max_quality_revisions + 1):
        report = quality_check(
            subject=subject,
            grade=grade,
            topic=topic,
            approved_lesson=approved_lesson,
            lecture=lecture,
        )

        if report.get("status") == "PASS":
            return lecture

        important = [
            issue for issue in report.get("issues", [])
            if issue.get("severity") in {"HIGH", "MEDIUM"}
        ]
        if not important:
            return lecture

        issue_text = json.dumps(important, ensure_ascii=False, indent=2)
        revision_prompt = LECTURE_REVISION_PROMPT.format(issues=issue_text) + f"""

SUBJECT: {subject}
GRADE: {grade}
TOPIC: {topic}

APPROVED LESSON REVIEW:
{approved_lesson}

CURRENT LECTURE:
{lecture}
"""
        lecture = clean_model_text(generate_text(revision_prompt, temperature=0.05))

    return lecture


def translate_to_urdu(subject, approved_lesson, english_lecture):
    prompt = LECTURE_TRANSLATION_PROMPT + f"""

SUBJECT: {subject}

APPROVED LESSON REVIEW:
{approved_lesson}

FINAL ENGLISH LECTURE:
{english_lecture}
"""
    return clean_model_text(generate_text(prompt, temperature=0.1))
