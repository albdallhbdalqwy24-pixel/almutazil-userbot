"""Graceful response for legacy theme assets absent from this source tree."""

from . import zedub
from ..core.managers import edit_or_reply


@zedub.zed_cmd(pattern="(?:ث|ن)(?:[1-9]|1[0-2])$")
async def unavailable_theme_command(event):
    await edit_or_reply(
        event,
        "**أوامر الثيمات مسجلة، لكن ملفات الثيمات الأصلية غير موجودة في السورس المنقول؛ "
        "لذلك لا يمكن إرسال ثيم ناقص. بقية الأوامر تعمل بشكل مستقل.**",
    )
