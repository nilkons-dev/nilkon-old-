# NILKON Music Player

Private, offline, dark black-and-blue liquid-glass music player (PySide6 + VLC).

## Run (Windows)
Recommended: Python 3.12 or 3.13 (64-bit) and VLC 64-bit.

1. Install **VLC 64-bit** (videolan.org) and **Python 3.10+**.
2. Double-click `Run_NILKON.bat`.

Optional packages: `numpy` + `miniaudio` make the sound waves follow the real song
(without them the waves are simulated); `mutagen` reads titles, artists and cover art.

## Real Windows installer (recommended)
`NILKON_Setup_<version>.exe` installs NILKON like any other program (Start menu, desktop shortcut, uninstaller). VLC is
built into the app, so nothing else needs to be installed. Build it either on GitHub (workflow `Build NILKON for Windows`,
download the artifact `NILKON-Windows`) or on your PC with `Build_Installer.bat` (needs Python, VLC 64-bit, Inno Setup 6).

## Make a Windows .exe
Double-click `Build_NILKON_EXE.bat`, choose folder build (fast start) or single file. The app appears in `dist\`, with the NILKON logo as its icon. VLC 64-bit must be installed on the PC that runs it.

## Online music
Open **Online** in the sidebar and start typing - results (songs only) appear as you type. Press play to stream; the player then keeps playing related songs automatically, like a radio. Use the ⋯ menu to add a song to any playlist or to your favourites without downloading it - those songs are there every time you open NILKON. The download button saves a song to your library for offline listening (default folder `~/Music/NILKON`, change it in Settings > Online & Discord). MP3 conversion needs ffmpeg, which `imageio-ffmpeg` provides. Only download music you are allowed to keep. If online playback stops working, press "Update music engine" in Settings.

Crash diagnostics are written to `~/.nilkon_music/crash.log`.

## Discord "Listening to"
1. discord.com/developers/applications > New Application (name it NILKON).
2. Copy the Application ID into Settings > Online & Discord.
3. Optional: Rich Presence > Art Assets > upload the logo with key `nilkon`.
Keep the Discord desktop app open.

## Features
- Multiple playlists, favorites, recently played, drag songs to reorder
- Play button on every song; ⋯ menu: rename, favorite, add to playlist, per-song equalizer, remove/delete
- Waves/spectrum/seek-bar waveform computed from the actual audio
- Settings: dark/light, colour + wave themes, built-in or custom background image, wave style, equalizer
- Remembers last song/position; Home suggests songs you play most
- Shortcuts: Space, Ctrl+←/→, Ctrl+↑/↓, Ctrl+E, Ctrl+, , Ctrl+O

Data is stored in `~/.nilkon_music`. Renaming a song changes its display name only, not the file.

## What's new in 1.7.0
- Real sound waves for online songs start within about a second of pressing play (live analysis straight from the stream).
- Paste a song link in the online search box to find that exact song.
- No more "not a bot" noise in the console: the music engine tries several clients quietly. If a song still asks for
  verification, choose your browser in Settings → Online & Discord.
- Settings: new Playback page (resume, start page, similar-songs autoplay, volume / skip steps, sleep timer),
  wave sensitivity and smoothness, window-title and pop-up options.
- Shortcuts: Alt + Left / Right skip inside a song.
- Safer library file (damaged or pruned files are kept as copies), many playback / radio fixes.

## 1.7.1 - speed
- Online songs now stream through a local buffering helper: one download ahead of the playback position, shared by the
  player and the sound waves. Songs start as soon as the first bytes arrive and do not stall mid-song while the download
  is ahead. The next song's first seconds are fetched in advance, and the first search results are prepared before you press Play.
- Search is lighter: a kept-alive connection and compressed answers; pictures are smaller, load newest-first and are
  remembered on disk (`~/.nilkon_music/img_cache`).
- Waves for local and online songs start within a fraction of a second (progressive analysis) and no longer jump when the analysis completes.
- Buttons, sliders and menus now follow the song colours.

## 1.13.1 - fix
- Fixed: "NILKON could not start ... PosterBand has no attribute _timers" (poster strip on Explore).
- Faster start: slow non-Qt modules (numpy, audio analysis, tags, stream proxy ...) load in the background while the window
  is built; the build removes unused Qt files (fewer files for Windows Defender to check on the first start).

## 1.13.0 - Oswald, poster band, new side bar
- Font: Oswald everywhere (bundled, SIL OFL licence in assets/fonts).
- Side bar: Overview, Explore, Library, Favorites, History with new icons that play a short animation when clicked;
  About is its own entry above Settings; buttons have a light hover/click animation; playlists show a big cover (48 px).
- One big search bar only on Overview and Explore. Playlist pages have a search icon next to the sort button; a pen
  button next to "choose picture" renames the playlist.
- Explore: poster band (wide banner + small card from assets/posters) with random fade-over every few seconds.
- Picture placeholders are neutral dark tiles with a note instead of blue gradients.
- Overview spectrum redrawn much lighter (fewer points, one glow, cached gradients); status wording made professional.
- First start of a new version begins with empty caches (pictures, suggestions, stream files); the old play history and
  taste profile are cleared once with this version. Playlists, favourites, downloads and settings are kept.
- Splash window no longer shows "not responding" when clicked; search/stream connections are pre-opened at start.

## 1.12.0 - splash, Snap Layouts, short share codes, steadier streams
- New start-up window: animated logo, NILKON name under it and a loading bar that follows the real loading steps.
  VLC (the sound engine) now starts loading the moment the program starts, in parallel with everything else.
- Windows 11 Snap Layouts: rest the mouse on the maximise button (or press Win+Z) to pick a layout.
- Playlist share codes are now short and always the same size (`NKP1-xxxxxxx`): the playlist is parked on a free
  paste service and the code is its key. If the service cannot be reached, the long offline code is used instead.
  `.nilkon` files work as before.
- Streams: when a song stops or "Connection lost" shows although the internet works, NILKON now retries with and without its
  local proxy, no longer repeats the last seconds when a stream ends a little early, and writes
  `~/.nilkon_music/playback.log` (send it if a song still fails).
- Icons: shortcuts use a new icon file name, so Windows drops the old cached cat icon. If the taskbar still shows the
  old icon: unpin NILKON, start it again and pin it again.
- Next 3 songs are prepared in advance (was 2).

## 1.11.0 - new look, sort, stronger network
- New logo: red cat-and-moon app icon, and the new animated logo beside the NILKON name, in Settings and in About.
- Default colours are now red + black (existing installs switch once; you can still change it in Settings).
- Playlists, Liked and Library can be sorted: Custom order, Title, Artist, Duration, Recently added (button on the playlist page; remembered per playlist).
- Online page always shows the skeleton loader while songs load; the last suggestions show instantly and refresh behind.
- Song pictures load faster (keep-alive connections, retries, atomic cache).
- Fixed: when a song ended or the net dropped, the next song did not start and the last second repeated. The stream proxy now closes
  cut-off downloads properly and a watchdog moves on if the position freezes.
- Faster start: the sound engine and yt-dlp warm up in the background while the window is built.

## 1.10.0 - home shelves, playlist pages, faster start
- Home shows the same suggestion rows as the Online page; rows load with a grey "skeleton" placeholder and the last
  rows are remembered, so they appear instantly on the next start.
- The song picture replaces the little record in the player bar.
- Playlist pages look like Spotify's: big cover (your own photo - click it - or a mosaic of the first songs), name,
  size, big Play button. Right-click a playlist > Change picture.
- Faster start: splash screen at once, leaner bundled VLC (video plugins removed, plugin list pre-built).
- Flat window bar: the close button now keeps the window border.

### "Error 4551: An Application Control policy has blocked this file" on another PC
Windows "Smart App Control" (or a company policy) blocks every program that is not digitally signed. Options:
1. Sign the app (the real fix): get a code-signing certificate (.pfx), add the repository secrets
   `SIGN_PFX_BASE64` (the .pfx as base64) and `SIGN_PFX_PASSWORD`; the Actions build then signs the app and installer.
   (Open-source projects may qualify for free signing at signpath.io.)
2. On the friend's PC: Settings > Privacy & security > Windows Security > App & browser control >
   Smart App Control > Off (note: it cannot be switched on again later), or use the portable zip
   (`NILKON_portable.zip`, right-click the zip > Properties > Unblock before extracting).
3. If the PC belongs to a school / company, the administrator has to allow the app.

## 1.9.0 - downloads, home shelves, tray, playlists
- Download: parallel pieces (much faster), written to a temporary folder and moved in place with retries, so the
  "WinError 32 ... used by another process" error and refused downloads are gone. The old engine stays as a fallback.
- Online page (no search): Spotify-style rows of cover cards with arrows on both sides; a search shows the normal list.
- The close button hides NILKON in the tray (Settings > Appearance to change); quit from the tray icon.
- Flat, simple window bar.
- Playlists: share (copy a share code or save a .nilkon file) and import (share code, .nilkon, Spotify CSV from
  exportify.net, or a text list). Sidebar: Playlists > + and the playlist's right-click menu.

## 1.8.0 - speed, suggestions, new title bar
- Online songs load faster: three stream lookups race in parallel, the song downloads in parallel pieces over
  kept-alive connections, and the first results are looked up in advance.
- Online page: "Made for you" suggestions - random at first, then they follow what you search, play, like and skip.
  Settings > Library > Reset listening statistics also resets this.
- New themed window bar (minimise / maximise / close) that follows the colour theme.

## 1.7.2 - connection handling
- No internet (or it drops while a song plays): NILKON waits, shows "Waiting for internet…", and continues the same song
  from the same second as soon as the connection is back. Searches and pictures that failed offline repeat by themselves.
- Songs no longer skip when the connection stops for a moment (the download keeps retrying for ~75 s).
- Play has its own lane (never waits behind searches), the same song is only looked up once, the first part of a song is
  smaller so it starts sooner on slow lines, and the music engine is warmed up when the app starts.
- When the music service asks for verification, a public relay is tried as a last resort before showing the message.
