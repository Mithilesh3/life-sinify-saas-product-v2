import logging

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

from .assets import LOGO, MANDALA
from .fonts import register_fonts
from .layout import PAGE_HEIGHT, PAGE_WIDTH

logger = logging.getLogger(__name__)


class PageDecorator:
    def __init__(self, force_watermark: bool = False):
        self.background = self._reader(MANDALA)
        self.logo = self._reader(LOGO)
        self.force_watermark = force_watermark
        self.regular_font, self.bold_font = register_fonts()

        self.gold = colors.HexColor("#c6a15b")
        self.primary = colors.HexColor("#1b2f4b")

    def _reader(self, path):
        try:
            if path.exists():
                return ImageReader(str(path))
        except Exception as exc:
            logger.warning("Failed loading asset %s: %s", path, exc)
        return None

    def _set_alpha(self, canvas, alpha):
        try:
            canvas.setFillAlpha(alpha)
        except Exception:
            pass

    def draw_background(self, canvas, doc):
        canvas.saveState()
        canvas.setFont(self.regular_font, 12)

        canvas.setFillColor(colors.white)
        canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

        if self.background is not None:
            # Full-page pattern layer so every page has visible sacred geometry.
            self._set_alpha(canvas, 0.16)
            canvas.drawImage(
                self.background,
                0,
                0,
                width=PAGE_WIDTH,
                height=PAGE_HEIGHT,
                preserveAspectRatio=False,
                mask="auto",
            )

            # Soft center emphasis similar to the reference cover treatment.
            size = min(PAGE_WIDTH, PAGE_HEIGHT) * 0.75
            x = (PAGE_WIDTH - size) / 2
            y = (PAGE_HEIGHT - size) / 2
            self._set_alpha(canvas, 0.08)
            canvas.drawImage(
                self.background,
                x,
                y,
                width=size,
                height=size,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto",
            )
            self._set_alpha(canvas, 1)

        if self.force_watermark:
            self._set_alpha(canvas, 0.12)
            canvas.setFillColor(self.primary)
            canvas.setFont(self.bold_font, 52)
            canvas.saveState()
            canvas.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
            canvas.rotate(32)
            canvas.drawCentredString(0, 0, "PREVIEW")
            canvas.restoreState()
            self._set_alpha(canvas, 1)

        canvas.setStrokeColor(self.gold)
        canvas.setLineWidth(2)
        canvas.line(20 * mm, PAGE_HEIGHT - 15 * mm, PAGE_WIDTH - 20 * mm, PAGE_HEIGHT - 15 * mm)

        canvas.setLineWidth(1)
        canvas.line(20 * mm, 15 * mm, PAGE_WIDTH - 20 * mm, 15 * mm)

        canvas.restoreState()

    def draw_header(self, canvas):
        if canvas.getPageNumber() == 1:
            return

        canvas.saveState()

        if self.logo is not None:
            canvas.drawImage(self.logo, 20 * mm, PAGE_HEIGHT - 25 * mm, width=100, height=25, mask="auto")

        canvas.setFont(self.bold_font, 10)
        canvas.setFillColor(self.primary)
        canvas.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 20 * mm, "Life Signify NumAI")

        canvas.restoreState()

    def draw_footer(self, canvas):
        canvas.saveState()

        canvas.setFont(self.regular_font, 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(PAGE_WIDTH - 20 * mm, 10 * mm, f"- {canvas.getPageNumber()} -")

        canvas.setFont(self.regular_font, 8)
        canvas.setFillColor(colors.lightgrey)
        canvas.drawString(20 * mm, 10 * mm, "CONFIDENTIAL - STRATEGIC INTELLIGENCE")

        canvas.restoreState()

    def decorate(self, canvas, doc):
        self.draw_background(canvas, doc)
        self.draw_header(canvas)
        self.draw_footer(canvas)

