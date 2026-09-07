import os
import streamlit as st
from google import genai
from google.genai import types


def get_client():
    api_key = None
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to Streamlit Secrets or your environment.")
    return genai.Client(api_key=api_key)


def get_model_name():
    try:
        configured = st.secrets.get("GEMINI_MODEL")
    except Exception:
        configured = None
    return configured or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


def source_parts(source_files):
    return [
        types.Part.from_bytes(data=source["data"], mime_type=source["mime_type"])
        for source in source_files
    ]


def generate_text(prompt, contents=None, temperature=0.2, json_mode=False):
    client = get_client()
    payload = [prompt]
    if contents:
        payload.extend(contents)
    config = {"temperature": temperature}
    if json_mode:
        config["response_mime_type"] = "application/json"
    response = client.models.generate_content(
        model=get_model_name(),
        contents=payload,
        config=config,
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text.strip()
