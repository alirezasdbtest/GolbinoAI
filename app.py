import os
import re
import time
import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import streamlit as st

# ============================================================
# تنظیمات سراسری
# ============================================================
WORKER_BASE = "https://broad-dew-8b34.alirezasaidi13802001.workers.dev/"
PAGE_URL = (
    "https://dl.raabindata.com/"
    "Index%20of%20WBC%20Data/"
    "Index%20of%20WBC%20First_microscope/"
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}
DOWNLOAD_DIR = "downloads"
LOG_FILE_PATH = "download_log.txt"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def write_log(message: str) -> None:
    """نوشتن لاگ در فایل و در session_state برای نمایش در UI."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass
    logs = st.session_state.setdefault("download_logs", [])
    logs.append(entry)
    if len(logs) > 200:
        st.session_state.download_logs = logs[-200:]


def _natural_key(name: str):
    """مرتب‌سازی طبیعی: file_2 قبل از file_10."""
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", name)]


def get_zip_links(page_url: str):
    """دریافت لیست لینک‌های ZIP؛ در صورت خطا از Worker استفاده می‌کند."""
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=30)
        r.raise_for_status()
    except Exception:
        try:
            relative = page_url.split("dl.raabindata.com/", 1)[1]
            proxied = f"{WORKER_BASE.rstrip('/')}/{relative}"
            r = requests.get(proxied, headers=HEADERS, timeout=60)
            r.raise_for_status()
        except Exception:
            return []

    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.search(r"\.zip$", href, re.IGNORECASE):
            links.append(urljoin(page_url, href))

    links = sorted(set(links),
                   key=lambda u: _natural_key(unquote(os.path.basename(u))))
    return links


def parse_range(raw: str, total: int):
    """
    تبدیل ورودی کاربر به لیست شماره‌ها.
    پشتیبانی: "1-20"، "20-30"، "5"، "5-"، "all"
    """
    raw = raw.strip().lower()
    if raw in ("all", "*", ""):
        return list(range(1, total + 1))
    if "-" in raw:
        left, _, right = raw.partition("-")
        try:
            a = int(left.strip())
            b = int(right.strip()) if right.strip() else total
        except ValueError:
            return None
    else:
        try:
            a = b = int(raw)
        except ValueError:
            return None
    if not (1 <= a <= b <= total):
        return None
    return list(range(a, b + 1))


def download_single_file(
    original_url: str,
    dest_folder: str,
    worker_base: str,
    max_retries: int = 5,
    progress_callback=None,
) -> bool:
    """
    دانلود یک فایل با قابلیت Resume.
    progress_callback(percent: float, filename: str) برای به‌روزرسانی UI.
    """
    filename = unquote(os.path.basename(original_url))
    filepath = os.path.join(dest_folder, filename)

    if "dl.raabindata.com/" in original_url:
        relative = original_url.split("dl.raabindata.com/", 1)[1]
    else:
        relative = original_url
    proxied_url = f"{worker_base.rstrip('/')}/{relative}"

    # دریافت حجم نهایی
    total_size = 0
    for attempt in range(1, max_retries + 1):
        try:
            head = requests.head(proxied_url, headers=HEADERS, timeout=30)
            total_size = int(head.headers.get("content-length", 0))
            break
        except Exception:
            if attempt == max_retries:
                write_log(f"Khata dar size-e {filename}")
            time.sleep(2 * attempt)

    for attempt in range(1, max_retries + 1):
        try:
            initial_pos = 0
            if os.path.exists(filepath):
                initial_pos = os.path.getsize(filepath)
                if total_size > 0 and initial_pos >= total_size:
                    write_log(f"[Skip] {filename} ghablan kamel shode")
                    if progress_callback:
                        progress_callback(100.0, filename)
                    return True
                elif total_size > 0 and initial_pos < total_size:
                    write_log(f"[Resume] {filename} az "
                              f"{initial_pos/1024/1024:.1f} MB")

            download_headers = HEADERS.copy()
            if initial_pos > 0:
                download_headers["Range"] = f"bytes={initial_pos}-"

            with requests.get(
                proxied_url,
                headers=download_headers,
                stream=True,
                timeout=(30, 180),
            ) as r:
                if initial_pos > 0 and r.status_code == 206:
                    mode = "ab"
                else:
                    mode = "wb"
                    initial_pos = 0

                r.raise_for_status()
                downloaded = initial_pos
                with open(filepath, mode) as f:
                    for chunk in r.iter_content(chunk_size=128 * 1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total_size > 0:
                                pct = min(100.0, downloaded / total_size * 100)
                                progress_callback(pct, filename)

            if total_size > 0 and os.path.getsize(filepath) < total_size:
                raise ValueError("Hajm-e download kamtar az hajm nahaee ast!")

            write_log(f"[Success] {filename} kamel shod")
            if progress_callback:
                progress_callback(100.0, filename)
            return True

        except Exception as e:
            write_log(f"Khata dar talash-e {attempt} baraye {filename}: {e}")
            if attempt < max_retries:
                time.sleep(5 * attempt)
            else:
                write_log(f"[Failed] {filename} pas az {max_retries} talash")
                return False


# ============================================================
# بخش Streamlit
# ============================================================
def _run_download_thread(selected_zips, total_files, start_num):
    """
    دانلود در thread جداگانه اجرا می‌شود تا UI بلاک نشود.
    وضعیت در st.session_state ذخیره می‌شود.
    """
    state = st.session_state
    state.download_status = "running"
    state.download_current_index = 0
    state.download_total = len(selected_zips)
    state.download_current_file = ""
    state.download_progress = 0.0
    state.download_finished = False
    state.download_failed = []

    def progress_cb(pct, fname):
        state.download_progress = pct
        state.download_current_file = fname

    for offset, url in enumerate(selected_zips):
        idx = start_num + offset
        fname = unquote(os.path.basename(url))
        state.download_current_index = offset + 1
        state.download_current_file = fname
        state.download_progress = 0.0
        ok = download_single_file(
            url, DOWNLOAD_DIR, WORKER_BASE, progress_callback=progress_cb
        )
        if not ok:
            state.download_failed.append(fname)

    state.download_status = "finished"
    state.download_finished = True
    write_log("Amaliat-e download be payan rasid.")


def render_download_section():
    """
    این تابع را در app.py فراخوانی کنید تا بخش دانلود نمایش داده شود.
    """
    st.subheader("Download ZIP files from Raabin Data")

    state = st.session_state

    # ---------- 1) دریافت لیست ----------
    if "zip_links" not in state:
        state.zip_links = None

    if st.button("Get file list / Update list"):
        with st.spinner("Fetching file list..."):
            links = get_zip_links(PAGE_URL)
        if not links:
            st.error("No ZIP file found or could not reach the server.")
            return
        state.zip_links = links
        st.success(f"{len(links)} ZIP file found.")

    if not state.zip_links:
        st.info("Click the button above to load the file list.")
        return

    total = len(state.zip_links)
    st.write(f"**Total files:** {total}")

    # نمایش نمونه‌ای از لیست (نه همه، برای جلوگیری از شلوغی)
    with st.expander("Show first 10 file names"):
        for i, u in enumerate(state.zip_links[:10], 1):
            st.text(f"[{i}] {unquote(os.path.basename(u))}")
        if total > 10:
            st.caption(f"... and {total - 10} more")

    # ---------- 2) پرسش بازه ----------
    range_input = st.text_input(
        "Which files? (e.g. `1-20` or `20-30` or `all`)",
        value="1-20",
        key="range_input",
    )
    indices = parse_range(range_input, total)
    if not indices:
        st.warning(f"Invalid range. Must be between 1 and {total}.")
        return

    st.caption(
        f"Selected: files **{indices[0]}** to **{indices[-1]}** "
        f"({len(indices)} files)"
    )

    # ---------- 3) شروع دانلود ----------
    if "download_status" not in state:
        state.download_status = "idle"

    if state.download_status == "running":
        st.warning("Download already in progress...")
        # ادامه نمایش وضعیت در پایین
    elif st.button("Start download", type="primary"):
        selected = [state.zip_links[n - 1] for n in indices]
        # پاک کردن وضعیت قبلی
        state.download_finished = False
        state.download_failed = []
        state.download_logs = []
        thread = threading.Thread(
            target=_run_download_thread,
            args=(selected, total, indices[0]),
            daemon=True,
        )
        thread.start()
        st.rerun()

    # ---------- 4) نمایش وضعیت ----------
    if state.download_status == "running":
        st.info(
            f"Downloading file {state.download_current_index}/"
            f"{state.download_total}: {state.download_current_file}"
        )
        st.progress(state.download_progress / 100.0)
        # هر ۲ ثانیه UI را دوباره اجرا کن تا پیشرفت به‌روز شود
        time.sleep(2)
        st.rerun()

    if state.download_status == "finished":
        st.success("Download finished.")
        if state.download_failed:
            st.error(f"Failed files ({len(state.download_failed)}): "
                     f"{', '.join(state.download_failed)}")
        else:
            st.success("All files downloaded successfully.")

        # نمایش لاگ
        with st.expander("Download log", expanded=False):
            for line in state.download_logs[-50:]:
                st.text(line)

        # دکمه بازنشانی برای دانلود بازه بعدی
        if st.button("Reset / Download another range"):
            state.download_status = "idle"
            state.download_finished = False
            st.rerun()
