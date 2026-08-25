"""Download Python attachments from the configured plugin channel without executing them.

Run this only on the Termux device that holds the user's local ``config.py``.
Downloaded files are stored outside ``zlzl/plugins`` so they cannot be imported
by the userbot automatically.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterDocument

from config import Development


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "extracted_channel_plugins"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"


def classify(filename: str) -> str:
    lowered = filename.lower()
    if any(marker in lowered for marker in ("vip", "premium", "paid", "مدفوع")):
        return "vip"
    if any(marker in lowered for marker in ("free", "public", "مجاني")):
        return "free"
    return "unclassified"


async def extract() -> None:
    if not Development.STRING_SESSION:
        raise RuntimeError("لا توجد STRING_SESSION في config.py.")
    if not Development.ZELZAL_A:
        raise RuntimeError("لا يوجد ZELZAL_A لتحديد قناة الإضافات.")

    OUTPUT_DIR.mkdir(mode=0o700, exist_ok=True)
    records: list[dict[str, object]] = []
    client = TelegramClient(
        StringSession(Development.STRING_SESSION),
        Development.APP_ID,
        Development.API_HASH,
    )
    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise RuntimeError("الجلسة في config.py غير صالحة أو منتهية.")
        entity = await client.get_entity(Development.ZELZAL_A)
        async for message in client.iter_messages(entity, filter=InputMessagesFilterDocument):
            filename = Path((message.file and message.file.name) or "").name
            if not filename.lower().endswith(".py"):
                continue
            destination = OUTPUT_DIR / filename
            if not destination.exists():
                await client.download_media(message, file=destination)
            records.append(
                {
                    "message_id": message.id,
                    "filename": filename,
                    "classification": classify(filename),
                    "path": str(destination.relative_to(ROOT)),
                }
            )
    finally:
        await client.disconnect()

    MANIFEST_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"تم استخراج {len(records)} ملف Python إلى: {OUTPUT_DIR}")
    print(f"قائمة الملفات: {MANIFEST_PATH}")
    print("لم يتم تشغيل أي ملف مستخرج.")


if __name__ == "__main__":
    asyncio.run(extract())
