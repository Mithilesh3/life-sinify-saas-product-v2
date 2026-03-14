import re

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, Table, TableStyle

from .layout import LEFT_MARGIN, PAGE_WIDTH, RIGHT_MARGIN


class Renderer:
    def __init__(self, styles):
        self.styles = styles

        self.body_style = styles["BodyText"]
        self.section_style = styles.get("SectionBanner", styles["Heading2"])

        self.primary = HexColor("#1b2f4b")
        self.accent = HexColor("#c6a15b")
        self.neutral = HexColor("#f5f7fa")

        self.full_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
        self.two_col_widths = self.proportional_widths(1, 1)
        self.three_col_widths = self.proportional_widths(1, 1, 1)
        self.two_col_width = self.two_col_widths[0]
        self.two_col_inner_width = self.two_col_width - 8

        self.metric_label_style = ParagraphStyle(
            "MetricLabel",
            parent=self.body_style,
            alignment=1,
            fontSize=8.5,
            leading=11,
            textColor=HexColor("#4a5568"),
        )
        self.metric_value_style = ParagraphStyle(
            "MetricValue",
            parent=styles["Heading1"],
            alignment=1,
            fontSize=26,
            leading=30,
            textColor=self.primary,
        )
        self.center_body_style = ParagraphStyle(
            "CenterBody",
            parent=self.body_style,
            alignment=1,
        )

    def normalize_text(self, text):
        if text is None:
            return ""
        normalized = " ".join(str(text).split())
        return re.sub(r"([a-z])([A-Z])", r"\1 \2", normalized)

    def proportional_widths(self, *weights, total=None):
        total_width = total or self.full_width
        resolved = list(weights) or [1]
        total_weight = sum(resolved) or len(resolved)
        return [total_width * (weight / total_weight) for weight in resolved]

    def section_banner(self, title):
        banner = Table(
            [[Paragraph(title, self.section_style)]],
            colWidths=[self.full_width],
        )

        banner.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), self.primary),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                    ("LEFTPADDING", (0, 0), (-1, -1), 14),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        banner.spaceAfter = 12
        return banner

    def paragraph(self, text):
        return Paragraph(self.normalize_text(text), self.body_style)

    def metric_card(self, label, value):
        score = 0
        try:
            score = int(value)
        except Exception:
            score = 0

        if score >= 75:
            color = HexColor("#e8f5ec")
        elif score >= 50:
            color = HexColor("#fff9e8")
        else:
            color = HexColor("#fdecec")

        table = Table(
            [
                [Paragraph(f"<b>{self.normalize_text(label)}</b>", self.metric_label_style)],
                [Paragraph(str(value), self.metric_value_style)],
            ],
            colWidths=[self.three_col_widths[0] - 6],
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), color),
                    ("BOX", (0, 0), (-1, -1), 1, HexColor("#d5dbe3")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )

        return table

    def metric_grid(self, metric_pairs):
        cards = [self.metric_card(label, value) for label, value in metric_pairs[:6]]
        while len(cards) < 6:
            cards.append(self.metric_card("N/A", "-"))

        rows = [cards[:3], cards[3:6]]

        grid = Table(rows, colWidths=self.three_col_widths)
        grid.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        return grid

    def insight_box(self, title, text, tone="neutral", width=None):
        palette = {
            "neutral": (HexColor("#f5f7fa"), HexColor("#d9e0e8")),
            "info": (HexColor("#edf5ff"), HexColor("#c6daf9")),
            "success": (HexColor("#eaf8ef"), HexColor("#c8e7d3")),
            "risk": (HexColor("#fff0f0"), HexColor("#f5cccc")),
        }
        bg, border = palette.get(tone, palette["neutral"])
        box_width = width or self.full_width

        box = Table(
            [
                [Paragraph(f"<b>{self.normalize_text(title)}</b>", self.styles["Heading4"])],
                [Paragraph(self.normalize_text(text) or "No insight available.", self.body_style)],
            ],
            colWidths=[box_width],
        )
        box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), bg),
                    ("BOX", (0, 0), (-1, -1), 1, border),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        return box

    def bullet_block(self, title, items):
        clean_items = [self.normalize_text(i) for i in (items or []) if str(i).strip()]
        if not clean_items:
            clean_items = ["No data available."]

        bullet_text = "<br/>".join([f"- {i}" for i in clean_items])
        return self.insight_box(title, bullet_text, tone="neutral")

    def icon_block(self, icon_path, title, text):
        if icon_path and getattr(icon_path, "exists", lambda: False)():
            img = Image(str(icon_path), width=26 * mm, height=26 * mm)
            img.hAlign = "CENTER"
            left = img
        else:
            return self.insight_box(title, text, tone="info")

        icon_width = min(70, self.full_width * 0.16)
        right = self.insight_box(title, text, tone="info", width=self.full_width - icon_width)

        block = Table([[left, right]], colWidths=[icon_width, self.full_width - icon_width])
        block.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return block

    def two_column_cards(self, left_title, left_text, right_title, right_text):
        left = self.insight_box(left_title, left_text, tone="success", width=self.two_col_inner_width)
        right = self.insight_box(right_title, right_text, tone="risk", width=self.two_col_inner_width)

        table = Table([[left, right]], colWidths=self.two_col_widths)
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        return table
