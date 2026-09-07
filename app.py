import streamlit as st

from lesson_generator import generate_lesson_draft
from lecture_generator import generate_final_lecture, translate_to_urdu
from quality_checker import quality_check
from utils import allowed_upload, build_source_files, clear_lecture_outputs, reset_app, render_urdu_markdown, safe_error_message

st.set_page_config(page_title="TeachersGuide", page_icon="📚", layout="wide")

DEFAULTS = {
    "stage": "create",
    "subject": "Biology",
    "grade": "Grade 9",
    "topic": "",
    "duration": "40 minutes",
    "instructions": "",
    "source_files": [],
    "lesson_draft": "",
    "approved_lesson": "",
    "lecture_recommendations": "",
    "english_lecture": "",
    "urdu_lecture": "",
    "quality_report": None,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def go_to(stage):
    st.session_state.stage = stage
    st.rerun()


def render_progress():
    labels = [("create", "1. Create Lesson"), ("review", "2. Review & Approve"), ("lecture", "3. Generate Lecture")]
    current_index = [x[0] for x in labels].index(st.session_state.stage)
    cols = st.columns(3)
    for i, (_, label) in enumerate(labels):
        marker = "✓" if i < current_index else ("●" if i == current_index else "○")
        cols[i].markdown(f"### {marker} {label}")


st.title("📚 TeachersGuide")
st.caption("AI lesson planning for school science teachers")
render_progress()
st.divider()

if st.session_state.stage == "create":
    st.subheader("Create Lesson")
    st.write("Upload the textbook/source material. TeachersGuide will use it as the factual source for the lesson.")

    col1, col2 = st.columns(2)
    with col1:
        subjects = ["Biology", "Chemistry", "Physics", "General Science"]
        st.session_state.subject = st.selectbox("Subject", subjects, index=subjects.index(st.session_state.subject))
        grades = ["Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10", "1st Year", "2nd Year", "Other"]
        st.session_state.grade = st.selectbox("Class / Grade", grades, index=grades.index(st.session_state.grade))
    with col2:
        st.session_state.topic = st.text_input("Topic / Lesson Title", value=st.session_state.topic, placeholder="e.g. Newton's Second Law of Motion")
        durations = ["20 minutes", "30 minutes", "40 minutes", "45 minutes", "60 minutes"]
        st.session_state.duration = st.selectbox("Lecture Duration", durations, index=durations.index(st.session_state.duration))

    st.session_state.instructions = st.text_area(
        "Optional teacher instructions",
        value=st.session_state.instructions,
        placeholder="Example: Keep the explanation very simple, use a familiar example, and include 3 questions.",
        height=110,
    )

    uploads = st.file_uploader(
        "Textbook / source material (PDF or images)",
        type=["pdf", "png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        help="Use the relevant textbook pages or source material. Clear scans/photos work best.",
    )
    if uploads:
        invalid = [f.name for f in uploads if not allowed_upload(f.name, f.size)]
        if invalid:
            st.error("These files could not be used: " + ", ".join(invalid))
        else:
            st.session_state.source_files = build_source_files(uploads)
            st.success(f"{len(uploads)} source file(s) ready.")

    if not st.session_state.source_files:
        st.info("Upload at least one PDF or image containing the lesson source material.")

    if st.button("✨ Generate Lesson Review", type="primary", use_container_width=True):
        if not st.session_state.topic.strip():
            st.error("Please enter a topic.")
        elif not st.session_state.source_files:
            st.error("Please upload at least one PDF or image.")
        else:
            try:
                with st.spinner("Reading source material and preparing a teacher-friendly lesson review..."):
                    draft = generate_lesson_draft(
                        st.session_state.subject, st.session_state.grade, st.session_state.topic,
                        st.session_state.duration, st.session_state.instructions, st.session_state.source_files,
                    )
                st.session_state.lesson_draft = draft
                st.session_state.lecture_recommendations = ""
                clear_lecture_outputs()
                go_to("review")
            except Exception as exc:
                st.error(safe_error_message(exc))

elif st.session_state.stage == "review":
    st.subheader("Review & Approve")
    st.caption("A quick, read-only summary of what TeachersGuide plans to teach. This is not the full lecture.")

    st.markdown(st.session_state.lesson_draft)

    st.divider()
    st.subheader("Teacher Recommendations for the Lecture")
    st.caption("Optional. Tell the AI how you want the final lecture taught. This does not directly edit the lesson review.")
    st.session_state.lecture_recommendations = st.text_area(
        "Recommendations",
        value=st.session_state.lecture_recommendations,
        placeholder="Examples: Make the language even simpler. Use a shopping-cart example. Ask more questions. Keep the explanation short. Include a simple board diagram.",
        height=120,
        label_visibility="collapsed",
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Approve & Continue", type="primary", use_container_width=True):
            if not st.session_state.lesson_draft.strip():
                st.error("The lesson review is empty.")
            else:
                st.session_state.approved_lesson = st.session_state.lesson_draft.strip()
                clear_lecture_outputs()
                go_to("lecture")
    with c2:
        if st.button("← Start Over", use_container_width=True):
            reset_app()
            st.rerun()

    st.info("Approval sets this review as the scientific/content boundary for lecture generation. Your recommendations guide teaching style, not the factual scope.")

elif st.session_state.stage == "lecture":
    st.subheader("Generate Lecture")
    m1, m2, m3 = st.columns(3)
    m1.metric("Subject", st.session_state.subject)
    m2.metric("Class", st.session_state.grade)
    m3.metric("Duration", st.session_state.duration)

    with st.expander("View approved lesson review", expanded=False):
        st.markdown(st.session_state.approved_lesson)

    if not st.session_state.english_lecture:
        if st.button("🎓 Generate English Lecture", type="primary", use_container_width=True):
            try:
                with st.spinner("Turning the approved lesson into a simple, student-friendly classroom lecture..."):
                    lecture = generate_final_lecture(
                        subject=st.session_state.subject,
                        grade=st.session_state.grade,
                        topic=st.session_state.topic,
                        duration=st.session_state.duration,
                        approved_lesson=st.session_state.approved_lesson,
                        teacher_instructions=st.session_state.instructions,
                        lecture_recommendations=st.session_state.lecture_recommendations,
                    )
                report = quality_check(
                    subject=st.session_state.subject,
                    grade=st.session_state.grade,
                    topic=st.session_state.topic,
                    approved_lesson=st.session_state.approved_lesson,
                    lecture=lecture,
                )
                st.session_state.english_lecture = lecture
                st.session_state.quality_report = report
                st.rerun()
            except Exception as exc:
                st.error(safe_error_message(exc))
    else:
        st.success("English lecture generated.")

        if st.session_state.quality_report:
            report = st.session_state.quality_report
            if report.get("status") == "PASS":
                st.success("AI quality check: PASS")
            else:
                st.warning("AI quality check found items that should be reviewed.")
            with st.expander("View AI quality check"):
                st.json(report)

        st.markdown("## English Lecture")
        st.markdown(st.session_state.english_lecture)

        st.divider()
        st.subheader("Urdu Translation")
        st.caption("Natural Pakistani classroom Urdu. Scientific terminology, formulas, symbols and units are preserved.")

        if not st.session_state.urdu_lecture:
            if st.button("🇵🇰 Translate to Urdu", use_container_width=True):
                try:
                    with st.spinner("Translating into natural Pakistani classroom Urdu..."):
                        st.session_state.urdu_lecture = translate_to_urdu(
                            subject=st.session_state.subject,
                            approved_lesson=st.session_state.approved_lesson,
                            english_lecture=st.session_state.english_lecture,
                        )
                    st.rerun()
                except Exception as exc:
                    st.error(safe_error_message(exc))
        else:
            render_urdu_markdown(st.session_state.urdu_lecture)

        st.divider()
        b1, b2 = st.columns(2)
        with b1:
            if st.button("← Back to Review", use_container_width=True):
                clear_lecture_outputs()
                go_to("review")
        with b2:
            if st.button("🆕 Create New Lesson", use_container_width=True):
                reset_app()
                st.rerun()
