# app.py
import streamlit as st
from PIL import Image
from pathlib import Path

from liquid_glass import inject_liquid_glass, glass_card, glass_divider

# ---------- تنظیمات صفحه ----------
st.set_page_config(
    page_title="گلبینو AI",
    page_icon="🫧",
    layout="centered",
)

# ---------- تزریق استایل Liquid Glass ----------
inject_liquid_glass("styles.css")

# ---------- بارگذاری منابع (کش‌شده) ----------
@st.cache_data
def load_logo():
    p = Path("assets/golbino_mascot.webp")
    if p.exists():
        return Image.open(p)
    return None

logo = load_logo()

# ---------- سایدبار ----------
with st.sidebar:
    if logo:
        st.image(logo, width=120)
    st.markdown("### 🫧 گلبینو AI")
    st.caption("دستیار هوشمند شما")
    glass_divider()
    st.markdown("**تنظیمات**")
    dark_mode = st.toggle("حالت تیره", value=False)
    language = st.selectbox("زبان", ["فارسی", "English"])
    glass_divider()
    st.caption("نسخه ۱.۰")

# ---------- هدر ----------
st.markdown(
    """
    <div class="lg-card lg-refract" style="text-align:center; margin-bottom:1.2rem;">
        <h1 style="margin:0; font-size:1.6rem; color:#29243A;">گلبینو AI</h1>
        <p style="margin:0.35rem 0 0; color:#5C5470;">دستیار هوشمند، سبک و شیشه‌ای ✨</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- چت ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("پیام خود را بنویسید…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # TODO: پاسخ واقعی مدل را اینجا قرار دهید
    reply = "این یک پاسخ نمونه است."
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# ---------- نمونه کارت شیشه‌ای ----------
glass_divider()
glass_card(
    """
    <h3 style="margin:0 0 0.4rem; font-size:1rem; color:#29243A;">💡 نکته</h3>
    <p style="margin:0; color:#5C5470; font-size:0.9rem;">
        برای دیدن شکست نور واقعی، این صفحه را در Chrome یا Edge باز کنید.
    </p>
    """,
    extra_class="lg-refract",
)
