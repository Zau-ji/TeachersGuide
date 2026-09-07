# TeachersGuide — V1

TeachersGuide is a simple AI lesson-planning assistant for high-school science teachers.

## V1 scope

Subjects:
- Biology
- Chemistry
- Physics
- General Science

Workflow:
1. Create Lesson
2. Review & Approve
3. Generate Lecture

The source material controls factual scope. The teacher approves the intermediate lesson before the
final lecture is generated.

## Architecture

```text
app.py
  ├── lesson_generator.py
  │     ├── gemini_client.py
  │     └── prompts.py
  ├── lecture_generator.py
  │     ├── gemini_client.py
  │     ├── prompts.py
  │     └── quality_checker.py
  ├── quality_checker.py
  │     ├── gemini_client.py
  │     └── prompts.py
  └── utils.py
```

No database, accounts, LMS, student portal, analytics, payments, voice, avatars, automatic image
generation or curriculum database are included in V1.

## Local setup

1. Install Python 3.10+.
2. Create a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create:

```text
.streamlit/secrets.toml
```

with:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_MODEL = "gemini-2.5-flash"
```

5. Run:

```bash
streamlit run app.py
```

## Streamlit Community Cloud

Push the project to GitHub.

In Streamlit Community Cloud:
- Create a new app from the GitHub repository.
- Main file: `app.py`
- Add the same keys under the app's Secrets settings.

Never commit `.streamlit/secrets.toml`.

## Reliability design

TeachersGuide deliberately uses several safeguards:

1. Source-first lesson generation.
2. Teacher review/editing.
3. Explicit approval gate.
4. Lecture generation from approved lesson only.
5. Separate AI quality check.
6. Up to two automatic high/medium-priority lecture revisions.
7. Teacher can inspect the quality report.

This does not mathematically guarantee zero mistakes. It is designed to reduce unsupported content,
contradictions and common generation errors while keeping the teacher in control.

## Important V1 behavior

The lecture duration is context only. TeachersGuide does not try to calculate whether the lesson
contains exactly 40/45/60 minutes of speaking material. The teacher decides pacing and can provide
instructions.

## File uploads

PDF and common image formats are supported. Uploaded source material is held in Streamlit session
state for the current session and is sent to Gemini when generating the lesson. There is no persistent
lesson database in V1.

## Future ideas

Possible later additions:
- Pakistani board/curriculum alignment
- more languages
- question/worksheet generation
- automatic diagrams/images
- lesson history
- student presentation mode
- export to Word/PDF
