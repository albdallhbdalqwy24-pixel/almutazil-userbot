import importlib
import sys, asyncio
import zlzl
from zlzl import BOTLOG_CHATID, HEROKU_APP, PM_LOGGER_GROUP_ID
from telethon import functions
from .Config import Config
from .core.logger import logging
from .core.session import zedub
from .utils import mybot, autoname, autovars, saves, supscrips
from .utils import add_bot_to_logger_group, load_plugins, setup_bot, startupmessage, verifyLoggerGroup
from .utils.tools import create_supergroup
from .sql_helper.globals import addgvar

LOGS = logging.getLogger("ZTele")
cmdhr = Config.COMMAND_HAND_LER

try:
    LOGS.info("⌭ جـارِ تحميـل الملحقـات ⌭")
    zedub.loop.run_until_complete(autovars())
    LOGS.info("✓ تـم تحميـل الملحقـات .. بنجـاح ✓")
except Exception as e:
    LOGS.error(f"- {e}")

if not Config.ALIVE_NAME:
    try:
        LOGS.info("⌭ بـدء إضافة الاسـم التلقـائـي ⌭")
        zedub.loop.run_until_complete(autoname())
        LOGS.info("✓ تـم إضافة فار الاسـم .. بـنجـاح ✓")
    except Exception as e:
        LOGS.error(f"- {e}")

try:
    LOGS.info("⌭ بـدء تنزيـل زدثــون ⌭")
    zedub.loop.run_until_complete(setup_bot())
    LOGS.info("✓ تـم تنزيـل زدثــون .. بـنجـاح ✓")
except Exception as e:
    LOGS.error(f"{str(e)}")
    sys.exit()

class CatCheck:
    def __init__(self):
        self.sucess = True
Catcheck = CatCheck()

try:
    LOGS.info("⌭ بـدء إنشـاء البـوت التلقـائـي ⌭")
    zedub.loop.run_until_complete(mybot())
    LOGS.info("✓ تـم إنشـاء البـوت .. بـنجـاح ✓")
except Exception as e:
    LOGS.error(f"- {e}")

LOGS.info("تم تعطيل الانضمام التلقائي إلى القنوات والمجموعات في إعداد Termux.")


async def ensure_requested_logger_groups():
    """Create logger groups once, only after the local setup explicitly requests it."""
    global BOTLOG_CHATID, PM_LOGGER_GROUP_ID
    if not getattr(Config, "AUTO_CREATE_LOG_GROUPS", False):
        return

    bot_username = Config.TG_BOT_USERNAME
    if not bot_username:
        LOGS.error("لا يمكن إنشاء مجموعات السجل قبل التحقق من توكن بوت الخدمة.")
        return

    created_any = False
    if Config.PRIVATE_GROUP_BOT_API_ID == 0:
        result, group_id = await create_supergroup(
            "مجموعة سجل البوت", zedub, bot_username, "سجل تشغيل البوت الخاص.", None
        )
        if result == "error":
            LOGS.error(f"تعذر إنشاء مجموعة السجل: {group_id}")
        else:
            Config.PRIVATE_GROUP_BOT_API_ID = group_id
            Config.BOTLOG_CHATID = group_id
            Config.BOTLOG = True
            BOTLOG_CHATID = group_id
            zlzl.BOTLOG_CHATID = group_id
            zlzl.BOTLOG = True
            addgvar("PRIVATE_GROUP_BOT_API_ID", str(group_id))
            created_any = True

    if Config.PM_LOGGER_GROUP_ID in (0, -100):
        result, group_id = await create_supergroup(
            "مجموعة تخزين البوت", zedub, bot_username, "تخزين رسائل وتنبيهات البوت الخاصة.", None
        )
        if result == "error":
            LOGS.error(f"تعذر إنشاء مجموعة التخزين: {group_id}")
        else:
            Config.PM_LOGGER_GROUP_ID = group_id
            PM_LOGGER_GROUP_ID = group_id
            zlzl.PM_LOGGER_GROUP_ID = group_id
            addgvar("PM_LOGGER_GROUP_ID", str(group_id))
            created_any = True

    if created_any:
        startup_module = importlib.import_module("zlzl.utils.startup")
        startup_module.BOTLOG = Config.BOTLOG
        startup_module.BOTLOG_CHATID = Config.BOTLOG_CHATID
        startup_module.PM_LOGGER_GROUP_ID = Config.PM_LOGGER_GROUP_ID
        LOGS.info("تم إنشاء مجموعات السجل والتخزين وحفظ معرّفاتها محلياً.")


async def startup_process():
    await ensure_requested_logger_groups()
    await verifyLoggerGroup()
    await load_plugins("plugins")
    await load_plugins("assistant")
    await verifyLoggerGroup()
    if BOTLOG_CHATID != "me":
        await add_bot_to_logger_group(BOTLOG_CHATID)
    if PM_LOGGER_GROUP_ID not in (0, -100):
        await add_bot_to_logger_group(PM_LOGGER_GROUP_ID)
    await startupmessage()
    Catcheck.sucess = True
    return


zedub.loop.run_until_complete(startup_process())

if len(sys.argv) not in (1, 3, 4):
    zedub.disconnect()
elif not Catcheck.sucess:
    if HEROKU_APP is not None:
        HEROKU_APP.restart()
else:
    try:
        zedub.run_until_disconnected()
    except ConnectionError:
        pass
