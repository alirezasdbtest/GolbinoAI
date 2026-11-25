
# -*- coding: utf-8 -*-
"""
GolbinoAI
رابط کاربری پژوهشی برای بررسی تصاویر میکروسکوپی خون محیطی
نسخه UI - بدون اتصال به مدل تشخیص واقعی
"""

from pathlib import Path
from datetime import datetime
import io
import random

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


# =========================================================
# 1. تنظیمات اولیه
# =========================================================

st.set_page_config(
    page_title="GolbinoAI | تحلیل هوشمند خون",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

LOGO_CANDIDATES = [
    ASSETS_DIR / "logo.png",
    ASSETS_DIR / "golbino_mascot.png",
    BASE_DIR / "golbino_mascot.png",
]

FONT_REGULAR_CANDIDATES = [
    FONTS_DIR / "Estedad-Regular.ttf",
    FONTS_DIR / "Vazirmatn-Regular.ttf",
]

FONT_BOLD_CANDIDATES = [
    FONTS_DIR / "Estedad-Bold.ttf",
    FONTS_DIR / "Vazirmatn-Bold.ttf",
]

CELL_NAMES = {
    "Neutrophil": "نوتروفیل",
    "Lymphocyte": "لنفوسیت",
    "Monocyte": "مونوسیت",
    "Eosinophil": "ائوزینوفیل",
    "Basophil": "بازوفیل",
}

CELL_COLORS = {
    "Neutrophil": "#62B6A8",
    "Lymphocyte": "#8C83D8",
    "Monocyte": "#D69B65",
    "Eosinophil": "#D77FA6",
    "Basophil": "#7199CE",
}

CELL_DESCRIPTIONS = {
    "Neutrophil": "نوتروفیل‌ها از مهم‌ترین سلول‌های سیستم ایمنی ذاتی هستند و در پاسخ به عفونت‌های باکتریایی نقش دارند.",
    "Lymphocyte": "لنفوسیت‌ها در پاسخ‌های ایمنی اختصاصی و تولید آنتی‌بادی نقش مهمی دارند.",
    "Monocyte": "مونوسیت‌ها از سلول‌های بزرگ خون هستند و می‌توانند به ماکروفاژها و سلول‌های دندریتیک تبدیل شوند.",
    "Eosinophil": "ائوزینوفیل‌ها در پاسخ به انگل‌ها و برخی واکنش‌های آلرژیک نقش دارند.",
    "Basophil": "بازوفیل‌ها از گلبول‌های سفید کم‌تعداد هستند و در واکنش‌های آلرژیک مشارکت دارند.",
}


# =========================================================
# 2. وضعیت برنامه
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "خانه"

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = None

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

if "selected_sample" not in st.session_state:
    st.session_state.selected_sample = None


def go_to(page):
    st.session_state.page = page
    st.rerun()


# =========================================================
# 3. توابع کمکی
# =========================================================

def find_file(candidates):
    for path in candidates:
        if path.exists() and path.is_file():
            return path
    return None


def load_logo():
    path = find_file(LOGO_CANDIDATES)
    if path:
        try:
            return Image.open(path).convert("RGBA")
        except Exception:
            return None
    return None


def get_font_css():
    regular = find_file(FONT_REGULAR_CANDIDATES)
    bold = find_file(FONT_BOLD_CANDIDATES)

    css = ""

    if regular:
        css += f"""
        @font-face {{
            font-family: 'GolbinoFont';
            src: url('assets/fonts/{regular.name}') format('truetype');
            font-weight: 400;
        }}
        """

    if bold:
        css += f"""
        @font-face {{
            font-family: 'GolbinoFont';
            src: url('assets/fonts/{bold.name}') format('truetype');
            font-weight: 700;
        }}
        """

    return css


def inject_css():
    font_css = get_font_css()

    st.markdown(
        f"""
        <style>
        {font_css}

        @import url('https://fonts.googleapis.com/css2?family=Estedad:wght@300;400;500;600;700;800&display=swap');

        :root {{
            --bg: #242232;
            --bg-soft: #302d40;
            --glass: rgba(255,255,255,0.075);
            --glass-strong: rgba(255,255,255,0.115);
            --border: rgba(255,255,255,0.15);
            --text: #F5F2FC;
            --muted: #C4BED5;
            --purple: #B6A1F5;
            --purple-dark: #8972D0;
            --mint: #9EDCCB;
            --pink: #E6A9C8;
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(ellipse at 12% 5%, rgba(135,110,190,.22), transparent 35%),
                radial-gradient(ellipse at 88% 18%, rgba(90,155,165,.13), transparent 32%),
                linear-gradient(145deg, #252333 0%, #302d40 52%, #242332 100%);
            color: var(--text);
            font-family: {'GolbinoFont' if find_file(FONT_REGULAR_CANDIDATES) else 'Estedad'}, sans-serif;
        }}

        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}

        [data-testid="stToolbar"] {{
            right: 1rem;
        }}

        [data-testid="stMainBlockContainer"] {{
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(42,39,57,.96), rgba(34,32,47,.98));
            border-left: 1px solid rgba(255,255,255,.10);
            border-right: none;
        }}

        [data-testid="stSidebar"] * {{
            color: var(--text);
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            text-align: right;
        }}

        [data-testid="stMarkdownContainer"],
        [data-testid="stText"],
        [data-testid="stCaptionContainer"],
        [data-testid="stAlert"] {{
            direction: rtl;
            text-align: right;
            color: var(--text);
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: #FAF8FF !important;
            font-family: inherit !important;
            letter-spacing: -0.4px;
        }}

        p, li, label {{
            color: var(--muted);
            line-height: 1.9;
        }}

        a {{
            color: #C6B4FF !important;
        }}

        /* دکمه‌ها */
        .stButton > button,
        .stDownloadButton > button {{
            border: 1px solid rgba(255,255,255,.20);
            border-radius: 15px;
            min-height: 45px;
            padding: .55rem 1.2rem;
            color: #F9F6FF;
            background: linear-gradient(
                135deg,
                rgba(160,137,224,.42),
                rgba(117,105,163,.27)
            );
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,.22),
                0 7px 22px rgba(10,8,25,.18);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            font-family: inherit;
            font-weight: 600;
            transition: all .2s ease;
        }}

        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            border-color: rgba(210,195,255,.65);
            background: linear-gradient(
                135deg,
                rgba(180,158,245,.55),
                rgba(135,120,190,.40)
            );
            transform: translateY(-2px);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,.30),
                0 12px 28px rgba(10,8,25,.28);
        }}

        .stButton > button:focus,
        .stDownloadButton > button:focus {{
            box-shadow: 0 0 0 2px rgba(190,170,255,.3);
        }}

        /* ورودی‌ها */
        [data-testid="stFileUploader"] {{
            direction: rtl;
            border: 1px dashed rgba(205,190,255,.42);
            border-radius: 20px;
            background: rgba(255,255,255,.045);
            padding: 12px;
        }}

        [data-testid="stFileUploader"] section {{
            background: transparent;
        }}

        [data-testid="stFileUploader"] button {{
            border-radius: 12px;
        }}

        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] div[data-baseweb="select"],
        [data-testid="stTextArea"] textarea {{
            direction: rtl;
            text-align: right;
            color: var(--text);
            background: rgba(255,255,255,.07);
            border-color: var(--border);
            border-radius: 13px;
        }}

        [data-testid="stDataFrame"] {{
            direction: ltr;
        }}

        /* کارت شیشه‌ای */
        .glass-card {{
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(
                    135deg,
                    rgba(255,255,255,.135),
                    rgba(255,255,255,.045) 48%,
                    rgba(180,160,230,.065)
                );
            border: 1px solid rgba(255,255,255,.17);
            border-radius: 24px;
            padding: 25px;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,.20),
                inset 0 -1px 0 rgba(255,255,255,.035),
                0 18px 45px rgba(8,7,22,.22);
            backdrop-filter: blur(24px) saturate(150%);
            -webkit-backdrop-filter: blur(24px) saturate(150%);
            margin-bottom: 16px;
        }}

        .glass-card:before {{
            content: "";
            position: absolute;
            top: 0;
            left: 9%;
            width: 72%;
            height: 1px;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255,255,255,.55),
                transparent
            );
        }}

        .glass-card:after {{
            content: "";
            pointer-events: none;
            position: absolute;
            top: -90px;
            right: -100px;
            width: 240px;
            height: 190px;
            border-radius: 50%;
            background: rgba(210,195,255,.08);
            filter: blur(40px);
        }}

        .hero {{
            padding: 48px 42px;
            border-radius: 30px;
            background:
                radial-gradient(circle at 12% 20%, rgba(189,166,255,.20), transparent 32%),
                radial-gradient(circle at 90% 80%, rgba(125,211,190,.13), transparent 28%),
                linear-gradient(135deg, rgba(255,255,255,.13), rgba(255,255,255,.035));
            border: 1px solid rgba(255,255,255,.19);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,.24),
                0 25px 65px rgba(7,6,20,.24);
            backdrop-filter: blur(30px) saturate(155%);
            -webkit-backdrop-filter: blur(30px) saturate(155%);
            margin-bottom: 26px;
            position: relative;
            overflow: hidden;
        }}

        .hero:before {{
            content: "";
            position: absolute;
            top: -130px;
            left: 20%;
            width: 420px;
            height: 240px;
            background: rgba(205,190,255,.10);
            filter: blur(65px);
            border-radius: 50%;
        }}

        .hero-title {{
            font-size: clamp(2rem, 4vw, 3.3rem);
            font-weight: 800;
            line-height: 1.5;
            color: #FFFFFF;
            margin: 0;
        }}

        .hero-subtitle {{
            font-size: 1.05rem;
            color: #D5CFE4;
            line-height: 2.1;
            margin-top: 12px;
            max-width: 780px;
        }}

        .eyebrow {{
            display: inline-block;
            color: #D6C9FF;
            border: 1px solid rgba(205,190,255,.26);
            background: rgba(185,165,245,.10);
            padding: 6px 14px;
            border-radius: 100px;
            font-size: .82rem;
            margin-bottom: 15px;
        }}

        .section-title {{
            font-size: 1.35rem;
            font-weight: 750;
            color: #F8F5FF;
            margin: 24px 0 14px 0;
        }}

        .muted {{
            color: #C3BDD3;
            line-height: 1.9;
        }}

        .metric-card {{
            padding: 20px;
            min-height: 130px;
            border-radius: 20px;
            background: linear-gradient(145deg, rgba(255,255,255,.12), rgba(255,255,255,.045));
            border: 1px solid rgba(255,255,255,.14);
            box-shadow: inset 0 1px 0 rgba(255,255,255,.15), 0 12px 28px rgba(0,0,0,.13);
            backdrop-filter: blur(18px);
        }}

        .metric-number {{
            font-size: 1.9rem;
            font-weight: 800;
            color: #F7F2FF;
            direction: ltr;
            text-align: right;
        }}

        .metric-label {{
            color: #C9C2D9;
            font-size: .9rem;
            margin-top: 5px;
        }}

        .cell-dot {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-left: 7px;
        }}

        .status-pill {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 100px;
            background: rgba(230,169,200,.13);
            color: #F1BED6;
            border: 1px solid rgba(230,169,200,.24);
            font-size: .78rem;
        }}

        .footer {{
            text-align: center;
            color: #9992AA;
            font-size: .8rem;
            padding: 30px 0 10px;
            border-top: 1px solid rgba(255,255,255,.08);
            margin-top: 45px;
        }}

        [data-testid="stSidebar"] .stRadio label {{
            padding: 7px 0;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] {{
            gap: 8px;
        }}

        [data-testid="stSidebar"] [role="radio"] {{
            border-radius: 13px;
            padding: 9px 12px;
        }}

        [data-testid="stSidebar"] [aria-checked="true"] {{
            background: rgba(177,153,240,.16);
            border: 1px solid rgba(205,190,255,.20);
        }}

        hr {{
            border-color: rgba(255,255,255,.10);
        }}

        @media (max-width: 768px) {{
            .hero {{
                padding: 30px 22px;
            }}
            .glass-card {{
                padding: 19px;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


inject_css()


# =========================================================
# 4. تصاویر نمونه نمایشی
# =========================================================

def make_demo_microscopy(seed=10, width=900, height=570):
    """
    تصویرسازی آموزشی و غیرواقعی از محیط اسمیر خون.
    این تصویر داده میکروسکوپی واقعی نیست.
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    noise = np_rng.normal(0, 5, (height, width, 3))
    base = np.zeros((height, width, 3), dtype=np.float32)
    base[:] = [224, 190, 194]
    base += noise
    base = np.clip(base, 0, 255).astype(np.uint8)

    img = Image.fromarray(base, "RGB").filter(ImageFilter.GaussianBlur(1.2))
    draw = ImageDraw.Draw(img, "RGBA")

    # گلبول‌های قرمز
    for _ in range(65):
        x = rng.randint(25, width - 25)
        y = rng.randint(25, height - 25)
        r = rng.randint(17, 31)

        draw.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=(190, 105, 125, 115),
            outline=(150, 75, 100, 90),
            width=2
        )
        draw.ellipse(
            (x-r*.45, y-r*.45, x+r*.45, y+r*.45),
            fill=(232, 175, 182, 120)
        )

    # چند سلول سفید نمایشی
    white_cells = [
        (220, 185, 47, (105, 75, 155, 210)),
        (570, 330, 42, (100, 100, 175, 215)),
        (720, 130, 36, (130, 80, 150, 210)),
    ]

    for x, y, r, nucleus_color in white_cells:
        draw.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=(238, 218, 218, 240),
            outline=(180, 145, 165, 230),
            width=3
        )

        for _ in range(5):
            nx = x + rng.randint(-r//2, r//2)
            ny = y + rng.randint(-r//2, r//2)
            nr = rng.randint(8, 15)
            draw.ellipse(
                (nx-nr, ny-nr, nx+nr, ny+nr),
                fill=nucleus_color
            )

    return img.filter(ImageFilter.GaussianBlur(.35))


def get_demo_samples():
    return [
        {
            "name": "نمونه نمایشی شماره ۱",
            "image": make_demo_microscopy(17),
            "description": "تصویرسازی آموزشی با ظاهر اسمیر خون؛ فاقد داده آزمایشگاهی واقعی."
        },
        {
            "name": "نمونه نمایشی شماره ۲",
            "image": make_demo_microscopy(42),
            "description": "تصویرسازی مصنوعی برای نمایش رابط کاربری؛ فاقد نتیجه تشخیصی."
        },
    ]


# =========================================================
# 5. PDF
# =========================================================

def create_pdf_report(report):
    """
    تولید PDF فارسی.
    برای خروجی صحیح فارسی، فونت فارسی باید در assets/fonts باشد.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_RIGHT, TA_CENTER
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle
        )
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        raise RuntimeError("کتابخانه reportlab نصب نیست.")

    font_path = find_file(FONT_REGULAR_CANDIDATES)
    bold_path = find_file(FONT_BOLD_CANDIDATES)

    if not font_path:
        raise RuntimeError(
            "فونت فارسی پیدا نشد. فایل Vazirmatn-Regular.ttf را در "
            "assets/fonts قرار بده."
        )

    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
    except ImportError:
        raise RuntimeError(
            "برای ساخت PDF فارسی باید arabic-reshaper و python-bidi نصب باشند."
        )

    pdfmetrics.registerFont(TTFont("Persian", str(font_path)))

    if bold_path:
        pdfmetrics.registerFont(TTFont("PersianBold", str(bold_path)))
        bold_font = "PersianBold"
    else:
        bold_font = "Persian"

    def fa(text):
        return get_display(arabic_reshaper.reshape(str(text)))

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=45,
        bottomMargin=45,
        title="GolbinoAI Report"
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PersianTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=19,
        leading=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#55447C")
    )

    normal_style = ParagraphStyle(
        "PersianNormal",
        parent=styles["Normal"],
        fontName="Persian",
        fontSize=10,
        leading=19,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#333333")
    )

    story = [
        Paragraph(fa("گزارش سامانه GolbinoAI"), title_style),
        Spacer(1, 18),
        Paragraph(fa("گزارش نمایشی - فاقد اعتبار تشخیصی"), normal_style),
        Spacer(1, 10),
        Paragraph(fa(f"نام تصویر: {report['filename']}"), normal_style),
        Paragraph(fa(f"تاریخ ثبت: {report['date']}"), normal_style),
        Spacer(1, 20),
    ]

    table_data = [
        [
            Paragraph(fa("نوع سلول"), normal_style),
            Paragraph(fa("تعداد نمایشی"), normal_style),
            Paragraph(fa("درصد نمایشی"), normal_style),
        ]
    ]

    for item in report["results"]:
        table_data.append([
            Paragraph(fa(item["name_fa"]), normal_style),
            Paragraph(str(item["count"]), normal_style),
            Paragraph(f"{item['percentage']}%", normal_style),
        ])

    table = Table(table_data, colWidths=[220, 100, 100], repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E1F5")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#D5CDE2")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))

    story.extend([
        table,
        Spacer(1, 24),
        Paragraph(
            fa(
                "توجه: اعداد این گزارش صرفاً برای نمایش قابلیت‌های رابط کاربری "
                "تولید شده‌اند و حاصل تحلیل تصویر یا مدل هوش مصنوعی نیستند."
            ),
            normal_style
        ),
    ])

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# =========================================================
# 6. اجزای رابط کاربری
# =========================================================

def section_title(title, subtitle=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="muted">{subtitle}</div>', unsafe_allow_html=True)


def glass_card(title, content, icon="✦"):
    st.markdown(
        f"""
        <div class="glass-card">
            <div style="font-size:1.4rem;margin-bottom:10px;">{icon}</div>
            <div style="font-size:1.08rem;font-weight:750;color:#F7F3FF;margin-bottom:9px;">
                {title}
            </div>
            <div class="muted">{content}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def metric_card(number, label):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">{number}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_header(title, subtitle):
    st.markdown(
        f"""
        <div style="margin-bottom:28px;">
            <div class="eyebrow">GOLBINOAI · پژوهش هوشمند خون‌شناسی</div>
            <h1 style="font-size:2.1rem;margin:0 0 8px 0;">{title}</h1>
            <div class="muted">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_footer():
    st.markdown(
        """
        <div class="footer">
            GolbinoAI · سامانه پژوهشی تحلیل تصاویر خون محیطی
            <br>
            این نسخه نمایشی است و جایگزین تشخیص متخصص آزمایشگاه نیست.
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 7. نوار کناری
# =========================================================

with st.sidebar:
    logo = load_logo()

    if logo:
        st.image(logo, width=105)
    else:
        st.markdown(
            "<div style='font-size:3rem;text-align:center;'>🩸</div>",
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div style="text-align:center;margin-bottom:20px;">
            <div style="font-size:1.55rem;font-weight:800;color:#F7F2FF;">
                GolbinoAI
            </div>
            <div style="font-size:.78rem;color:#BDB5D0;">
                Intelligent Blood Cell Analysis
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### فضای کاری")

    pages = [
        "خانه",
        "بررسی تصویر",
        "نمونه‌های نمایشی",
        "گزارش‌ها",
        "راهنمای سلول‌ها",
        "درباره پروژه",
    ]

    current_index = pages.index(st.session_state.page) if st.session_state.page in pages else 0

    selected_page = st.radio(
        "منوی اصلی",
        pages,
        index=current_index,
        label_visibility="collapsed"
    )

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

    st.markdown("---")

    st.markdown(
        """
        <div style="
            background:rgba(255,255,255,.055);
            border:1px solid rgba(255,255,255,.10);
            border-radius:15px;
            padding:14px;
            font-size:.82rem;
            color:#C9C2D9;
            line-height:1.9;
        ">
            <b style="color:#F3EDFF;">وضعیت سامانه</b><br>
            رابط کاربری: فعال<br>
            مدل تشخیص: متصل نشده<br>
            حالت: نسخه پژوهشی اولیه
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 8. صفحه خانه
# =========================================================

if st.session_state.page == "خانه":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">نسل جدید تحلیل تصاویر خون محیطی</div>
            <div class="hero-title">
                نگاهی هوشمندتر<br>
                به دنیای سلول‌های خونی
            </div>
            <div class="hero-subtitle">
                GolbinoAI بستری پژوهشی برای بررسی تصاویر میکروسکوپی خون محیطی،
                مطالعه پنج گروه اصلی گلبول سفید و توسعه ابزارهای هوشمند
                در حوزه خون‌شناسی است.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns([1.35, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="glass-card" style="min-height:255px;">
                <div class="eyebrow">شروع کار</div>
                <div style="font-size:1.65rem;font-weight:800;color:#FFF;margin-bottom:10px;">
                    آماده بررسی یک تصویر هستید؟
                </div>
                <div class="muted">
                    تصویر اسمیر خون محیطی خود را بارگذاری کنید و در محیط
                    GolbinoAI پیش‌نمایش و اطلاعات آن را مشاهده کنید.
                    اتصال مدل تشخیص در نسخه‌های بعدی انجام خواهد شد.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("🔬  شروع بررسی تصویر", key="home_start", use_container_width=True):
            go_to("بررسی تصویر")

    with right:
        logo = load_logo()
        if logo:
            st.image(logo, use_container_width=True)
        else:
            st.markdown(
                """
                <div class="glass-card" style="
                    min-height:255px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    text-align:center;
                    font-size:6rem;
                ">🩸</div>
                """,
                unsafe_allow_html=True
            )

    section_title("قابلیت‌های سامانه", "ابزارهایی برای یک تجربه پژوهشی منظم و قابل توسعه")

    c1, c2, c3 = st.columns(3)

    with c1:
        glass_card(
            "بارگذاری تصویر",
            "دریافت تصاویر میکروسکوپی با فرمت‌های رایج و نمایش پیش‌نمایش.",
            "📤"
        )

    with c2:
        glass_card(
            "مطالعه پنج گروه سلولی",
            "آشنایی با نوتروفیل، لنفوسیت، مونوسیت، ائوزینوفیل و بازوفیل.",
            "🔬"
        )

    with c3:
        glass_card(
            "گزارش پژوهشی",
            "ساختار اولیه گزارش و خروجی PDF برای نتایج نمایشی.",
            "📄"
        )

    section_title("گروه‌های سلولی مورد مطالعه")

    cols = st.columns(5)

    for col, (key, name) in zip(cols, CELL_NAMES.items()):
        with col:
            color = CELL_COLORS[key]
            st.markdown(
                f"""
                <div class="metric-card" style="min-height:110px;">
                    <div style="
                        width:12px;height:12px;border-radius:50%;
                        background:{color};margin-bottom:13px;
                        box-shadow:0 0 14px {color};
                    "></div>
                    <div style="font-weight:750;color:#F7F2FF;">
                        {name}
                    </div>
                    <div style="font-size:.75rem;color:#BDB6CE;direction:ltr;text-align:right;">
                        {key}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    render_footer()


# =========================================================
# 9. صفحه بررسی تصویر
# =========================================================

elif st.session_state.page == "بررسی تصویر":

    render_header(
        "بررسی تصویر",
        "تصویر میکروسکوپی خون محیطی را بارگذاری و اطلاعات آن را مشاهده کنید."
    )

    st.markdown(
        """
        <div class="glass-card">
            <div style="font-size:1.1rem;font-weight:750;color:#FFF;">
                📁 انتخاب تصویر
            </div>
            <div class="muted">
                فرمت‌های مجاز: JPG، JPEG، PNG و TIFF
                <br>
                برای نتایج علمی معتبر، تصویر باید کیفیت و وضوح مناسبی داشته باشد.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader(
        "تصویر موردنظر را انتخاب کنید",
        type=["jpg", "jpeg", "png", "tif", "tiff"],
        key="image_uploader"
    )

    if uploaded is not None:
        try:
            image = Image.open(uploaded).convert("RGB")
            st.session_state.uploaded_image = image
            st.session_state.uploaded_name = uploaded.name

            st.markdown("---")
            section_title("پیش‌نمایش تصویر")

            img_col, info_col = st.columns([1.4, 1], gap="large")

            with img_col:
                st.image(
                    image,
                    caption=uploaded.name,
                    use_container_width=True
                )

            with info_col:
                glass_card(
                    "اطلاعات فایل",
                    f"""
                    نام فایل: {uploaded.name}<br>
                    ابعاد: {image.width} × {image.height}<br>
                    فرمت: {image.format or 'نامشخص'}<br>
                    حالت رنگ: {image.mode}
                    """,
                    "📋"
                )

                st.markdown(
                    """
                    <div class="glass-card">
                        <span class="status-pill">نسخه بدون مدل تشخیص</span>
                        <div style="font-weight:750;color:#FFF;margin-top:12px;">
                            آماده‌سازی تصویر
                        </div>
                        <div class="muted">
                            در حال حاضر مدل یادگیری عمیق به رابط متصل نیست.
                            کلیک روی دکمه بررسی، تشخیص واقعی انجام نمی‌دهد.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if st.button(
                "🔍  بررسی تصویر",
                key="analyze_uploaded",
                use_container_width=True
            ):
                st.warning(
                    "مدل تشخیص هنوز به GolbinoAI متصل نشده است. "
                    "تصویر دریافت و نمایش داده شده، اما هیچ تشخیص یا شمارش واقعی انجام نشده است."
                )

        except Exception as e:
            st.error(f"خطا در خواندن تصویر: {e}")

    else:
        st.markdown(
            """
            <div class="glass-card" style="text-align:center;padding:45px 20px;">
                <div style="font-size:3rem;margin-bottom:12px;">🖼️</div>
                <div style="font-size:1.2rem;font-weight:750;color:#FFF;">
                    هنوز تصویری انتخاب نشده است
                </div>
                <div class="muted">
                    تصویر میکروسکوپی خود را از قسمت بالا بارگذاری کنید.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    render_footer()


# =========================================================
# 10. صفحه نمونه‌های نمایشی
# =========================================================

elif st.session_state.page == "نمونه‌های نمایشی":

    render_header(
        "نمونه‌های نمایشی",
        "تصاویر و نتایج زیر صرفاً برای نمایش طراحی رابط کاربری تولید شده‌اند."
    )

    st.warning(
        "تصاویر این صفحه مصنوعی و غیرواقعی هستند. اعداد و نتایج نمونه نیز "
        "خروجی مدل هوش مصنوعی نیستند و نباید به‌عنوان داده آزمایشگاهی استفاده شوند."
    )

    samples = get_demo_samples()

    demo_results = {
        "Neutrophil": 42,
        "Lymphocyte": 28,
        "Monocyte": 12,
        "Eosinophil": 10,
        "Basophil": 8,
    }

    for index, sample in enumerate(samples):
        st.markdown(f"### {sample['name']}")

        image_col, result_col = st.columns([1.2, 1], gap="large")

        with image_col:
            st.image(
                sample["image"],
                use_container_width=True,
                caption="تصویرسازی مصنوعی — فاقد داده میکروسکوپی واقعی"
            )

        with result_col:
            st.markdown(
                """
                <div class="glass-card">
                    <span class="status-pill">نتیجه کاملاً نمایشی</span>
                    <h3 style="margin-top:12px;">خلاصه نمونه</h3>
                    <div class="muted">
                        مقادیر زیر فقط برای نمایش نحوه ارائه نتایج در رابط کاربری هستند.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            for cell, count in demo_results.items():
                color = CELL_COLORS[cell]
                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                        padding:9px 13px;
                        margin:6px 0;
                        background:rgba(255,255,255,.055);
                        border:1px solid rgba(255,255,255,.09);
                        border-radius:12px;
                    ">
                        <span style="color:{color};font-weight:700;">
                            {CELL_NAMES[cell]}
                        </span>
                        <span style="color:#FFF;direction:ltr;font-weight:700;">
                            {count}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")

    render_footer()


# =========================================================
# 11. صفحه گزارش‌ها
# =========================================================

elif st.session_state.page == "گزارش‌ها":

    render_header(
        "گزارش‌ها",
        "مشاهده گزارش‌های نمایشی و دریافت خروجی PDF."
    )

    st.warning(
        "این بخش در نسخه فعلی شامل گزارش‌های نمونه است. "
        "هیچ‌کدام از اعداد زیر از تحلیل واقعی تصویر به دست نیامده‌اند."
    )

    report_data = []

    for cell, count in {
        "Neutrophil": 42,
        "Lymphocyte": 28,
        "Monocyte": 12,
        "Eosinophil": 10,
        "Basophil": 8,
    }.items():
        report_data.append({
            "نام انگلیسی": cell,
            "نام فارسی": CELL_NAMES[cell],
            "تعداد نمایشی": count,
            "درصد نمایشی": count
        })

    df = pd.DataFrame(report_data)

    a, b, c = st.columns(3)

    with a:
        metric_card("100", "تعداد کل نمایشی")

    with b:
        metric_card("5", "گروه سلولی")

    with c:
        metric_card("DEMO", "نوع گزارش")

    section_title("جدول خلاصه")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    report = {
        "filename": st.session_state.uploaded_name or "Demo_Sample",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "results": [
            {
                "name_fa": CELL_NAMES[cell],
                "count": count,
                "percentage": count
            }
            for cell, count in {
                "Neutrophil": 42,
                "Lymphocyte": 28,
                "Monocyte": 12,
                "Eosinophil": 10,
                "Basophil": 8,
            }.items()
        ]
    }

    if st.button("ساخت گزارش PDF", use_container_width=True):
        try:
            pdf_bytes = create_pdf_report(report)

            st.download_button(
                "⬇️ دریافت گزارش PDF",
                data=pdf_bytes,
                file_name="GolbinoAI_Demo_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as e:
            st.error(str(e))

    render_footer()


# =========================================================
# 12. راهنمای سلول‌ها
# =========================================================

elif st.session_state.page == "راهنمای سلول‌ها":

    render_header(
        "راهنمای سلول‌ها",
        "آشنایی مقدماتی با پنج گروه اصلی گلبول سفید مورد مطالعه در پروژه."
    )

    for cell, name in CELL_NAMES.items():
        color = CELL_COLORS[cell]

        st.markdown(
            f"""
            <div class="glass-card">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="
                        width:13px;height:13px;border-radius:50%;
                        background:{color};
                        box-shadow:0 0 16px {color};
                    "></div>
                    <div style="font-size:1.18rem;font-weight:800;color:#FFF;">
                        {name}
                    </div>
                    <div style="
                        direction:ltr;
                        color:#AFA8C0;
                        font-size:.85rem;
                        margin-right:auto;
                    ">
                        {cell}
                    </div>
                </div>
                <div class="muted" style="margin-top:12px;">
                    {CELL_DESCRIPTIONS[cell]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    render_footer()


# =========================================================
# 13. درباره پروژه
# =========================================================

elif st.session_state.page == "درباره پروژه":

    render_header(
        "درباره GolbinoAI",
        "یک پروژه پژوهشی در مسیر توسعه ابزارهای هوشمند خون‌شناسی."
    )

    st.markdown(
        """
        <div class="glass-card">
            <div style="font-size:1.45rem;font-weight:800;color:#FFF;">
                GolbinoAI
            </div>
            <div class="muted" style="margin-top:12px;">
                GolbinoAI با هدف توسعه یک بستر پژوهشی برای تحلیل تصاویر
                میکروسکوپی خون محیطی طراحی شده است. تمرکز پروژه بر شناسایی
                و مکان‌یابی پنج گروه اصلی گلبول سفید در تصاویر اسمیر خون است.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    section_title("اهداف پژوهشی")

    c1, c2 = st.columns(2)

    with c1:
        glass_card(
            "تشخیص و مکان‌یابی",
            "توسعه مدل‌های بینایی ماشین برای شناسایی و مکان‌یابی سلول‌های سفید خون.",
            "🎯"
        )

    with c2:
        glass_card(
            "ارزیابی مدل",
            "بررسی عملکرد مدل با معیارهایی مانند Precision، Recall و mAP.",
            "📊"
        )

    section_title("گروه‌های مورد بررسی")

    for cell, name in CELL_NAMES.items():
        st.markdown(
            f"""
            <div style="
                display:flex;
                justify-content:space-between;
                padding:12px 16px;
                margin:7px 0;
                border-radius:13px;
                background:rgba(255,255,255,.055);
                border:1px solid rgba(255,255,255,.09);
            ">
                <span style="color:#F5F1FF;font-weight:650;">{name}</span>
                <span style="direction:ltr;color:#BEB6D0;">{cell}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown(
        """
        <div class="muted">
            <b style="color:#F3EDFF;">وضعیت توسعه:</b>
            نسخه فعلی شامل رابط کاربری و محتوای نمایشی است.
            مدل تشخیص هنوز به برنامه متصل نشده است.
        </div>
        """,
        unsafe_allow_html=True
    )

    render_footer()
