# app.py — Golbino AI · Liquid Glass UI (Light Theme)
# فقط Streamlit + Pillow. آماده دیپلوی روی Streamlit Cloud.

import streamlit as st
from PIL import Image
from pathlib import Path

# ============================================================
# 0) تنظیمات صفحه
# ============================================================
st.set_page_config(
    page_title="گلبینو AI",
    page_icon="🫧",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================
# 1) Liquid Glass — SVG filter (برای شکست نور واقعی)
# ============================================================
_SVG = """
<svg xmlns="http://www.w3.org/2000/svg"
     style="position:absolute;width:0;height:0;overflow:hidden;pointer-events:none"
     aria-hidden="true">
  <defs>
    <filter id="lg-dist" x="-10%" y="-10%" width="120%" height="120%"
            color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.008 0.008"
                    numOctaves="2" seed="92" result="noise"/>
      <feGaussianBlur in="noise" stdDeviation="2" result="blurred"/>
      <feDisplacementMap in="SourceGraphic" in2="blurred" scale="70"
                         xChannelSelector="R" yChannelSelector="G"/>
    </filter>
    <filter id="lg-dist-light" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.012 0.012"
                    numOctaves="1" seed="42" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="28"
                         xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
</svg>
"""

# ============================================================
# 2) CSS — شیشه روشن، نرم و سبک
# ============================================================
_CSS = """
:root{
  --lg-blur:14px;
  --lg-sat:170%;
  --lg-bg:rgba(255,255,255,.30);
  --lg-bg-strong:rgba(255,255,255,.50);
  --lg-border:rgba(255,255,255,.78);
  --lg-radius:26px;
  --lg-shadow:
    0 10px 34px rgba(31,25,66,.08),
    inset 0 4px 18px rgba(255,255,255,.55),
    inset 0 -2px 8px rgba(128,101,184,.05);
  --accent:#8065B8;
}

/* پس‌زمینه گرادیانی خیلی نرم روشن */
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1100px 750px at 8% -12%,  #EFE9FA 0%, transparent 62%),
    radial-gradient(1000px 700px at 112% 18%, #E5F1F8 0%, transparent 58%),
    radial-gradient(900px 650px at 50% 118%,  #F8EBF4 0%, transparent 62%),
    #F8F9FC;
  background-attachment:fixed;
}
[data-testid="stHeader"]{background:transparent;}

/* فونت و اندازه‌ها */
html, body, [class*="css"]{
  font-family: -apple-system, "SF Pro Text", "Segoe UI",
               "Vazirmatn", Tahoma, sans-serif;
  color:#29243A;
}
h1,h2,h3{letter-spacing:-.01em;}

/* ================= شیشه پایه ================= */
.lg-card,
.glass-container{
  background:var(--lg-bg);
  -webkit-backdrop-filter:blur(var(--lg-blur)) saturate(var(--lg-sat));
  backdrop-filter:blur(var(--lg-blur)) saturate(var(--lg-sat));
  border:1px solid var(--lg-border);
  border-radius:var(--lg-radius);
  box-shadow:var(--lg-shadow);
  padding:1.25rem 1.4rem;
  position:relative;
  overflow:hidden;
  will-change:backdrop-filter;
  transition:transform .25s ease, box-shadow .25s ease;
}
.lg-card::before,
.glass-container::before{
  content:"";
  position:absolute; top:0; left:8%; right:8%; height:1px;
  background:linear-gradient(90deg, transparent,
              rgba(255,255,255,.95), transparent);
  pointer-events:none;
}
.lg-card:hover,
.glass-container:hover{
  transform:translateY(-2px);
  box-shadow:
    0 14px 40px rgba(31,25,66,.12),
    inset 0 4px 20px rgba(255,255,255,.65);
}

/* نسخه واقعی شکست نور (Chrome/Edge) */
.lg-refract{
  -webkit-backdrop-filter:blur(10px) saturate(180%) url(#lg-dist);
  backdrop-filter:blur(10px) saturate(180%) url(#lg-dist);
}

/* ================= سایدبار ================= */
[data-testid="stSidebar"]{background:transparent;}
[data-testid="stSidebar"] > div:first-child{
  background:rgba(255,255,255,.45);
  -webkit-backdrop-filter:blur(22px) saturate(180%);
  backdrop-filter:blur(22px) saturate(180%);
  border-right:1px solid rgba(255,255,255,.65);
  box-shadow:8px 0 32px rgba(31,25,66,.05);
}

/* ================= دکمه‌ها ================= */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button{
  background:rgba(255,255,255,.38) !important;
  color:#29243A !important;
  -webkit-backdrop-filter:blur(10px) saturate(180%);
  backdrop-filter:blur(10px) saturate(180%);
  border:1px solid rgba(255,255,255,.88) !important;
  border-radius:16px !important;
  box-shadow:
    0 4px 16px rgba(31,25,66,.07),
    inset 0 1px 0 rgba(255,255,255,.9);
  font-weight:600;
  padding:.55rem 1.1rem !important;
  transition:transform .18s ease, background .18s ease;
}
.stButton > button:hover{
  background:rgba(255,255,255,.58) !important;
  border-color:rgba(128,101,184,.42) !important;
  transform:translateY(-1px);
}
.stButton > button:active{transform:translateY(0);}

/* دکمه primary */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"]{
  background:linear-gradient(135deg,
      rgba(128,101,184,.88), rgba(107,82,163,.92)) !important;
  color:#fff !important;
  border:1px solid rgba(255,255,255,.35) !important;
}

/* ================= ورودی‌ها ================= */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div{
  background:rgba(255,255,255,.48) !important;
  -webkit-backdrop-filter:blur(8px) saturate(160%);
  backdrop-filter:blur(8px) saturate(160%);
  border:1px solid rgba(255,255,255,.82) !important;
  border-radius:14px !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.9);
  color:#29243A !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus{
  border-color:rgba(128,101,184,.6) !important;
  box-shadow:
    0 0 0 3px rgba(128,101,184,.15),
    inset 0 1px 0 rgba(255,255,255,.9) !important;
}

/* ================= چت ================= */
[data-testid="stChatMessage"]{
  background:rgba(255,255,255,.34);
  -webkit-backdrop-filter:blur(12px) saturate(170%);
  backdrop-filter:blur(12px) saturate(170%);
  border:1px solid rgba(255,255,255,.72);
  border-radius:22px;
  padding:.9rem 1.05rem;
  margin-bottom:.55rem;
  box-shadow:0 4px 18px rgba(31,25,66,.05);
}
[data-testid="stChatInput"] textarea{
  background:rgba(255,255,255,.55) !important;
  -webkit-backdrop-filter:blur(10px) saturate(170%);
  backdrop-filter:blur(10px) saturate(170%);
  border:1px solid rgba(255,255,255,.85) !important;
  border-radius:18px !important;
}

/* ================= جداکننده ================= */
.lg-divider{
  height:1px; margin:1rem 0;
  background:linear-gradient(90deg, transparent,
              rgba(128,101,184,.25), transparent);
}

/* ================= اسکرول‌بار ================= */
::-webkit-scrollbar{width:8px;height:8px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{
  background:rgba(128,101,184,.25);border-radius:8px;
}
::-webkit-scrollbar-thumb:hover{background:rgba(128,101,184,.45);}

/* ================= Fallback ================= */
@supports not (backdrop-filter: url(#lg-dist)){
  .lg-card, .glass-container, [data-testid="stChatMessage"]{
    background:rgba(255,255,255,.78);
  }
}
@media (prefers-reduced-motion: reduce){
  .lg-card, .glass-container, .stButton > button,
  [data-testid="stChatMessage"]{
    -webkit-backdrop-filter:none !important;
    backdrop-filter:none !important;
    background:rgba(255,255,255,.88) !important;
    transition:none !important;
  }
  .lg-card:hover, .glass-container:hover{transform:none !important;}
}
@media (max-width: 640px){
  :root{--lg-blur:9px;}
  .lg-card, .glass-container{padding:.9rem 1rem; border-radius:20px;}
  .lg-refract{
    -webkit-backdrop-filter:blur(8px) url(#lg-dist-light);
    backdrop-filter:blur(8px) url(#lg-dist-light);
  }
}
"""

# تزریق SVG و CSS
st.markdown(_SVG, unsafe_allow_html=True)
st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)

# ============================================================
# 3) بارگذاری منابع
# ============================================================
@st.cache_data(show_spinner=False)
def load_logo():
    for p in ("assets/golbino_mascot.webp",
              "assets/golbino_mascot.png",
              "golbino_mascot.png",
              "golbino_mascot.webp"):
        if Path(p).exists():
            return Image.open(p)
    return None


logo = load_logo()

# ============================================================
# 4) سایدبار
# ============================================================
with st.sidebar:
    if logo:
        col_a, col_b = st.columns([1, 2], vertical_alignment="center")
        with col_a:
            st.image(logo, width=64)
        with col_b:
            st.markdown("### 🫧 گلبینو")
    else:
        st.markdown("## 🫧 گلبینو AI")

    st.caption("دستیار هوشمند شما")
    st.markdown('<div class="lg-divider"></div>', unsafe_allow_html=True)

    st.markdown("**تنظیمات**")
    language = st.selectbox("زبان", ["فارسی", "English"], index=0)
    theme_mode = st.radio(
        "حالت نمایش",
        ["شیشه روشن (Liquid Glass)", "شیشه واقعی (Chrome)"],
        index=0,
    )
    st.toggle("افکت شکست نور", value=True,
              help="فقط در Chrome/Edge پشتیبانی می‌شود")

    st.markdown('<div class="lg-divider"></div>', unsafe_allow_html=True)

    if st.button("🗑️ پاک کردن گفتگو", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="lg-divider"></div>', unsafe_allow_html=True)
    st.caption("نسخه ۱.۰ • دموی UI")

# ============================================================
# 5) هدر
# ============================================================
st.markdown(
    """
    <div class="lg-card lg-refract"
         style="text-align:center;margin-bottom:1.1rem;">
      <div style="font-size:2rem;line-height:1;">🫧</div>
      <h1 style="margin:.4rem 0 0;font-size:1.55rem;color:#29243A;">
        گلبینو AI
      </h1>
      <p style="margin:.35rem 0 0;color:#5C5470;font-size:.92rem;">
        دستیار هوشمند، سبک و شیشه‌ای ✨
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 6) چت
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "سلام! من گلبینو هستم. چطور می‌تونم کمکتون کنم؟ 🫧"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("پیام خود را بنویسید…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # پاسخ نمونه (بعداً مدل واقعی جایگزین می‌شود)
    reply = f"پیام شما دریافت شد: «{prompt}» — این یک پاسخ نمونه است."
    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
    with st.chat_message("assistant"):
        st.markdown(reply)

# ============================================================
# 7) کارت پایانی
# ============================================================
st.markdown('<div class="lg-divider"></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="small")
with c1:
    st.markdown(
        """
        <div class="lg-card" style="text-align:center;">
          <div style="font-size:1.4rem;">⚡</div>
          <div style="font-weight:600;color:#29243A;margin-top:.3rem;">
            سریع
          </div>
          <div style="font-size:.8rem;color:#5C5470;margin-top:.2rem;">
            پاسخ فوری
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """
        <div class="lg-card" style="text-align:center;">
          <div style="font-size:1.4rem;">🔒</div>
          <div style="font-weight:600;color:#29243A;margin-top:.3rem;">
            امن
          </div>
          <div style="font-size:.8rem;color:#5C5470;margin-top:.2rem;">
            بدون ذخیره‌سازی
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """
        <div class="lg-card" style="text-align:center;">
          <div style="font-size:1.4rem;">✨</div>
          <div style="font-weight:600;color:#29243A;margin-top:.3rem;">
            سبک
          </div>
          <div style="font-size:.8rem;color:#5C5470;margin-top:.2rem;">
            شیشه مایع
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="text-align:center;margin-top:1.4rem;color:#8A84A0;
                font-size:.78rem;">
      گلبینو AI — دموی رابط کاربری
    </div>
    """,
    unsafe_allow_html=True,
)
