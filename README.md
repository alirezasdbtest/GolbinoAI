# GolbinoAI

رابط کاربری پژوهشی برای تحلیل تصاویر میکروسکوپی خون محیطی و بررسی پنج گروه گلبول سفید.

## اجرا در سیستم شخصی
```bash
pip install -r requirements.txt
streamlit run app.py
```

## انتشار در Streamlit Community Cloud
- Repository: مخزن GitHub خودتان
- Branch: `main`
- Main file path: `app.py`

ساختار باید در ریشه مخزن به این صورت باشد:
```text
app.py
requirements.txt
.streamlit/config.toml
assets/golbino_mascot.png  # اختیاری
```

## وضعیت فعلی
این نسخه رابط کاربری اولیه است. هنوز مدل تشخیص به آن متصل نشده و نتایج ساختگی تولید نمی‌کند.
