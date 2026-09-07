# TeachersGuide

TeachersGuide is a simple AI lesson-planning assistant for school science teachers in Pakistan.

## V2 workflow

1. **Create Lesson** — choose subject, grade, topic and duration; upload textbook/source material.
2. **Review & Approve** — receive a concise, read-only teaching outline with formulas, board work and visual suggestions. Add optional teacher recommendations for how the final lecture should be taught.
3. **Generate Lecture** — generate a simple, student-friendly English classroom lecture from the approved outline, run an AI quality check, and optionally translate the final lecture into natural Pakistani classroom Urdu with RTL display.

## Core rule

**The source controls the facts and scope. AI controls the teaching.**

The duration is context only. TeachersGuide does not calculate minute-by-minute timing or decide whether content is enough for the selected duration.

## V2 improvements

- Review page is read-only and concise; it is not a full lecture editor.
- Teacher recommendations are kept separate from factual lesson content and are passed to the lecture writer.
- Formulas use Markdown/LaTeX rendering instead of showing raw LaTeX in a text area.
- Prompts emphasize simple, natural Pakistani classroom English and avoid academic/university-style wording.
- Quality checking explicitly looks for misleading analogies, speed/acceleration confusion, overly complex language, and formula corruption.
- Urdu output is rendered right-to-left while mathematical/scientific notation is kept left-to-right.
- Uploaded PDF/image bytes are sent with `Part.from_bytes` rather than treated as file paths.

## Local setup

```bash
python -m venv .venv
```

On Windows PowerShell, activation may be blocked by execution policy. You can skip activation and use the environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Create `.streamlit/secrets.toml` locally:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_MODEL = "gemini-3.6-flash"
```

Never commit the real `secrets.toml` to GitHub.

## Deployment

Upload the source files to GitHub. On Streamlit Community Cloud, add the same values under the app's Secrets settings.

Do not upload `__pycache__`, `.pyc` files, ZIP archives, or the real `.streamlit/secrets.toml`.
