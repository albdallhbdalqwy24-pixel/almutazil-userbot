from .extdl import *
from .paste import *
# memeifyhelpers can be imported while this package is still loading through
# format -> functions.  Make the command helper available before optional
# helpers below to avoid a circular-import failure.
from . import utils as _zedutils

flag = True
_install_attempts = 0
while flag:
    try:
        from . import format as _format
        from . import tools as _zedtools
        from . import utils as _zedutils
        from .events import *
        from .format import *
        from .tools import *
        from .utils import *

        break
    except ModuleNotFoundError as e:
        install_pip(e.name)
        _install_attempts += 1
        if _install_attempts > 5:
            break
