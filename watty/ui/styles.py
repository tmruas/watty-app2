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
    # Viewport: Streamlit injeta o shell; isto duplica no body (alguns motores ainda interpretam).
    st.markdown(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <style>
    /* Fredoka: alternativa web open-source ao Feather Bold (fonte proprietária Duolingo — design.duolingo.com). */
    @import url("https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:ital,wght@0,400..1000;1,400..1000&family=Varela+Round&display=swap");

    /* Raiz: rem escala com zoom do browser; box-sizing previsível */
    html {
        font-size: 110%;
        box-sizing: border-box;
    }
    *, *::before, *::after {
        box-sizing: inherit;
    }

    /* Altura mínima em vez de 100vh fixo: evita cortar conteúdo ao fazer zoom */
    html, body, #root, [data-testid="stAppViewContainer"], .stApp {
        min-height: 100vh !important;
        min-height: 100dvh !important;
    }
    .stApp {
        height: auto !important;
        max-height: none !important;
    }

    /* Sem scroll horizontal: zoom extremo não alarga a página (código faz scroll local) */
    html {
        overflow-x: hidden;
    }
    body, #root, [data-testid="stAppViewContainer"], .stApp,
    section[data-testid="stMain"], section[data-testid="stSidebar"] {
        overflow-x: hidden;
        max-width: 100%;
    }
    [data-testid="stAppViewContainer"] {
        min-width: 0 !important;
    }
    section[data-testid="stMain"] {
        position: relative !important;
        min-width: 0 !important;
        flex: 1 1 auto !important;
        overflow-wrap: break-word;
    }
    .main .block-container {
        max-width: 100% !important;
        min-width: 0 !important;
    }
    .stApp img, .stApp picture > img {
        max-width: 100%;
        height: auto;
    }
    .stApp pre, .stMarkdown pre, [data-testid="stMarkdownContainer"] pre {
        max-width: 100%;
        overflow-x: auto;
    }

    /* Fundo lavanda + tipografia display arredondada (Fredoka; Nunito como fallback). */
    .stApp {
        background-color: #E6DDF5;
        font-family: "Fredoka", "Nunito", "Segoe UI", system-ui, -apple-system, sans-serif;
        line-height: 1.4;
    }

    /* Input de chat fixo no fundo: sem padding extra o rodapé fica por baixo da barra. */
    .main .block-container {
        padding-bottom: max(7rem, calc(env(safe-area-inset-bottom, 0rem) + 5.5rem)) !important;
    }

    .stApp > header {
        background-color: transparent;
    }

    /* st.chat_input fica fixo ao fundo; sem isto o rodapé fica por baixo e parece “invisível” */
    .stApp div.block-container {
        padding-bottom: max(8rem, 9.375rem) !important;
    }

    section[data-testid="stSidebar"] button[aria-label="Fullscreen"] {
        display: none !important;
    }

    /* Desktop: sidebar sempre visível; sem botão hamburger/collapse */
    @media (min-width: 769px) {
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stToolbar"] [data-testid="collapsedControl"],
        [data-testid="stToolbar"] [data-testid="stSidebarCollapseButton"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        section[data-testid="stSidebar"] {
            transform: translateX(0) !important;
            visibility: visible !important;
        }
    }

    /* Mobile: controlos da sidebar visíveis + ícone hamburger custom */
    @media (max-width: 768px) {
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
    }

    /*
     * --- Sidebar (contentor principal, logo WATTY, “Menu do Watty”) ---
     * 1) Padding/margin-top reduzidos ou removidos na cadeia até ao logo.
     * 2) Flex column + justify-content: flex-start (sem center / space-*).
     * 3) Ocultar decorações / blocos vazios que actuam como espaçadores.
     * Largura dinâmica: layout._inject_watty_sidebar_chrome (st.markdown no main).
     */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 0.1875rem solid #D1C4E9;
        box-shadow: 0.125rem 0 0.9375rem rgba(0, 0, 0, 0.05);
        padding-top: 0 !important;
        margin-top: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: stretch !important;
        /* DIN Next Rounded: tipografia Duolingo (local se instalada); web: Varela Round + Nunito */
        font-family: "DIN Next Rounded", "Varela Round", "Nunito", "Fredoka", "Segoe UI", system-ui, sans-serif !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: stretch !important;
        flex: 1 1 auto !important;
    }

    section[data-testid="stSidebar"] > div > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: stretch !important;
        gap: 1rem !important;
    }

    /* Contentor principal dos widgets da sidebar: fluxo em coluna + espaçamento uniforme */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
        gap: 1rem !important;
        row-gap: 1rem !important;
        column-gap: 1rem !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: stretch !important;
    }

    [data-testid="stSidebar"] div.block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Primeiro widget da coluna: sem empurrão extra (logo) */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div.element-container:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Widget da imagem do logo + <img> */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        object-fit: contain !important;
        display: block !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* “Menu do Watty”: ~+40% face a 1.54rem; afastar da caixa de boas-vindas */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #4A148C !important;
        font-weight: 800 !important;
        font-size: clamp(1.35rem, 0.85rem + 2.2vw, 2.25rem) !important;
        line-height: 1.2 !important;
        margin-top: 0.25rem !important;
        margin-bottom: 1rem !important;
        position: static !important;
    }

    /* “O que queres fazer?” — fluxo normal, sem sobreposição com Aprender */
    [data-testid="stSidebar"] p.watty-sidebar-section-title {
        color: #4A148C !important;
        font-weight: 600 !important;
        font-size: clamp(1.35rem, 1rem + 1.4vw, 1.75rem) !important;
        line-height: 1.25 !important;
        margin: 0 !important;
        margin-bottom: 1rem !important;
        letter-spacing: 0.01em !important;
        position: static !important;
    }
    [data-testid="stSidebar"] div.element-container:has(p.watty-sidebar-section-title) {
        position: static !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    [data-testid="stSidebar"] div.element-container:has(p.watty-sidebar-section-title) [data-testid="stMarkdownContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
        width: 100% !important;
        border: none !important;
        border-top: 0.0625rem solid #e1d5f0 !important;
    }

    /* Espaçadores / decoração Streamlit no topo da sidebar */
    [data-testid="stSidebar"] [data-testid="stDecoration"] {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:empty {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaption"] {
        color: #5c4a7a !important;
        font-size: 1.12rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #311B52 !important;
        font-size: 1.225rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
    }

    /* Selectbox na sidebar: texto do valor +40%; abrir lista sem editar o campo */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] {
        font-size: 1.225rem !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] input,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] textarea {
        pointer-events: none !important;
        user-select: none !important;
        caret-color: transparent !important;
        cursor: pointer !important;
    }
    /* Algumas versões do Streamlit usam combobox div em vez de input */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [role="combobox"] {
        user-select: none !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [contenteditable="true"] {
        pointer-events: none !important;
        user-select: none !important;
        caret-color: transparent !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child {
        cursor: pointer !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
        color: #311B52 !important;
    }

    [data-testid="stSidebar"] div[role="alert"] {
        background-color: rgba(76, 175, 80, 0.1) !important;
        border: 0.0625rem solid rgba(76, 175, 80, 0.45) !important;
        color: #1b5e20 !important;
    }

    [data-testid="stSidebar"] div[role="alert"] * {
        color: inherit !important;
    }
    [data-testid="stSidebar"] div[role="alert"] {
        font-size: 1.12rem !important;
        line-height: 1.35 !important;
    }

    /* Nav: espaçamento entre botões vem do gap do stVerticalBlock; evitar margens extra */
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_aprender,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_treinar,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_resumos,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_watty_tv,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_jogos,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_ranking {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        position: static !important;
    }

    /* Nav: inativo = texto roxo escuro, sem caixa; ícone + label à esquerda */
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_aprender button,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_treinar button,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_resumos button,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_watty_tv button,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_jogos button {
        background-color: transparent !important;
        color: #311B52 !important;
        border: 0.125rem solid transparent !important;
        border-radius: 0.75rem !important;
        box-shadow: none !important;
        font-weight: 800 !important;
        font-size: 1.33rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        padding: 0.85rem 0.55rem !important;
        min-height: 3.15rem !important;
        justify-content: flex-start !important;
        transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
    }

    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_aprender button:hover,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_treinar button:hover,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_resumos button:hover,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_watty_tv button:hover,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_jogos button:hover {
        background-color: rgba(156, 39, 176, 0.08) !important;
        color: #4A148C !important;
    }

    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_aprender button:active,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_treinar button:active,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_resumos button:active,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_watty_tv button:active,
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_jogos button:active {
        transform: none !important;
    }

    /* Ícones Material nos botões da navegação (+~40%) */
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_aprender button span[data-testid="stIconMaterial"],
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_treinar button span[data-testid="stIconMaterial"],
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_resumos button span[data-testid="stIconMaterial"],
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_watty_tv button span[data-testid="stIconMaterial"],
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_jogos button span[data-testid="stIconMaterial"],
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_ranking button span[data-testid="stIconMaterial"] {
        font-size: 1.65rem !important;
        line-height: 1 !important;
    }

    /* Ranking: desativado, preto e branco sobre fundo branco */
    [data-testid="stSidebar"] div.element-container.st-key-watty_nav_ranking button {
        filter: grayscale(1) !important;
        background-color: #f5f5f5 !important;
        color: #424242 !important;
        border: 0.0625rem solid #bdbdbd !important;
        box-shadow: none !important;
        font-weight: 800 !important;
        font-size: 1.33rem !important;
        white-space: pre-line !important;
        border-radius: 0.75rem !important;
        text-transform: uppercase !important;
        justify-content: flex-start !important;
        padding: 0.85rem 0.55rem !important;
        min-height: 3.15rem !important;
        opacity: 1 !important;
    }

    .stMarkdown p, .stMarkdown li, p, label, .stRadio label {
        color: #311B52 !important;
        font-weight: 500;
    }

    /* Botões roxos na área principal: texto branco, escala com a viewport */
    section[data-testid="stMain"] div.stButton > button:first-child {
        background-color: #7B1FA2 !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: clamp(0.88rem, 2.4vw + 0.35rem, 1.2rem) !important;
        border-radius: clamp(0.75rem, 2vw, 1rem);
        border: 0.125rem solid #6A1B9A !important;
        box-shadow: 0 clamp(0.1875rem, 0.8vw, 0.375rem) 0 #5a1582;
        padding: clamp(0.45rem, 1.2vw, 0.65rem) clamp(0.75rem, 3vw, 1.5rem) !important;
        transition: all 0.1s ease;
        text-transform: uppercase;
        letter-spacing: clamp(0.02em, 0.2vw, 0.06em);
    }
    section[data-testid="stMain"] div.stButton > button:first-child:active {
        box-shadow: 0 0 0 #5a1582;
        transform: translateY(clamp(0.1875rem, 0.8vw, 0.375rem));
    }
    section[data-testid="stMain"] div.stButton > button:first-child:hover {
        background-color: #8E24AA !important;
        color: #ffffff !important;
    }
    /* Conteúdo textual e ícones Material dentro dos botões da main */
    section[data-testid="stMain"] div.stButton > button:first-child p,
    section[data-testid="stMain"] div.stButton > button:first-child span {
        color: #ffffff !important;
    }

    section[data-testid="stMain"] .block-container {
        position: relative !important;
        width: 100% !important;
        max-width: 100% !important;
    }

    /*
     * Cartão de perfil: topo direito da área de conteúdo principal.
     * left: auto + right explícito evita herança de "left" do Streamlit que empurrava para a esquerda.
     */
    div.element-container.st-key-watty_profile_bar {
        position: absolute !important;
        top: 0 !important;
        left: auto !important;
        right: max(1rem, env(safe-area-inset-right, 0rem)) !important;
        inset-inline-start: auto !important;
        inset-inline-end: max(1rem, env(safe-area-inset-right, 0rem)) !important;
        z-index: 1000020 !important;
        width: auto !important;
        max-width: min(20rem, 90dvw, 100%) !important;
        margin: 0 !important;
        margin-inline-start: auto !important;
        margin-inline-end: 0 !important;
        padding: 0.35rem 0 0 0 !important;
        pointer-events: auto !important;
    }
    div.element-container.st-key-watty_profile_bar > div {
        width: auto !important;
    }
    div.element-container.st-key-watty_profile_bar div.stButton {
        width: auto !important;
    }
    div.element-container.st-key-watty_profile_bar div.stButton > button {
        background-color: #7B1FA2 !important;
        color: #ffffff !important;
        border: 0.125rem solid #6A1B9A !important;
        border-radius: 9999px !important;
        box-shadow: 0 0.125rem 0.75rem rgba(106, 27, 154, 0.35) !important;
        font-family: "Fredoka", "Nunito", "Segoe UI", system-ui, sans-serif !important;
        font-weight: 700 !important;
        font-size: clamp(0.78rem, 1.8vw + 0.2rem, 0.95rem) !important;
        letter-spacing: 0.01em !important;
        min-height: clamp(2.15rem, 5vw, 2.55rem) !important;
        max-width: min(18rem, 100%, 72dvw) !important;
        padding: clamp(0.25rem, 1vw, 0.4rem) clamp(0.45rem, 2vw, 0.7rem) !important;
        gap: 0.35rem !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-transform: none !important;
        box-sizing: border-box !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    div.element-container.st-key-watty_profile_bar div.stButton > button:hover {
        background-color: #8E24AA !important;
        color: #ffffff !important;
        border-color: #7B1FA2 !important;
        box-shadow: 0 0.1875rem 1rem rgba(106, 27, 154, 0.45) !important;
    }
    div.element-container.st-key-watty_profile_bar div.stButton > button:active {
        box-shadow: 0 0.0625rem 0.5rem rgba(106, 27, 154, 0.3) !important;
        transform: translateY(0.0625rem);
    }
    /* Ícone avatar (Material) + texto: branco sobre roxo */
    div.element-container.st-key-watty_profile_bar button span[data-testid="stIconMaterial"] {
        font-size: clamp(1.2rem, 3vw, 1.45rem) !important;
        line-height: 1 !important;
        color: #ffffff !important;
    }
    div.element-container.st-key-watty_profile_bar button span[data-testid="stMarkdownContainer"],
    div.element-container.st-key-watty_profile_bar button p {
        margin: 0 !important;
        padding: 0 !important;
        color: #ffffff !important;
    }

    /* Botões dentro do popover do perfil (mesma paleta) */
    div.element-container.st-key-watty_popover_perfil div.stButton > button,
    div.element-container.st-key-watty_popover_logout div.stButton > button {
        background-color: #7B1FA2 !important;
        color: #ffffff !important;
        border: 0.125rem solid #6A1B9A !important;
        border-radius: clamp(0.625rem, 2vw, 0.875rem) !important;
        font-weight: 800 !important;
        font-size: clamp(0.82rem, 2vw + 0.2rem, 1rem) !important;
        padding: clamp(0.4rem, 1.2vw, 0.55rem) clamp(0.6rem, 2vw, 1rem) !important;
        text-transform: none !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 0.125rem 0 #5a1582 !important;
    }
    div.element-container.st-key-watty_popover_perfil div.stButton > button:hover,
    div.element-container.st-key-watty_popover_logout div.stButton > button:hover {
        background-color: #8E24AA !important;
        color: #ffffff !important;
    }
    div.element-container.st-key-watty_popover_perfil div.stButton > button p,
    div.element-container.st-key-watty_popover_logout div.stButton > button p,
    div.element-container.st-key-watty_popover_perfil div.stButton > button span,
    div.element-container.st-key-watty_popover_logout div.stButton > button span {
        color: #ffffff !important;
    }
    @media (max-width: 768px) {
        div.element-container.st-key-watty_profile_bar {
            right: max(0.75rem, env(safe-area-inset-right, 0rem)) !important;
            inset-inline-end: max(0.75rem, env(safe-area-inset-right, 0rem)) !important;
            max-width: min(18rem, 100%, 92dvw) !important;
        }
        div.element-container.st-key-watty_profile_bar div.stButton > button {
            font-size: clamp(0.72rem, 3.5vw, 0.85rem) !important;
            min-height: clamp(2.1rem, 6vw, 2.4rem) !important;
            padding: clamp(0.22rem, 1.2vw, 0.32rem) clamp(0.4rem, 2vw, 0.55rem) !important;
        }
    }

    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 0.125rem solid #D1C4E9;
        border-radius: 1rem;
        padding: 0.9375rem;
        border-bottom: 0.3125rem solid #FFC107;
        box-shadow: 0 0.25rem 0.625rem rgba(156, 39, 176, 0.1);
        text-align: center;
    }

    div[data-testid="metric-container"] label {
        font-weight: 800;
        color: #7B1FA2 !important;
        font-size: clamp(0.8rem, 0.65rem + 0.6vw, 1rem);
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-weight: 900;
        color: #4A148C !important;
        font-size: clamp(1.35rem, 1rem + 2.5vw, 2.25rem);
    }

    h1, h2, h3 {
        color: #4A148C !important;
        font-weight: 900 !important;
        letter-spacing: -0.02em;
        line-height: 1.08;
    }
    h1 {
        font-size: clamp(1.35rem, 0.55rem + 2.8vw, 2.2rem) !important;
    }
    h2 {
        font-size: clamp(1.22rem, 0.5rem + 2.2vw, 1.9rem) !important;
    }
    h3 {
        font-size: clamp(1.1rem, 0.45rem + 1.6vw, 1.6rem) !important;
    }

    .stTextInput input, .stTextArea textarea {
        border-radius: 1rem;
        border: 0.125rem solid #D1C4E9;
        padding: clamp(0.65rem, 0.5rem + 0.6vw, 0.875rem);
        font-size: clamp(0.95rem, 0.85rem + 0.35vw, 1.0625rem);
        font-weight: 600;
        background-color: #FFFFFF !important;
        color: #4A148C !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #FFC107;
        box-shadow: 0 0 0 0.1875rem rgba(255, 193, 7, 0.3);
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

    /* Vídeos embutidos: proporção 16:9. NÃO aplicar o mesmo a iframe genérico:
       os custom components (login wizard) usam iframe com altura definida por JS;
       height/aspect-ratio com !important quebrava o setFrameHeight e cortava em mobile. */
    video {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        aspect-ratio: 16 / 9;
    }

    iframe {
        width: 100% !important;
        max-width: 100% !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Sidebar em telemóvel: largura total quando aberta (menu hamburger nativo do Streamlit) */
        [data-testid="stSidebar"] {
            max-width: 100% !important;
        }

        /* Área principal: filas de colunas passam a coluna única com scroll natural */
        section[data-testid="stMain"] [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            flex-wrap: wrap !important;
            align-items: stretch !important;
            gap: 0.75rem !important;
            width: 100% !important;
            min-width: 0 !important;
        }
        section[data-testid="stMain"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            width: 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
            flex: 1 1 auto !important;
        }

        section[data-testid="stMain"] .block-container {
            padding-left: max(1rem, env(safe-area-inset-left, 0rem)) !important;
            padding-right: max(1rem, env(safe-area-inset-right, 0rem)) !important;
        }

        section[data-testid="stMain"] div.stButton > button:first-child {
            width: 100%;
            font-size: clamp(0.85rem, 2.5vw, 1.05rem) !important;
            padding: clamp(0.45rem, 1.5vw, 0.55rem) clamp(0.6rem, 2vw, 0.9rem) !important;
        }

        div[data-testid="metric-container"] {
            padding: 0.625rem;
        }

        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            font-size: 1.625rem;
        }

        .stTextInput input, .stTextArea textarea {
            font-size: 1rem;
            padding: 0.75rem;
        }
    }

    /* Desktop: filas flexíveis — ao aumentar zoom, colunas passam para a linha seguinte */
    @media (min-width: 769px) {
        section[data-testid="stMain"] [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: clamp(0.5rem, 1.5vw, 1rem) !important;
            min-width: 0 !important;
        }
        section[data-testid="stMain"] [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex: 1 1 clamp(9rem, 28%, 100%) !important;
            min-width: min(100%, 9rem) !important;
            max-width: 100% !important;
        }
    }

    @media (max-width: 480px) {
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
        border-radius: 0.375rem;
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

    .watty-app-footer {
        margin-top: 2.5rem;
        padding: 1.25rem 0 0.5rem;
        border-top: 0.125rem solid rgba(49, 27, 82, 0.12);
        text-align: center;
    }
    .watty-app-footer__nav {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 0.35rem 0.5rem;
        font-size: 1.02rem;
        font-weight: 600;
        color: #311B52;
    }
    .watty-app-footer__sep {
        color: rgba(49, 27, 82, 0.35);
        user-select: none;
    }
    .watty-app-footer__label {
        color: rgba(49, 27, 82, 0.75);
        margin-right: 0.25rem;
    }
    .watty-app-footer__group {
        display: inline-flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 0.25rem;
    }
    .watty-app-footer .watty-app-footer__link {
        color: #4A148C !important;
        text-decoration: underline;
        text-underline-offset: 0.1875rem;
        font-weight: 700;
    }
    .watty-app-footer .watty-app-footer__link:hover {
        color: #7B1FA2 !important;
    }

    /* Rodapé só no login: links sublinhados, responsivo */
    .watty-login-footer {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: 0.35rem 0.65rem;
        margin-top: 1.75rem;
        padding: 1rem 0.75rem 0.5rem;
        border-top: 0.125rem solid rgba(49, 27, 82, 0.12);
        font-size: clamp(0.88rem, 2.8vw, 1.02rem);
        font-weight: 600;
        color: #311B52;
        text-align: center;
        max-width: 100%;
    }
    .watty-login-footer__link {
        color: #4A148C !important;
        text-decoration: underline;
        text-underline-offset: 0.1875rem;
        font-weight: 700;
        white-space: nowrap;
    }
    .watty-login-footer__link:hover {
        color: #7B1FA2 !important;
    }
    .watty-login-footer__sep {
        color: rgba(49, 27, 82, 0.35);
        user-select: none;
    }
    @media (max-width: 480px) {
        .watty-login-footer {
            flex-direction: column;
            gap: 0.5rem;
        }
        .watty-login-footer__sep {
            display: none;
        }
    }

    </style>
""".replace(
            "__HAMBURGER_BG__", bg
        ),
        unsafe_allow_html=True,
    )
