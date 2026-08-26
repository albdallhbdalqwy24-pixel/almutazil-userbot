import sys
from subprocess import PIPE, Popen


PIP_COMPATIBILITY_MAP = {
    # Python removed cgi in 3.13. The maintained compatibility package
    # restores the original import name on modern Termux Python releases.
    "cgi": "legacy-cgi",
    # The import name is ``git``, but PyPI distributes it as GitPython.
    "git": "GitPython",
    "imdb": "IMDbPY",
    "search_engine_parser": "search-engine-parser",
    "fontTools": "fonttools",
    "barcode": "python-barcode",
    "gtts": "gTTS",
    "pySmartDL": "pySmartDL",
    "pymediainfo": "pymediainfo",
    "youtube_search": "youtube-search",
    "speedtest": "speedtest-cli",
}


def resolve_pip_package(module_name):
    return PIP_COMPATIBILITY_MAP.get(module_name, module_name)


def install_pip(pipfile):
    package_name = resolve_pip_package(pipfile)
    print(f"installing {package_name}")
    pip_cmd = [sys.executable, "-m", "pip", "install", package_name]
    process = Popen(pip_cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return stdout
