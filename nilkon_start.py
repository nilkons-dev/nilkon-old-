"""Start-up file of the installed app: the splash screen (animated logo + loading bar) appears at once, then the player
is loaded behind it, step by step, so the bar really moves."""
import sys


def _load(app, splash):
    steps = (("vlc_boot", "Starting the sound engine…", 0.10),
             ("theme", "Loading the look…", 0.18),
             ("library", "Reading your library…", 0.28),
             ("online", "Preparing online music…", 0.38),
             ("widgets", "Building the interface…", 0.50),
             ("panels", "Building the interface…", 0.60),
             ("tracklist", "Building the interface…", 0.68),
             ("home", "Building the interface…", 0.76),
             ("online_page", "Building the interface…", 0.82),
             ("settings_dialog", "Building the interface…", 0.88),
             ("music_player", "Almost ready…", 0.94))
    for name, text, value in steps:
        splash.set_progress(value, text)
        app.processEvents()
        try:
            __import__(name)
        except Exception:
            if name == "vlc_boot":                  # reported nicely later by music_player.main
                continue
            raise
    splash.set_progress(0.97, "Almost ready…")
    app.processEvents()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    from splash_screen import Splash
    splash = Splash()
    splash.show()
    app.processEvents()
    try:
        _load(app, splash)
    except Exception:
        splash.close()
        raise
    import music_player
    sys.exit(music_player.main(app, splash))
