"""Ecrã de perfil do utilizador autenticado (layout inspirado em apps de gamificação)."""

from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime

import streamlit as st


_MONTHS_PT = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)


def _parse_created_at(raw: str | None) -> datetime | None:
    if not raw:
        return None
    s = str(raw).strip()
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _join_line_pt(created_at: str | None) -> str:
    dt = _parse_created_at(created_at)
    if dt is None:
        return "Bem-vindo ao Watty."
    m = _MONTHS_PT[max(0, min(dt.month - 1, 11))]
    return f"Por aqui desde {m} de {dt.year}"


def _pseudo_username(email: str) -> str:
    local = (email or "").split("@", 1)[0] if "@" in (email or "") else (email or "aluno")
    tail = hashlib.sha256((email or "").encode()).hexdigest()[:6]
    base = re.sub(r"[^a-zA-Z0-9]", "", local) or "Aluno"
    return f"{base}{tail}"


def _initials(nome: str) -> str:
    parts = [p for p in (nome or "").strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return (parts[0][0] if parts[0] else "?").upper()
    return (parts[0][0] + parts[-1][0]).upper()[:2]


def _stat_icon(kind: str) -> str:
    """Marcador visual à esquerda de cada cartão (emoji + estilo)."""
    sym = {"flame": "🔥", "bolt": "⚡", "shield": "🛡️", "medal": "🏅"}.get(kind, "📊")
    e = html.escape(sym, quote=True)
    return f'<span class="wp-stat-ico" aria-hidden="true">{e}</span>'


def render_perfil_view() -> None:
    nome = str(st.session_state.get("nome_display") or "").strip()
    email = str(st.session_state.get("nome_aluno") or "").strip()
    xp = int(st.session_state.get("xp", 0) or 0)
    nivel = int(st.session_state.get("nivel", 1) or 1)
    streak = int(st.session_state.get("streak", 0) or 0)
    created_at = st.session_state.get("user_created_at")

    nome_h = html.escape(nome or "—")
    user_h = html.escape(_pseudo_username(email))
    join_h = html.escape(_join_line_pt(created_at if isinstance(created_at, str) else None))
    initials_h = html.escape(_initials(nome or email))

    streak_s = html.escape(str(streak))
    xp_s = html.escape(str(xp))
    nivel_s = html.escape(str(nivel))

    st.markdown(
        f"""
<style>
.watty-perfil-page {{
    width: 100%;
    max-width: min(28rem, calc(100dvw - 2.5rem));
    margin: 0 auto clamp(1.25rem, 4vw, 2rem);
    padding-inline: clamp(0.25rem, 2vw, 0.5rem);
    box-sizing: border-box;
    font-family: "Fredoka", "Nunito", "Segoe UI", system-ui, sans-serif;
    color: #e8eef2;
    font-size: clamp(0.9rem, 2.2vw + 0.35rem, 1rem);
}}
.watty-perfil-page .wp-banner {{
    position: relative;
    background: #2b60ab;
    border-radius: clamp(0.875rem, 3.5vw, 1.125rem);
    min-height: clamp(7.5rem, 28vw, 9.75rem);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: clamp(0.75rem, 2.5vw, 1.1rem);
    box-shadow: 0 0.25rem 1rem rgba(0,0,0,0.15);
}}
.watty-perfil-page .wp-edit {{
    position: absolute;
    top: clamp(0.45rem, 2vw, 0.65rem);
    right: clamp(0.45rem, 2vw, 0.65rem);
    width: clamp(2rem, 7vw, 2.35rem);
    height: clamp(2rem, 7vw, 2.35rem);
    border-radius: 50%;
    border: 0.125rem solid #6A1B9A;
    background: #7B1FA2;
    color: #fff;
    font-size: clamp(0.85rem, 2.5vw, 1rem);
    line-height: 1;
    cursor: default;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0.125rem 0.5rem rgba(0,0,0,0.2);
}}
.watty-perfil-page .wp-avatar {{
    width: clamp(4.25rem, 22vw, 5.75rem);
    height: clamp(4.25rem, 22vw, 5.75rem);
    border-radius: clamp(0.65rem, 2vw, 1rem);
    background: linear-gradient(145deg, #f0d9b5 0%, #c9a86c 45%, #8b6914 100%);
    color: #3d2914;
    font-weight: 700;
    font-size: clamp(1.15rem, 5vw, 1.7rem);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0.375rem 1.25rem rgba(0,0,0,0.25);
    border: clamp(0.125rem, 0.5vw, 0.1875rem) solid rgba(255,255,255,0.35);
}}
.watty-perfil-page .wp-head {{
    padding: 0 clamp(0.05rem, 1vw, 0.15rem) clamp(0.55rem, 2vw, 0.85rem);
    border-bottom: 0.0625rem solid #2d3d47;
    margin-bottom: clamp(0.85rem, 2.5vw, 1.15rem);
}}
.watty-perfil-page .wp-name {{
    font-size: clamp(1.12rem, 4.2vw + 0.2rem, 1.48rem);
    font-weight: 700;
    color: #fff;
    margin: 0 0 0.15rem;
    letter-spacing: 0.01em;
    line-height: 1.15;
    word-break: break-word;
}}
.watty-perfil-page .wp-user {{
    font-size: clamp(0.78rem, 2.2vw + 0.2rem, 0.92rem);
    color: #8fa3ad;
    margin: 0 0 clamp(0.35rem, 1.5vw, 0.5rem);
    word-break: break-all;
}}
.watty-perfil-page .wp-join {{
    font-size: clamp(0.82rem, 2.3vw + 0.2rem, 0.98rem);
    color: #e8eef2;
    margin: 0 0 clamp(0.45rem, 1.8vw, 0.65rem);
    line-height: 1.35;
}}
.watty-perfil-page .wp-social-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: clamp(0.4rem, 2vw, 0.75rem);
    flex-wrap: wrap;
}}
.watty-perfil-page .wp-social {{
    font-size: clamp(0.75rem, 2vw + 0.15rem, 0.9rem);
    font-weight: 600;
    color: #49c0f8;
    margin: 0;
    flex: 1 1 auto;
    min-width: 0;
}}
.watty-perfil-page .wp-flag {{
    font-size: clamp(1.1rem, 4vw, 1.4rem);
    line-height: 1;
    flex-shrink: 0;
}}
.watty-perfil-page .wp-section-title {{
    font-size: clamp(0.95rem, 2.8vw + 0.2rem, 1.08rem);
    font-weight: 700;
    color: #fff;
    margin: 0 0 clamp(0.55rem, 2vw, 0.85rem);
}}
.watty-perfil-page .wp-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 10.5rem), 1fr));
    gap: clamp(0.45rem, 2vw, 0.75rem);
}}
.watty-perfil-page .wp-card {{
    background-color: #B19CD9;
    border: 0.0625rem solid rgba(255, 255, 255, 0.35);
    border-radius: clamp(0.6875rem, 2.5vw, 0.875rem);
    padding: clamp(0.55rem, 2vw, 0.85rem) clamp(0.6rem, 2.2vw, 0.9rem);
    display: flex;
    align-items: center;
    gap: clamp(0.45rem, 2vw, 0.7rem);
    min-height: clamp(3.65rem, 18vw, 4.35rem);
}}
.watty-perfil-page .wp-stat-ico {{
    width: clamp(1.45rem, 6vw, 1.85rem);
    height: clamp(1.45rem, 6vw, 1.85rem);
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: clamp(1.05rem, 4.5vw, 1.38rem);
    line-height: 1;
    color: #FFFFFF;
    /* Emoji: aproximação a branco (não são SVG; fill não aplica) */
    filter: brightness(0) invert(1);
}}
.watty-perfil-page .wp-stat-val {{
    font-size: clamp(1rem, 3.5vw + 0.2rem, 1.25rem);
    font-weight: 700;
    color: #FFFFFF;
    margin: 0;
    line-height: 1.15;
}}
.watty-perfil-page .wp-stat-lbl {{
    font-size: clamp(0.65rem, 1.8vw + 0.1rem, 0.76rem);
    color: #FFFFFF;
    margin: 0.1rem 0 0;
    line-height: 1.2;
}}
.watty-perfil-page .wp-foot {{
    margin-top: clamp(0.9rem, 3vw, 1.35rem);
    font-size: clamp(0.68rem, 1.8vw + 0.1rem, 0.8rem);
    color: #6b7c88;
    text-align: center;
    line-height: 1.35;
    padding-inline: clamp(0.15rem, 1.5vw, 0.5rem);
}}
</style>
<div class="watty-perfil-page">
  <div class="wp-banner">
    <span class="wp-edit" title="Em breve">✎</span>
    <div class="wp-avatar" aria-hidden="true">{initials_h}</div>
  </div>
  <div class="wp-head">
    <p class="wp-name">{nome_h}</p>
    <p class="wp-user">{user_h}</p>
    <p class="wp-join">{join_h}</p>
    <div class="wp-social-row">
      <p class="wp-social">Segue 0 · Tem 0 seguidores</p>
      <span class="wp-flag" title="Português">🇵🇹</span>
    </div>
  </div>
  <p class="wp-section-title">Estatísticas</p>
  <div class="wp-grid">
    <div class="wp-card">
      {_stat_icon("flame")}
      <div>
        <p class="wp-stat-val">{streak_s}</p>
        <p class="wp-stat-lbl">Dias seguidos</p>
      </div>
    </div>
    <div class="wp-card">
      {_stat_icon("bolt")}
      <div>
        <p class="wp-stat-val">{xp_s}</p>
        <p class="wp-stat-lbl">Total de XP</p>
      </div>
    </div>
    <div class="wp-card">
      {_stat_icon("shield")}
      <div>
        <p class="wp-stat-val">{nivel_s}</p>
        <p class="wp-stat-lbl">Nível atual</p>
      </div>
    </div>
    <div class="wp-card">
      {_stat_icon("medal")}
      <div>
        <p class="wp-stat-val">0</p>
        <p class="wp-stat-lbl">Pódios</p>
      </div>
    </div>
  </div>
  <p class="wp-foot">O progresso é sincronizado com a folha na nuvem (Google Sheets).</p>
</div>
""",
        unsafe_allow_html=True,
    )
