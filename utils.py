import re
import streamlit as st

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
MAX_FILE_SIZE_MB = 50
MAX_TOTAL_SIZE_MB = 100


def allowed_upload(filename, size_bytes):
    ext = "." + filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS and size_bytes <= MAX_FILE_SIZE_MB * 1024 * 1024


def build_source_files(uploaded_files):
    """Convert Streamlit UploadedFile objects into stable session-state dictionaries."""
    total = 0
    sources = []

    for file in uploaded_files:
        data = file.getvalue()
        total += len(data)

        if total > MAX_TOTAL_SIZE_MB * 1024 * 1024:
            raise ValueError(
                f"Total source upload size must be <= {MAX_TOTAL_SIZE_MB} MB."
            )

        mime = file.type or "application/octet-stream"
        sources.append(
            {
                "name": file.name,
                "mime_type": mime,
                "data": data,
                "size": len(data),
            }
        )

    return sources


def clean_model_text(text):
    """Remove accidental markdown fences around plain text/JSON responses."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json|text|markdown)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def safe_error_message(exc):
    """Keep API/UI errors readable without dumping implementation details."""
    msg = str(exc).strip()
    if not msg:
        return "Something went wrong. Please try again."

    lowered = msg.lower()
    if "api key" in lowered or "authentication" in lowered:
        return "Gemini API authentication failed. Check your GEMINI_API_KEY."
    if "quota" in lowered or "rate limit" in lowered:
        return "Gemini API quota/rate limit reached. Please try again later."
    if "timeout" in lowered:
        return "The AI request timed out. Please try again."

    return f"TeachersGuide could not complete the request: {msg}"


def clear_lecture_outputs():
    st.session_state.english_lecture = ""
    st.session_state.urdu_lecture = ""
    st.session_state.quality_report = None


def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.session_state.stage = "create"
    st.session_state.subject = "Biology"
    st.session_state.grade = "Grade 9"
    st.session_state.topic = ""
    st.session_state.duration = "40 minutes"
    st.session_state.instructions = ""
    st.session_state.source_files = []
    st.session_state.lesson_draft = ""
    st.session_state.approved_lesson = ""
    st.session_state.english_lecture = ""
    st.session_state.urdu_lecture = ""
    st.session_state.quality_report = None
    st.session_state.revision_instruction = ""
