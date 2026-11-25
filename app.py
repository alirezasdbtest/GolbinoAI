
import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
from io import BytesIO
import random
import math
import base64

# =========================================
# GolbinoAI | Medical AI Research Interface
# =========================================

st.set_page_config(
    page_title="GolbinoAI | تحلیل هوشمند خون",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE = Path(__file__).parent
ASSETS = BASE / "assets"
FONTS = ASSETS / "fonts"

# ---------- Session state ----------
if "page" not in st.session_state:
    st.session_state.page = "خانه"

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "selected_demo" not in st.session_state:
    st.session_state.selected_demo = 0

# ---------- Demo image generator ----------
def make_blood_image(seed=1, size=(900, 620)):
    random.seed(seed)
    img = Image.new("RGB", size, (225, 190, 198))
    draw = ImageDraw.Draw(img, "RGBA")

    # Background texture
    for _ in range(4500):
        x = random.randint(0, size[0])
        y = random.randint(0, size[1])
        r = random.randint(1, 4)
        color = random.choice([
            (255, 225, 230, 30),
            (130, 75, 90, 18),
            (255, 245, 240, 35)
        ])
        draw.ellipse((x-r, y-r, x+r, y+r), fill=color)

    # Red blood cells
    for _ in range(42):
        x = random.randint(25, size[0]-25)
        y = random.randint(25, size[1]-25)
        r = random.randint(17, 29)
        draw.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=(178, 75, 91, 125),
            outline=(130, 48, 70, 110),
            width=3
        )
        draw.ellipse(
            (x-r//2, y-r//2, x+r//2, y+r//2),
            fill=(235, 165, 170, 110)
        )

    # White blood cell
    cx, cy = size[0]//2, size[1]//2
    radius = 68
    draw.ellipse(
        (cx-radius, cy-radius, cx+radius, cy+radius),
        fill=(244, 228, 222, 245),
        outline=(255, 255, 255, 255),
        width=7
    )

    # Nucleus
    for _ in range(5):
        angle = random.uniform(0, math.pi*2)
        x = cx + int(math.cos(angle)*25)
        y = cy + int(math.sin(angle)*25)
        r = random.randint(18, 27)
        draw.ellipse(
            (x-r, y-r, x+r, y+r),
            fill=(93, 67, 145, 230),
            outline=(70, 48, 120, 240),
            width=3
        )

    # Subtle blur for microscope-like appearance
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    return img


DEMO_IMAGES = [
    make_blood_image(12),
    make_blood_image(28)
]

DEMO_RESULTS = [
    {
        "name": "نمونه آزمایشی شماره ۱",
        "cells": [
            ("Neutrophil", "نوتروفیل", 12, "۷۵٪"),
            ("Lymphocyte", "لنفوسیت", 5, "۸۲٪"),
            ("Monocyte", "مونوسیت", 2, "۷۸٪"),
            ("Eosinophil", "ائوزینوفیل", 1, "۷۱٪"),
            ("Basophil", "بازوفیل", 0, "—"),
        ],
        "total": 20
    },
    {
        "name": "نمونه آزمایشی شماره ۲",
        "cells": [
            ("Neutrophil", "نوتروفیل", 8, "۸۱٪"),
            ("Lymphocyte", "لنفوسیت", 9, "۸۷٪"),
            ("Monocyte", "مونوسیت", 1, "۷۴٪"),
            ("Eosinophil", "ائوزینوفیل", 2, "۷۹٪"),
            ("Basophil", "بازوفیل", 1, "۷۰٪"),
        ],
        "total": 21
    }
]

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Estedad:wght@300;400;500;600;700;800&display=swap');

:root {
    --ink: #29243a;
    --muted: #625b72;
    --purple: #7656bd;
    --pink: #c879a6;
    --glass: rgba(255,255,255,.40);
    --line: rgba(255,255,255,.76);
}

html, body, [class*="css"], .stApp {
    font-family: 'Estedad', sans-serif !important;
}

.stApp {
    background:
      radial-gradient(ellipse at 8% 8%, rgba(174,146,220,.38), transparent 36%),
      radial-gradient(ellipse at 95% 18%, rgba(220,151,181,.32), transparent 34%),
      radial-gradient(ellipse at 55% 95%, rgba(137,176,211,.38), transparent 42%),
      linear-gradient(135deg, #d8d4e3 0%, #e5dce7 48%, #d4dce8 100%);
    background-attachment: fixed;
    color: var(--ink);
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4, p, label, li, span {
    font-family: 'Estedad', sans-serif !important;
}

h1, h2, h3, h4 {
    color: #30283f !important;
    font-weight: 750 !important;
}

p, li, label {
    color: #40394e;
    line-height: 2;
}

small {
    color: #5d536e !important;
}

/* Strong Liquid Glass surfaces */
.glass {
    position: relative;
    isolation: isolate;
    overflow: hidden;
    background:
      linear-gradient(135deg,
        rgba(255,255,255,.72) 0%,
        rgba(255,255,255,.32) 42%,
        rgba(245,239,255,.40) 100%);
    backdrop-filter: blur(32px) saturate(190%);
    -webkit-backdrop-filter: blur(32px) saturate(190%);
    border: 1px solid rgba(255,255,255,.88);
    border-top: 1.5px solid rgba(255,255,255,.98);
    border-left: 1px solid rgba(255,255,255,.82);
    border-radius: 28px;
    box-shadow:
      0 22px 55px rgba(62,48,92,.13),
      0 5px 15px rgba(62,48,92,.07),
      inset 0 1.5px 1px rgba(255,255,255,.95),
      inset 0 -1px 2px rgba(90,70,120,.10);
}

.glass:before {
    content: "";
    position: absolute;
    z-index: -1;
    top: -55%;
    left: -20%;
    width: 140%;
    height: 85%;
    transform: rotate(-12deg);
    background: linear-gradient(
      180deg,
      rgba(255,255,255,.48),
      rgba(255,255,255,.04),
      transparent
    );
    pointer-events: none;
}

.glass:after {
    content: "";
    position: absolute;
    top: 0;
    left: 8%;
    width: 84%;
    height: 1px;
    background: linear-gradient(90deg, transparent, white, transparent);
    pointer-events: none;
}

/* Hero */
.hero {
    position: relative;
    overflow: hidden;
    padding: 48px;
    border-radius: 36px;
    background:
      radial-gradient(circle at 85% 15%, rgba(255,255,255,.72), transparent 28%),
      linear-gradient(120deg,
        rgba(183,161,222,.78),
        rgba(229,184,207,.70),
        rgba(172,198,226,.78));
    border: 1px solid rgba(255,255,255,.92);
    box-shadow:
      0 25px 65px rgba(69,52,102,.17),
      inset 0 2px 2px rgba(255,255,255,.95);
}

.hero h1 {
    font-size: clamp(28px, 4vw, 46px) !important;
    line-height: 1.8 !important;
    color: #30263f !important;
}

.hero p {
    color: #433950 !important;
    font-size: 16px;
    max-width: 760px;
}

.hero-kicker {
    color: #55436e;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: .2px;
}

/* Glass action */
.action-glass {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 105px;
    height: 105px;
    border-radius: 32px;
    font-size: 48px;
    background: linear-gradient(145deg,
      rgba(255,255,255,.82),
      rgba(255,255,255,.30));
    border: 1px solid rgba(255,255,255,.95);
    box-shadow:
      0 16px 35px rgba(70,52,110,.18),
      inset 0 2px 2px white;
    backdrop-filter: blur(24px) saturate(180%);
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    font-family: 'Estedad', sans-serif !important;
    color: white !important;
    background: linear-gradient(125deg, #7658b9, #a16eae) !important;
    border: 1px solid rgba(255,255,255,.70) !important;
    border-radius: 17px !important;
    min-height: 48px;
    padding: 8px 22px !important;
    font-weight: 650 !important;
    box-shadow:
      0 9px 22px rgba(91,64,142,.25),
      inset 0 1px 1px rgba(255,255,255,.45);
    transition: all .22s ease;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 30px rgba(91,64,142,.32);
    border-color: white !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(245,242,250,.58) !important;
    backdrop-filter: blur(38px) saturate(190%);
    -webkit-backdrop-filter: blur(38px) saturate(190%);
    border-left: 1px solid rgba(255,255,255,.85);
    box-shadow: -12px 0 40px rgba(62,48,92,.10);
}

section[data-testid="stSidebar"] * {
    font-family: 'Estedad', sans-serif !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255,255,255,.40);
    border: 1px solid rgba(255,255,255,.58);
    border-radius: 14px;
    padding: 8px 12px;
    margin-bottom: 6px;
}

/* Inputs */
.stTextInput input, .stTextArea textarea,
[data-baseweb="select"] > div {
    background: rgba(255,255,255,.78) !important;
    color: #30283f !important;
    border: 1px solid rgba(255,255,255,.95) !important;
    border-radius: 15px !important;
}

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,.48);
    border: 1.5px dashed rgba(111,83,166,.55);
    border-radius: 22px;
    padding: 18px;
    backdrop-filter: blur(20px);
}

[data-testid="stFileUploader"] * {
    color: #40364f !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: rgba(255,255,255,.48);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,.82);
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 10px 30px rgba(62,48,92,.09),
                inset 0 1px 1px white;
}

[data-testid="stMetricLabel"] {
    color: #5d536e !important;
}

[data-testid="stMetricValue"] {
    color: #59428d !important;
    font-weight: 800 !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    direction: ltr;
    border-radius: 16px;
    overflow: hidden;
}

/* Direction helpers */
.ltr {
    direction: ltr !important;
    unicode-bidi: isolate;
    display: inline-block;
    text-align: left;
}

.caption {
    color: #625970;
    font-size: 12px;
}

hr {
    border-color: rgba(255,255,255,.7) !important;
}

#MainMenu, footer {
    visibility: hidden;
}

@media(max-width: 768px) {
    .hero { padding: 26px 22px; }
    .glass { border-radius: 22px; }
    .action-glass { width: 78px; height: 78px; font-size: 36px; }
}
</style>
""", unsafe_allow_html=True)


# ---------- Navigation helpers ----------
def go(page):
    st.session_state.page = page
    st.rerun()


def glass_start():
    st.markdown(
        '<div class="action-glass">🔬</div>',
        unsafe_allow_html=True
    )


def show_demo_result(index):
    result = DEMO_RESULTS[index]
    st.markdown(
        f'<div class="glass" style="padding:22px;margin-top:12px">'
        f'<h3>{result["name"]}</h3>'
        f'<p>نتیجه شبیه‌سازی‌شده برای نمایش رابط کاربری</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    a, b = st.columns(2)
    a.metric("تعداد سلول‌های نمونه", result["total"])
    b.metric("وضعیت", "دموی نمایشی")

    st.markdown("### طبقه‌بندی نمونه سلول‌ها")
    st.dataframe(
        {
            "Cell class": [x[0] for x in result["cells"]],
            "نام فارسی": [x[1] for x in result["cells"]],
            "تعداد": [x[2] for x in result["cells"]],
            "Confidence": [x[3] for x in result["cells"]],
        },
        use_container_width=True,
        hide_index=True
    )


# ---------- Sidebar ----------
with st.sidebar:
    logo_path = ASSETS / "logo.png"

    if logo_path.exists():
        st.image(str(logo_path), width=115)
    else:
        st.markdown(
            "<div style='font-size:40px;text-align:center'>🩸</div>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<h2 style='text-align:center;margin:0'>GolbinoAI</h2>"
        "<p style='text-align:center;color:#655b75;font-size:12px'>"
        "هوش مصنوعی در خون‌شناسی</p>",
        unsafe_allow_html=True
    )
    st.divider()

    nav = st.radio(
        "ناوبری",
        ["خانه", "تحلیل تصویر", "گزارش‌ها", "راهنمای سلول‌ها", "درباره پروژه"],
        index=[
            "خانه", "تحلیل تصویر", "گزارش‌ها",
            "راهنمای سلول‌ها", "درباره پروژه"
        ].index(st.session_state.page),
        label_visibility="collapsed"
    )

    if nav != st.session_state.page:
        go(nav)

    st.divider()
    st.caption("نسخه پژوهشی · Research Prototype")


# =========================================
# HOME
# =========================================
if st.session_state.page == "خانه":

    st.markdown("""
    <div class="hero">
        <div class="hero-kicker">✦ هوش مصنوعی در خدمت علوم پزشکی</div>
        <h1>از یک قطره خون، تا بینشی هوشمند.</h1>
        <p>
            GolbinoAI بستری پژوهشی برای تحلیل تصاویر میکروسکوپی
            اسمیر خون محیطی و شناسایی پنج گروه اصلی گلبول سفید است.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("### شروع کار با GolbinoAI")

    c1, c2, c3 = st.columns([1, 2, 2])

    with c1:
        glass_start()

    with c2:
        st.markdown("#### آماده تحلیل یک تصویر هستید؟")
        st.write("تصویر میکروسکوپی خود را بارگذاری کنید و وارد محیط بررسی شوید.")
        if st.button("شروع بررسی تصویر  ←", use_container_width=True):
            go("تحلیل تصویر")

    with c3:
        st.markdown("""
        <div class="glass" style="padding:20px;height:100%">
            <div style="font-size:30px">📄</div>
            <h3>گزارش تحلیل</h3>
            <p>مشاهده نتایج نمونه و دریافت خروجی PDF</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("مشاهده گزارش‌ها", use_container_width=True):
            go("گزارش‌ها")

    st.write("")
    st.markdown("### نمونه تصاویر میکروسکوپی")

    demo_cols = st.columns(2)

    for i, col in enumerate(demo_cols):
        with col:
            st.markdown(
                f'<div class="glass" style="padding:16px">'
                f'<h3>نمونه نمایشی {i+1}</h3>'
                f'<p>تصویر مصنوعی برای پیش‌نمایش رابط کاربری</p>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.image(DEMO_IMAGES[i], use_container_width=True)
            if st.button(
                f"مشاهده نتیجه نمونه {i+1}",
                key=f"demo_{i}",
                use_container_width=True
            ):
                st.session_state.selected_demo = i
                st.session_state.page = "گزارش‌ها"
                st.rerun()

    st.write("")
    st.markdown("### پنج گروه اصلی گلبول سفید")

    cells = [
        ("Neutrophil", "نوتروفیل", "🟣"),
        ("Lymphocyte", "لنفوسیت", "🔵"),
        ("Monocyte", "مونوسیت", "🟢"),
        ("Eosinophil", "ائوزینوفیل", "🩷"),
        ("Basophil", "بازوفیل", "🟠")
    ]

    cols = st.columns(5)
    for col, (en, fa, emoji) in zip(cols, cells):
        with col:
            st.markdown(
                f'<div class="glass" style="padding:20px 8px;text-align:center">'
                f'<div style="font-size:30px">{emoji}</div>'
                f'<b>{fa}</b><br>'
                f'<span class="ltr" style="font-size:11px">{en}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.info(
        "توجه: تصاویر و نتایج این صفحه صرفاً داده‌های ساختگی برای نمایش "
        "قابلیت‌های رابط کاربری هستند و خروجی مدل تشخیصی نیستند."
    )


# =========================================
# IMAGE ANALYSIS
# =========================================
elif st.session_state.page == "تحلیل تصویر":

    st.title("🔬 تحلیل تصویر میکروسکوپی")
    st.write("تصویر اسمیر خون محیطی را انتخاب کنید.")

    uploaded = st.file_uploader(
        "بارگذاری تصویر",
        type=["png", "jpg", "jpeg", "tif", "tiff"],
        help="فرمت‌های PNG، JPG و TIFF پشتیبانی می‌شوند."
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")

        left, right = st.columns([1.45, 1])

        with left:
            st.markdown("#### پیش‌نمایش تصویر")
            st.image(image, use_container_width=True)

        with right:
            st.markdown(
                '<div class="glass" style="padding:22px">',
                unsafe_allow_html=True
            )
            st.markdown("#### مشخصات فایل")
            st.write(f"**نام:** {uploaded.name}")
            st.write(f"**ابعاد:** {image.width} × {image.height}")
            st.write(f"**حجم:** {uploaded.size / 1024:.1f} KB")
            st.write(f"**فرمت:** {uploaded.type}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        if st.button("✨ بررسی تصویر", use_container_width=True):
            st.session_state.analysis_done = True

        if st.session_state.analysis_done:
            st.warning(
                "این خروجی صرفاً نمایشی است. مدل واقعی هنوز به سامانه متصل نشده "
                "و هیچ تشخیص پزشکی یا تحلیل واقعی انجام نشده است."
            )
            st.markdown("### پیش‌نمایش نتیجه نمایشی")
            st.image(image, caption="تصویر ورودی - بدون تشخیص واقعی")
            st.markdown(
                '<div class="glass" style="padding:20px">'
                '<h3>نتیجه آزمایشی</h3>'
                '<p>برای نمایش رابط گزارش، از نمونه نمایشی استفاده کنید. '
                'نتایج این بخش قابل استناد پزشکی نیستند.</p>'
                '</div>',
                unsafe_allow_html=True
            )
            if st.button("رفتن به گزارش نمونه"):
                st.session_state.selected_demo = 0
                go("گزارش‌ها")

    else:
        st.markdown("""
        <div class="glass" style="padding:34px;text-align:center">
            <div style="font-size:48px">🧫</div>
            <h3>منتظر تصویر شما هستیم</h3>
            <p>یک تصویر میکروسکوپی انتخاب کنید تا پیش‌نمایش آن نمایش داده شود.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### یا برای آزمایش رابط از تصاویر نمونه استفاده کنید.")
        a, b = st.columns(2)
        with a:
            st.image(DEMO_IMAGES[0], use_container_width=True)
            if st.button("استفاده از نمونه ۱", use_container_width=True):
                st.session_state.selected_demo = 0
                st.session_state.analysis_done = True
                go("گزارش‌ها")
        with b:
            st.image(DEMO_IMAGES[1], use_container_width=True)
            if st.button("استفاده از نمونه ۲", use_container_width=True):
                st.session_state.selected_demo = 1
                st.session_state.analysis_done = True
                go("گزارش‌ها")


# =========================================
# REPORTS + PDF
# =========================================
elif st.session_state.page == "گزارش‌ها":

    st.title("📄 گزارش تحلیل")
    idx = st.session_state.selected_demo
    result = DEMO_RESULTS[idx]

    st.markdown(
        '<div class="glass" style="padding:22px">'
        '<h3>گزارش نمونه آزمایشی</h3>'
        '<p>این گزارش برای آزمایش ظاهر و قابلیت خروجی PDF ساخته شده است. '
        'داده‌ها ساختگی هستند و نتیجه تشخیص واقعی محسوب نمی‌شوند.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    show_demo_result(idx)

    st.write("")
    st.markdown("### دریافت گزارش")

    def create_pdf():
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table,
            TableStyle, Image as PDFImage
        )
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_RIGHT, TA_CENTER
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=38,
            leftMargin=38,
            topMargin=38,
            bottomMargin=38
        )

        styles = getSampleStyleSheet()
        font_path = FONTS / "Vazirmatn-Regular.ttf"
        font_bold_path = FONTS / "Vazirmatn-Bold.ttf"

        persian_ready = False
        try:
            from arabic_reshaper import reshape
            from bidi.algorithm import get_display

            if font_path.exists():
                pdfmetrics.registerFont(TTFont("Vazirmatn", str(font_path)))
                font_name = "Vazirmatn"
                if font_bold_path.exists():
                    pdfmetrics.registerFont(
                        TTFont("Vazirmatn-Bold", str(font_bold_path))
                    )
                    bold_name = "Vazirmatn-Bold"
                else:
                    bold_name = font_name
                persian_ready = True
            else:
                font_name = "Helvetica"
                bold_name = "Helvetica-Bold"

            def rtl(text):
                if persian_ready:
                    return get_display(reshape(str(text)))
                return str(text)

        except Exception:
            font_name = "Helvetica"
            bold_name = "Helvetica-Bold"

            def rtl(text):
                return str(text)

        title_style = ParagraphStyle(
            "TitleCustom",
            parent=styles["Title"],
            fontName=bold_name,
            fontSize=19,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#59428d")
        )

        normal_style = ParagraphStyle(
            "NormalCustom",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=10,
            leading=18,
            alignment=TA_RIGHT
        )

        story = []
        story.append(Paragraph("GolbinoAI", title_style))
        story.append(Paragraph(
            rtl("گزارش نمایشی تحلیل تصویر میکروسکوپی"),
            title_style
        ))
        story.append(Spacer(1, 18))
        story.append(Paragraph(
            rtl("هشدار: این گزارش شامل داده‌های ساختگی است و خروجی مدل واقعی نیست."),
            normal_style
        ))
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            rtl("نام نمونه: " + result["name"]),
            normal_style
        ))
        story.append(Paragraph(
            rtl("تعداد کل سلول‌های نمونه: " + str(result["total"])),
            normal_style
        ))
        story.append(Spacer(1, 18))

        table_data = [
            ["Cell class", rtl("نام فارسی"), rtl("تعداد"), "Confidence"]
        ]

        for en, fa, count, confidence in result["cells"]:
            table_data.append([en, rtl(fa), str(count), confidence])

        table = Table(
            table_data,
            colWidths=[135, 130, 75, 100],
            repeatRows=1
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7658b9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#ddd5eb")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f5f1fa")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))

        story.append(table)
        story.append(Spacer(1, 22))
        story.append(Paragraph(
            rtl("این خروجی صرفاً برای نمایش قابلیت گزارش‌گیری سامانه تولید شده است."),
            normal_style
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue(), persian_ready

    try:
        pdf_bytes, persian_pdf = create_pdf()

        if not persian_pdf:
            st.warning(
                "برای نمایش صحیح فارسی در PDF، فایل‌های فونت Vazirmatn "
                "را طبق راهنما در پوشه assets/fonts قرار بده."
            )

        st.download_button(
            "⬇️ دانلود گزارش PDF",
            data=pdf_bytes,
            file_name=f"GolbinoAI_Demo_Report_{idx+1}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"ساخت PDF با خطا مواجه شد: {e}")


# =========================================
# CELL GUIDE
# =========================================
elif st.session_state.page == "راهنمای سلول‌ها":

    st.title("راهنمای سلول‌های سفید")

    descriptions = [
        ("Neutrophil", "نوتروفیل", "نقش مهمی در دفاع ذاتی بدن دارد."),
        ("Lymphocyte", "لنفوسیت", "از اجزای کلیدی سیستم ایمنی اختصاصی است."),
        ("Monocyte", "مونوسیت", "در پاسخ ایمنی و تبدیل به ماکروفاژ نقش دارد."),
        ("Eosinophil", "ائوزینوفیل", "در برخی پاسخ‌های آلرژیک و مقابله با انگل‌ها نقش دارد."),
        ("Basophil", "بازوفیل", "در واکنش‌های حساسیتی و آزادسازی هیستامین نقش دارد.")
    ]

    for en, fa, desc in descriptions:
        st.markdown(
            f'<div class="glass" style="padding:20px;margin-bottom:14px">'
            f'<span class="ltr">{en}</span>'
            f'<h3>{fa}</h3><p>{desc}</p></div>',
            unsafe_allow_html=True
        )


# =========================================
# ABOUT
# =========================================
elif st.session_state.page == "درباره پروژه":

    st.title("درباره GolbinoAI")

    st.markdown("""
    <div class="glass" style="padding:28px">
        <h2>GolbinoAI</h2>
        <p>
        یک پروژه پژوهشی در زمینه پردازش تصویر پزشکی و یادگیری عمیق،
        با تمرکز بر شناسایی و طبقه‌بندی پنج گروه اصلی گلبول سفید
        در تصاویر میکروسکوپی اسمیر خون محیطی است.
        </p>
        <p class="ltr">
        Neutrophil · Lymphocyte · Monocyte · Eosinophil · Basophil
        </p>
    </div>
    """, unsafe_allow_html=True)
