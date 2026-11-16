"""Builds the Windows application:  dist/NILKON/NILKON.exe  (+ NILKON_Setup_<version>.exe when Inno Setup is installed).

Needs: Python 3.10+ (64-bit) with the packages of requirements.txt and pyinstaller, and VLC 64-bit installed
(its files are copied into the app, so the finished app does not need VLC on the user's PC).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from appinfo import APP_VERSION  # noqa: E402


def find_vlc() -> Path:
    cands = [os.environ.get("VLC_DIR", ""), r"C:\Program Files\VideoLAN\VLC", r"C:\Program Files (x86)\VideoLAN\VLC"]
    for c in cands:
        if c and (Path(c) / "libvlc.dll").exists():
            return Path(c)
    sys.exit("VLC 64-bit was not found. Install it from videolan.org (or set VLC_DIR) and run this again.")


def sign(path: Path) -> None:
    """Signs a file when a certificate is configured (SIGN_PFX_FILE + SIGN_PFX_PASSWORD); otherwise does nothing."""
    pfx = os.environ.get("SIGN_PFX_FILE")
    if not pfx or not Path(pfx).exists():
        return
    import glob
    tools = sorted(glob.glob(r"C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe"))
    if not tools:
        print("signtool not found - not signed:", path)
        return
    subprocess.check_call([tools[-1], "sign", "/f", pfx, "/p", os.environ.get("SIGN_PFX_PASSWORD", ""), "/fd", "SHA256",
                           "/tr", "http://timestamp.digicert.com", "/td", "SHA256", str(path)])
    print("signed:", path.name)


def prune_app(folder: Path) -> None:
    """Fewer files = a faster first start (Windows Defender checks every file the first time it is loaded)."""
    removed = 0
    for pattern in ("opengl32sw.dll", "Qt6Pdf*.dll", "Qt6Quick*.dll", "Qt6Qml*.dll", "Qt6VirtualKeyboard*.dll",
                    "Qt6Designer*.dll", "Qt6Test*.dll"):
        for f in folder.rglob(pattern):
            try:
                f.unlink()
                removed += 1
            except OSError:
                pass
    for name in ("translations", "qml"):
        for d in list(folder.rglob(name)):
            if d.is_dir() and "PySide6" in d.parts:
                shutil.rmtree(d, ignore_errors=True)
                removed += 1
    print("Pruned", removed, "unused files")


def main() -> None:
    vlc_dir = find_vlc()
    bundle = ROOT / "vlc_bundle"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir()
    for name in ("libvlc.dll", "libvlccore.dll"):
        shutil.copy2(vlc_dir / name, bundle / name)
    shutil.copytree(vlc_dir / "plugins", bundle / "plugins")
    # NILKON only plays audio: drop the video / interface / script plugins (smaller app, quicker start-up)
    for sub in ("lua", "gui", "video_output", "video_filter", "video_chroma", "video_splitter", "visualization",
                "stream_out", "text_renderer", "spu", "control"):
        shutil.rmtree(bundle / "plugins" / sub, ignore_errors=True)
    # a ready plugin list makes VLC start without scanning every plugin file
    gen = vlc_dir / "vlc-cache-gen.exe"
    if gen.exists():
        r = subprocess.run([str(gen), str(bundle / "plugins")], capture_output=True)
        print("plugin cache:", "created" if r.returncode == 0 else "skipped")
    print("VLC copied from", vlc_dir)

    def has(mod: str) -> bool:
        return subprocess.run([sys.executable, "-c", f"import {mod}"], capture_output=True).returncode == 0

    extra = []
    for mod, flag in (("mutagen", "--collect-submodules"), ("miniaudio", "--collect-all"), ("yt_dlp", "--collect-all"),
                      ("imageio_ffmpeg", "--collect-all"), ("pypresence", "--collect-submodules")):
        if has(mod):
            extra += [flag, mod]

    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed", "--onedir",
           "--name", "NILKON", "--icon", str(ROOT / "assets" / "logo.ico"),
           "--add-data", f"{ROOT / 'assets'};assets", "--add-data", f"{bundle};vlc",
           "--hidden-import", "PySide6.QtSvg", "--hidden-import", "music_player", "--exclude-module", "tkinter",
           "--exclude-module", "PySide6.QtWebEngineCore", "--exclude-module", "PySide6.QtWebEngineWidgets",
           "--exclude-module", "PySide6.QtQuick", "--exclude-module", "PySide6.QtQml",
           "--exclude-module", "PySide6.Qt3DCore", "--exclude-module", "PySide6.QtCharts",
           "--exclude-module", "PySide6.QtDataVisualization", *extra, str(ROOT / "nilkon_start.py")]
    subprocess.check_call(cmd, cwd=ROOT)
    exe = ROOT / "dist" / "NILKON" / "NILKON.exe"
    if not exe.exists():
        sys.exit("Build failed: NILKON.exe was not created.")
    print("App built:", exe)
    try:
        prune_app(exe.parent)
    except Exception as exc:                      # pruning is only an optimisation
        print("Pruning skipped:", exc)
    sign(exe)

    iscc = shutil.which("iscc") or next((p for p in (r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
                                                    r"C:\Program Files\Inno Setup 6\ISCC.exe") if Path(p).exists()), None)
    if iscc:
        subprocess.check_call([iscc, f"/DAppVersion={APP_VERSION}", str(ROOT / "installer.iss")], cwd=ROOT)
        for f in (ROOT / "installer_output").glob("*.exe"):
            sign(f)
        print("Installer built in:", ROOT / "installer_output")
    else:
        print("Inno Setup was not found - skipped the installer (the app folder dist\\NILKON works on its own).")


if __name__ == "__main__":
    main()
