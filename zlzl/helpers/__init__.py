from . import fonts
from .aiohttp_helper import AioHttp
from .utils import *

flag = True
_install_attempts = 0
while flag:
    try:
        from .functions import *
        from .memeifyhelpers import *
        from .progress import *
        from .qhelper import process
        from .tools import *
        from .utils import _zedtools, _zedutils, _format

        break
    except ModuleNotFoundError as e:
        install_pip(e.name)
        _install_attempts += 1
        if _install_attempts > 5:
            break
