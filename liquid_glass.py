# liquid_glass.py
"""
ماژول کمکی برای تزریق افکت Liquid Glass در Streamlit.
شامل:
- SVG filter برای شکست نور (Refraction)
- تزریق styles.css
- تابع کمکی برای ساخت کارت شیشه‌ای سفارشی
"""
import streamlit as st
from pathlib import Path


# ---- SVG Filter (یک بار در کل صفحه تزریق می‌شود) ----
_LIQUID_GLASS_SVG = """
<svg xmlns="http://www.w3.org/2000/svg"
     style="position:absolute; width:0; height:0; overflow:hidden; pointer-events:none;"
     aria-hidden="true">
  <defs>
    <!-- فیلتر اصلی: شکست نور + نویز مایع -->
    <filter id="lg-dist" x="-10%" y="-10%" width="120%" height="120%"
            color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise"
                    baseFrequency="0.008 0.008"
                    numOctaves="2"
                    seed="92"
                    result="noise" />
      <feGaussianBlur in="noise" stdDeviation="2" result="blurred" />
      <feDisplacementMap in="SourceGraphic"
                         in2="blurred"
                         scale="70"
                         xChannelSelector="R"
                         yChannelSelector="G" />
    </filter>

    <!-- نسخه سبک‌تر برای دستگاه‌های ضعیف -->
    <filter id="lg-dist-light" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise"
                    baseFrequency="0.01 0.01"
                    numOctaves="1"
                    seed="42"
                    result="noise" />
      <feDisplacementMap in="SourceGraphic"
                         in2="noise"
                         scale="30"
                         xChannelSelector="R"
                         yChannelSelector="G" />
    </filter>
  </defs>
</svg>
"""


def inject_liquid_glass(css_path: str = "styles.css") -> None:
    """
    SVG filter و فایل CSS را به صفحه تزریق می‌کند.
    این تابع را یک بار در ابتدای app.py صدا بزنید (بعد از st.set_page_config).
    """
    # 1) تزریق SVG filter
    st.markdown(_LIQUID_GLASS_SVG, unsafe_allow_html=True)

    # 2) تزریق CSS
    css_file = Path(css_path)
    if css_file.exists():
        css = css_file.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"فایل {css_path} پیدا نشد. استایل شیشه‌ای اعمال نشد.")


def glass_card(body_html: str, extra_class: str = "") -> None:
    """
    یک کارت شیشه‌ای سفارشی رندر می‌کند.
    body_html می‌تواند شامل هر HTML مجاز باشد.
    """
    st.markdown(
        f'<div class="lg-card {extra_class}">{body_html}</div>',
        unsafe_allow_html=True,
    )


def glass_divider() -> None:
    """خط جداکننده شیشه‌ای نازک."""
    st.markdown('<div class="lg-divider"></div>', unsafe_allow_html=True)
