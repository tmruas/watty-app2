"""Caminhos do projeto (independentes do cwd)."""
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent

# Padding horizontal total (px) somado à largura intrínseca do logo para a sidebar.
WATTY_SIDEBAR_LOGO_PADDING_H = 32
ASSETS_DIR = PROJECT_ROOT / "assets"
ASSETS_IMAGES = ASSETS_DIR / "images"


def hamburger_png_path() -> Path:
    return ASSETS_IMAGES / "hamburger_menu.png"


LOGO_SUPERIOR_NAMES = (
    "watty_logosuperior.jpeg",
    "watty_logosuperior.jpg",
    "watty_logosuperior.png",
)


def watty_logosuperior_path() -> Path:
    """Logo da sidebar: primeiro ficheiro existente na raiz do projeto (jpeg/jpg/png)."""
    for name in LOGO_SUPERIOR_NAMES:
        p = PROJECT_ROOT / name
        if p.is_file():
            return p
    return PROJECT_ROOT / LOGO_SUPERIOR_NAMES[0]


def read_png_dimensions(path: Path) -> tuple[int, int] | None:
    """Lê (largura, altura) do chunk IHDR de um PNG."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    if data[12:16] != b"IHDR":
        return None
    w = int.from_bytes(data[16:20], "big")
    h = int.from_bytes(data[20:24], "big")
    if w > 0 and h > 0:
        return (w, h)
    return None


def read_jpeg_dimensions(path: Path) -> tuple[int, int] | None:
    """Lê (largura, altura) a partir de um segmento SOF do JPEG, sem dependências externas."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None
    i = 2
    n = len(data)
    while i < n - 1:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        i += 2
        if marker in (0xD8,):  # SOI
            continue
        if marker == 0xD9:  # EOI
            break
        if marker == 0xDA:  # SOS — dimensões já lidas ou formato incomum
            break
        if i + 2 > n:
            break
        seg_len = (data[i] << 8) | data[i + 1]
        i += 2
        if seg_len < 2 or i + seg_len - 2 > n:
            break
        payload = data[i : i + seg_len - 2]
        i += seg_len - 2
        if marker in (
            0xC0,
            0xC1,
            0xC2,
            0xC3,
            0xC5,
            0xC6,
            0xC7,
            0xC9,
            0xCA,
            0xCB,
            0xCD,
            0xCE,
            0xCF,
        ):
            if len(payload) < 5:
                continue
            h = (payload[1] << 8) | payload[2]
            w = (payload[3] << 8) | payload[4]
            if w > 0 and h > 0:
                return (w, h)
    return None


def read_raster_dimensions(path: Path) -> tuple[int, int] | None:
    """Dimensões intrínsecas de JPEG ou PNG."""
    suf = path.suffix.lower()
    if suf in (".jpg", ".jpeg"):
        return read_jpeg_dimensions(path)
    if suf == ".png":
        return read_png_dimensions(path)
    return None


def watty_sidebar_width_px(logo_path: Path) -> int:
    """Largura da sidebar em px: largura da imagem + padding; limitado a intervalo razoável."""
    dims = read_raster_dimensions(logo_path)
    w = dims[0] if dims else 240
    total = w + WATTY_SIDEBAR_LOGO_PADDING_H
    return max(200, min(520, total))
