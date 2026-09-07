import re
import html
import streamlit as st

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
MAX_FILE_SIZE_MB = 50
MAX_TOTAL_SIZE_MB = 100


def allowed_upload(filename, size_bytes):
    ext = "." + filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS and size_bytes <= MAX_FILE_SIZE_MB * 1024 * 1024


def build_source_files(uploaded_files):
    total = 0
    sources = []
    for file in uploaded_files:
        data = file.getvalue()
        total += len(data)
        if total > MAX_TOTAL_SIZE_MB * 1024 * 1024:
            raise ValueError(f"Total source upload size must be <= {MAX_TOTAL_SIZE_MB} MB.")
        sources.append({
            "name": file.name,
            "mime_type": file.type or "application/octet-stream",
            "data": data,
            "size": len(data),
        })
    return sources


def clean_model_text(text):
    text = (text or "").strip()
    text = re.sub(r"^```(?:json|text|markdown)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def safe_error_message(exc):
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
    st.session_state.lecture_recommendations = ""
    st.session_state.english_lecture = ""
    st.session_state.urdu_lecture = ""
    st.session_state.quality_report = None


def render_urdu_markdown(markdown_text):
    """Render Urdu RTL while keeping formulas, code and numeric/scientific lines LTR."""
    text = (markdown_text or "").strip()
    if not text:
        return

    # Render line-by-line so normal Urdu is RTL while equations remain LTR.
    lines = text.splitlines()
    in_code = False
    paragraph = []

    def flush_paragraph():
        nonlocal paragraph
        if not paragraph:
            return
        content = " ".join(x.strip() for x in paragraph).strip()
        if content:
            st.markdown(
                f"<div dir='rtl' style='text-align:right; line-height:1.9; margin-bottom:0.7rem'>{content}</div>",
                unsafe_allow_html=True,
            )
        paragraph = []

    for raw in lines:
        line = raw.strip()
        if line.startswith("```"):
            flush_paragraph()
            in_code = not in_code
            if in_code:
                st.markdown("<div dir='ltr'>", unsafe_allow_html=True)
            else:
                st.markdown("</div>", unsafe_allow_html=True)
            continue

        if in_code:
            st.code(line, language=None)
            continue

        if not line:
            flush_paragraph()
            continue

        # Display math / equation lines: keep LTR and let Streamlit render MathJax.
        if line.startswith("$$") or line.startswith("\\[") or line.endswith("$$"):
            flush_paragraph()
            st.markdown(line)
            continue

        # Headings
        if re.match(r"^#{1,6}\s", line):
            flush_paragraph()
            heading = re.sub(r"^#{1,6}\s+", "", line)
            st.markdown(
                f"<div dir='rtl' style='text-align:right; margin-top:1rem; margin-bottom:0.4rem'><strong>{html.escape(heading)}</strong></div>",
                unsafe_allow_html=True,
            )
            continue

        # Bullets / numbered items: render them as RTL HTML.
        m = re.match(r"^(?:[-*]|\d+[.)])\s+(.*)$", line)
        if m:
            flush_paragraph()
            item = html.escape(m.group(1))
            st.markdown(
                f"<div dir='rtl' style='text-align:right; margin-bottom:0.35rem'>• {item}</div>",
                unsafe_allow_html=True,
            )
            continue

        # Lines that are mostly formulas/numbers/scientific notation stay LTR.
        if re.fullmatch(r"[A-Za-z0-9\s=+\-*/().,:²³%°µ≤≥<>^_\\{}$]+", line):
            flush_paragraph()
            st.markdown(f"<div dir='ltr' style='text-align:left'>{line}</div>", unsafe_allow_html=True)
            continue

        paragraph.append(line)

    flush_paragraph()
