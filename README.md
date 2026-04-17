# YTVault 🔴 — YouTube Downloader

A modern, feature-rich desktop app to download YouTube videos and audio in the highest available quality.

---

## ✨ Features

| Feature | Details |
|---|---|
| Video download | MP4, up to 4K/8K |
| Audio download | MP3 (320 kbps) or M4A |
| Quality selector | Auto-detects all available resolutions |
| Thumbnail preview | Shows title, channel, duration, views |
| Progress bar | Real-time % + speed + ETA |
| Batch downloads | Queue multiple URLs at once |
| Playlist support | Downloads entire playlists |
| Subtitle download | Optional EN subtitles |
| Download history | Tracks all past downloads |
| Custom output folder | Browse and set any directory |
| Custom filename template | yt-dlp syntax supported |
| Dark mode | Always-on beautiful dark UI |

---

## 🛠 Installation

### Prerequisites

1. **Python 3.10+** — https://python.org/downloads  
2. **FFmpeg** (required for audio conversion & merging video+audio streams)
   - **Windows**: Download from https://ffmpeg.org/download.html → add `bin/` to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` or `sudo dnf install ffmpeg`

### Install Python dependencies

```bash
# Clone or download this folder, then:
cd ytdl

# (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate.bat      # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the app

```bash
python main.py
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `yt-dlp` | ≥ 2024.1.0 | YouTube extraction engine |
| `PyQt6` | ≥ 6.6.0 | Desktop GUI framework |
| FFmpeg (system) | any | Audio conversion, stream merging |

---

## 🚀 Quick Start

1. Launch the app with `python main.py`
2. Paste a YouTube URL into the input field
3. Click **Fetch Info** — thumbnail, title, and quality options will appear
4. Choose **Format** (Video/Audio) and **Quality**
5. Click **⬇ Download**
6. Watch the progress bar and enjoy!

---

## 🗂 Project Structure

```
ytdl/
├── main.py          # Full application (single-file, ~700 lines)
├── requirements.txt # Python dependencies
└── README.md        # This file
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `yt-dlp not installed` warning | Run `pip install yt-dlp` |
| `FFmpeg not found` warning | Install FFmpeg and add to PATH |
| Video merges as `.webm` instead of `.mp4` | Ensure FFmpeg is installed |
| Error 429 / rate limited | Wait a few minutes and retry |
| Private/age-restricted video fails | Expected — yt-dlp cannot bypass these |

---

## ⚖️ Legal Notice

This tool is intended for **personal, fair-use downloads** only (e.g., offline viewing of content you have rights to). Downloading copyrighted content without permission may violate YouTube's Terms of Service and applicable laws. Use responsibly.

---

## 🔄 Updating yt-dlp

YouTube frequently changes its internals. Keep yt-dlp updated:

```bash
pip install -U yt-dlp
```

Or from within the app's virtual environment.
