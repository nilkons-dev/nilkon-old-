"""Loads VLC and warms it up in the background. Imported first (by the splash screen), so VLC's slow plugin scan runs
while the rest of the program is still loading."""
import os
import sys
import threading
from pathlib import Path

def _use_bundled_vlc():
    """The installed app carries its own copy of VLC (folder 'vlc' next to the program), so nothing else is needed."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    folder = base / "vlc"
    lib = folder / "libvlc.dll"
    if not lib.exists():
        return
    os.environ["PYTHON_VLC_LIB_PATH"] = str(lib)
    os.environ["PYTHON_VLC_MODULE_PATH"] = str(folder / "plugins")
    os.environ["VLC_PLUGIN_PATH"] = str(folder / "plugins")
    try:
        os.add_dll_directory(str(folder))
    except Exception:
        pass


_use_bundled_vlc()

try:
    import vlc
    VLC_ERROR = None
except Exception as _exc:  # reported nicely once the QApplication exists
    vlc = None
    VLC_ERROR = _exc

_VLC_BASE_ARGS = ["--no-video", "--quiet", "--no-osd", "--no-stats", "--no-metadata-network-access"]
_prewarm = {"instance": None, "thread": None}


def _prewarm_vlc():
    """Scanning VLC's plugins is the slowest part of start-up, so it runs in the background while the window is built."""
    try:
        _prewarm["instance"] = vlc.Instance(*_VLC_BASE_ARGS)
    except Exception:
        _prewarm["instance"] = None


def _prewarm_ytdlp():
    try:
        import online as _online
        _online._ytdlp()
    except Exception:
        pass


threading.Thread(target=_prewarm_ytdlp, name="ytdlp-prewarm", daemon=True).start()
if vlc is not None:
    _prewarm["thread"] = threading.Thread(target=_prewarm_vlc, name="vlc-prewarm", daemon=True)
    _prewarm["thread"].start()

