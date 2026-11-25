import streamlit as st
from pathlib import Path
from PIL import Image
import io
import time

st.set_page_config(
    page_title="GolbinoAI | هوش سلول‌های خونی",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
MASCOT = ASSETS / "golbino_mascot.png"

# ---------------- Theme / RTL / Liquid Glass ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap');

:root {
  --ink: #283044;
  --muted: #727b91;
  --lavender: #a99af5;
  --pink: #f6b6c9;
  --sky: #a9d8f5;
  --mint: #b9e8dc;
  --cream: #fffaf5;
  --glass: rgba(255,255,255,.62);
  --line: rgba(255,255,255,.82);
}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: 'Vazirmatn', sans-serif !important;
  color: var(--ink);
}
.stApp {
  background:
    radial-gradient(ellipse at 12% 8%, rgba(246,182,201,.36), transparent 31%),
    radial-gradient(ellipse at 88% 12%, rgba(169,216,245,.45), transparent 30%),
    radial-gradient(ellipse at 68% 82%, rgba(185,232,220,.38), transparent 33%),
    linear-gradient(135deg, #fffaf5 0%, #f8f6ff 48%, #f2faff 100%);
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(255,250,245,.38); }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(255,255,255,.76), rgba(249,246,255,.64));
  border-left: 1px solid rgba(255,255,255,.9);
  backdrop-filter: blur(28px) saturate(180%);
  -webkit-backdrop-filter: blur(28px) saturate(180%);
}
[data-testid="stSidebar"] * { font-family: 'Vazirmatn', sans-serif !important; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1440px; }
h1,h2,h3,h4,p,li,label,span,div { letter-spacing: 0 !important; }
h1,h2,h3 { color: #283044 !important; }
p,li,.stCaption { color: #606b80; }
.glass {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.88);
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(255,255,255,.78), rgba(255,255,255,.42));
  box-shadow: 0 18px 55px rgba(95,105,145,.10), inset 0 1px 0 rgba(255,255,255,.95);
  backdrop-filter: blur(26px) saturate(175%);
  -webkit-backdrop-filter: blur(26px) saturate(175%);
  padding: 24px;
}
.glass:before {
  content:"";
  position:absolute; inset:0 0 auto 0; height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,1),transparent);
}
.hero {
  background:
    radial-gradient(circle at 80% 20%, rgba(255,255,255,.72), transparent 30%),
    linear-gradient(115deg, rgba(255,255,255,.83), rgba(239,232,255,.62) 52%, rgba(226,245,255,.68));
  border:1px solid rgba(255,255,255,.92);
  border-radius:34px; padding:36px;
  box-shadow:0 24px 70px rgba(107,108,157,.13), inset 0 1px 0 white;
  backdrop-filter:blur(30px) saturate(190%);
}
.eyebrow {
  display:inline-block; padding:7px 13px; border-radius:999px;
  background:rgba(255,255,255,.72); border:1px solid white;
  color:#7768bd; font-size:13px; font-weight:700;
}
.brand { font-size:34px; font-weight:900; color:#4f477f; line-height:1.2; }
.brand span { color:#9b85e8; }
.hero-title { font-size: clamp(30px, 4vw, 48px); font-weight:900; line-height:1.5; color:#30334b; margin:14px 0 8px; }
.hero-sub { font-size:17px; line-height:2.1; color:#667087; max-width:650px; }
.metric {
  border-radius:22px; padding:19px 20px; min-height:112px;
  background:rgba(255,255,255,.58); border:1px solid rgba(255,255,255,.9);
  box-shadow:0 12px 35px rgba(105,112,150,.08), inset 0 1px 0 white;
  backdrop-filter:blur(20px) saturate(170%);
}
.metric-label { color:#778096; font-size:13px; }
.metric-value { color:#3d4260; font-size:27px; font-weight:900; margin-top:8px; }
.section-title {font-size:23px;font-weight:850;color:#333750;margin:8px 0 16px;}
.soft-chip {display:inline-block;padding:6px 11px;border-radius:99px;background:rgba(169,154,245,.14);color:#7768bd;font-size:12px;font-weight:700;}
.cell-card {
 border:1px solid rgba(255,255,255,.92); border-radius:20px;
 background:rgba(255,255,255,.56); padding:16px;
 box-shadow:0 10px 28px rgba(110,117,150,.07);
}
.cell-dot {width:11px;height:11px;border-radius:50%;display:inline-block;margin-left:8px;}
div.stButton > button {
 border:1px solid rgba(255,255,255,.95) !important;
 border-radius:15px !important; padding:.65rem 1.2rem !important;
 background:linear-gradient(120deg,#a99af5,#8dc9eb) !important;
 color:white !important; font-family:'Vazirmatn',sans-serif !important;
 font-weight:800 !important; box-shadow:0 9px 22px rgba(141,135,218,.22) !important;
}
div.stButton > button:hover {transform:translateY(-1px);filter:brightness(1.04);}
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"] {
 border-radius:14px !important; background:rgba(255,255,255,.72) !important;
}
[data-testid="stFileUploader"] section {
 background:rgba(255,255,255,.56); border:1px dashed #b8afea; border-radius:22px;
}
footer {visibility:hidden;}
#MainMenu {visibility:hidden;}
/* RTL: apply to the whole Streamlit surface while keeping Latin identifiers readable */
[data-testid="stAppViewContainer"] .main {direction:rtl;text-align:right;}
[data-testid="stSidebar"] {direction:rtl;text-align:right;}
[data-testid="stMarkdownContainer"] {direction:rtl;text-align:right;}
[data-testid="stWidgetLabel"] {direction:rtl;text-align:right;}
small {direction:rtl;}
@media (max-width: 800px) {
 .hero {padding:22px;border-radius:25px;}
 .glass {padding:18px;border-radius:22px;}
 .brand {font-size:28px;}
}
</style>
""", unsafe_allow_html=True)

# ---------------- Helpers ----------------
def glass(content: str):
    st.markdown(f'<div class="glass">{content}</div>', unsafe_allow_html=True)

def mascot(width=220):
    if MASCOT.exists():
        st.image(str(MASCOT), width=width)
    else:
        st.markdown("<div style='font-size:100px;text-align:center'>🧬</div>", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
with st.sidebar:
    if MASCOT.exists():
        st.image(str(MASCOT), width=105)
    st.markdown('<div class="brand">Golbino<span>AI</span></div>', unsafe_allow_html=True)
    st.caption("دستیار هوشمند بررسی گلبول‌های سفید")
    st.divider()
    page = st.radio(
        "ناوبری",
        ["خانه", "تحلیل تصویر", "راهنمای سلول‌ها", "گزارش‌ها", "درباره پروژه"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown('<span class="soft-chip">نسخه پژوهشی · ۰.۱</span>', unsafe_allow_html=True)
    st.caption("این سامانه در حال توسعه است و خروجی آن جایگزین نظر متخصص آزمایشگاه نیست.")

# ---------------- Pages ----------------
if page == "خانه":
    left, right = st.columns([1.45, 1], vertical_alignment="center")
    with left:
        st.markdown("""
        <div class="hero">
          <span class="eyebrow">✦ هوش مصنوعی در خدمت علوم آزمایشگاهی</span>
          <div class="hero-title">از یک قطره خون،<br>تا بینشی هوشمند.</div>
          <div class="hero-sub">
            گلبینو به پژوهشگران کمک می‌کند تصاویر میکروسکوپی خون را
            بررسی کنند و گلبول‌های سفید را با کمک بینایی ماشین شناسایی کنند.
          </div>
          <div style="margin-top:22px"><span class="soft-chip">White Blood Cell Analysis</span>
          &nbsp; <span class="soft-chip">Computer Vision</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("شروع تحلیل تصویر  ←", key="home_analyze"):
            st.session_state["nav_target"] = "تحلیل تصویر"
            st.rerun()
    with right:
        mascot(280)
        st.markdown("<div style='text-align:center;color:#7d789d;font-weight:700'>سلام! من گلبینو هستم 🌸</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">در یک نگاه</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col, label, value, note in [
        (c1,"گروه سلولی","۵ نوع","طبقه‌بندی گلبول‌های سفید"),
        (c2,"وضعیت مدل","در حال آموزش","اتصال مدل در مرحله بعد"),
        (c3,"نوع ورودی","تصویر میکروسکوپی","JPG · PNG · TIFF"),
        (c4,"نسخه سامانه","۰.۱","پروتوتایپ پژوهشی"),
    ]:
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-label">{note}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">گلبول‌های سفید چه هستند؟</div>', unsafe_allow_html=True)
    cells = [
        ("نوتروفیل","Neutrophil","#9c8be8","دفاع اولیه در برابر عوامل بیماری‌زا"),
        ("لنفوسیت","Lymphocyte","#83bfe8","نقش کلیدی در پاسخ ایمنی اختصاصی"),
        ("مونوسیت","Monocyte","#e9a5bb","مشارکت در پاک‌سازی و تنظیم ایمنی"),
        ("ائوزینوفیل","Eosinophil","#e9b978","مرتبط با پاسخ‌های آلرژیک و انگلی"),
        ("بازوفیل","Basophil","#91cdbd","مشارکت در واکنش‌های التهابی و آلرژیک"),
    ]
    cols = st.columns(5)
    for col,(fa,en,color,desc) in zip(cols,cells):
        with col:
            st.markdown(f'<div class="cell-card"><span class="cell-dot" style="background:{color}"></span><b>{fa}</b><br><small style="color:#7c8498">{en}</small><p style="font-size:12px;margin-top:10px">{desc}</p></div>',unsafe_allow_html=True)

elif page == "تحلیل تصویر":
    st.markdown('<span class="eyebrow">IMAGE ANALYSIS</span>', unsafe_allow_html=True)
    st.title("تحلیل تصویر میکروسکوپی")
    st.write("تصویر اسمیر خون محیطی را بارگذاری کن تا برای تحلیل آماده شود.")
    uploaded = st.file_uploader("انتخاب تصویر", type=["png","jpg","jpeg","tif","tiff"], help="فرمت‌های PNG، JPG و TIFF پشتیبانی می‌شوند.")
    if uploaded:
        try:
            image = Image.open(uploaded).convert("RGB")
            a,b = st.columns([1.35,1], gap="large")
            with a:
                st.image(image, caption="تصویر بارگذاری‌شده", use_container_width=True)
            with b:
                st.markdown('<div class="glass"><div class="section-title">مشخصات تصویر</div>',unsafe_allow_html=True)
                st.write(f"**نام فایل:** {uploaded.name}")
                st.write(f"**ابعاد:** {image.width} × {image.height}")
                st.write(f"**حجم:** {uploaded.size/1024:.1f} KB")
                st.write("**وضعیت:** آماده برای اتصال مدل")
                st.markdown('<span class="soft-chip">Model not connected</span></div>',unsafe_allow_html=True)
                st.info("در این نسخه هنوز مدل تشخیص به سامانه متصل نشده است؛ بنابراین نتیجه ساختگی نمایش داده نمی‌شود.")
        except Exception as e:
            st.error(f"خواندن تصویر با مشکل مواجه شد: {e}")
    else:
        st.markdown('<div class="glass" style="text-align:center;padding:42px"><div style="font-size:48px">🔬</div><h3>تصویرت را اینجا بیاور</h3><p>برای شروع، یک تصویر میکروسکوپی واضح انتخاب کن.</p></div>',unsafe_allow_html=True)

elif page == "راهنمای سلول‌ها":
    st.title("راهنمای گلبول‌های سفید")
    st.write("آشنایی کوتاه با پنج گروه اصلی مورد بررسی در GolbinoAI.")
    data = [
        ("نوتروفیل","Neutrophil","فراوان‌ترین نوع گلبول سفید در خون محیطی؛ دارای هسته چندلوبی و گرانول‌های ظریف."),
        ("لنفوسیت","Lymphocyte","معمولاً هسته گرد و متراکم دارد و در ایمنی اختصاصی نقش مهمی ایفا می‌کند."),
        ("مونوسیت","Monocyte","از بزرگ‌ترین گلبول‌های سفید؛ هسته اغلب کلیوی‌شکل و سیتوپلاسم نسبتاً فراوان دارد."),
        ("ائوزینوفیل","Eosinophil","با گرانول‌های درشت نارنجی-قرمز شناخته می‌شود."),
        ("بازوفیل","Basophil","دارای گرانول‌های آبی-بنفش تیره که گاهی هسته را می‌پوشانند."),
    ]
    for fa,en,desc in data:
        st.markdown(f'<div class="cell-card" style="margin-bottom:12px"><b>{fa}</b> <span style="color:#8b83bd">· {en}</span><p style="margin:8px 0 0">{desc}</p></div>',unsafe_allow_html=True)

elif page == "گزارش‌ها":
    st.title("گزارش‌های تحلیل")
    st.markdown('<div class="glass" style="text-align:center;padding:42px"><div style="font-size:48px">📚</div><h3>هنوز گزارشی ثبت نشده</h3><p>پس از اتصال مدل و فعال‌شدن ذخیره‌سازی، گزارش تحلیل‌ها در این بخش نمایش داده می‌شوند.</p></div>',unsafe_allow_html=True)

elif page == "درباره پروژه":
    st.title("درباره GolbinoAI")
    st.markdown("""
    <div class="hero">
      <span class="eyebrow">RESEARCH PROTOTYPE</span>
      <div class="hero-title">دیدن دقیق‌تر،<br>فهمیدن هوشمندتر.</div>
      <div class="hero-sub">GolbinoAI یک نمونه پژوهشی برای تحلیل تصاویر میکروسکوپی خون محیطی با استفاده از بینایی ماشین و یادگیری عمیق است.</div>
    </div>
    """,unsafe_allow_html=True)
    st.write("")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass"><h3>هدف پروژه</h3><p>شناسایی و مکان‌یابی پنج گروه اصلی گلبول سفید در تصاویر اسمیر خون محیطی و فراهم‌کردن بستری برای ارزیابی پژوهشی مدل‌های یادگیری عمیق.</p></div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass"><h3>فناوری‌ها</h3><p>Python · Streamlit · OpenCV · PyTorch · YOLO · FastAPI (در مراحل بعد)</p></div>',unsafe_allow_html=True)
    st.warning("GolbinoAI یک ابزار پژوهشی در حال توسعه است و برای تشخیص یا تصمیم‌گیری بالینی تأیید نشده است.")

st.markdown("<div style='text-align:center;color:#9aa0b2;font-size:12px;margin-top:45px'>GolbinoAI · ساخته‌شده برای پژوهش در بینایی ماشین پزشکی</div>",unsafe_allow_html=True)
