
# -*- coding: utf-8 -*-
"""
GolbinoAI
رابط پژوهشی تحلیل تصاویر میکروسکوپی خون محیطی
نسخه روشن و Liquid Glass
توجه: در این نسخه مدل تشخیص واقعی متصل نیست.
"""

from pathlib import Path
from datetime import datetime
import io
import random
import html

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


# =========================================================
# 1. تنظیمات برنامه
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

LOGO_PATHS = [
    ASSETS_DIR / "logo.png",
    ASSETS_DIR / "golbino_mascot.png",
    BASE_DIR / "golbino_mascot.png",
]

FONT_REGULAR_PATHS = [
    FONTS_DIR / "Vazirmatn-Regular.ttf",
    FONTS_DIR / "Estedad-Regular.ttf",
]

FONT_BOLD_PATHS = [
    FONTS_DIR / "Vazirmatn-Bold.ttf",
    FONTS_DIR / "Estedad-Bold.ttf",
]

CELL_INFO = {
    "Neutrophil": {
        "fa": "نوتروفیل",
        "color": "#39A99A",
        "description": "نوتروفیل‌ها از مهم‌ترین سلول‌های سیستم ایمنی ذاتی هستند و در پاسخ به عفونت‌های باکتریایی نقش دارند."
    },
    "Lymphocyte": {
        "fa": "لنفوسیت",
        "color": "#8872C5",
        "description": "لنفوسیت‌ها در پاسخ‌های ایمنی اختصاصی و تولید آنتی‌بادی نقش مهمی دارند."
    },
    "Monocyte": {
        "fa": "مونوسیت",
        "color": "#C58B4F",
        "description": "مونوسیت‌ها از سلول‌های بزرگ خون هستند و می‌توانند به ماکروفاژها و سلول‌های دندریتیک تبدیل شوند."
    },
    "Eosinophil": {
        "fa": "ائوزینوفیل",
        "color": "#CB729A",
        "description": "ائوزینوفیل‌ها در پاسخ به انگل‌ها و برخی واکنش‌های آلرژیک نقش دارند."
    },
    "Basophil": {
        "fa": "بازوفیل",
        "color": "#568BC4",
        "description": "بازوفیل‌ها از سلول‌های کم‌تعداد خون هستند و در واکنش‌های آلرژیک مشارکت دارند."
    },
}


# =========================================================
# 2. مدیریت وضعیت برنامه
# =========================================================

DEFAULT_STATE = {
    "page": "خانه",
    "uploaded_image": None,
    "uploaded_name": None,
    "uploaded_size": None,
    "sample_reports": [],
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


def navigate(page):
    st.session_state.page = page
    st.rerun()


# =========================================================
# 3. توابع فایل و لوگو
# =========================================================

def find_existing_file(paths):
    for path in paths:
        if path.exists() and path.is_file():
            return path
    return None


def load_logo():
    path = find_existing_file(LOGO_PATHS)

    if path:
        try:
            return Image.open(path).convert("RGBA")
        except Exception:
            return None

    return None


def get_font_path(bold=False):
    paths = FONT_BOLD_PATHS if bold else FONT_REGULAR_PATHS
    return find_existing_file(paths)


# =========================================================
# 4. استایل کامل رابط کاربری
# =========================================================

def inject_css():

    st.markdown(
        """
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Estedad:wght@300;400;500;600;700;800&display=swap');

        :root {
            --background: #F1EEF7;
            --background-soft: #E9E4F1;

            --surface: rgba(255,255,255,0.72);
            --surface-strong: rgba(255,255,255,0.90);

            --border: rgba(105,86,145,0.14);

            --text: #29243A;
            --text-secondary: #625B70;
            --text-muted: #81798E;

            --purple: #8065B8;
            --purple-dark: #68509E;
            --purple-light: #EAE3F6;

            --green: #438F7B;
            --pink: #B65F88;
        }

        /* -------------------------
           پس‌زمینه اصلی
        ------------------------- */

        html,
        body,
        [data-testid="stAppViewContainer"] {

            background:
                radial-gradient(
                    ellipse at 10% 5%,
                    rgba(193,174,230,0.42),
                    transparent 36%
                ),
                radial-gradient(
                    ellipse at 90% 20%,
                    rgba(174,216,204,0.30),
                    transparent 34%
                ),
                linear-gradient(
                    145deg,
                    #F5F2FA 0%,
                    #ECE8F4 52%,
                    #F3F0F8 100%
                );

            color: var(--text);
            font-family: 'Estedad', sans-serif;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1450px;
            padding-top: 2.1rem;
            padding-bottom: 4rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        /* -------------------------
           نوار کناری
        ------------------------- */

        [data-testid="stSidebar"] {

            background:
                linear-gradient(
                    180deg,
                    #EAE5F2 0%,
                    #E2DCEC 100%
                );

            border-left: 1px solid rgba(105,86,145,0.12);
            border-right: none;
        }

        [data-testid="stSidebar"] * {
            color: #302941;
            font-family: 'Estedad', sans-serif;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            text-align: right;
            direction: rtl;
        }

        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: 7px;
        }

        [data-testid="stSidebar"] [role="radio"] {
            padding: 9px 12px;
            border-radius: 13px;
        }

        [data-testid="stSidebar"] [aria-checked="true"] {
            background: rgba(128,101,184,0.14);
            border: 1px solid rgba(128,101,184,0.20);
        }

        /* -------------------------
           متن‌ها و راست‌چین
        ------------------------- */

        [data-testid="stMarkdownContainer"],
        [data-testid="stText"],
        [data-testid="stCaptionContainer"] {
            direction: rtl;
            text-align: right;
            color: var(--text);
            font-family: 'Estedad', sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #29243A !important;
            font-family: 'Estedad', sans-serif !important;
            letter-spacing: -0.4px;
        }

        p, li, label {
            color: var(--text-secondary);
            line-height: 2;
        }

        strong, b {
            color: #302941;
        }

        a {
            color: #765BAE !important;
        }

        /* -------------------------
           کارت شیشه‌ای
        ------------------------- */

        .glass-card {

            position: relative;
            overflow: hidden;

            background:
                linear-gradient(
                    135deg,
                    rgba(255,255,255,0.91),
                    rgba(255,255,255,0.60) 55%,
                    rgba(225,216,245,0.48)
                );

            border: 1px solid rgba(255,255,255,0.90);
            border-radius: 24px;

            padding: 25px;

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.98),
                inset 0 -1px 0 rgba(255,255,255,0.35),
                0 14px 38px rgba(65,48,100,0.10);

            backdrop-filter: blur(25px) saturate(160%);
            -webkit-backdrop-filter: blur(25px) saturate(160%);

            margin-bottom: 17px;
        }

        .glass-card:before {

            content: "";
            position: absolute;

            top: 0;
            left: 8%;

            width: 75%;
            height: 1px;

            background:
                linear-gradient(
                    90deg,
                    transparent,
                    rgba(255,255,255,1),
                    transparent
                );
        }

        .glass-card:after {

            content: "";
            pointer-events: none;

            position: absolute;
            top: -100px;
            right: -100px;

            width: 240px;
            height: 190px;

            border-radius: 50%;
            background: rgba(195,178,235,0.12);

            filter: blur(45px);
        }

        /* -------------------------
           Hero
        ------------------------- */

        .hero {

            position: relative;
            overflow: hidden;

            padding: 48px 44px;
            border-radius: 30px;

            background:
                radial-gradient(
                    circle at 10% 20%,
                    rgba(180,155,225,0.25),
                    transparent 35%
                ),
                radial-gradient(
                    circle at 90% 80%,
                    rgba(145,205,185,0.22),
                    transparent 30%
                ),
                linear-gradient(
                    135deg,
                    rgba(255,255,255,0.94),
                    rgba(238,232,248,0.76)
                );

            border: 1px solid rgba(255,255,255,0.95);

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,1),
                0 22px 55px rgba(65,48,100,0.12);

            backdrop-filter: blur(30px) saturate(165%);
            -webkit-backdrop-filter: blur(30px) saturate(165%);

            margin-bottom: 28px;
        }

        .hero-title {
            font-size: clamp(2rem, 4vw, 3.2rem);
            font-weight: 800;
            line-height: 1.65;
            color: #29243A;
            margin: 0;
        }

        .hero-subtitle {
            font-size: 1rem;
            color: #625B70;
            line-height: 2.2;
            margin-top: 12px;
            max-width: 780px;
        }

        .eyebrow {

            display: inline-block;

            color: #70549E;

            border: 1px solid rgba(126,99,177,0.22);
            background: rgba(154,127,207,0.11);

            padding: 6px 14px;
            border-radius: 100px;

            font-size: 0.82rem;
            margin-bottom: 15px;
        }

        /* -------------------------
           کارت‌های آماری
        ------------------------- */

        .metric-card {

            padding: 21px;
            min-height: 125px;

            border-radius: 20px;

            background:
                linear-gradient(
                    145deg,
                    rgba(255,255,255,0.94),
                    rgba(246,242,251,0.76)
                );

            border: 1px solid rgba(255,255,255,0.94);

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,1),
                0 11px 27px rgba(65,48,100,0.08);

            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }

        .metric-number {

            font-size: 1.85rem;
            font-weight: 800;

            color: #302941;

            direction: ltr;
            text-align: right;
        }

        .metric-label {
            color: #625B70;
            font-size: 0.88rem;
            margin-top: 5px;
        }

        /* -------------------------
           عنوان بخش‌ها
        ------------------------- */

        .section-heading {
            font-size: 1.35rem;
            font-weight: 800;
            color: #302941;
            margin-top: 30px;
            margin-bottom: 7px;
        }

        .section-description {
            color: #71697F;
            font-size: 0.91rem;
            line-height: 2;
            margin-bottom: 18px;
        }

        .muted {
            color: #625B70;
            line-height: 2;
        }

        /* -------------------------
           دکمه‌ها
        ------------------------- */

        .stButton > button,
        .stDownloadButton > button {

            min-height: 46px;
            padding: 0.55rem 1.2rem;

            border-radius: 15px;

            color: #FFFFFF;

            background:
                linear-gradient(
                    135deg,
                    #8065B8,
                    #68509E
                );

            border: 1px solid rgba(255,255,255,0.65);

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.25),
                0 8px 20px rgba(104,80,158,0.20);

            font-family: 'Estedad', sans-serif;
            font-weight: 650;

            transition: all 0.2s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {

            color: #FFFFFF;

            background:
                linear-gradient(
                    135deg,
                    #9176CA,
                    #765CAB
                );

            transform: translateY(-2px);

            box-shadow:
                0 12px 25px rgba(104,80,158,0.24);
        }

        .stButton > button:focus,
        .stDownloadButton > button:focus {
            box-shadow: 0 0 0 3px rgba(128,101,184,0.18);
        }

        /* -------------------------
           ورودی‌ها
        ------------------------- */

        [data-testid="stFileUploader"] {

            direction: rtl;

            border: 1px dashed rgba(126,99,177,0.38);
            border-radius: 20px;

            background: rgba(255,255,255,0.48);

            padding: 13px;
        }

        [data-testid="stFileUploader"] section {
            background: transparent;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea {

            direction: rtl;
            text-align: right;

            color: #302941 !important;

            background: rgba(255,255,255,0.75);

            border: 1px solid rgba(105,86,145,0.16);
            border-radius: 13px;
        }

        [data-testid="stSelectbox"] div[data-baseweb="select"] {
            background: rgba(255,255,255,0.75);
            border-radius: 13px;
        }

        [data-testid="stDataFrame"] {
            direction: ltr;
        }

        /* -------------------------
           وضعیت و برچسب‌ها
        ------------------------- */

        .status-pill {

            display: inline-block;

            padding: 6px 12px;

            border-radius: 100px;

            background: rgba(182,95,136,0.10);
            color: #974568;

            border: 1px solid rgba(182,95,136,0.20);

            font-size: 0.78rem;
        }

        .footer {

            text-align: center;

            color: #777083;
            font-size: 0.82rem;

            padding: 28px 0 10px;

            border-top: 1px solid rgba(105,86,145,0.12);

            margin-top: 45px;
        }

        hr {
            border-color: rgba(105,86,145,0.13);
        }

        /* -------------------------
           نمایش موبایل
        ------------------------- */

        @media (max-width: 768px) {

            .hero {
                padding: 30px 22px;
            }

            .glass-card {
                padding: 19px;
            }

            .hero-title {
                font-size: 2rem;
            }
        }

        </style>
        """,
        unsafe_allow_html=True
    )


inject_css()


# =========================================================
# 5. توابع اجزای رابط
# =========================================================

def render_section(title, description=None):

    st.markdown(
        f"""
        <div class="section-heading">{title}</div>
        """,
        unsafe_allow_html=True
    )

    if description:
        st.markdown(
            f"""
            <div class="section-description">{description}</div>
            """,
            unsafe_allow_html=True
        )


def render_card(title, description, icon="✦"):

    st.markdown(
        f"""
        <div class="glass-card">

            <div style="
                font-size:1.65rem;
                margin-bottom:12px;
            ">
                {icon}
            </div>

            <div style="
                font-size:1.08rem;
                font-weight:800;
                color:#302941;
                margin-bottom:9px;
            ">
                {title}
            </div>

            <div class="muted">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric(number, label):

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-number">
                {number}
            </div>

            <div class="metric-label">
                {label}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def render_footer():

    st.markdown(
        """
        <div class="footer">
            <b>GolbinoAI</b>
            <br>
            سامانه پژوهشی تحلیل تصاویر خون محیطی
            <br>
            نسخه رابط کاربری اولیه
        </div>
        """,
        unsafe_allow_html=True
    )


def render_page_header(title, description):

    st.markdown(
        f"""
        <div style="margin-bottom:28px;">

            <div class="eyebrow">
                GOLBINOAI · INTELLIGENT BLOOD ANALYSIS
            </div>

            <h1 style="
                font-size:2.1rem;
                margin:0 0 8px 0;
                color:#29243A;
            ">
                {title}
            </h1>

            <div class="muted">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 6. ساخت تصاویر نمایشی مصنوعی
# =========================================================

def create_demo_image(seed=10, width=1000, height=650):

    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    # پس‌زمینه بافت‌دار
    noise = np_rng.normal(
        loc=0,
        scale=4,
        size=(height, width, 3)
    )

    base = np.zeros((height, width, 3), dtype=np.float32)
    base[:] = [232, 204, 207]

    base += noise
    base = np.clip(base, 0, 255).astype(np.uint8)

    image = Image.fromarray(base, "RGB")
    image = image.filter(ImageFilter.GaussianBlur(1.1))

    draw = ImageDraw.Draw(image, "RGBA")

    # گلبول‌های قرمز مصنوعی
    for _ in range(90):

        x = rng.randint(25, width - 25)
        y = rng.randint(25, height - 25)
        r = rng.randint(17, 31)

        draw.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=(183, 101, 120, 100),
            outline=(153, 78, 103, 120),
            width=2
        )

        draw.ellipse(
            (
                x-r*.43,
                y-r*.43,
                x+r*.43,
                y+r*.43
            ),
            fill=(238, 188, 192, 145)
        )

    # سلول‌های سفید نمایشی
    white_cells = [
        (230, 200, 48, (105, 76, 157, 225)),
        (590, 370, 43, (104, 91, 172, 225)),
        (790, 160, 38, (132, 77, 150, 225)),
        (430, 520, 35, (117, 88, 165, 225)),
    ]

    for x, y, radius, nucleus_color in white_cells:

        draw.ellipse(
            (
                x-radius,
                y-radius,
                x+radius,
                y+radius
            ),
            fill=(245, 227, 228, 245),
            outline=(185, 149, 166, 240),
            width=3
        )

        for _ in range(5):

            nx = x + rng.randint(-radius//2, radius//2)
            ny = y + rng.randint(-radius//2, radius//2)
            nr = rng.randint(8, 15)

            draw.ellipse(
                (
                    nx-nr,
                    ny-nr,
                    nx+nr,
                    ny+nr
                ),
                fill=nucleus_color
            )

    return image.filter(ImageFilter.GaussianBlur(0.35))


DEMO_SAMPLES = [
    {
        "name": "نمونه نمایشی شماره ۱",
        "image": create_demo_image(17),
        "description": "تصویرسازی مصنوعی با ظاهر اسمیر خون؛ فاقد داده میکروسکوپی واقعی."
    },
    {
        "name": "نمونه نمایشی شماره ۲",
        "image": create_demo_image(42),
        "description": "تصویرسازی آموزشی برای نمایش رابط کاربری؛ فاقد نتیجه تشخیصی."
    },
]


# =========================================================
# 7. PDF فارسی
# =========================================================

def make_persian_pdf(report):

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

        import arabic_reshaper
        from bidi.algorithm import get_display

    except ImportError:
        raise RuntimeError(
            "کتابخانه‌های PDF نصب نیستند. requirements.txt را بررسی کن."
        )

    regular_font = get_font_path(False)
    bold_font_path = get_font_path(True)

    if not regular_font:
        raise RuntimeError(
            "فونت فارسی پیدا نشد. فایل Vazirmatn-Regular.ttf را در "
            "assets/fonts قرار بده."
        )

    pdfmetrics.registerFont(
        TTFont("GolbinoPersian", str(regular_font))
    )

    if bold_font_path:

        pdfmetrics.registerFont(
            TTFont("GolbinoPersianBold", str(bold_font_path))
        )

        heading_font = "GolbinoPersianBold"

    else:
        heading_font = "GolbinoPersian"

    def fa(value):
        shaped = arabic_reshaper.reshape(str(value))
        return get_display(shaped)

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
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
        "GolbinoTitle",
        parent=styles["Title"],
        fontName=heading_font,
        fontSize=19,
        leading=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#68509E")
    )

    normal_style = ParagraphStyle(
        "GolbinoNormal",
        parent=styles["Normal"],
        fontName="GolbinoPersian",
        fontSize=10,
        leading=20,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#302941")
    )

    story = []

    story.append(
        Paragraph(
            fa("گزارش سامانه GolbinoAI"),
            title_style
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            fa("گزارش نمایشی - فاقد اعتبار تشخیصی"),
            normal_style
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            fa("نام فایل: " + report["filename"]),
            normal_style
        )
    )

    story.append(
        Paragraph(
            fa("تاریخ ثبت: " + report["date"]),
            normal_style
        )
    )

    story.append(Spacer(1, 20))

    table_data = [
        [
            Paragraph(fa("نام سلول"), normal_style),
            Paragraph(fa("تعداد نمایشی"), normal_style),
            Paragraph(fa("درصد نمایشی"), normal_style),
        ]
    ]

    for row in report["results"]:

        table_data.append([
            Paragraph(fa(row["name"]), normal_style),
            Paragraph(str(row["count"]), normal_style),
            Paragraph(str(row["percentage"]) + "%", normal_style),
        ])

    table = Table(
        table_data,
        colWidths=[220, 100, 100],
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAE3F6")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8D0E5")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ])
    )

    story.append(table)
    story.append(Spacer(1, 24))

    story.append(
        Paragraph(
            fa(
                "توجه: اعداد این گزارش صرفاً برای نمایش قابلیت‌های رابط کاربری "
                "تولید شده‌اند و حاصل تحلیل تصویر یا مدل یادگیری عمیق نیستند."
            ),
            normal_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# 8. نوار کناری و منو
# =========================================================

PAGES = [
    "خانه",
    "بررسی تصویر",
    "نمونه‌های نمایشی",
    "گزارش‌ها",
    "راهنمای سلول‌ها",
    "درباره پروژه",
]

with st.sidebar:

    logo = load_logo()

    if logo:
        st.image(logo, width=115)
    else:
        st.markdown(
            "<div style='font-size:3.5rem;text-align:center;'>🩸</div>",
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div style="text-align:center;margin-bottom:20px;">

            <div style="
                font-size:1.65rem;
                font-weight:850;
                color:#302941;
            ">
                GolbinoAI
            </div>

            <div style="
                font-size:.76rem;
                color:#71697F;
                direction:ltr;
            ">
                Intelligent Blood Cell Analysis
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### فضای کاری")

    current_page = st.session_state.page

    selected_index = (
        PAGES.index(current_page)
        if current_page in PAGES
        else 0
    )

    selected_page = st.radio(
        "منوی اصلی",
        PAGES,
        index=selected_index,
        label_visibility="collapsed"
    )

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

    st.markdown("---")

    st.markdown(
        """
        <div style="
            background:rgba(255,255,255,.58);
            border:1px solid rgba(255,255,255,.90);
            border-radius:17px;
            padding:15px;
            box-shadow:0 8px 22px rgba(65,48,100,.06);
        ">

            <div style="
                color:#302941;
                font-weight:800;
                margin-bottom:10px;
            ">
                وضعیت سامانه
            </div>

            <div style="color:#625B70;font-size:.84rem;line-height:2.2;">
                رابط کاربری: فعال<br>
                بارگذاری تصویر: فعال<br>
                مدل تشخیص: متصل نشده<br>
                حالت: نسخه پژوهشی
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 9. صفحه خانه
# =========================================================

if st.session_state.page == "خانه":

    st.markdown(
        """
        <div class="hero">

            <div class="eyebrow">
                نسل جدید تحلیل تصاویر خون محیطی
            </div>

            <div class="hero-title">
                نگاهی هوشمندتر<br>
                به دنیای سلول‌های خونی
            </div>

            <div class="hero-subtitle">
                GolbinoAI بستری پژوهشی برای بررسی تصاویر میکروسکوپی
                خون محیطی، مطالعه پنج گروه اصلی گلبول سفید و توسعه
                ابزارهای هوشمند در حوزه خون‌شناسی است.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns([1.25, 0.85], gap="large")

    with left:

        st.markdown(
            """
            <div class="glass-card" style="min-height:230px;">

                <div class="eyebrow">
                    شروع کار
                </div>

                <div style="
                    font-size:1.55rem;
                    font-weight:850;
                    color:#302941;
                    margin-bottom:12px;
                ">
                    آماده بررسی یک تصویر هستید؟
                </div>

                <div class="muted">
                    تصویر اسمیر خون محیطی خود را بارگذاری کنید و
                    اطلاعات و پیش‌نمایش آن را در محیط GolbinoAI مشاهده کنید.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "🔬  شروع بررسی تصویر",
            use_container_width=True,
            key="home_start"
        ):
            navigate("بررسی تصویر")

    with right:

        if logo := load_logo():
            st.image(logo, use_container_width=True)

        else:
            st.markdown(
                """
                <div class="glass-card" style="
                    min-height:230px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:6rem;
                ">
                    🩸
                </div>
                """,
                unsafe_allow_html=True
            )

    render_section(
        "قابلیت‌های سامانه",
        "ابزارهایی برای یک تجربه پژوهشی منظم و قابل توسعه"
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        render_card(
            "بارگذاری تصویر",
            "دریافت تصاویر میکروسکوپی با فرمت‌های رایج و نمایش پیش‌نمایش.",
            "📤"
        )

    with c2:
        render_card(
            "مطالعه پنج گروه سلولی",
            "آشنایی با نوتروفیل، لنفوسیت، مونوسیت، ائوزینوفیل و بازوفیل.",
            "🔬"
        )

    with c3:
        render_card(
            "گزارش پژوهشی",
            "ساختار اولیه گزارش و خروجی PDF برای نتایج نمایشی.",
            "📄"
        )

    render_section("گروه‌های سلولی مورد مطالعه")

    cols = st.columns(5)

    for col, (key, info) in zip(cols, CELL_INFO.items()):

        with col:

            st.markdown(
                f"""
                <div class="metric-card">

                    <div style="
                        width:12px;
                        height:12px;
                        border-radius:50%;
                        background:{info['color']};
                        box-shadow:0 0 12px {info['color']};
                        margin-bottom:13px;
                    "></div>

                    <div style="
                        font-weight:800;
                        color:#302941;
                    ">
                        {info['fa']}
                    </div>

                    <div style="
                        font-size:.74rem;
                        color:#81798E;
                        direction:ltr;
                        text-align:right;
                        margin-top:5px;
                    ">
                        {key}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    render_footer()


# =========================================================
# 10. صفحه بررسی تصویر
# =========================================================

elif st.session_state.page == "بررسی تصویر":

    render_page_header(
        "بررسی تصویر",
        "تصویر میکروسکوپی خون محیطی را بارگذاری و اطلاعات آن را مشاهده کنید."
    )

    st.markdown(
        """
        <div class="glass-card">

            <div style="
                font-size:1.15rem;
                font-weight:800;
                color:#302941;
                margin-bottom:10px;
            ">
                📁 انتخاب تصویر
            </div>

            <div class="muted">
                فرمت‌های مجاز: JPG، JPEG، PNG و TIFF
                <br>
                برای بررسی پژوهشی، تصویر باید وضوح و کیفیت مناسبی داشته باشد.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "تصویر موردنظر را انتخاب کنید",
        type=["jpg", "jpeg", "png", "tif", "tiff"],
        key="image_uploader"
    )

    if uploaded_file is not None:

        try:

            image = Image.open(uploaded_file).convert("RGB")

            st.session_state.uploaded_image = image
            st.session_state.uploaded_name = uploaded_file.name
            st.session_state.uploaded_size = uploaded_file.size

            render_section("پیش‌نمایش تصویر")

            image_col, info_col = st.columns(
                [1.35, 1],
                gap="large"
            )

            with image_col:

                st.image(
                    image,
                    caption=uploaded_file.name,
                    use_container_width=True
                )

            with info_col:

                st.markdown(
                    f"""
                    <div class="glass-card">

                        <div style="
                            font-weight:800;
                            font-size:1.1rem;
                            color:#302941;
                            margin-bottom:15px;
                        ">
                            اطلاعات فایل
                        </div>

                        <div class="muted">
                            نام فایل:
                            <b>{html.escape(uploaded_file.name)}</b>
                            <br>
                            ابعاد تصویر:
                            <b>{image.width} × {image.height}</b>
                            <br>
                            فرمت:
                            <b>{image.format or 'نامشخص'}</b>
                            <br>
                            حجم:
                            <b>{uploaded_file.size / 1024:.1f} KB</b>
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    """
                    <div class="glass-card">

                        <span class="status-pill">
                            مدل تشخیص متصل نشده
                        </span>

                        <div style="
                            font-weight:800;
                            color:#302941;
                            margin-top:13px;
                            margin-bottom:7px;
                        ">
                            وضعیت پردازش
                        </div>

                        <div class="muted">
                            تصویر با موفقیت بارگذاری شده است.
                            در نسخه فعلی، مدل یادگیری عمیق به برنامه
                            متصل نیست و تشخیص واقعی انجام نمی‌شود.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if st.button(
                "🔍  بررسی تصویر",
                use_container_width=True,
                key="analyze_image"
            ):

                st.warning(
                    "تصویر دریافت شده است؛ اما مدل تشخیص هنوز متصل نیست. "
                    "بنابراین هیچ شناسایی، شمارش یا نتیجه تشخیصی تولید نشده است."
                )

        except Exception as error:

            st.error(f"خطا در خواندن تصویر: {error}")

    else:

        st.markdown(
            """
            <div class="glass-card" style="
                text-align:center;
                padding:50px 20px;
            ">

                <div style="
                    font-size:3.5rem;
                    margin-bottom:12px;
                ">
                    🖼️
                </div>

                <div style="
                    font-size:1.2rem;
                    font-weight:800;
                    color:#302941;
                ">
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
# 11. صفحه نمونه‌های نمایشی
# =========================================================

elif st.session_state.page == "نمونه‌های نمایشی":

    render_page_header(
        "نمونه‌های نمایشی",
        "تصاویر و داده‌های زیر صرفاً برای نمایش رابط کاربری ساخته شده‌اند."
    )

    st.warning(
        "تصاویر این صفحه مصنوعی هستند و داده میکروسکوپی واقعی نیستند. "
        "اعداد نمونه نیز خروجی مدل هوش مصنوعی نیستند."
    )

    demo_results = {
        "Neutrophil": 42,
        "Lymphocyte": 28,
        "Monocyte": 12,
        "Eosinophil": 10,
        "Basophil": 8,
    }

    for sample in DEMO_SAMPLES:

        render_section(sample["name"], sample["description"])

        image_col, result_col = st.columns(
            [1.2, 1],
            gap="large"
        )

        with image_col:

            st.image(
                sample["image"],
                use_container_width=True,
                caption="تصویرسازی مصنوعی - فاقد داده میکروسکوپی واقعی"
            )

        with result_col:

            st.markdown(
                """
                <div class="glass-card">

                    <span class="status-pill">
                        نتیجه کاملاً نمایشی
                    </span>

                    <div style="
                        font-size:1.2rem;
                        font-weight:800;
                        color:#302941;
                        margin-top:13px;
                    ">
                        خلاصه نمونه
                    </div>

                    <div class="muted">
                        مقادیر زیر فقط برای نمایش نحوه ارائه نتایج هستند.
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            for cell, count in demo_results.items():

                info = CELL_INFO[cell]

                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;

                        padding:11px 14px;
                        margin:7px 0;

                        background:rgba(255,255,255,.68);

                        border:1px solid rgba(255,255,255,.92);
                        border-radius:13px;

                        box-shadow:0 5px 15px rgba(65,48,100,.045);
                    ">

                        <span style="
                            color:{info['color']};
                            font-weight:800;
                        ">
                            {info['fa']}
                        </span>

                        <span style="
                            color:#302941;
                            direction:ltr;
                            font-weight:800;
                        ">
                            {count}
                        </span>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")

    render_footer()


# =========================================================
# 12. صفحه گزارش‌ها
# =========================================================

elif st.session_state.page == "گزارش‌ها":

    render_page_header(
        "گزارش‌ها",
        "مشاهده گزارش‌های نمایشی و دریافت خروجی PDF."
    )

    st.warning(
        "این بخش شامل داده‌های نمونه است. هیچ‌کدام از اعداد زیر "
        "از تحلیل واقعی تصویر به دست نیامده‌اند."
    )

    demo_results = {
        "Neutrophil": 42,
        "Lymphocyte": 28,
        "Monocyte": 12,
        "Eosinophil": 10,
        "Basophil": 8,
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        render_metric("100", "تعداد کل نمایشی")

    with col2:
        render_metric("5", "گروه سلولی")

    with col3:
        render_metric("DEMO", "نوع گزارش")

    render_section("جدول خلاصه")

    table_rows = []

    for cell, count in demo_results.items():

        table_rows.append({
            "نام انگلیسی": cell,
            "نام فارسی": CELL_INFO[cell]["fa"],
            "تعداد نمایشی": count,
            "درصد نمایشی": f"{count}%"
        })

    df = pd.DataFrame(table_rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    report_filename = (
        st.session_state.uploaded_name
        or "Demo_Sample"
    )

    report = {
        "filename": report_filename,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "results": [
            {
                "name": CELL_INFO[cell]["fa"],
                "count": count,
                "percentage": count,
            }
            for cell, count in demo_results.items()
        ]
    }

    if st.button(
        "ساخت گزارش PDF",
        use_container_width=True
    ):

        try:

            pdf_data = make_persian_pdf(report)

            st.download_button(
                "⬇️ دریافت گزارش PDF",
                data=pdf_data,
                file_name="GolbinoAI_Demo_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as error:

            st.error(str(error))

    render_footer()


# =========================================================
# 13. صفحه راهنمای سلول‌ها
# =========================================================

elif st.session_state.page == "راهنمای سلول‌ها":

    render_page_header(
        "راهنمای سلول‌ها",
        "آشنایی مقدماتی با پنج گروه اصلی گلبول سفید."
    )

    for cell, info in CELL_INFO.items():

        st.markdown(
            f"""
            <div class="glass-card">

                <div style="
                    display:flex;
                    align-items:center;
                    gap:12px;
                ">

                    <div style="
                        width:13px;
                        height:13px;
                        flex-shrink:0;

                        border-radius:50%;

                        background:{info['color']};
                        box-shadow:0 0 13px {info['color']};
                    "></div>

                    <div style="
                        font-size:1.2rem;
                        font-weight:850;
                        color:#302941;
                    ">
                        {info['fa']}
                    </div>

                    <div style="
                        direction:ltr;
                        color:#81798E;
                        font-size:.83rem;
                        margin-right:auto;
                    ">
                        {cell}
                    </div>

                </div>

                <div class="muted" style="margin-top:13px;">
                    {info['description']}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    render_footer()


# =========================================================
# 14. صفحه درباره پروژه
# =========================================================

elif st.session_state.page == "درباره پروژه":

    render_page_header(
        "درباره GolbinoAI",
        "یک پروژه پژوهشی در مسیر توسعه ابزارهای هوشمند خون‌شناسی."
    )

    st.markdown(
        """
        <div class="glass-card">

            <div style="
                font-size:1.6rem;
                font-weight:850;
                color:#302941;
            ">
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

    render_section("اهداف پژوهشی")

    col1, col2 = st.columns(2)

    with col1:

        render_card(
            "تشخیص و مکان‌یابی",
            "توسعه مدل‌های بینایی ماشین برای شناسایی و مکان‌یابی سلول‌های سفید خون.",
            "🎯"
        )

    with col2:

        render_card(
            "ارزیابی مدل",
            "بررسی عملکرد مدل با معیارهایی مانند Precision، Recall و mAP.",
            "📊"
        )

    render_section("گروه‌های مورد بررسی")

    for cell, info in CELL_INFO.items():

        st.markdown(
            f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;

                padding:13px 16px;
                margin:8px 0;

                border-radius:14px;

                background:rgba(255,255,255,.68);
                border:1px solid rgba(255,255,255,.92);

                box-shadow:0 5px 15px rgba(65,48,100,.04);
            ">

                <span style="
                    color:#302941;
                    font-weight:750;
                ">
                    {info['fa']}
                </span>

                <span style="
                    direction:ltr;
                    color:#81798E;
                    font-size:.85rem;
                ">
                    {cell}
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown(
        """
        <div class="muted">
            <b style="color:#302941;">وضعیت توسعه:</b>
            نسخه فعلی شامل رابط کاربری و محتوای نمایشی است.
            مدل تشخیص هنوز به برنامه متصل نشده است.
        </div>
        """,
        unsafe_allow_html=True
    )

    render_footer()
