
import os
import re
import time
import html
import threading
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote, quote

import requests
import streamlit as st
from bs4 import BeautifulSoup


# ============================================================
# تنظیمات اصلی
# ============================================================

st.set_page_config(
    page_title="Raabin WBC Downloader",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGE_URL = (
    "https://dl.raabindata.com/"
    "Index%20of%20WBC%20Data/"
    "Index%20of%20WBC%20First_microscope/"
)

WORKER_BASE = (
    "https://broad-dew-8b34.alirezasaidi13802001.workers.dev/"
)

DOWNLOAD_DIR = Path("downloads")
PARTIAL_DIR = DOWNLOAD_DIR / ".partial"

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
PARTIAL_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

CHUNK_SIZE = 256 * 1024
MAX_RETRIES = 4
TIMEOUT = (30, 180)


# ============================================================
# استایل رابط کاربری
# ============================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Vazirmatn', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 5%,
                rgba(151, 130, 210, 0.13),
                transparent 35%
            ),
            linear-gradient(135deg, #f5f3fa, #eeedf5);
        color: #29243a;
    }

    [data-testid="stSidebar"] {
        background: #e9e5f1;
        border-right: 1px solid rgba(100, 80, 140, 0.12);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    h1, h2, h3, p, label, span {
        color: #29243a;
    }

    .hero {
        padding: 30px;
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.85);
        box-shadow: 0 12px 35px rgba(45, 35, 75, 0.08);
        backdrop-filter: blur(18px);
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 29px;
        font-weight: 800;
        color: #302747;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 15px;
        color: #625b70;
        line-height: 2;
    }

    .info-card {
        padding: 20px;
        border-radius: 18px;
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(255,255,255,0.9);
        box-shadow: 0 6px 20px rgba(45,35,75,0.05);
        min-height: 115px;
    }

    .info-number {
        font-size: 25px;
        font-weight: 800;
        color: #8065b8;
    }

    .info-label {
        font-size: 13px;
        color: #625b70;
    }

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #302747;
        margin: 15px 0;
    }

    .small-note {
        color: #70687d;
        font-size: 13px;
        line-height: 1.9;
    }

    div.stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(128,101,184,0.25);
        font-family: 'Vazirmatn', sans-serif;
        font-weight: 600;
        min-height: 43px;
    }

    div.stButton > button[kind="primary"] {
        background: #8065b8;
        color: white;
        border: none;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #6e54a7;
        color: white;
    }

    [data-testid="stProgressBar"] > div > div {
        background-color: #8065b8;
    }

    code {
        direction: ltr;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# وضعیت برنامه
# ============================================================

DEFAULT_STATE = {
    "zip_links": None,
    "download_logs": [],
    "download_status": "idle",
    "download_failed": [],
    "download_success": [],
    "download_current_file": "",
    "download_current_index": 0,
    "download_total": 0,
    "download_progress": 0.0,
    "download_started": False,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# توابع عمومی
# ============================================================

def add_log(message: str):
    """ثبت پیام در گزارش برنامه."""

    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"

    logs = st.session_state.download_logs
    logs.append(entry)

    if len(logs) > 300:
        st.session_state.download_logs = logs[-300:]


def natural_key(value: str):
    """مرتب‌سازی طبیعی نام فایل‌ها."""

    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    ]


def safe_filename(filename: str) -> str:
    """جلوگیری از نام فایل نامعتبر."""

    filename = unquote(filename)
    filename = os.path.basename(filename)
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename)

    return filename.strip(" .")


def get_worker_url(original_url: str) -> str:
    """ساخت آدرس Worker از آدرس اصلی."""

    parsed = urlsplit(original_url)

    relative_path = parsed.path.lstrip("/")

    if parsed.query:
        relative_path += "?" + parsed.query

    return WORKER_BASE.rstrip("/") + "/" + relative_path


def get_url_candidates(original_url: str):
    """آدرس Worker و آدرس اصلی را به‌عنوان مسیرهای جایگزین برمی‌گرداند."""

    worker_url = get_worker_url(original_url)

    if worker_url == original_url:
        return [original_url]

    return [worker_url, original_url]


# ============================================================
# دریافت فهرست فایل‌ها
# ============================================================

def fetch_directory(url: str):
    """دریافت محتوای صفحه فهرست فایل‌ها."""

    errors = []

    for candidate in get_url_candidates(url):

        try:
            response = requests.get(
                candidate,
                headers=HEADERS,
                timeout=TIMEOUT,
            )

            response.raise_for_status()

            if not response.text.strip():
                raise ValueError("پاسخ سرور خالی است.")

            return response.text

        except Exception as exc:
            errors.append(str(exc))

    raise RuntimeError(
        "دریافت فهرست فایل‌ها ناموفق بود: "
        + " | ".join(errors)
    )


def get_zip_links():
    """استخراج لینک فایل‌های ZIP از صفحه Raabin."""

    page_html = fetch_directory(PAGE_URL)

    soup = BeautifulSoup(page_html, "html.parser")

    links = []

    for anchor in soup.find_all("a", href=True):

        href = anchor.get("href", "").strip()

        if not href:
            continue

        if not re.search(r"\.zip(?:$|\?)", href, re.IGNORECASE):
            continue

        full_url = urljoin(PAGE_URL, href)

        links.append(full_url)

    links = sorted(
        set(links),
        key=lambda url: natural_key(
            safe_filename(urlsplit(url).path.split("/")[-1])
        ),
    )

    return links


# ============================================================
# پردازش بازه انتخابی
# ============================================================

def parse_range(raw: str, total: int):
    """
    نمونه ورودی:
    all
    1-20
    20-30
    5
    5-
    1,3,5
    1-5,8,10-12
    """

    raw = raw.strip().lower()

    if raw in ("all", "*"):
        return list(range(1, total + 1))

    if not raw:
        return None

    selected = set()

    try:

        parts = raw.split(",")

        for part in parts:

            part = part.strip()

            if not part:
                return None

            if "-" in part:

                left, right = part.split("-", 1)

                start = int(left.strip())
                end = int(right.strip()) if right.strip() else total

            else:

                start = int(part)
                end = start

            if start < 1 or end < start or end > total:
                return None

            selected.update(range(start, end + 1))

        return sorted(selected)

    except (ValueError, TypeError):
        return None


# ============================================================
# دانلود فایل
# ============================================================

def get_total_size(response, downloaded_before: int):
    """تشخیص حجم واقعی فایل از هدرهای پاسخ."""

    content_range = response.headers.get("Content-Range", "")

    match = re.search(r"/(\d+)$", content_range)

    if match:
        return int(match.group(1))

    content_length = response.headers.get("Content-Length")

    if content_length:

        try:
            length = int(content_length)

            if response.status_code == 206:
                return downloaded_before + length

            return length

        except ValueError:
            pass

    return 0


def download_single_file(
    original_url: str,
    overwrite: bool,
    progress_callback=None,
):
    """
    دانلود با قابلیت Resume.
    فایل ابتدا با پسوند part ذخیره می‌شود.
    پس از اتمام و بررسی حجم، به ZIP تبدیل می‌شود.
    """

    filename = safe_filename(
        urlsplit(original_url).path.split("/")[-1]
    )

    if not filename:
        raise ValueError("نام فایل معتبر نیست.")

    final_path = DOWNLOAD_DIR / filename
    partial_path = PARTIAL_DIR / (filename + ".part")

    # اگر فایل کامل از قبل موجود است
    if final_path.exists() and not overwrite:

        add_log(f"رد شد؛ فایل از قبل وجود دارد: {filename}")

        if progress_callback:
            progress_callback(100, filename)

        return "skipped"

    errors = []

    for candidate in get_url_candidates(original_url):

        for attempt in range(1, MAX_RETRIES + 1):

            try:

                downloaded_before = (
                    partial_path.stat().st_size
                    if partial_path.exists()
                    else 0
                )

                headers = HEADERS.copy()

                if downloaded_before > 0:
                    headers["Range"] = f"bytes={downloaded_before}-"

                with requests.get(
                    candidate,
                    headers=headers,
                    stream=True,
                    timeout=TIMEOUT,
                    allow_redirects=True,
                ) as response:

                    if response.status_code not in (200, 206):
                        response.raise_for_status()

                    # اگر سرور Range را پشتیبانی نکند، از ابتدا شروع می‌کنیم.
                    if response.status_code == 206:

                        content_range = response.headers.get(
                            "Content-Range", ""
                        )

                        match = re.match(
                            r"bytes\s+(\d+)-(\d+)/(\d+|\*)",
                            content_range,
                            re.IGNORECASE,
                        )

                        if not match:
                            raise ValueError(
                                "پاسخ Range سرور معتبر نیست."
                            )

                        actual_start = int(match.group(1))

                        if actual_start != downloaded_before:
                            raise ValueError(
                                "موقعیت Resume با پاسخ سرور مطابقت ندارد."
                            )

                        mode = "ab"

                    else:

                        downloaded_before = 0
                        mode = "wb"

                    total_size = get_total_size(
                        response,
                        downloaded_before,
                    )

                    downloaded = downloaded_before

                    if progress_callback and total_size > 0:
                        progress_callback(
                            downloaded / total_size * 100,
                            filename,
                        )

                    with open(partial_path, mode) as file:

                        for chunk in response.iter_content(
                            chunk_size=CHUNK_SIZE
                        ):

                            if not chunk:
                                continue

                            file.write(chunk)
                            downloaded += len(chunk)

                            if progress_callback and total_size > 0:

                                percentage = (
                                    downloaded / total_size
                                ) * 100

                                progress_callback(
                                    min(percentage, 99.9),
                                    filename,
                                )

                        file.flush()
                        os.fsync(file.fileno())

                actual_size = partial_path.stat().st_size

                if total_size > 0 and actual_size != total_size:
                    raise ValueError(
                        f"حجم فایل کامل نیست؛ "
                        f"دریافت‌شده: {actual_size:,} "
                        f"از {total_size:,} بایت"
                    )

                if actual_size <= 0:
                    raise ValueError("فایل دانلودشده خالی است.")

                # جایگزینی فایل نهایی پس از تکمیل
                os.replace(partial_path, final_path)

                add_log(
                    f"دانلود موفق: {filename} "
                    f"({actual_size / 1024 / 1024:.2f} MB)"
                )

                if progress_callback:
                    progress_callback(100, filename)

                return "success"

            except Exception as exc:

                error_message = str(exc)

                errors.append(
                    f"{filename} | تلاش {attempt} | {error_message}"
                )

                add_log(
                    f"خطا در {filename} "
                    f"(تلاش {attempt}): {error_message}"
                )

                if attempt < MAX_RETRIES:
                    time.sleep(min(attempt * 2, 8))

        # اگر Worker جواب نداد، مسیر اصلی امتحان می‌شود.
        # فایل نیمه‌دانلودشده حفظ می‌شود تا امکان Resume باقی بماند.

    raise RuntimeError(
        f"دانلود {filename} ناموفق بود. "
        + " | ".join(errors[-4:])
    )


# ============================================================
# اجرای دانلود و نمایش زنده پیشرفت
# ============================================================

def run_download(selected_urls, overwrite):
    """دانلود ترتیبی فایل‌ها با به‌روزرسانی مستقیم رابط کاربری."""

    total = len(selected_urls)

    st.session_state.download_status = "running"
    st.session_state.download_total = total
    st.session_state.download_current_index = 0
    st.session_state.download_current_file = ""
    st.session_state.download_progress = 0.0
    st.session_state.download_failed = []
    st.session_state.download_success = []
    st.session_state.download_logs = []

    overall_progress = st.progress(0.0)
    file_progress = st.progress(0.0)

    status_box = st.status(
        "در حال آماده‌سازی دانلود...",
        expanded=True,
    )

    current_text = st.empty()
    detail_text = st.empty()

    try:

        for index, url in enumerate(selected_urls, start=1):

            filename = safe_filename(
                urlsplit(url).path.split("/")[-1]
            )

            st.session_state.download_current_index = index
            st.session_state.download_current_file = filename
            st.session_state.download_progress = 0.0

            current_text.markdown(
                f"**فایل {index} از {total}:** `{filename}`"
            )

            file_progress.progress(0.0)

            def update_file_progress(percent, current_filename):

                percent = max(0.0, min(float(percent), 100.0))

                st.session_state.download_progress = percent

                file_progress.progress(
                    percent / 100.0
                )

                detail_text.caption(
                    f"پیشرفت فایل جاری: {percent:.1f}%"
                )

            try:

                result = download_single_file(
                    url,
                    overwrite=overwrite,
                    progress_callback=update_file_progress,
                )

                if result == "success":
                    st.session_state.download_success.append(filename)

                elif result == "skipped":
                    st.session_state.download_success.append(
                        filename + " (موجود)"
                    )

            except Exception as exc:

                st.session_state.download_failed.append(filename)

                add_log(
                    f"دانلود ناموفق {filename}: {exc}"
                )

            overall_progress.progress(index / total)

        st.session_state.download_status = "finished"

        status_box.update(
            label="عملیات دانلود به پایان رسید.",
            state="complete",
            expanded=True,
        )

    except Exception as exc:

        st.session_state.download_status = "error"

        add_log(f"خطای کلی برنامه: {exc}")

        status_box.update(
            label="عملیات با خطا متوقف شد.",
            state="error",
            expanded=True,
        )

    finally:

        st.session_state.download_current_file = ""


# ============================================================
# اجزای رابط کاربری
# ============================================================

def render_header():

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                🧬 Raabin WBC Downloader
            </div>
            <div class="hero-subtitle">
                ابزار دریافت و مدیریت فایل‌های دیتاست
                <b>Raabin-WBC</b>
                <br>
                انتخاب بازه فایل‌ها، دانلود با قابلیت Resume
                و مشاهده وضعیت دریافت اطلاعات.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_statistics():

    links = st.session_state.zip_links or []

    downloaded_count = len(
        list(DOWNLOAD_DIR.glob("*.zip"))
    )

    success_count = len(
        st.session_state.download_success
    )

    failed_count = len(
        st.session_state.download_failed
    )

    col1, col2, col3, col4 = st.columns(4)

    cards = [
        (col1, len(links), "فایل شناسایی‌شده"),
        (col2, downloaded_count, "فایل موجود"),
        (col3, success_count, "دانلود موفق"),
        (col4, failed_count, "دانلود ناموفق"),
    ]

    for col, number, label in cards:

        with col:

            st.markdown(
                f"""
                <div class="info-card">
                    <div class="info-number">{number:,}</div>
                    <div class="info-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_file_list():

    links = st.session_state.zip_links

    if not links:
        return

    with st.expander(
        f"مشاهده فهرست فایل‌ها ({len(links)} فایل)",
        expanded=False,
    ):

        search = st.text_input(
            "جست‌وجوی نام فایل",
            key="filename_search",
        )

        filtered = []

        for index, url in enumerate(links, start=1):

            filename = safe_filename(
                urlsplit(url).path.split("/")[-1]
            )

            if search.lower() in filename.lower():
                filtered.append((index, filename))

        if not filtered:

            st.info("فایلی با این نام پیدا نشد.")

        else:

            st.caption(
                f"{len(filtered)} فایل نمایش داده می‌شود."
            )

            for index, filename in filtered[:200]:

                st.text(f"{index:04d}  |  {filename}")

            if len(filtered) > 200:
                st.caption(
                    "برای جلوگیری از شلوغی، فقط ۲۰۰ نتیجه اول نمایش داده شد."
                )


def render_download_controls():

    links = st.session_state.zip_links

    if not links:
        return

    total = len(links)

    st.markdown(
        '<div class="section-title">تنظیم دانلود</div>',
        unsafe_allow_html=True,
    )

    range_value = st.text_input(
        "شماره فایل‌های موردنظر",
        value="1-20",
        placeholder="مثلاً 1-20 یا 1,3,5 یا all",
        key="download_range",
    )

    indices = parse_range(range_value, total)

    if indices is None:

        st.error(
            f"بازه واردشده معتبر نیست. شماره فایل‌ها باید بین ۱ و {total} باشند."
        )

        return

    selected_urls = [
        links[index - 1]
        for index in indices
    ]

    st.caption(
        f"تعداد فایل انتخاب‌شده: **{len(selected_urls)}** "
        f"| اولین فایل: **{indices[0]}** "
        f"| آخرین فایل: **{indices[-1]}**"
    )

    overwrite = st.checkbox(
        "دانلود مجدد فایل‌هایی که قبلاً دریافت شده‌اند",
        value=False,
    )

    st.warning(
        "فایل‌ها روی فضای ذخیره‌سازی سرور اجرای Streamlit ذخیره می‌شوند، "
        "نه مستقیماً روی کامپیوتر شما."
    )

    if st.button(
        "شروع دانلود",
        type="primary",
        use_container_width=True,
        disabled=not selected_urls,
    ):

        run_download(
            selected_urls,
            overwrite=overwrite,
        )


def render_results():

    status = st.session_state.download_status

    if status not in ("finished", "error"):
        return

    st.divider()

    st.markdown(
        '<div class="section-title">گزارش عملیات</div>',
        unsafe_allow_html=True,
    )

    success = st.session_state.download_success
    failed = st.session_state.download_failed

    col1, col2 = st.columns(2)

    with col1:
        st.metric("دانلود موفق", len(success))

    with col2:
        st.metric("دانلود ناموفق", len(failed))

    if failed:

        st.error("برخی فایل‌ها دانلود نشدند.")

        with st.expander("مشاهده فایل‌های ناموفق", expanded=True):

            for filename in failed:
                st.text(filename)

    if success:

        with st.expander("مشاهده فایل‌های موفق"):

            for filename in success:
                st.text(filename)


def render_logs():

    logs = st.session_state.download_logs

    with st.expander("گزارش فنی و لاگ‌ها", expanded=False):

        if not logs:

            st.info("هنوز گزارشی ثبت نشده است.")

        else:

            st.code(
                "\n".join(logs[-100:]),
                language="text",
            )

            st.download_button(
                "دریافت فایل گزارش",
                data="\n".join(logs).encode("utf-8"),
                file_name="download_log.txt",
                mime="text/plain",
                use_container_width=True,
            )


# ============================================================
# اجرای اصلی
# ============================================================

def main():

    render_header()

    with st.sidebar:

        st.markdown("## 🧬 Raabin WBC")

        st.caption("Dataset Downloader")

        st.divider()

        st.markdown("### اطلاعات منبع")

        st.markdown(
            """
            - **Dataset:** Raabin-WBC
            - **Directory:** First Microscope
            - **Format:** ZIP
            - **Download:** Resume enabled
            """
        )

        st.divider()

        st.markdown("### مسیر ذخیره‌سازی")

        st.code(str(DOWNLOAD_DIR.resolve()))

        st.caption(
            "این مسیر متعلق به محیط اجرای برنامه است."
        )

    # دریافت فهرست فایل‌ها

    col1, col2 = st.columns([3, 1])

    with col1:

        st.markdown(
            '<div class="section-title">فهرست دیتاست</div>',
            unsafe_allow_html=True,
        )

    with col2:

        if st.button(
            "دریافت / به‌روزرسانی فهرست",
            use_container_width=True,
        ):

            try:

                with st.spinner("در حال دریافت فهرست فایل‌ها..."):

                    links = get_zip_links()

                st.session_state.zip_links = links

                if links:

                    st.success(
                        f"{len(links)} فایل ZIP شناسایی شد."
                    )

                else:

                    st.warning(
                        "هیچ فایل ZIP در صفحه پیدا نشد."
                    )

            except Exception as exc:

                st.error(
                    f"دریافت فهرست ناموفق بود: {exc}"
                )

    if not st.session_state.zip_links:

        st.info(
            "برای مشاهده فایل‌های دیتاست، ابتدا روی "
            "«دریافت / به‌روزرسانی فهرست» کلیک کن."
        )

        return

    render_statistics()

    st.divider()

    render_file_list()

    st.divider()

    render_download_controls()

    render_results()

    render_logs()

    st.divider()

    st.markdown(
        """
        <p class="small-note">
        Raabin WBC Downloader |
        ابزار کمکی دریافت فایل‌های دیتاست
        </p>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
