"""Theme commands backed by local assets shipped with this source."""

from pathlib import Path

from . import zedub
from ..core.managers import edit_or_reply

THEME_ASSETS = {
    "ث1": ("theme-photo-1.jpg", "ثيم الصورة 1"),
    "ث2": ("theme-video-2.mp4", "ثيم الفيديو 2"),
}
THEME_ASSET_DIR = Path(__file__).resolve().parents[1] / "theme_assets"


@zedub.zed_cmd(pattern="((?:ث|ن)(?:[1-9]|1[0-2]))$")
async def local_theme_command(event):
    command = event.pattern_match.group(1)
    asset = THEME_ASSETS.get(command)
    if asset:
        asset_path = THEME_ASSET_DIR / asset[0]
        if asset_path.exists():
            return await event.client.send_file(
                event.chat_id,
                str(asset_path),
                caption=f"**{asset[1]}**",
                reply_to=event.reply_to_msg_id,
            )
    await edit_or_reply(
        event,
        "**هذا الثيم لم تُضف له صورة أو فيديو بعد.**\n"
        "المتاح حالياً: `.ث1` للصورة و`.ث2` للفيديو.",
    )
