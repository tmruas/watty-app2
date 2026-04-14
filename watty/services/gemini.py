import os

import streamlit as st
from google import genai


def init_gemini_from_secrets() -> None:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]


def get_gemini_client():
    return genai.Client()
