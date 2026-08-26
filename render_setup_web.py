"""Temporary, password-protected Render setup page for ZTele.

Telegram values are accepted over the Render HTTPS endpoint and passed only to
the child process environment. They are never written to config.py or Git.
"""

from __future__ import annotations

import hmac
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from flask import Flask, Response, request


ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
process_lock = threading.Lock()
userbot_process: subprocess.Popen[str] | None = None


PAGE = """<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>إعداد ZTele المؤقت</title>
<style>body{margin:0;background:#0f172a;color:#e2e8f0;font-family:system-ui;padding:24px}.box{max-width:640px;margin:auto;background:#172033;border:1px solid #334155;border-radius:16px;padding:24px}h1{margin-top:0}p{color:#cbd5e1;line-height:1.7}label{display:block;margin:15px 0 6px;font-weight:700}input{width:100%;box-sizing:border-box;padding:12px;border-radius:9px;border:1px solid #475569;background:#0b1220;color:#fff}button{margin-top:20px;width:100%;padding:13px;border:0;border-radius:9px;background:#2563eb;color:#fff;font-weight:700;font-size:16px}.note{background:#111827;padding:12px;border-radius:8px;font-size:14px}.ok{color:#86efac}.err{color:#fca5a5}</style></head><body><main class="box"><h1>إعداد ZTele المؤقت</h1>
<p>هذه الصفحة محمية. القيم تُرسل إلى عملية التشغيل فقط ولا تُحفظ في Git أو في <code>config.py</code>.</p>{message}
<form method="post" action="/configure"><label>كلمة حماية الصفحة</label><input name="setup_password" type="password" required autocomplete="current-password">
<label>API ID</label><input name="APP_ID" inputmode="numeric" required>
<label>API Hash</label><input name="API_HASH" required>
<label>String Session</label><input name="STRING_SESSION" required>
<label>توكن البوت المساعد</label><input name="TG_BOT_TOKEN" required>
<label>Owner ID</label><input name="OWNER_ID" inputmode="numeric" required>
<label>اسم العرض</label><input name="ALIVE_NAME" value="ZTele">
<label>معرف مجموعة السجل (اختياري)</label><input name="PRIVATE_GROUP_BOT_API_ID" value="0">
<label>معرف مجموعة التخزين (اختياري)</label><input name="PM_LOGGER_GROUP_ID" value="0">
<button type="submit">حفظ وتشغيل مؤقتاً</button></form>
<p class="note">تتوقف النسخة المجانية عند الخمول أو إعادة التشغيل، ولا تحفظ هذه القيم بعدها. لا تستخدمها لتشغيل دائم.</p></main></body></html>"""


def html(message: str = "") -> Response:
    return Response(
        PAGE.replace("{message}", message),
        content_type="text/html; charset=utf-8",
    )


def setup_password() -> str:
    return os.environ.get("SETUP_PASSWORD", "")


def safe_integer(value: str, field: str, allow_zero: bool = True) -> str:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} يجب أن يكون رقماً صحيحاً.") from error
    if not allow_zero and parsed == 0:
        raise ValueError(f"{field} مطلوب.")
    return str(parsed)


def build_environment(values: dict[str, str]) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "APP_ID": safe_integer(values.get("APP_ID", ""), "API ID", allow_zero=False),
            "API_HASH": values.get("API_HASH", "").strip(),
            "STRING_SESSION": values.get("STRING_SESSION", "").strip(),
            "TG_BOT_TOKEN": values.get("TG_BOT_TOKEN", "").strip(),
            "OWNER_ID": safe_integer(values.get("OWNER_ID", ""), "Owner ID", allow_zero=False),
            "ALIVE_NAME": values.get("ALIVE_NAME", "ZTele").strip() or "ZTele",
            "PRIVATE_GROUP_BOT_API_ID": safe_integer(values.get("PRIVATE_GROUP_BOT_API_ID", "0"), "معرف السجل"),
            "PM_LOGGER_GROUP_ID": safe_integer(values.get("PM_LOGGER_GROUP_ID", "0"), "معرف التخزين"),
            "DATABASE_URL": "sqlite:///render_runtime.db",
            "AUTO_CREATE_LOG_GROUPS": "false",
            "ZELZAL_A": "0",
            "PYTHONUNBUFFERED": "1",
        }
    )
    for key in ("API_HASH", "STRING_SESSION", "TG_BOT_TOKEN"):
        if not environment[key]:
            raise ValueError(f"{key} مطلوب.")
    return environment


def stream_userbot_output(process: subprocess.Popen[str]) -> None:
    """Forward every child-process line to Render's primary log stream."""
    if process.stdout is None:
        return
    for line in process.stdout:
        print(f"[USERBOT] {line}", end="", flush=True)
    exit_code = process.wait()
    print(f"[USERBOT] process exited with code {exit_code}", flush=True)


@app.get("/healthz")
def healthz() -> Response:
    running = userbot_process is not None and userbot_process.poll() is None
    return Response("ok" if running else "setup", status=200, content_type="text/plain")


@app.get("/")
def index() -> Response:
    if not setup_password():
        return html('<p class="err">يجب ضبط SETUP_PASSWORD في إعدادات Render أولاً.</p>')
    return html()


@app.post("/configure")
def configure() -> Response:
    global userbot_process
    expected_password = setup_password()
    supplied_password = request.form.get("setup_password", "")
    if not expected_password or not hmac.compare_digest(supplied_password, expected_password):
        return html('<p class="err">كلمة الحماية غير صحيحة.</p>')
    try:
        environment = build_environment(dict(request.form))
    except ValueError as error:
        return html(f'<p class="err">{error}</p>')

    with process_lock:
        if userbot_process is not None and userbot_process.poll() is None:
            return html('<p class="ok">اليوزربوت يعمل بالفعل في هذه النسخة المؤقتة.</p>')
        userbot_process = subprocess.Popen(
            [sys.executable, "-u", "-m", "zlzl"],
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        threading.Thread(
            target=stream_userbot_output,
            args=(userbot_process,),
            daemon=True,
        ).start()
        time.sleep(0.5)
        if userbot_process.poll() is not None:
            return html('<p class="err">تعذر بدء اليوزربوت. افتح سجل Render؛ ستظهر تفاصيل الخطأ تحت USERBOT.</p>')
    return html('<p class="ok">تم بدء اليوزربوت. راقب السجل من لوحة Render للتأكد من الإقلاع.</p>')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
