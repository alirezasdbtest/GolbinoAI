# app.py — Golbino AI · تشخیص گلبول سفید (UI + دمو)
# وابستگی‌ها: streamlit, pillow  (فقط همین دو)

import hashlib
import random
from io import BytesIO

import streamlit as st
from PIL import Image, ImageDraw

# ============================================================
# 0) تنظیمات صفحه
# ============================================================
st.set_page_config(
    page_title="گلبینو AI · تشخیص گلبول سفید",
    page_icon="🩸",
    layout="centered",
)

# ============================================================
# 1) Liquid Glass — SVG filter
# ============================================================
_SVG = """
<svg xmlns="http://www.w3.org/2000/svg"
     style="position:absolute;width:0;height:0;overflow:hidden;pointer-events:none"
     aria-hidden="true">
  <defs>
    <filter id="lg-dist" x="-10%" y="-10%" width="120%" height="120%">
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
# 2) CSS — شیشه روشن
# ============================================================
_CSS = """
:root{
  --lg-blur:14px; --lg-sat:170%;
  --lg-bg:rgba(255,255,255,.32);
  --lg-border:rgba(255,255,255,.78);
  --lg-radius:24px;
  --lg-shadow:0 10px 34px rgba(31,25,66,.08),
              inset 0 4px 18px rgba(255,255,255,.55);
}
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1100px 750px at 8% -12%,  #EFE9FA 0%, transparent 62%),
    radial-gradient(1000px 700px at 112% 18%, #E5F1F8 0%, transparent 58%),
    radial-gradient(900px 650px at 50% 118%,  #F8EBF4 0%, transparent 62%),
    #F8F9FC;
  background-attachment:fixed;
}
[data-testid="stHeader"]{background:transparent;}
html,body,[class*="css"]{
  font-family:-apple-system,"SF Pro Text","Segoe UI","Vazirmatn",Tahoma,sans-serif;
  color:#29243A;
}

.lg-card{
  background:var(--lg-bg);
  -webkit-backdrop-filter:blur(var(--lg-blur)) saturate(var(--lg-sat));
  backdrop-filter:blur(var(--lg-blur)) saturate(var(--lg-sat));
  border:1px solid var(--lg-border);
  border-radius:var(--lg-radius);
  box-shadow:var(--lg-shadow);
  padding:1.15rem 1.3rem;
  position:relative;overflow:hidden;
  transition:transform .25s ease, box-shadow .25s ease;
}
.lg-card::before{
  content:"";position:absolute;top:0;left:8%;right:8%;height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.95),transparent);
}
.lg-card:hover{
  transform:translateY(-2px);
  box-shadow:0 14px 40px rgba(31,25,66,.12),
             inset 0 4px 20px rgba(255,255,255,.65);
}
.lg-refract{
  -webkit-backdrop-filter:blur(10px) saturate(180%) url(#lg-dist);
  backdrop-filter:blur(10px) saturate(180%) url(#lg-dist);
}

.stButton>button{
  background:rgba(255,255,255,.38)!important;
  color:#29243A!important;
  -webkit-backdrop-filter:blur(10px) saturate(180%);
  backdrop-filter:blur(10px) saturate(180%);
  border:1px solid rgba(255,255,255,.88)!important;
  border-radius:16px!important;
  box-shadow:0 4px 16px rgba(31,25,66,.07);
  font-weight:600;padding:.55rem 1.1rem!important;
}
[data-testid="stFileUploaderDropzone"]{
  background:rgba(255,255,255,.42)!important;
  -webkit-backdrop-filter:blur(12px) saturate(180%);
  backdrop-filter:blur(12px) saturate(180%);
  border:1.5px dashed rgba(128,101,184,.4)!important;
  border-radius:22px!important;
  padding:1.2rem!important;
}
[data-testid="stProgress"] > div > div > div > div{
  background:linear-gradient(90deg,#8065B8,#6B52A3)!important;
}
.lg-divider{
  height:1px;margin:1.2rem 0;
  background:linear-gradient(90deg,transparent,rgba(128,101,184,.25),transparent);
}
@media (prefers-reduced-motion: reduce){
  .lg-card{transition:none!important;}
  .lg-card:hover{transform:none!important;}
}
@media (max-width:640px){
  :root{--lg-blur:9px;}
  .lg-card{padding:.9rem 1rem;border-radius:20px;}
  .lg-refract{
    -webkit-backdrop-filter:blur(8px) url(#lg-dist-light);
    backdrop-filter:blur(8px) url(#lg-dist-light);
  }
}
"""

st.markdown(_SVG, unsafe_allow_html=True)
st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)

# ============================================================
# 3) کلاس‌های WBC
# ============================================================
CLASSES = [
    ("نوتروفیل",   "Neutrophil", "#4A90E2"),
    ("لنفوسیت",    "Lymphocyte", "#7B68EE"),
    ("مونوسیت",    "Monocyte",   "#50C878"),
    ("ائوزینوفیل", "Eosinophil", "#FF8C42"),
    ("بازوفیل",    "Basophil",   "#D946EF"),
]

# ============================================================
# 4) نمونه ساختگی خون + تشخیص نمایشی (کش‌شده)
# ============================================================
@st.cache_data(show_spinner=False)
def build_sample():
    """
    یک اسمیر خون ساختگی می‌سازد و نسخه‌ی annotate‌شده را هم برمی‌گرداند.
    هیچ مدلی درگیر نیست — فقط برای نمایش ظاهر خروجی است.
    """
    rng = random.Random(42)
    size = 480
    base = Image.new("RGB", (size, size), (252, 246, 240))
    d = ImageDraw.Draw(base)

    # RBCs (پس‌زمینه)
    for _ in range(220):
        cx = rng.randint(-10, size + 10)
        cy = rng.randint(-10, size + 10)
        r = rng.randint(7, 12)
        col = rng.choice([(232, 178, 178), (228, 172, 172), (238, 186, 186)])
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        r2 = r // 2
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(242, 196, 196))

    # WBCs — (cx, cy, r, class_index)
    wbcs = [
        (120, 140, 24, 0),   # Neutrophil
        (330, 110, 26, 1),   # Lymphocyte
        (400, 300, 22, 0),   # Neutrophil
        (200, 380, 30, 2),   # Monocyte
        (95,  300, 23, 0),   # Neutrophil
        (280, 240, 25, 1),   # Lymphocyte
    ]
    cyto_colors = [(248, 228, 240), (250, 232, 242), (245, 225, 238)]
    nuc_colors  = [(130, 90, 170), (110, 70, 160), (150, 100, 180)]
    for (cx, cy, r, cls) in wbcs:
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=cyto_colors[cls % 3],
                  outline=(200, 160, 200), width=1)
        nr = r - 6
        d.ellipse([cx - nr, cy - nr, cx + nr, cy + nr],
                  fill=nuc_colors[cls % 3])

    # annotate
    ann_img = base.copy()
    ann = ImageDraw.Draw(ann_img)
    for (cx, cy, r, cls) in wbcs:
        color = CLASSES[cls][2]
        br = r + 8
        ann.rectangle([cx - br, cy - br, cx + br, cy + br],
                      outline=color, width=3)

    return base, ann_img, wbcs


def summarize_wbcs(wbcs):
    counts = {}
    for (_, _, _, cls) in wbcs:
        counts[cls] = counts.get(cls, 0) + 1
    return counts


# ============================================================
# 5) پیش‌بینی ساختگی برای تصویر آپلودی
#    (بعداً با onnxruntime جایگزین می‌شود)
# ============================================================
def mock_predict(image_bytes: bytes):
    h = hashlib.sha256(image_bytes).digest()
    rng = random.Random(int.from_bytes(h[:8], "big"))
    raw = [rng.random() ** 2 for _ in CLASSES]
    s = sum(raw)
    probs = [r / s for r in raw]
    top = max(range(len(probs)), key=lambda i: probs[i])
    return probs, top


# ============================================================
# 6) هدر
# ============================================================
st.markdown(
    """
    <div class="lg-card lg-refract"
         style="text-align:center;margin-bottom:1rem;">
      <div style="font-size:2rem;line-height:1;">🩸</div>
      <h1 style="margin:.4rem 0 0;font-size:1.5rem;color:#29243A;">
        گلبینو AI
      </h1>
      <p style="margin:.35rem 0 0;color:#5C5470;font-size:.9rem;">
        تشخیص خودکار انواع گلبول سفید از تصویر میکروسکوپی خون
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="lg-card"
         style="border-left:4px solid #E0A800;
                background:rgba(255,248,225,.6);margin-bottom:1rem;">
      <strong>⚠️ هشدار:</strong> این یک دموی آموزشی است و
      <strong>جایگزین نظر پزشک یا آزمایشگاه نیست</strong>.
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 7) بخش نمونه نمایشی
# ============================================================
st.markdown(
    '<div class="lg-card" style="padding:.9rem 1.1rem;'
    'font-weight:700;color:#29243A;margin-bottom:.7rem;">'
    '🔬 نمونه نمایشی'
    '</div>',
    unsafe_allow_html=True,
)

sample_base, sample_ann, sample_wbcs = build_sample()
counts = summarize_wbcs(sample_wbcs)

col_a, col_b = st.columns(2, gap="small")
with col_a:
    st.image(sample_base, caption="تصویر خام میکروسکوپ",
             use_container_width=True)
with col_b:
    st.image(sample_ann, caption="گلبول‌های سفید شناسایی‌شده",
             use_container_width=True)

# افسانه رنگ‌ها + آمار
legend_html = "".join(
    f'<span style="display:inline-flex;align-items:center;'
    f'gap:.35rem;margin:.15rem .55rem .15rem 0;font-size:.82rem;color:#29243A;">'
    f'<span style="width:10px;height:10px;border-radius:3px;'
    f'background:{color};display:inline-block;"></span>{fa}</span>'
    for (fa, en, color) in CLASSES
)
stats_html = " • ".join(
    f'{CLASSES[ci][0]}: <strong>{n}</strong>'
    for ci, n in sorted(counts.items())
)
st.markdown(
    f"""
    <div class="lg-card" style="padding:.9rem 1.1rem;margin-top:.5rem;">
      <div style="font-size:.85rem;color:#5C5470;margin-bottom:.35rem;">
        راهنمای رنگ‌ها
      </div>
      <div>{legend_html}</div>
      <div style="margin-top:.7rem;font-size:.88rem;color:#29243A;">
        🧫 <strong>{len(sample_wbcs)}</strong> گلبول سفید شناسایی شد —
        {stats_html}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="lg-divider"></div>', unsafe_allow_html=True)

# ============================================================
# 8) آپلود تصویر کاربر
# ============================================================
st.markdown(
    '<div class="lg-card" style="padding:.9rem 1.1rem;'
    'font-weight:700;color:#29243A;margin-bottom:.7rem;">'
    '📤 تصویر خودت را آپلود کن'
    '</div>',
    unsafe_allow_html=True,
)

uploaded = st.file_uploader(
    "تصویر میکروسکوپی خون (PNG / JPG)",
    type=["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"],
    label_visibility="collapsed",
)

if uploaded is not None:
    raw_bytes = uploaded.getvalue()
    img = Image.open(BytesIO(raw_bytes))
    probs, top = mock_predict(raw_bytes)
    top_fa, top_en, top_color = CLASSES[top]
    conf = probs[top] * 100

    col1, col2 = st.columns([1, 1.2], gap="small")
    with col1:
        st.image(img, caption="تصویر آپلودشده",
                 use_container_width=True)
    with col2:
        st.markdown(
            f"""
            <div class="lg-card" style="padding:1rem 1.2rem;">
              <div style="font-size:.8rem;color:#5C5470;">نتیجه تشخیص</div>
              <div style="font-size:1.4rem;font-weight:700;
                          color:#29243A;margin-top:.25rem;">
                <span style="display:inline-block;width:12px;height:12px;
                             border-radius:4px;background:{top_color};
                             margin-left:.4rem;"></span>
                {top_fa}
              </div>
              <div style="font-size:.82rem;color:#8065B8;margin-top:.1rem;">
                {top_en}
              </div>
              <div style="font-size:.9rem;color:#5C5470;margin-top:.55rem;">
                اطمینان مدل: <strong>{conf:.1f}٪</strong>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="lg-card" style="padding:.9rem 1.1rem;margin-top:.6rem;">'
        '<div style="font-size:.85rem;color:#5C5470;margin-bottom:.55rem;">'
        'توزیع احتمال کلاس‌ها</div>',
        unsafe_allow_html=True,
    )
    order = sorted(range(len(CLASSES)), key=lambda i: probs[i], reverse=True)
    for i in order:
        fa, en, _ = CLASSES[i]
        st.progress(probs[i], text=f"{fa} — {probs[i]*100:.1f}٪")
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption(
        "ℹ️ این نتیجه هنوز توسط مدل واقعی تولید نشده؛ "
        "بعد از آموزش مدل با دیتاست BloodMNIST، این بخش جایگزین می‌شود."
    )

else:
    st.info("👆 یک تصویر میکروسکوپی آپلود کن تا نتیجه نمایش داده شود.")

# ============================================================
# 9) فوتر
# ============================================================
st.markdown(
    """
    <div style="text-align:center;margin-top:1.6rem;color:#8A84A0;
                font-size:.78rem;">
      گلبینو AI — دموی رابط کاربری • نسخه ۱.۰
    </div>
    """,
    unsafe_allow_html=True,
)
