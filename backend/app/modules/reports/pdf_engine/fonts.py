import logging
from functools import lru_cache
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .assets import FONTS

logger = logging.getLogger(__name__)

FONT_SOURCES = {
    "NotoSans": {
        "filename": "NotoSans-Regular.ttf",
        "url": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
    },
    "NotoSansBold": {
        "filename": "NotoSans-Bold.ttf",
        "url": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf",
    },
    "NotoSansDeva": {
        "filename": "NotoSansDevanagari-Regular.ttf",
        "url": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf",
    },
    "NotoSansDevaBold": {
        "filename": "NotoSansDevanagari-Bold.ttf",
        "url": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf",
    },
}


def _download_if_missing(font_path: Path, url: str) -> Path:
    FONTS.mkdir(parents=True, exist_ok=True)
    if font_path.exists():
        return font_path

    try:
        with urlopen(url, timeout=20) as response:
            font_path.write_bytes(response.read())
        logger.info("Downloaded report font: %s", font_path.name)
    except (OSError, URLError) as exc:
        logger.warning("Unable to download font %s: %s", font_path.name, exc)

    return font_path


def _register_font(font_name: str, filename: str, url: str) -> bool:
    font_path = _download_if_missing(FONTS / filename, url)
    if not font_path.exists():
        return False

    try:
        pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
        return True
    except Exception as exc:
        logger.warning("Unable to register font %s from %s: %s", font_name, font_path, exc)
        return False


@lru_cache(maxsize=1)
def register_fonts():
    registered = {
        font_name: _register_font(font_name, meta["filename"], meta["url"])
        for font_name, meta in FONT_SOURCES.items()
    }

    regular = "NotoSansDeva" if registered.get("NotoSansDeva") else "NotoSans"
    bold = "NotoSansDevaBold" if registered.get("NotoSansDevaBold") else "NotoSansBold"

    if not registered.get(regular):
        raise RuntimeError("Required report font could not be registered.")
    if not registered.get(bold):
        bold = regular

    try:
        pdfmetrics.registerFontFamily(
            "NotoSansDevaFamily",
            normal=regular,
            bold=bold,
        )
    except Exception:
        logger.debug("Font family already registered or unavailable.", exc_info=True)

    return regular, bold
