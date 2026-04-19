"""Vista Watty TV — grelha responsiva (mobile-first) com vídeo e título por cartão."""

from __future__ import annotations

import html as html_lib
from pathlib import Path
from typing import TypedDict

import streamlit as st
from streamlit import runtime
from streamlit.components import v1 as st_components


class WattyTvCard(TypedDict):
    """Dados de um cartão antes de resolver URLs de media."""

    video: Path
    thumb: Path
    title: str


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _media_url(path: Path, mimetype: str, coord: str) -> str | None:
    if not path.is_file():
        return None
    if not runtime.exists():
        return None
    inst = runtime.get_instance()
    if inst is None:
        return None
    try:
        return inst.media_file_mgr.add(str(path.resolve()), mimetype, coord)
    except OSError:
        return None


def _video_entries() -> list[WattyTvCard]:
    root = _project_root()
    pub = root / "watty_login_wizard" / "frontend" / "public"
    return [
        {
            "video": root / "wattyvid1.mp4",
            "thumb": pub / "watty3.png",
            "title": "Como tirar o máximo do teu tutor Watty",
        },
        {
            "video": root / "wattyvid2.mp4",
            "thumb": pub / "watty4.png",
            "title": "Dicas de revisão antes do teste intermédio",
        },
    ]


def _card_inner_html(
    idx: int,
    video_url: str | None,
    poster_url: str | None,
    title: str,
) -> str:
    title_e = html_lib.escape(title)
    poster_attr = html_lib.escape(poster_url or "", quote=True)
    video_attr = html_lib.escape(video_url or "", quote=True)

    if video_url:
        media_inner = (
            f'<video controls playsinline preload="metadata" poster="{poster_attr}" src="{video_attr}">'
            "</video>"
        )
    else:
        bg = f' style="background:url({poster_attr}) center/cover no-repeat #111;"' if poster_url else ""
        media_inner = (
            f'<div class="media-fallback"{bg}>'
            "<span>Vídeo em falta — coloca o .mp4 na raiz do projeto.</span>"
            "</div>"
        )

    return f"""<article class="card" data-watty-tv-card="{idx}">
  <div class="media">{media_inner}</div>
  <div class="card-foot">
    <p class="card-title">{title_e}</p>
  </div>
</article>"""


def build_watty_tv_grid_html(
    resolved: list[tuple[str | None, str | None, str]],
) -> str:
    """Constroi o documento HTML completo da grelha Watty TV (função pura, testável).

    Cada entrada de ``resolved`` é ``(video_url, poster_url, title)``.
    """
    cards_html = "".join(
        _card_inner_html(i, vu, pu, t) for i, (vu, pu, t) in enumerate(resolved)
    )

    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }}
  .watty-tv-grid {{
    display: grid;
    width: 100%;
    max-width: 920px;
    margin: 0 auto;
    gap: 1.5rem;
    grid-template-columns: 1fr;
    align-items: start;
    padding: 0;
  }}
  @media (min-width: 768px) {{
    .watty-tv-grid {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
  }}
  @media (min-width: 1100px) {{
    .watty-tv-grid {{
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    }}
  }}
  .card {{
    width: 100%;
    margin: 0;
    background: #000;
    border-radius: 14px;
    overflow: hidden;
  }}
  .media {{
    position: relative;
    width: 100%;
    aspect-ratio: 9 / 16;
    background: #0a0a0a;
  }}
  .media video {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    border: 0;
    border-radius: 0;
  }}
  .media-fallback {{
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #e6e0f5;
    font-size: 13px;
    font-weight: 700;
    text-align: center;
    padding: 12px;
  }}
  .card-foot {{
    background: #000;
    padding: 8px 10px 10px;
  }}
  .card-title {{
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    line-height: 1.25;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
</style>
</head>
<body>
  <div class="watty-tv-grid">
    {cards_html}
  </div>
</body>
</html>
"""


def render_watty_tv() -> None:
    """Grelha com vídeos Watty TV (um iframe HTML, grelha responsiva)."""
    st.markdown(
        """
<style>
.watty-tv-page-title {
  font-family: "Fredoka", "Nunito", "Segoe UI", system-ui, sans-serif;
  color: #311B52;
  font-weight: 900;
  font-size: clamp(1.35rem, 0.55rem + 2.5vw, 2rem);
  margin: 0 0 0.25rem 0;
}
.watty-tv-sub {
  color: #5c4a7a;
  font-size: 1.02rem;
  margin: 0 0 1.25rem 0;
}
</style>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="watty-tv-page-title">Watty TV</p>'
        '<p class="watty-tv-sub">Vídeos escolhidos para te acompanhar nos estudos.</p>',
        unsafe_allow_html=True,
    )

    entries = _video_entries()
    resolved: list[tuple[str | None, str | None, str]] = []
    for idx, item in enumerate(entries):
        base = f"watty_tv:{idx}"
        video_url = _media_url(item["video"], "video/mp4", f"{base}:video")
        poster_url = _media_url(item["thumb"], "image/png", f"{base}:poster")
        resolved.append((video_url, poster_url, item["title"]))

    grid_html = build_watty_tv_grid_html(resolved)
    st_components.html(grid_html, height=900, scrolling=True)
