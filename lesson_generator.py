from gemini_client import generate_text, upload_source_files
from prompts import LESSON_GENERATION_PROMPT, LESSON_REVISION_PROMPT
from utils import clean_model_text


def generate_lesson_draft(
    subject,
    grade,
    topic,
    duration,
    instructions,
    source_files,
):
    client, uploaded_sources = upload_source_files(source_files)

    metadata = f"""
SUBJECT: {subject}
GRADE: {grade}
TOPIC: {topic}
LECTURE DURATION CONTEXT: {duration}
TEACHER INSTRUCTIONS: {instructions or "None"}
"""

    prompt = LESSON_GENERATION_PROMPT + "\n\n" + metadata

    response = client.models.generate_content(
        model=__import__("gemini_client").get_model_name(),
        contents=[prompt, *uploaded_sources],
        config={"temperature": 0.15},
    )

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty lesson draft.")

    return clean_model_text(text)


def revise_lesson(subject, grade, topic, lesson, revision_instruction):
    prompt = (
        LESSON_REVISION_PROMPT
        + f"""

SUBJECT: {subject}
GRADE: {grade}
TOPIC: {topic}

EXISTING LESSON:
{lesson}

TEACHER REVISION INSTRUCTION:
{revision_instruction}
"""
    )
    return clean_model_text(generate_text(prompt, temperature=0.1))
