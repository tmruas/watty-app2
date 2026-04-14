"""CSS global Watty (Streamlit markdown)."""
import base64

import streamlit as st

from watty.paths import hamburger_png_path


def hamburger_icon_css_url() -> str:
    """PNG do ícone menu embutido em data-URI para o CSS do Streamlit."""
    try:
        path = hamburger_png_path()
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f"url('data:image/png;base64,{b64}')"
    except OSError:
        return "none"


def inject_global_styles() -> None:
    bg = hamburger_icon_css_url()
    st.markdown(
        """
    <style>
    /* 1. O Fundo Principal (Lavanda/Lilás Watty) */
    .stApp {
        background-color: #E6DDF5;
    }

    .stApp > header {
        background-color: transparent;
    }

    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stToolbar"] [data-testid="collapsedControl"],
    [data-testid="stToolbar"] [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 1001;
    }

    [data-testid="collapsedControl"] button,
    button[data-testid="stSidebarCollapseButton"] {
        opacity: 1 !important;
        visibility: visible !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    section[data-testid="stSidebar"] button[aria-label="Fullscreen"] {
        display: none !important;
    }

    [data-testid="stSidebarCollapseButton"] span[data-testid="stIconMaterial"],
    [data-testid="collapsedControl"] span[data-testid="stIconMaterial"],
    header[data-testid="stHeader"] button span[data-testid="stIconMaterial"],
    header.stAppHeader button span[data-testid="stIconMaterial"] {
        font-size: 0 !important;
        line-height: 0 !important;
        color: transparent !important;
        width: 2rem !important;
        height: 2rem !important;
        min-width: 2rem !important;
        display: inline-block !important;
        overflow: hidden !important;
        background-image: __HAMBURGER_BG__;
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }

    .stMarkdown p, .stMarkdown li, p, label, .stRadio label {
        color: #311B52 !important;
        font-weight: 500;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 3px solid #D1C4E9;
        box-shadow: 2px 0px 15px rgba(0,0,0,0.05);
    }

    [data-testid="stSidebar"] * {
        color: #4A148C !important;
        font-weight: 600;
    }

    div.stButton > button:first-child {
        background-color: #9C27B0 !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        border-radius: 16px;
        border: 2px solid #7B1FA2;
        box-shadow: 0px 6px 0px #7B1FA2;
        padding: 10px 24px;
        transition: all 0.1s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:first-child:active {
        box-shadow: 0px 0px 0px #7B1FA2;
        transform: translateY(6px);
    }
    div.stButton > button:first-child:hover {
        background-color: #AB47BC !important;
    }

    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 2px solid #D1C4E9;
        border-radius: 16px;
        padding: 15px;
        border-bottom: 5px solid #FFC107;
        box-shadow: 0 4px 10px rgba(156, 39, 176, 0.1);
        text-align: center;
    }

    div[data-testid="metric-container"] label {
        font-weight: 800;
        color: #7B1FA2 !important;
        font-size: 14px;
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-weight: 900;
        color: #4A148C !important;
        font-size: 32px;
    }

    h1, h2, h3 {
        color: #4A148C !important;
        font-weight: 900 !important;
        letter-spacing: -0.5px;
    }

    .stTextInput input, .stTextArea textarea {
        border-radius: 16px;
        border: 2px solid #D1C4E9;
        padding: 14px;
        font-size: 16px;
        font-weight: 600;
        background-color: #FFFFFF !important;
        color: #4A148C !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #FFC107;
        box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.3);
    }

    .tw-size-8 { width: 2rem !important; height: 2rem !important; min-width: 2rem !important; }
    .tw-w-full { width: 100% !important; }
    .tw-h-auto { height: auto !important; }
    .tw-object-contain { object-fit: contain; }
    .tw-aspect-video { aspect-ratio: 16 / 9; }
    .tw-aspect-square { aspect-ratio: 1 / 1; }
    .tw-max-w-full { max-width: 100% !important; }

    [data-testid="stImage"] img {
        width: 100% !important;
        height: auto !important;
        object-fit: contain;
    }

    iframe, video {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        aspect-ratio: 16 / 9;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        [data-testid="stSidebar"] {
            width: min(86vw, 340px) !important;
            min-width: min(86vw, 340px) !important;
        }

        [data-testid="stHorizontalBlock"] {
            gap: 0.75rem;
        }

        [data-testid="column"] {
            min-width: calc(50% - 0.5rem) !important;
        }

        div.stButton > button:first-child {
            width: 100%;
            font-size: 16px !important;
            padding: 10px 14px;
        }

        div[data-testid="metric-container"] {
            padding: 10px;
        }

        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            font-size: 24px;
        }

        .stTextInput input, .stTextArea textarea {
            font-size: 15px;
            padding: 12px;
        }
    }

    @media (max-width: 480px) {
        h1 {
            font-size: 1.6rem !important;
        }
        h2 {
            font-size: 1.35rem !important;
        }
        h3 {
            font-size: 1.15rem !important;
        }

        [data-testid="column"] {
            min-width: 100% !important;
        }
    }

    @keyframes watty-shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .watty-chat-skeleton {
        display: flex;
        flex-direction: column;
        gap: 0.65rem;
        padding: 0.25rem 0;
        width: 100%;
        max-width: 100%;
    }
    .watty-chat-skeleton .watty-sk-line {
        height: 0.85rem;
        border-radius: 6px;
        background: linear-gradient(
            90deg,
            #e8e0f2 0%,
            #f5f1fb 35%,
            #dcd4e8 65%,
            #e8e0f2 100%
        );
        background-size: 200% 100%;
        animation: watty-shimmer 1.35s ease-in-out infinite;
    }
    .watty-chat-skeleton .watty-sk-w100 { width: 100%; }
    .watty-chat-skeleton .watty-sk-w95 { width: 95%; }
    .watty-chat-skeleton .watty-sk-w85 { width: 85%; }
    .watty-chat-skeleton .watty-sk-w60 { width: 60%; }
    </style>
""".replace(
            "__HAMBURGER_BG__", bg
        ),
        unsafe_allow_html=True,
    )
