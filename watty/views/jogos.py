"""Biblioteca de jogos HTML estáticos: grelha de cartões e player embutido."""

from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import unquote

import streamlit as st
import streamlit.components.v1 as components

ALLOWED_GAME_FILES: frozenset[str] = frozenset(
    {
        "jogo ADM8 modulo 7.html",
        "jogo ADM9.html",
        "jogo.html",
        "jogo_conserta_o_tempo.html",
        "jogo_fa_nr_1.html",
        "jogo_facto_fake.html",
        "jogo_filosofia.html",
        "jogo_geografia.html",
        "jogo_macs_1.html",
        "mercado_jogo (1).html",
    }
)

# Ordem fixa da grelha; títulos alinhados aos <title> dos HTML.
_GAMES_ROWS: list[dict[str, str]] = [
    {
        "filename": "jogo ADM8 modulo 7.html",
        "title": "Economia Módulo 7: O Grande Governo (Simulador)",
        "cover": "linear-gradient(135deg,#1e3a5f 0%,#f1c40f 55%,#2c3e50 100%)",
    },
    {
        "filename": "jogo ADM9.html",
        "title": "Módulo 2: O Lobo de Wall Street (Mecanismos de Mercado)",
        "cover": "linear-gradient(135deg,#0f2027 0%,#f1c40f 50%,#203a43 100%)",
    },
    {
        "filename": "jogo.html",
        "title": "EcoGov: Global Edition - Masterclass Economia",
        "cover": "linear-gradient(135deg,#0f172a 0%,#3b82f6 45%,#1e293b 100%)",
    },
    {
        "filename": "jogo_conserta_o_tempo.html",
        "title": "WATTY - Conserta o Tempo (Definitivo)",
        "cover": "linear-gradient(135deg,#9B5DE5 0%,#F15BB5 60%,#6D3AB5 100%)",
    },
    {
        "filename": "jogo_fa_nr_1.html",
        "title": "WATTY - Fã Nº 1",
        "cover": "linear-gradient(135deg,#0D0814 0%,#9B5DE5 50%,#26183A 100%)",
    },
    {
        "filename": "jogo_facto_fake.html",
        "title": "WATTY - Facto ou Fake? (Mega Base de Dados)",
        "cover": "linear-gradient(135deg,#F3EEFF 0%,#9B5DE5 40%,#6D3AB5 100%)",
    },
    {
        "filename": "jogo_filosofia.html",
        "title": "WATTY - Feed das Falácias",
        "cover": "linear-gradient(135deg,#1A1025 0%,#E63946 45%,#9B5DE5 100%)",
    },
    {
        "filename": "jogo_geografia.html",
        "title": "WATTY - Geo-Alvo (Modo Exame)",
        "cover": "linear-gradient(135deg,#0D0814 0%,#22c55e 40%,#9B5DE5 100%)",
    },
    {
        "filename": "jogo_macs_1.html",
        "title": "Afinador de Quotas - O Desafio dos 100 Níveis",
        "cover": "linear-gradient(135deg,#F3EEFF 0%,#F15BB5 50%,#9B5DE5 100%)",
    },
    {
        "filename": "mercado_jogo (1).html",
        "title": "Watty | Ministro da Economia",
        "cover": "linear-gradient(135deg,#0a0a12 0%,#a78bfa 45%,#f43f5e 100%)",
    },
]


def games_dir() -> Path:
    """Pasta ``watty/static/jogos`` com os ficheiros ``.html``."""
    return Path(__file__).resolve().parent.parent / "static" / "jogos"


def _repo_relative_game_path(filename: str) -> str:
    """Caminho legível tipo ``watty/static/jogos/nome.html``."""
    try:
        root = Path(__file__).resolve().parents[2]
        rel = (games_dir() / filename).resolve().relative_to(root)
        return rel.as_posix()
    except ValueError:
        return f"watty/static/jogos/{filename}"


def _query_param_first(key: str) -> str | None:
    qp = st.query_params
    if key not in qp:
        return None
    raw = qp[key]
    v = raw[0] if isinstance(raw, (list, tuple)) else raw
    s = str(v or "").strip()
    return s or None


def get_active_game_filename() -> str | None:
    """Nome do ficheiro do jogo activo via ``?watty_game=`` se existir e for permitido."""
    raw = _query_param_first("watty_game")
    if raw is None:
        return None
    name = unquote(raw)
    if name not in ALLOWED_GAME_FILES:
        return None
    path = games_dir() / name
    if not path.is_file():
        return None
    return name


def _short_title(title: str, max_len: int = 52) -> str:
    t = title.strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def _inject_game_library_button_styles() -> None:
    """Estiliza botões-cartão (Streamlit não deixa ``<a>`` em markdown funcionar de forma fiável)."""
    st.markdown(
        """
<style>
section[data-testid="stMain"] div.element-container[class*="st-key-watty_game_card_"] button {
  background: #2a2a2e !important;
  color: #ffffff !important;
  border: 0.0625rem solid rgba(255,255,255,0.08) !important;
  border-radius: 0.95rem !important;
  min-height: 10.25rem !important;
  padding: 0.75rem 0.85rem !important;
  box-shadow: 0 0.35rem 1rem rgba(0,0,0,0.18) !important;
  font-family: "Fredoka", "Nunito", "Segoe UI", system-ui, sans-serif !important;
  font-weight: 800 !important;
  font-size: 0.95rem !important;
  line-height: 1.25 !important;
  letter-spacing: 0.01em !important;
  text-align: left !important;
  white-space: normal !important;
  justify-content: flex-start !important;
  align-items: flex-start !important;
  text-transform: none !important;
}
section[data-testid="stMain"] div.element-container[class*="st-key-watty_game_card_"] button:hover {
  background: #35353a !important;
  color: #ffffff !important;
  border-color: rgba(156, 39, 176, 0.45) !important;
}
section[data-testid="stMain"] div.element-container[class*="st-key-watty_game_card_"] button p {
  color: #ffffff !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_jogos_library() -> None:
    """Grelha de cartões: cada cartão é um ``st.button`` que abre o HTML de ``watty/static/jogos/`` na app."""
    st.markdown(
        """
<div class="watty-game-lib-head">
  <h1 class="watty-game-lib-h1">O que vamos jogar?</h1>
</div>
<style>
.watty-game-lib-head { margin-bottom: 1.1rem; }
.watty-game-lib-h1 {
  color: #311B52;
  font-weight: 900;
  font-size: clamp(1.35rem, 0.55rem + 2.8vw, 2.1rem);
  margin: 0;
  line-height: 1.15;
  font-family: "Fredoka", "Nunito", "Segoe UI", system-ui, sans-serif;
}
</style>
""",
        unsafe_allow_html=True,
    )
    _inject_game_library_button_styles()

    n_cols = 3
    for i in range(0, len(_GAMES_ROWS), n_cols):
        cols = st.columns(n_cols, gap="medium")
        for j in range(n_cols):
            idx = i + j
            if idx >= len(_GAMES_ROWS):
                break
            row = _GAMES_ROWS[idx]
            fn = row["filename"]
            title = row["title"]
            cover = row["cover"].replace('"', "'")
            label = f"🎮 {_short_title(title, 46)}"
            with cols[j]:
                st.markdown(
                    f'<div class="watty-gl-cover" style="height:5.25rem;border-radius:0.85rem;margin-bottom:0.5rem;background:{cover};"></div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    label,
                    key=f"watty_game_card_{idx}",
                    help=f"{title}\n({_repo_relative_game_path(fn)})",
                    use_container_width=True,
                ):
                    st.query_params["watty_game"] = fn
                    st.session_state.watty_main_section = "jogos"
                    st.rerun()


def render_jogos_player(filename: str) -> None:
    """Lê o HTML do disco e embute com ``components.html``; botão para fechar o jogo."""
    if filename not in ALLOWED_GAME_FILES:
        st.error("Jogo não permitido.")
        return
    path = games_dir() / filename
    if not path.is_file():
        st.error(f"Ficheiro em falta: `{html.escape(filename)}`. Coloca o HTML em `watty/static/jogos/`.")
        return

    if st.button("← Voltar à biblioteca", key="watty_jogos_voltar", type="primary"):
        try:
            del st.query_params["watty_game"]
        except Exception:
            pass
        st.session_state.watty_main_section = "jogos"
        st.rerun()

    title_disp = next((r["title"] for r in _GAMES_ROWS if r["filename"] == filename), filename)
    st.caption(title_disp)

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        st.error(f"Não foi possível ler o jogo: {e}")
        return

    components.html(content, height=1050, scrolling=True)
