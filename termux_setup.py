#!/usr/bin/env python3
"""Local Termux setup wizard for AlMutazil.

The server binds only to 127.0.0.1 and requires a random one-time URL token.
It never exposes the setup page on the public internet.
"""

from __future__ import annotations

import html
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.py"
LOG_PATH = ROOT / "termux_setup.log"
TOKEN = secrets.token_urlsafe(24)
PORT = int(os.environ.get("ALMUTAZIL_SETUP_PORT", "8787"))
SESSION_FLOWS: dict[str, dict[str, object]] = {}
# Packages that commonly trigger native source builds or are optional on Android.
# Keep the basic userbot path free from native compiler work on Termux.
TERMUX_EXCLUDED = (
    "psutil",
    "psycopg2-binary",
    "py-tgcalls",
    "pytgcalls",
    "pyqt5",
    "opentele",
    "numpy",
    "vcsi",
    "moviepy",
    "lxml",
    "lxml_html_clean",
    "pyquery",
    "pygithub",
    "pynacl",
    "ujson",
    "regex",
    "tgcrypto",
    "search-engine-parser",
)


def is_termux_excluded(line: str) -> bool:
    candidate = line.strip().lower()
    if not candidate or candidate.startswith(("#", "-r ", "--")):
        return False
    package_name = re.split(r"[<=>!~\[;\s]", candidate, maxsplit=1)[0]
    return package_name in TERMUX_EXCLUDED


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def normalize_phone(value: str) -> str:
    digits = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
    phone = (value or "").translate(digits).replace("＋", "+")
    return re.sub(r"[\s\-()]+", "", phone)


def page(message: str = "", error: str = "") -> bytes:
    notice = (
        f'<div class="notice ok">{esc(message)}</div>' if message else ""
    )
    if error:
        notice += f'<div class="notice error">{esc(error)}</div>'
    body = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>إعداد AlMutazil — بوقاصد اليافعي</title>
<style>
:root {{ color-scheme: dark; --bg:#0d1117; --card:#161b22; --line:#30363d; --accent:#2f81f7; --muted:#8b949e; }}
* {{ box-sizing:border-box; }} body {{ margin:0; padding:22px 14px 40px; background:linear-gradient(145deg,#0d1117,#151b25); color:#f0f6fc; font-family:system-ui,-apple-system,"Segoe UI",sans-serif; }}
main {{ max-width:620px; margin:auto; }} .brand {{ text-align:center; margin:10px 0 20px; }} h1 {{ margin:0 0 8px; font-size:28px; }} .sub {{ color:var(--muted); line-height:1.7; }}
.card {{ background:rgba(22,27,34,.96); border:1px solid var(--line); border-radius:18px; padding:20px; box-shadow:0 14px 42px #0007; }}
label {{ display:block; margin:15px 0 7px; font-weight:700; }} small {{ display:block; color:var(--muted); font-weight:400; margin-top:4px; line-height:1.5; }}
input {{ width:100%; border:1px solid var(--line); border-radius:10px; background:#0d1117; color:#f0f6fc; padding:13px; font-size:15px; }} input:focus {{ outline:2px solid var(--accent); border-color:transparent; }}
button {{ width:100%; margin-top:22px; border:0; border-radius:11px; padding:14px; background:var(--accent); color:white; font-weight:800; font-size:16px; }} .secondary {{ display:block; margin-top:12px; padding:13px; border:1px solid var(--accent); border-radius:11px; color:#8ab4f8; text-align:center; text-decoration:none; font-weight:800; }}
.notice {{ margin:0 0 16px; padding:12px; border-radius:10px; line-height:1.6; }} .ok {{ background:#173b2a; color:#aff5c4; }} .error {{ background:#4a1f24; color:#ffb4b4; }}
.warn {{ margin-top:18px; color:#f2cc60; font-size:13px; line-height:1.7; }} code {{ background:#0d1117; padding:2px 5px; border-radius:5px; }}
</style></head><body><main>
<section class="brand"><h1>AlMutazil</h1><div class="sub">معالج إعداد محلي على Termux</div></section>
<section class="card">{notice}
<form method="post" action="/?token={esc(TOKEN)}">
<label>Telegram API ID<small>رقم APP_ID من my.telegram.org</small></label>
<input name="APP_ID" inputmode="numeric" required placeholder="12345678">
<label>Telegram API Hash</label>
<input name="API_HASH" required autocomplete="off" placeholder="رمز API Hash">
<label>String Session<small>يمكنك إنشاؤها من زر استخراج الجلسة؛ ستعود إلى هذه الخانة تلقائياً بعد ذلك.</small></label>
<input name="STRING_SESSION" autocomplete="off" required placeholder="أنشئها من الزر أدناه أو الصق جلسة جاهزة">
<label>توكن بوت الخدمة</label>
<input name="TG_BOT_TOKEN" autocomplete="off" required placeholder="توكن BotFather">
<label>معرّف مجموعة السجل<small>ضع 0 إذا لا تملك مجموعة مخصصة.</small></label>
<input name="PRIVATE_GROUP_BOT_API_ID" inputmode="numeric" value="0">
<label>معرّف مجموعة التخزين<small>ضع المعرف كاملاً بالشكل -100…، أو 0 إذا لا تملك مجموعة مخصصة.</small></label>
<input name="PM_LOGGER_GROUP_ID" inputmode="numeric" value="0">
<label>أيدي المالك<small>ضع 0 ليستخدم السورس أيدي الحساب بعد تسجيل الدخول.</small></label>
<input name="OWNER_ID" inputmode="numeric" value="0">
<label>رابط قاعدة البيانات<small>اتركه فارغاً لاستخدام SQLite المحلي. لا تضع رابطاً عشوائياً.</small></label>
<input name="DATABASE_URL" autocomplete="off" placeholder="اختياري">
<label>اسم الحساب الظاهر</label>
<input name="ALIVE_NAME" value="بوقاصد اليافعي">
<label>المنطقة الزمنية</label>
<input name="TZ" value="Asia/Riyadh">
<button type="submit">حفظ الإعدادات وبدء التثبيت</button>
</form>
<a id="session-link" class="secondary" href="/session?token={esc(TOKEN)}">استخراج String Session من Telegram</a>
<script>
const form = document.querySelector("form");
["APP_ID", "API_HASH", "STRING_SESSION"].forEach((name) => {{
  const field = form?.elements?.namedItem(name);
  const saved = sessionStorage.getItem("almutazil_" + name);
  if (field && !field.value && saved) field.value = saved;
}});
const sessionLink = document.getElementById("session-link");
if (sessionLink) {{
  sessionLink.addEventListener("click", () => {{
    ["APP_ID", "API_HASH"].forEach((name) => {{
      const field = form?.elements?.namedItem(name);
      sessionStorage.setItem("almutazil_" + name, field?.value || "");
    }});
  }});
}}
</script>
<div class="warn">هذه الصفحة محلية على جهازك فقط وتعمل على 127.0.0.1. لا تشارك الرابط أو القيم السرية. بعد الحفظ سيتم إنشاء <code>config.py</code> بصلاحيات خاصة ثم بدء تثبيت المكتبات.</div>
</section></main></body></html>"""
    return body.encode("utf-8")


def write_config(values: dict[str, str]) -> None:
    def integer(name: str, default: str = "0") -> str:
        raw = (values.get(name) or default).strip()
        return str(int(raw or default))

    database_url = values.get("DATABASE_URL", "").strip() or None
    content = f'''from sample_config import Config\n\n\nclass Development(Config):\n    APP_ID = {integer("APP_ID")}\n    API_HASH = {values.get("API_HASH", "").strip()!r}\n    ALIVE_NAME = {values.get("ALIVE_NAME", "بوقاصد اليافعي").strip()!r}\n    DB_URI = {database_url!r}\n    STRING_SESSION = {values.get("STRING_SESSION", "").strip()!r}\n    TG_BOT_TOKEN = {values.get("TG_BOT_TOKEN", "").strip()!r}\n    PRIVATE_GROUP_BOT_API_ID = {integer("PRIVATE_GROUP_BOT_API_ID")}\n    OWNER_ID = {integer("OWNER_ID")}\n    COMMAND_HAND_LER = "."\n    SUDO_COMMAND_HAND_LER = "."\n    TZ = {values.get("TZ", "Asia/Riyadh").strip()!r}\n'''
    content = content.replace(
        f"    PRIVATE_GROUP_BOT_API_ID = {integer('PRIVATE_GROUP_BOT_API_ID')}\n",
        f"    PRIVATE_GROUP_BOT_API_ID = {integer('PRIVATE_GROUP_BOT_API_ID')}\n"
        f"    PM_LOGGER_GROUP_ID = {integer('PM_LOGGER_GROUP_ID')}\n"
        "    HEROKU_API_KEY = None\n"
        "    HEROKU_APP_NAME = None\n",
    )
    temporary = CONFIG_PATH.with_suffix(".py.tmp")
    temporary.write_text(content, encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(CONFIG_PATH)


def install_and_start() -> None:
    # Start every installation with a clean log so stale failures are not
    # mistaken for errors from the current attempt.
    with LOG_PATH.open("w", encoding="utf-8") as log:
        log.write("\n=== AlMutazil setup started ===\n")
        log.flush()
        requirements = ROOT / "requirements.txt"
        if "com.termux" in os.environ.get("PREFIX", ""):
            # Keep the production requirements unchanged. These packages are not
            # buildable on Android and are optional for the basic userbot flow.
            filtered = ROOT / ".requirements-termux.txt"
            lines = requirements.read_text(encoding="utf-8").splitlines()
            pkg = shutil.which("pkg")
            if pkg:
                log.write("Installing Termux binary packages.\n")
                numpy_result = subprocess.run(
                    [pkg, "install", "python-numpy", "python-lxml", "ffmpeg", "git", "-y"],
                    cwd=ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
                if numpy_result.returncode != 0:
                    log.write("Termux python-numpy installation failed; pip may try the source build.\n")
            else:
                log.write("Termux pkg command was not found; continuing with filtered pip requirements.\n")
            filtered.write_text(
                "\n".join(line for line in lines if not is_termux_excluded(line)) + "\n",
                encoding="utf-8",
            )
            requirements = filtered
            log.write("Using Termux-compatible optional dependency filter.\n")
        command = [sys.executable, "-m", "pip", "install", "-r", str(requirements)]
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        if requirements.name == ".requirements-termux.txt":
            requirements.unlink(missing_ok=True)
        if result.returncode != 0:
            log.write(f"\nInstallation failed with exit code {result.returncode}.\n")
            return
        log.write("\nInstallation completed. Starting AlMutazil.\n")
        log.flush()
        subprocess.Popen(
            [sys.executable, "-m", "zlzl"],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )


def ensure_telethon() -> bool:
    """Install the sole dependency needed by the local session page if absent."""
    try:
        import telethon  # noqa: F401
    except ModuleNotFoundError:
        print("جارِ تثبيت Telethon لفتح صفحة تسجيل Telegram المحلية...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "Telethon"])
        if result.returncode != 0:
            print("تعذر تثبيت Telethon. أعد المحاولة بعد التحقق من اتصال الإنترنت.")
            return False
    return True


def session_page(message: str = "", error: str = "", flow_id: str = "", password_step: bool = False, session_value: str = "", values: dict[str, str] | None = None) -> bytes:
    values = values or {}
    notice = f'<div class="notice ok">{esc(message)}</div>' if message else ""
    if error:
        notice += f'<div class="notice error">{esc(error)}</div>'
    if session_value:
        form = f'''<label>String Session</label>
<textarea id="session" readonly>{esc(session_value)}</textarea>
<button type="button" onclick="navigator.clipboard.writeText(document.getElementById('session').value)">نسخ كود الجلسة</button>
<a class="secondary" href="/?token={esc(TOKEN)}">العودة إلى الإعداد وحفظ الجلسة</a>
<div class="warn">تم حفظ الجلسة مؤقتاً في المتصفح المحلي وستظهر في نموذج الإعداد عند الرجوع. لا ترسلها لأي شخص.</div>'''
    elif password_step:
        form = f'''<p class="sub">تم قبول كود Telegram، لكن الحساب محمي بالتحقق بخطوتين.</p>
<form method="post" action="/session/verify?token={esc(TOKEN)}">
<input type="hidden" name="flow_id" value="{esc(flow_id)}">
<label>كلمة مرور التحقق بخطوتين</label>
<input name="password" type="password" required autocomplete="off">
<button type="submit">إكمال استخراج الجلسة</button>
</form>'''
    elif flow_id:
        form = f'''<p class="sub">تم إرسال كود تسجيل الدخول إلى Telegram. أدخله هنا.</p>
<form method="post" action="/session/verify?token={esc(TOKEN)}">
<input type="hidden" name="flow_id" value="{esc(flow_id)}">
<label>كود Telegram</label>
<input name="code" inputmode="numeric" autocomplete="one-time-code" required>
<button type="submit">التحقق وإظهار الجلسة</button>
</form>'''
    else:
        form = f'''<form method="post" action="/session?token={esc(TOKEN)}">
<label>Telegram API ID</label>
<input name="api_id" inputmode="numeric" required placeholder="12345678" value="{esc(values.get('api_id', ''))}">
<label>Telegram API Hash</label>
<input name="api_hash" required autocomplete="off" value="{esc(values.get('api_hash', ''))}">
<label>رقم الجوال<small>استخدم الصيغة الدولية مثل +9665xxxxxxxx</small></label>
<input name="phone" inputmode="tel" required placeholder="+966" value="{esc(values.get('phone', ''))}">
<button type="submit">إرسال كود Telegram</button>
</form>'''
    body = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>استخراج String Session</title><style>
:root {{ color-scheme: dark; --bg:#0d1117; --card:#161b22; --line:#30363d; --accent:#2f81f7; --muted:#8b949e; }} * {{ box-sizing:border-box; }} body {{ margin:0; padding:22px 14px 40px; background:linear-gradient(145deg,#0d1117,#151b25); color:#f0f6fc; font-family:system-ui,-apple-system,"Segoe UI",sans-serif; }} main {{ max-width:620px; margin:auto; }} .brand {{ text-align:center; margin:10px 0 20px; }} h1 {{ margin:0 0 8px; font-size:27px; }} .sub {{ color:var(--muted); line-height:1.7; }} .card {{ background:rgba(22,27,34,.96); border:1px solid var(--line); border-radius:18px; padding:20px; box-shadow:0 14px 42px #0007; }} label {{ display:block; margin:15px 0 7px; font-weight:700; }} small {{ display:block; color:var(--muted); font-weight:400; margin-top:4px; line-height:1.5; }} input,textarea {{ width:100%; border:1px solid var(--line); border-radius:10px; background:#0d1117; color:#f0f6fc; padding:13px; font-size:15px; }} textarea {{ min-height:150px; direction:ltr; word-break:break-all; }} input:focus,textarea:focus {{ outline:2px solid var(--accent); border-color:transparent; }} button {{ width:100%; margin-top:22px; border:0; border-radius:11px; padding:14px; background:var(--accent); color:white; font-weight:800; font-size:16px; }} .notice {{ margin:0 0 16px; padding:12px; border-radius:10px; line-height:1.6; }} .ok {{ background:#173b2a; color:#aff5c4; }} .error {{ background:#4a1f24; color:#ffb4b4; }} .warn {{ margin-top:18px; color:#f2cc60; font-size:13px; line-height:1.7; }}
</style></head><body><main><section class="brand"><h1>استخراج String Session</h1><div class="sub">AlMutazil — يعمل محلياً على جهازك فقط</div></section><section class="card">{notice}{form}<div class="warn">لا تشارك رابط الصفحة أو كود الجلسة. هذه الصفحة مرتبطة بـ 127.0.0.1 ولا تحفظ الجلسة في ملف السجل.</div></section></main><script>
const savedSession = document.getElementById("session");
if (savedSession) sessionStorage.setItem("almutazil_STRING_SESSION", savedSession.value);
["api_id", "api_hash"].forEach((name) => {{
  const field = document.querySelector('[name="' + name + '"]');
  const saved = sessionStorage.getItem("almutazil_" + name.toUpperCase());
  if (field && !field.value && saved) field.value = saved;
}});
</script></body></html>'''
    return body.encode("utf-8")


def _run_loop(loop: object) -> None:
    import asyncio

    asyncio.set_event_loop(loop)
    loop.run_forever()


def begin_session(api_id: int, api_hash: str, phone: str) -> tuple[str, object, object, threading.Thread]:
    import asyncio
    from telethon import TelegramClient
    from telethon.sessions import StringSession

    loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=_run_loop, args=(loop,), daemon=True)
    loop_thread.start()
    client = TelegramClient(StringSession(), api_id, api_hash, loop=loop)

    async def send_code() -> str:
        await client.connect()
        sent = await client.send_code_request(phone)
        return sent.phone_code_hash

    phone_code_hash = asyncio.run_coroutine_threadsafe(send_code(), loop).result(timeout=120)
    return phone_code_hash, client, loop, loop_thread


def finish_session(flow: dict[str, object], code: str = "", password: str = "") -> tuple[str, str]:
    import asyncio
    from telethon.errors import SessionPasswordNeededError

    client = flow["client"]
    loop = flow["loop"]

    async def sign_in() -> tuple[str, str]:
        if flow.get("password_step"):
            await client.sign_in(password=password)
        else:
            try:
                await client.sign_in(
                    phone=flow["phone"],
                    code=code,
                    phone_code_hash=flow["phone_code_hash"],
                )
            except SessionPasswordNeededError:
                flow["password_step"] = True
                return "", "password"
        session_value = client.session.save()
        await client.disconnect()
        return session_value, "done"

    result = asyncio.run_coroutine_threadsafe(sign_in(), loop).result(timeout=120)
    if result[1] == "done":
        loop.call_soon_threadsafe(loop.stop)
        flow["loop_thread"].join(timeout=5)
        loop.close()
    return result


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args: object) -> None:
        return

    def authorized(self) -> bool:
        query_token = parse_qs(urlparse(self.path).query).get("token", [""])[0]
        return secrets.compare_digest(query_token, TOKEN)

    def send_page(self, data: bytes, status: int = 200) -> None:
        try:
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            # The browser may close/reload while the local page is being sent.
            # This is harmless and must not print a traceback in Termux.
            return

    def do_GET(self) -> None:  # noqa: N802
        if not self.authorized():
            self.send_page(page(error="الرابط غير صالح أو انتهت جلسة الإعداد."), 403)
            return
        route = urlparse(self.path).path
        self.send_page(session_page() if route == "/session" else page())

    def do_POST(self) -> None:  # noqa: N802
        if not self.authorized():
            self.send_page(page(error="الرابط غير صالح أو انتهت جلسة الإعداد."), 403)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        values = {key: items[0] for key, items in parse_qs(raw, keep_blank_values=True).items()}
        route = urlparse(self.path).path
        if route == "/session":
            try:
                raw_api_id = values.get("api_id", "").strip()
                api_hash = values.get("api_hash", "").strip()
                phone = normalize_phone(values.get("phone", ""))
                if not raw_api_id.isdigit():
                    raise ValueError("APP_ID يجب أن يكون رقماً صحيحاً بدون أحرف")
                api_id = int(raw_api_id)
                if api_id <= 0:
                    raise ValueError("APP_ID يجب أن يكون أكبر من صفر")
                if not api_hash:
                    raise ValueError("API_HASH فارغ؛ أدخل قيمة API Hash كاملة")
                if not re.fullmatch(r"\+[0-9]{8,15}", phone):
                    raise ValueError("رقم الجوال يجب أن يكون بالصيغة الدولية مثل +9665xxxxxxxx")
                flow_id = secrets.token_urlsafe(18)
                phone_code_hash, client, loop, loop_thread = begin_session(api_id, api_hash, phone)
                SESSION_FLOWS[flow_id] = {
                    "phone": phone,
                    "phone_code_hash": phone_code_hash,
                    "client": client,
                    "loop": loop,
                    "loop_thread": loop_thread,
                    "password_step": False,
                }
                self.send_page(session_page(message="تم إرسال كود Telegram.", flow_id=flow_id))
            except Exception as exc:  # noqa: BLE001
                self.send_page(session_page(error=f"تعذر إرسال الكود: {exc}", values=values), 400)
            return
        if route == "/session/verify":
            flow_id = values.get("flow_id", "")
            flow = SESSION_FLOWS.get(flow_id)
            if not flow:
                self.send_page(session_page(error="انتهت جلسة الاستخراج، ابدأ من جديد."), 400)
                return
            try:
                session_value, status = finish_session(
                    flow,
                    code=values.get("code", "").strip(),
                    password=values.get("password", ""),
                )
                if status == "password":
                    self.send_page(session_page(message="أدخل كلمة مرور التحقق بخطوتين.", flow_id=flow_id, password_step=True))
                else:
                    SESSION_FLOWS.pop(flow_id, None)
                    self.send_page(session_page(message="تم إنشاء الجلسة بنجاح.", session_value=session_value))
            except Exception as exc:  # noqa: BLE001
                self.send_page(session_page(error=f"تعذر التحقق: {exc}", flow_id=flow_id, password_step=bool(flow.get("password_step"))), 400)
            return
        if route != "/":
            self.send_page(page(error="المسار غير موجود."), 404)
            return
        try:
            if not values.get("APP_ID", "").strip().isdigit():
                raise ValueError("APP_ID يجب أن يكون رقماً فقط")
            if not values.get("API_HASH", "").strip():
                raise ValueError("API_HASH مطلوب")
            if not values.get("STRING_SESSION", "").strip():
                raise ValueError("أنشئ String Session من الزر قبل حفظ الإعدادات")
            if not values.get("TG_BOT_TOKEN", "").strip():
                raise ValueError("توكن بوت الخدمة مطلوب لهذا السورس")
            write_config(values)
        except Exception as exc:  # noqa: BLE001
            self.send_page(page(error=str(exc)), 400)
            return
        self.send_page(page("تم حفظ الإعدادات. بدأ تثبيت المتطلبات؛ راقب termux_setup.log عند الحاجة."))
        threading.Thread(target=install_and_start, daemon=True).start()


def main() -> None:
    if not ensure_telethon():
        return
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}/?token={TOKEN}"
    print(f"افتح هذا الرابط في متصفح الجوال:\n{url}")
    opener = shutil.which("termux-open-url")
    if opener:
        subprocess.Popen([opener, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("بعد تعبئة النموذج سيُنشأ config.py وتبدأ عملية التثبيت والتشغيل.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nتم إيقاف معالج الإعداد.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
