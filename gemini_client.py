import os
import streamlit as st
from google import genai


def get_client():
    """Create a Gemini client using Streamlit secrets or an environment variable."""
    api_key = None

    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

    api_key = api_key or os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to Streamlit Secrets or your environment."
        )

    return genai.Client(api_key=api_key)


def get_model_name():
    """Keep the model configurable so the app does not depend on a hard-coded model forever."""
    try:
        configured = st.secrets.get("GEMINI_MODEL")
    except Exception:
        configured = None

    return configured or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def upload_source_files(source_files):
    """Upload source bytes through the Gemini Files API."""
    client = get_client()
    uploaded = []

    for source in source_files:
        uploaded.append(
            client.files.upload(
                file=source["data"],
                config={"mime_type": source["mime_type"]},
            )
        )

    return client, uploaded


def generate_text(prompt, contents=None, temperature=0.2, json_mode=False):
    """Centralized Gemini generation helper."""
    client = get_client()
    model = get_model_name()

    payload = [prompt]
    if contents:
        payload.extend(contents)

    config = {
        "temperature": temperature,
    }

    if json_mode:
        config["response_mime_type"] = "application/json"

    response = client.models.generate_content(
        model=model,
        contents=payload,
        config=config,
    )

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")

    return text.strip()
