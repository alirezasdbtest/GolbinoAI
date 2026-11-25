
import streamlit as st
from pathlib import Path
from PIL import Image
import base64
import io

# ==========================================
# GolbinoAI | Modern Medical AI Interface
# ==========================================

st.set_page_config(
    page_title="GolbinoAI | هوش مصنوعی خون‌شناسی",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

def load_image_base64(path):
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return None

logo = load_image_base64(ASSETS_DIR / "logo.png")

# ---------- CSS ----------
st.markdown("""
<style>

/* Persian font */
@import url('https://fonts.googleapis.com/css2?family=Estedad:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg: #f5f3fa;
    --text: #29253a;
    --muted: #716b83;
    --purple: #8b70d6;
    --pink: #e9a4c7;
    --blue: #9bc9ed;
    --mint: #9edcc8;
}

/* Main app */
html, body, [class*="css"], .stApp {
    font-family: 'Estedad', sans-serif !important;
    color: var(--text) !important;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 10%, rgba(220,190,255,.42), transparent 38%),
        radial-gradient(ellipse at 90% 20%, rgba(255,197,222,.40), transparent 35%),
        radial-gradient(ellipse at 50% 100%, rgba(174,220,255,.42), transparent 40%),
        #f7f5fb;
    direction: rtl;
}

/* Main content */
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* All text */
p, label, span, div, h1, h2, h3, h4 {
    font-family: 'Estedad', sans-serif !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,.52) !important;
    backdrop-filter: blur(32px) saturate(180%);
    -webkit-backdrop-filter: blur(32px) saturate(180%);
    border-left: 1px solid rgba(255,255,255,.85);
    box-shadow: -8px 0 35px rgba(80,60,120,.07);
}

section[data-testid="stSidebar"] * {
    direction: rtl;
    text-align: right;
}

/* Glass panels */
.glass {
    position: relative;
    overflow: hidden;
    background: linear-gradient(
        135deg,
        rgba(255,255,255,.78),
        rgba(255,255,255,.38)
    );
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid rgba(255,255,255,.9);
    border-top: 1px solid rgba(255,255,255,1);
    border-radius: 28px;
    box-shadow:
        0 12px 40px rgba(91,70,130,.09),
        inset 0 1px 1px rgba(255,255,255,.95),
        inset 0 -1px 1px rgba(160,140,190,.08);
    padding: 28px;
}

.glass::before {
    content: "";
    position: absolute;
    top: 0;
    left: 8%;
    width: 84%;
    height: 1px;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255,255,255,1),
        transparent
    );
}

/* Hero */
.hero {
    padding: 48px 42px;
    border-radius: 34px;
    background:
        radial-gradient(circle at 5% 10%, rgba(255,255,255,.8), transparent 35%),
        linear-gradient(125deg, rgba(225,211,255,.82), rgba(255,220,235,.78), rgba(213,237,255,.82));
    border: 1px solid rgba(255,255,255,.95);
    box-shadow: 0 18px 55px rgba(116,90,160,.12),
                inset 0 1px 2px white;
    position: relative;
    overflow: hidden;
}

.hero h1 {
    color: #39304e !important;
    font-size: clamp(28px, 4vw, 43px) !important;
    font-weight: 800 !important;
    line-height: 1.8 !important;
}

.hero p {
    color: #554d68 !important;
    font-size: 16px;
    line-height: 2.1;
}

/* Titles */
h1, h2, h3 {
    color: #342d47 !important;
    font-weight: 700 !important;
}

/* Body text */
.stMarkdown, .stMarkdown p, .stMarkdown li {
    color: #484256 !important;
    line-height: 2;
}

/* Metric */
[data-testid="stMetric"] {
    background: rgba(255,255,255,.68);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,.9);
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 8px 25px rgba(80,60,120,.06);
}

[data-testid="stMetricValue"] {
    color: #6550a0 !important;
    font-weight: 800 !important;
}

/* Buttons */
.stButton > button {
    font-family: 'Estedad', sans-serif !important;
    border-radius: 18px !important;
    border: 1px solid rgba(255,255,255,.95) !important;
    background: linear-gradient(135deg, #a58be4, #d59bc8) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px 25px !important;
    box-shadow: 0 7px 20px rgba(137,105,190,.22);
    transition: all .25s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(137,105,190,.3);
}

/* Inputs */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,.8) !important;
    color: #302a40 !important;
    border: 1px solid #e1d9ef !important;
    border-radius: 15px !important;
    font-family: 'Estedad', sans-serif !important;
}

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,.65);
    border: 1px dashed #b8a7dc;
    border-radius: 22px;
    padding: 15px;
}

/* Upload text */
[data-testid="stFileUploader"] * {
    color: #51466d !important;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"] {
    background: rgba(255,255,255,.8);
    border-radius: 14px;
}

/* Tables */
[data-testid="stDataFrame"] {
    direction: ltr;
    border-radius: 16px;
    overflow: hidden;
}

/* English and numeric data */
.ltr {
    direction: ltr !important;
    unicode-bidi: isolate;
    display: inline-block;
    text-align: left;
}

/* Sidebar navigation */
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255,255,255,.45);
    border-radius: 13px;
    padding: 8px 12px;
    margin-bottom: 5px;
}

/* Footer */
footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

/* Responsive */
@media(max-width: 768px) {
    .hero {
        padding: 28px 22px;
    }
    .glass {
        padding: 20px;
        border-radius: 22px;
    }
}

</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    if logo:
        st.markdown(
            f'<div style="text-align:center;padding:12px">'
            f'<img src="data:image/png;base64,{logo}" '
            f'style="width:115px;height:115px;object-fit:contain;">'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<h1 style='text-align:center;color:#765db1'>🩸 GolbinoAI</h1>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<p style='text-align:center;color:#81758f;font-size:12px'>"
        "سامانه هوشمند تحلیل سلول‌های خونی</p>",
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "منوی اصلی",
        ["خانه", "تحلیل تصویر", "راهنمای سلول‌ها", "گزارش‌ها", "درباره پروژه"],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("GolbinoAI · Research Prototype")

# ---------- Home ----------
if page == "خانه":

    st.markdown("""
    <div class="hero">
        <div style="font-size:14px;color:#65558c;font-weight:600">
            ✦ هوش مصنوعی در خدمت علوم پزشکی
        </div>
        <h1>از یک قطره خون، تا بینشی هوشمند.</h1>
        <p>
            به GolbinoAI خوش آمدید؛ بستری پژوهشی برای تحلیل هوشمند
            تصاویر میکروسکوپی و شناسایی انواع گلبول‌های سفید.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.subheader("نگاهی به دنیای سلول‌های خونی")

    cols = st.columns(5)

    cells = [
        ("Neutrophil", "نوتروفیل", "🟣", "#eee5ff"),
        ("Lymphocyte", "لنفوسیت", "🔵", "#e4efff"),
        ("Monocyte", "مونوسیت", "🟢", "#e1f5ed"),
        ("Eosinophil", "ائوزینوفیل", "🩷", "#ffe8ef"),
        ("Basophil", "بازوفیل", "🟠", "#fff0dc"),
    ]

    for col, (en, fa, emoji, color) in zip(cols, cells):
        with col:
            st.markdown(f"""
            <div class="glass" style="padding:20px 10px;text-align:center">
                <div style="font-size:32px">{emoji}</div>
                <div style="font-weight:700;color:#39304e">{fa}</div>
                <div dir="ltr" style="font-size:11px;color:#706782">{en}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    st.subheader("نمای کلی سامانه")

    c1, c2, c3 = st.columns(3)
    c1.metric("گروه سلولی", "۵", "کلاس هدف")
    c2.metric("نوع سامانه", "AI", "تحلیل تصویر")
    c3.metric("وضعیت مدل", "در حال توسعه", "نسخه پژوهشی")

    st.info("در نسخه فعلی، مدل تشخیص هنوز به رابط کاربری متصل نشده است.")

# ---------- Image Analysis ----------
elif page == "تحلیل تصویر":

    st.title("تحلیل تصویر میکروسکوپی")
    st.write("تصویر اسمیر خون محیطی خود را برای مشاهده و آماده‌سازی بارگذاری کنید.")

    uploaded = st.file_uploader(
        "انتخاب تصویر",
        type=["png", "jpg", "jpeg", "tif", "tiff"]
    )

    if uploaded:
        image = Image.open(uploaded)

        st.success("تصویر با موفقیت بارگذاری شد.")

        left, right = st.columns([1.5, 1])

        with left:
            st.image(image, caption="تصویر بارگذاری‌شده", use_container_width=True)

        with right:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.subheader("مشخصات تصویر")
            st.write(f"**نام فایل:** {uploaded.name}")
            st.write(f"**ابعاد:** {image.width} × {image.height}")
            st.write(f"**فرمت:** {image.format}")
            st.write(f"**حالت رنگی:** {image.mode}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.warning(
            "مدل هوش مصنوعی هنوز به این بخش متصل نشده است؛ "
            "بنابراین نتیجه تشخیص یا شمارش سلولی نمایش داده نمی‌شود."
        )

# ---------- Cell Guide ----------
elif page == "راهنمای سلول‌ها":

    st.title("راهنمای انواع گلبول سفید")

    descriptions = [
        ("Neutrophil", "نوتروفیل", "فراوان‌ترین نوع گلبول سفید و از اجزای اصلی دفاع ذاتی بدن."),
        ("Lymphocyte", "لنفوسیت", "از اجزای مهم سیستم ایمنی اختصاصی."),
        ("Monocyte", "مونوسیت", "در دفاع ایمنی و تبدیل به ماکروفاژها نقش دارد."),
        ("Eosinophil", "ائوزینوفیل", "در پاسخ‌های آلرژیک و مقابله با برخی انگل‌ها نقش دارد."),
        ("Basophil", "بازوفیل", "در واکنش‌های حساسیتی و آزادسازی هیستامین نقش دارد."),
    ]

    for en, fa, desc in descriptions:
        with st.container():
            st.markdown(f"""
            <div class="glass" style="margin-bottom:14px">
                <div dir="ltr" style="color:#856bc1;font-size:12px">{en}</div>
                <h3>{fa}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

# ---------- Reports ----------
elif page == "گزارش‌ها":

    st.title("گزارش‌های تحلیل")
    st.markdown("""
    <div class="glass">
        <h3>هنوز گزارشی ثبت نشده است.</h3>
        <p>پس از اتصال مدل و پیاده‌سازی تاریخچه تحلیل‌ها،
        گزارش‌های شما در این قسمت نمایش داده خواهند شد.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------- About ----------
elif page == "درباره پروژه":

    st.title("درباره GolbinoAI")

    st.markdown("""
    <div class="glass">
        <h2>GolbinoAI</h2>
        <p>
        یک پروژه پژوهشی در زمینه پردازش تصویر پزشکی و یادگیری عمیق
        با تمرکز بر شناسایی و طبقه‌بندی پنج گروه اصلی گلبول سفید
        در تصاویر میکروسکوپی اسمیر خون محیطی است.
        </p>
        <p dir="ltr">Neutrophil · Lymphocyte · Monocyte · Eosinophil · Basophil</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption("GolbinoAI — Research Prototype")
