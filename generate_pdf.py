"""
Professional PDF Generator for SSC STUDY PREP HUB
- Embeds Logo & Exam Branding
- Styled with Dark Slate & Gold theme
- Full-page invisible hyperlink redirecting clicks to YouTube channel
- Social media links (Telegram & YouTube)
- Multi-category Current Affairs (India, States, World, Economy, Sports, Sci-Tech, MCQs)
"""

import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

YOUTUBE_URL = "https://www.youtube.com/@sscstudyprephub"
TELEGRAM_URL = "https://t.me/sscstudyprephub"

CATEGORY_CONFIG = [
    ("national", "🇮🇳 NATIONAL & GOVERNANCE NEWS", "#1E3A8A"),
    ("states_schemes", "🏛️ STATES NEWS & WELFARE SCHEMES", "#047857"),
    ("international", "🌐 INTERNATIONAL & GLOBAL AFFAIRS", "#4338CA"),
    ("economy", "💰 ECONOMY, BANKING & COMMERCE", "#B45309"),
    ("science_defence", "🚀 SCIENCE, DEFENCE & TECHNOLOGY", "#0E7490"),
    ("sports", "🏆 SPORTS & TOURNAMENTS", "#BE123C"),
    ("appointments_awards", "👤 APPOINTMENTS, RESIGNATIONS & AWARDS", "#7C3AED"),
]

def add_decorations_and_links(c, doc):
    w, h = A4
    
    # 1. Full-page invisible clickable hyperlink to YouTube
    c.linkURL(YOUTUBE_URL, (0, 0, w, h), relative=0, thickness=0)

    # 2. Running header for page 2 and onwards
    if doc.page > 1:
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#374151"))
        c.drawString(36, h - 25, "SSC STUDY PREP HUB  |  Daily Current Affairs Capsule")

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#D97706"))
        c.drawRightString(w - 36, h - 25, "YouTube: @sscstudyprephub")

        c.setStrokeColor(colors.HexColor("#E5E7EB"))
        c.setLineWidth(0.6)
        c.line(36, h - 28, w - 36, h - 28)

    # 3. Running footer line
    c.setStrokeColor(colors.HexColor("#E5E7EB"))
    c.setLineWidth(0.6)
    c.line(36, 30, w - 36, 30)

    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(colors.HexColor("#D97706"))
    c.drawString(36, 18, "👉 TAP ANYWHERE ON THIS PAGE TO SUBSCRIBE: youtube.com/@sscstudyprephub")

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and write 'Page X of Y'.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        w, h = A4
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#6B7280"))
            self.drawRightString(w - 36, 18, f"Page {self._pageNumber} of {num_pages}")
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

def generate_pdf(current_affairs_data, output_pdf_path, logo_image_path):
    w, h = A4
    margin = 36
    usable_width = w - (margin * 2)

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#111827"),
        alignment=TA_LEFT
    )

    subtitle_style = ParagraphStyle(
        "HeaderSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#D97706"),
        alignment=TA_LEFT
    )

    date_style = ParagraphStyle(
        "HeaderDate",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#4B5563"),
        alignment=TA_LEFT
    )

    social_badge_style = ParagraphStyle(
        "SocialBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    section_banner_style = ParagraphStyle(
        "SectionBanner",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.white,
        alignment=TA_LEFT
    )

    news_title_style = ParagraphStyle(
        "NewsTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#0F172A"),
        alignment=TA_LEFT
    )

    news_bullet_style = ParagraphStyle(
        "NewsBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155"),
        alignment=TA_JUSTIFY
    )

    exam_pointer_style = ParagraphStyle(
        "ExamPointer",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#92400E"),
        alignment=TA_LEFT
    )

    quiz_question_style = ParagraphStyle(
        "QuizQuestion",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1E293B")
    )

    quiz_option_style = ParagraphStyle(
        "QuizOption",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#475569")
    )

    quiz_answer_style = ParagraphStyle(
        "QuizAnswer",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#047857")
    )

    story = []

    # ==================== BRAND HEADER ====================
    date_str = current_affairs_data.get("date_str", datetime.datetime.now().strftime("%A, %d %B %Y"))

    logo_flowable = None
    if os.path.exists(logo_image_path):
        logo_flowable = RLImage(logo_image_path, width=60, height=60)

    text_header_col = [
        Paragraph("SSC STUDY PREP HUB", title_style),
        Paragraph("DAILY CURRENT AFFAIRS CAPSULE", subtitle_style),
        Paragraph(f"📅 <b>{date_str}</b> | Target: SSC CGL, CHSL, MTS, CPO, CDS, NDA & Banking", date_style),
    ]

    header_data = [
        [logo_flowable if logo_flowable else "", text_header_col]
    ]
    header_table = Table(header_data, colWidths=[68, usable_width - 68])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # Socials Callout Ribbon
    social_data = [
        [
            Paragraph("✈️ <b>TELEGRAM:</b> @sscstudyprephub", social_badge_style),
            Paragraph("▶️ <b>YOUTUBE:</b> @sscstudyprephub (Tap Page to Subscribe)", social_badge_style)
        ]
    ]
    social_table = Table(social_data, colWidths=[usable_width * 0.45, usable_width * 0.55])
    social_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#0284C7")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#DC2626")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(social_table)
    story.append(Spacer(1, 10))

    # ==================== CATEGORIES ====================
    for cat_key, cat_title, cat_color in CATEGORY_CONFIG:
        items = current_affairs_data.get(cat_key, [])
        if not items:
            continue

        sec_banner = Table(
            [[Paragraph(f"<b>{cat_title}</b>", section_banner_style)]],
            colWidths=[usable_width]
        )
        sec_banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(cat_color)),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))
        story.append(sec_banner)
        story.append(Spacer(1, 5))

        for idx, it in enumerate(items, 1):
            title = it.get("title", "")
            points = it.get("points", [])
            exam_pointer = it.get("exam_pointer", "")

            item_flowables = []
            item_flowables.append(Paragraph(f"<b>{idx}. {title}</b>", news_title_style))
            item_flowables.append(Spacer(1, 2.5))

            for pt in points:
                item_flowables.append(Paragraph(f"• {pt}", news_bullet_style))
                item_flowables.append(Spacer(1, 1.5))

            if exam_pointer:
                callout_data = [[Paragraph(f"<b>📌 Exam Pointer / Static GK:</b> {exam_pointer}", exam_pointer_style)]]
                callout_tbl = Table(callout_data, colWidths=[usable_width - 8])
                callout_tbl.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LINELEFT", (0, 0), (-1, -1), 2, colors.HexColor("#D97706")),
                ]))
                item_flowables.append(Spacer(1, 2))
                item_flowables.append(callout_tbl)

            item_flowables.append(Spacer(1, 6))
            story.append(KeepTogether(item_flowables))

        story.append(Spacer(1, 3))

    # ==================== DAILY EXAM BOOSTER QUIZ ====================
    quiz_items = current_affairs_data.get("daily_quiz", [])
    if quiz_items:
        quiz_banner = Table(
            [[Paragraph("<b>🎯 DAILY EXAM BOOSTER - PRACTICE MCQS</b>", section_banner_style)]],
            colWidths=[usable_width]
        )
        quiz_banner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(quiz_banner)
        story.append(Spacer(1, 5))

        for q_idx, q in enumerate(quiz_items, 1):
            q_flowables = []
            q_flowables.append(Paragraph(f"<b>Q{q_idx}. {q.get('question')}</b>", quiz_question_style))
            q_flowables.append(Spacer(1, 2))
            
            for opt in q.get("options", []):
                q_flowables.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{opt}", quiz_option_style))
            
            ans = q.get("answer", "")
            if ans:
                q_flowables.append(Spacer(1, 1.5))
                q_flowables.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Key:</b> {ans}", quiz_answer_style))
            
            q_flowables.append(Spacer(1, 5))
            story.append(KeepTogether(q_flowables))

    # ==================== BOTTOM WATERMARK PROMO ====================
    promo_box = Table(
        [[
            Paragraph(
                "📢 <b>SUBSCRIBE FOR DAILY REVISION:</b> YouTube: <b>@sscstudyprephub</b> | "
                "Telegram: <b>@sscstudyprephub</b> (Tap anywhere on page to visit YouTube!)",
                social_badge_style
            )
        ]],
        colWidths=[usable_width]
    )
    promo_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1E293B")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(Spacer(1, 6))
    story.append(promo_box)

    doc.build(
        story,
        canvasmaker=NumberedCanvas,
        onFirstPage=add_decorations_and_links,
        onLaterPages=add_decorations_and_links
    )
    print(f"Generated PDF successfully: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")
    return output_pdf_path

if __name__ == "__main__":
    from fetch_news import fetch_all_current_affairs
    data = fetch_all_current_affairs()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_file = os.path.join(base_dir, "logo.jpg")
    output_pdf = os.path.join(base_dir, f"SSC_Current_Affairs_{datetime.date.today().strftime('%Y_%m_%d')}.pdf")
    generate_pdf(data, output_pdf, logo_file)
