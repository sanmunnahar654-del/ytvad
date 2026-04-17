#!/usr/bin/env python3
"""
YTVault - YouTube Downloader
A modern, feature-rich desktop application for downloading YouTube videos and audio.
"""

import sys
import os
import json
import threading
import subprocess
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QProgressBar,
    QFileDialog, QScrollArea, QFrame, QSplitter, QTextEdit,
    QTabWidget, QCheckBox, QSpinBox, QMessageBox, QListWidget,
    QListWidgetItem, QSizePolicy, QStackedWidget, QGridLayout
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation,
    QEasingCurve, QRect, pyqtProperty, QObject
)
from PyQt6.QtGui import (
    QFont, QPixmap, QIcon, QPalette, QColor, QImage,
    QPainter, QBrush, QPen, QLinearGradient, QFontMetrics,
    QMovie, QCursor
)
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


# ─────────────────────────────────────────────
#  CONSTANTS & THEME
# ─────────────────────────────────────────────

DARK_THEME = {
    "bg_primary":    "#0D0D0F",
    "bg_secondary":  "#141418",
    "bg_card":       "#1A1A20",
    "bg_hover":      "#22222A",
    "accent":        "#FF3B5C",
    "accent_dim":    "#C42D47",
    "accent_glow":   "rgba(255,59,92,0.15)",
    "text_primary":  "#F0F0F5",
    "text_secondary":"#8888A0",
    "text_muted":    "#555568",
    "border":        "#2A2A35",
    "border_active": "#FF3B5C",
    "success":       "#00D67F",
    "warning":       "#FFB347",
    "error":         "#FF4C6A",
    "progress_bg":   "#1E1E28",
}

APP_STYLE = """
QMainWindow, QWidget#root {
    background-color: #0D0D0F;
    color: #F0F0F5;
}

QWidget {
    background-color: transparent;
    color: #F0F0F5;
    font-family: 'SF Pro Display', 'Segoe UI Variable', 'Inter', sans-serif;
}

QLineEdit {
    background-color: #1A1A20;
    border: 1.5px solid #2A2A35;
    border-radius: 10px;
    padding: 12px 16px;
    color: #F0F0F5;
    font-size: 14px;
    selection-background-color: #FF3B5C;
}
QLineEdit:focus {
    border-color: #FF3B5C;
    background-color: #1E1E26;
}
QLineEdit::placeholder {
    color: #555568;
}

QPushButton {
    background-color: #FF3B5C;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #FF5272;
}
QPushButton:pressed {
    background-color: #C42D47;
}
QPushButton:disabled {
    background-color: #2A2A35;
    color: #555568;
}

QPushButton#secondary {
    background-color: #1A1A20;
    color: #F0F0F5;
    border: 1.5px solid #2A2A35;
}
QPushButton#secondary:hover {
    background-color: #22222A;
    border-color: #FF3B5C;
    color: #FF3B5C;
}

QComboBox {
    background-color: #1A1A20;
    border: 1.5px solid #2A2A35;
    border-radius: 10px;
    padding: 11px 16px;
    color: #F0F0F5;
    font-size: 13px;
}
QComboBox:focus, QComboBox:hover {
    border-color: #FF3B5C;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #8888A0;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: #1A1A20;
    border: 1px solid #2A2A35;
    border-radius: 8px;
    color: #F0F0F5;
    selection-background-color: #FF3B5C;
    padding: 4px;
}

QProgressBar {
    background-color: #1E1E28;
    border-radius: 6px;
    border: none;
    height: 8px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #FF3B5C, stop:1 #FF7E95);
    border-radius: 6px;
}

QScrollBar:vertical {
    background-color: #141418;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background-color: #2A2A35;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #FF3B5C;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background-color: #141418;
    height: 6px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background-color: #2A2A35;
    border-radius: 3px;
}

QCheckBox {
    spacing: 8px;
    font-size: 13px;
    color: #8888A0;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.5px solid #2A2A35;
    background-color: #1A1A20;
}
QCheckBox::indicator:checked {
    background-color: #FF3B5C;
    border-color: #FF3B5C;
    image: none;
}
QCheckBox:hover { color: #F0F0F5; }

QListWidget {
    background-color: #141418;
    border: none;
    border-radius: 10px;
}
QListWidget::item {
    padding: 0px;
    border: none;
}
QListWidget::item:selected {
    background-color: transparent;
}

QTabWidget::pane {
    border: none;
    background-color: transparent;
}
QTabBar::tab {
    background-color: transparent;
    color: #555568;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #FF3B5C;
    border-bottom: 2px solid #FF3B5C;
}
QTabBar::tab:hover:!selected {
    color: #8888A0;
}

QTextEdit {
    background-color: #141418;
    border: 1px solid #2A2A35;
    border-radius: 10px;
    color: #8888A0;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 12px;
    padding: 10px;
}

QSplitter::handle {
    background-color: #2A2A35;
    width: 1px;
}

QToolTip {
    background-color: #1A1A20;
    color: #F0F0F5;
    border: 1px solid #2A2A35;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""


# ─────────────────────────────────────────────
#  WORKER THREADS
# ─────────────────────────────────────────────

class FetchInfoWorker(QThread):
    """Fetches video metadata without downloading."""
    info_ready    = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url.strip()

    def run(self):
        if not YT_DLP_AVAILABLE:
            self.error_occurred.emit("yt-dlp is not installed. Run: pip install yt-dlp")
            return
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'noplaylist': False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.info_ready.emit(info)
        except yt_dlp.utils.DownloadError as e:
            self.error_occurred.emit(f"Could not fetch video info: {str(e)[:200]}")
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {str(e)[:200]}")


class DownloadWorker(QThread):
    """Handles the actual download with progress reporting."""
    progress_update = pyqtSignal(float, str, str)   # percent, speed, eta
    status_update   = pyqtSignal(str)
    download_done   = pyqtSignal(str)                # output file path
    error_occurred  = pyqtSignal(str)

    def __init__(self, url, format_id, output_dir, filename_tmpl,
                 audio_only=False, audio_fmt="mp3",
                 download_subs=False, extra_opts=None):
        super().__init__()
        self.url          = url
        self.format_id    = format_id
        self.output_dir   = output_dir
        self.filename_tmpl = filename_tmpl
        self.audio_only   = audio_only
        self.audio_fmt    = audio_fmt
        self.download_subs = download_subs
        self.extra_opts   = extra_opts or {}
        self._last_filename = ""

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total   = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                speed   = d.get('_speed_str', '—')
                eta     = d.get('_eta_str', '—')
                pct     = (downloaded / total * 100) if total else 0
                self.progress_update.emit(pct, speed, eta)
            except Exception:
                pass
        elif d['status'] == 'finished':
            self._last_filename = d.get('filename', '')
            self.status_update.emit("Processing…")
        elif d['status'] == 'error':
            self.error_occurred.emit("Download error during transfer.")

    def run(self):
        if not YT_DLP_AVAILABLE:
            self.error_occurred.emit("yt-dlp is not installed.")
            return
        try:
            outtmpl = os.path.join(self.output_dir, self.filename_tmpl)
            ydl_opts = {
                'outtmpl':        outtmpl,
                'progress_hooks': [self._progress_hook],
                'quiet':          True,
                'no_warnings':    True,
            }
            if self.audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.audio_fmt,
                    'preferredquality': '320' if self.audio_fmt == 'mp3' else '0',
                }]
            else:
                if self.format_id and self.format_id not in ('best', 'bestvideo'):
                    ydl_opts['format'] = f"{self.format_id}+bestaudio/best"
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                ydl_opts['merge_output_format'] = 'mp4'

            if self.download_subs:
                ydl_opts['writesubtitles']   = True
                ydl_opts['writeautomaticsub'] = True
                ydl_opts['subtitleslangs']   = ['en']

            ydl_opts.update(self.extra_opts)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.download_done.emit(self._last_filename)
        except yt_dlp.utils.DownloadError as e:
            self.error_occurred.emit(str(e)[:300])
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {str(e)[:300]}")


class ThumbnailLoader(QThread):
    """Downloads thumbnail image from URL."""
    image_ready = pyqtSignal(QPixmap)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            import urllib.request
            data = urllib.request.urlopen(self.url, timeout=10).read()
            img  = QImage()
            img.loadFromData(data)
            px = QPixmap.fromImage(img)
            self.image_ready.emit(px)
        except Exception:
            pass


# ─────────────────────────────────────────────
#  CUSTOM WIDGETS
# ─────────────────────────────────────────────

class GlowButton(QPushButton):
    """Primary action button with animated glow effect."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))


class CardFrame(QFrame):
    """A styled card container."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            CardFrame {{
                background-color: {DARK_THEME['bg_card']};
                border: 1px solid {DARK_THEME['border']};
                border-radius: 14px;
            }}
        """)


class StatusBadge(QLabel):
    """Colored status pill label."""
    COLORS = {
        'idle':        ('#555568', '#1A1A20'),
        'fetching':    ('#FFB347', '#2A2010'),
        'ready':       ('#00D67F', '#0D2018'),
        'downloading': ('#4EA8FF', '#0D1A28'),
        'done':        ('#00D67F', '#0D2018'),
        'error':       ('#FF4C6A', '#280D12'),
        'cancelled':   ('#555568', '#1A1A20'),
    }

    def __init__(self, status='idle', parent=None):
        super().__init__(parent)
        self.setStatus(status)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setStatus(self, status):
        fg, bg = self.COLORS.get(status, self.COLORS['idle'])
        label_map = {
            'idle':        '● Idle',
            'fetching':    '◌ Fetching…',
            'ready':       '● Ready',
            'downloading': '↓ Downloading',
            'done':        '✓ Complete',
            'error':       '✕ Error',
            'cancelled':   '○ Cancelled',
        }
        self.setText(label_map.get(status, status))
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                border-radius: 8px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)


class DownloadHistoryItem(QWidget):
    """One row in the download history list."""
    def __init__(self, title, url, fmt, ts, status, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        icon = QLabel('🎬' if fmt in ('mp4', 'video') else '🎵')
        icon.setFixedWidth(28)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 18px;")
        layout.addWidget(icon)

        info = QVBoxLayout()
        info.setSpacing(2)
        t = QLabel(title[:60] + ('…' if len(title) > 60 else ''))
        t.setStyleSheet(f"color: {DARK_THEME['text_primary']}; font-size: 13px; font-weight: 500;")
        u = QLabel(url[:50] + '…')
        u.setStyleSheet(f"color: {DARK_THEME['text_muted']}; font-size: 11px;")
        info.addWidget(t)
        info.addWidget(u)
        layout.addLayout(info, 1)

        right = QVBoxLayout()
        right.setSpacing(2)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        badge = StatusBadge(status)
        ts_label = QLabel(ts)
        ts_label.setStyleSheet(f"color: {DARK_THEME['text_muted']}; font-size: 11px;")
        ts_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(badge, alignment=Qt.AlignmentFlag.AlignRight)
        right.addWidget(ts_label)
        layout.addLayout(right)

        self.setStyleSheet(f"""
            DownloadHistoryItem {{
                background-color: {DARK_THEME['bg_card']};
                border-radius: 10px;
                border: 1px solid {DARK_THEME['border']};
            }}
            DownloadHistoryItem:hover {{
                background-color: {DARK_THEME['bg_hover']};
                border-color: {DARK_THEME['border_active']};
            }}
        """)


class BatchURLItem(QWidget):
    """Row for batch URL list."""
    remove_requested = pyqtSignal(object)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(8)

        self.url_label = QLabel(url[:80] + ('…' if len(url) > 80 else ''))
        self.url_label.setStyleSheet(f"color: {DARK_THEME['text_secondary']}; font-size: 13px;")
        layout.addWidget(self.url_label, 1)

        self.status_badge = StatusBadge('idle')
        layout.addWidget(self.status_badge)

        remove_btn = QPushButton('✕')
        remove_btn.setFixedSize(28, 28)
        remove_btn.setObjectName('secondary')
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {DARK_THEME['text_muted']};
                border: none;
                font-size: 13px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                color: {DARK_THEME['error']};
                background-color: rgba(255,76,106,0.1);
            }}
        """)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_btn)

        self.setStyleSheet(f"""
            BatchURLItem {{
                background-color: {DARK_THEME['bg_card']};
                border-radius: 8px;
                border: 1px solid {DARK_THEME['border']};
            }}
        """)
        self.url = url

    def setStatus(self, status):
        self.status_badge.setStatus(status)


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────

class YTVaultWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YTVault")
        self.setMinimumSize(980, 720)
        self.resize(1120, 780)

        self._video_info     = None
        self._formats        = []
        self._download_dir   = str(Path.home() / "Downloads")
        self._history        = []
        self._batch_items    = []
        self._fetch_worker   = None
        self._dl_worker      = None
        self._thumb_loader   = None
        self._batch_queue    = []
        self._batch_index    = 0

        self._build_ui()
        self._apply_style()
        self._check_dependencies()

    # ── Dependency check ────────────────────────────────────

    def _check_dependencies(self):
        missing = []
        if not YT_DLP_AVAILABLE:
            missing.append("yt-dlp  →  pip install yt-dlp")
        try:
            subprocess.run(['ffmpeg', '-version'],
                           capture_output=True, timeout=5, check=True)
        except Exception:
            missing.append("FFmpeg  →  https://ffmpeg.org/download.html")

        if missing:
            msg = "Some dependencies are missing:\n\n" + "\n".join(missing)
            msg += "\n\nThe app may have limited functionality."
            self._log(f"⚠  Missing: {', '.join(missing)}", color=DARK_THEME['warning'])
            QTimer.singleShot(400, lambda: self._show_dep_warning(msg))

    def _show_dep_warning(self, msg):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Dependencies Missing")
        dlg.setText(msg)
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setStyleSheet(APP_STYLE + "QMessageBox { background: #141418; }")
        dlg.exec()

    # ── UI Construction ─────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        root.setStyleSheet(f"background-color: {DARK_THEME['bg_primary']};")
        self.setCentralWidget(root)

        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Sidebar ──
        sidebar = self._build_sidebar()
        outer.addWidget(sidebar)

        # ── Main content ──
        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_downloader_page())   # 0
        self.pages.addWidget(self._build_batch_page())         # 1
        self.pages.addWidget(self._build_history_page())       # 2
        self.pages.addWidget(self._build_settings_page())      # 3
        outer.addWidget(self.pages, 1)

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {DARK_THEME['bg_secondary']};
                border-right: 1px solid {DARK_THEME['border']};
            }}
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(4)

        # Logo
        logo = QLabel("YTVault")
        logo.setStyleSheet(f"""
            QLabel {{
                color: {DARK_THEME['accent']};
                font-size: 22px;
                font-weight: 800;
                letter-spacing: -0.5px;
                padding: 8px 4px 20px 4px;
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(logo)

        # Nav buttons
        nav_items = [
            ("⬇  Download",  0),
            ("≡  Batch",     1),
            ("◷  History",   2),
            ("⚙  Settings",  3),
        ]
        self._nav_btns = []
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, i=idx: self._switch_page(i))
            btn.setStyleSheet(self._nav_btn_style(False))
            layout.addWidget(btn)
            self._nav_btns.append(btn)

        self._nav_btns[0].setChecked(True)
        self._nav_btns[0].setStyleSheet(self._nav_btn_style(True))

        layout.addStretch()

        # Version / status
        ver = QLabel("v1.0.0  •  yt-dlp powered")
        ver.setStyleSheet(f"color: {DARK_THEME['text_muted']}; font-size: 11px; border: none; background: transparent;")
        ver.setWordWrap(True)
        layout.addWidget(ver)
        return sidebar

    def _nav_btn_style(self, active):
        if active:
            return f"""
                QPushButton {{
                    background-color: rgba(255,59,92,0.12);
                    color: {DARK_THEME['accent']};
                    border: none;
                    border-radius: 9px;
                    padding: 11px 14px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 600;
                }}
            """
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {DARK_THEME['text_secondary']};
                border: none;
                border-radius: 9px;
                padding: 11px 14px;
                text-align: left;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {DARK_THEME['bg_hover']};
                color: {DARK_THEME['text_primary']};
            }}
        """

    def _switch_page(self, idx):
        self.pages.setCurrentIndex(idx)
        for i, btn in enumerate(self._nav_btns):
            active = (i == idx)
            btn.setChecked(active)
            btn.setStyleSheet(self._nav_btn_style(active))

    # ── Downloader Page ──────────────────────────────────────

    def _build_downloader_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        # Header
        header = QLabel("Download Video or Audio")
        header.setStyleSheet(f"color: {DARK_THEME['text_primary']}; font-size: 20px; font-weight: 700;")
        layout.addWidget(header)

        # ── URL Input Card ──
        url_card = CardFrame()
        url_layout = QVBoxLayout(url_card)
        url_layout.setContentsMargins(20, 18, 20, 18)
        url_layout.setSpacing(12)

        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here…")
        self.url_input.setMinimumHeight(46)
        self.url_input.returnPressed.connect(self._fetch_info)
        url_row.addWidget(self.url_input, 1)

        self.fetch_btn = GlowButton("Fetch Info")
        self.fetch_btn.setMinimumHeight(46)
        self.fetch_btn.setFixedWidth(120)
        self.fetch_btn.clicked.connect(self._fetch_info)
        url_row.addWidget(self.fetch_btn)
        url_layout.addLayout(url_row)

        # Status row
        status_row = QHBoxLayout()
        self.status_badge = StatusBadge('idle')
        self.status_label = QLabel("Enter a URL and click Fetch Info")
        self.status_label.setStyleSheet(f"color: {DARK_THEME['text_muted']}; font-size: 12px;")
        status_row.addWidget(self.status_badge)
        status_row.addWidget(self.status_label, 1)
        url_layout.addLayout(status_row)
        layout.addWidget(url_card)

        # ── Video Info + Options (side by side) ──
        middle = QHBoxLayout()
        middle.setSpacing(18)

        # Thumbnail & metadata
        self.info_card = CardFrame()
        info_layout = QHBoxLayout(self.info_card)
        info_layout.setContentsMargins(16, 16, 16, 16)
        info_layout.setSpacing(16)

        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(180, 102)
        self.thumb_label.setStyleSheet(f"""
            QLabel {{
                background-color: {DARK_THEME['bg_secondary']};
                border-radius: 8px;
                color: {DARK_THEME['text_muted']};
                font-size: 28px;
            }}
        """)
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setText("▶")
        info_layout.addWidget(self.thumb_label)

        meta = QVBoxLayout()
        meta.setSpacing(6)
        meta.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.title_label = QLabel("No video loaded")
        self.title_label.setStyleSheet(f"color: {DARK_THEME['text_primary']}; font-size: 14px; font-weight: 600;")
        self.title_label.setWordWrap(True)

        self.channel_label = QLabel("—")
        self.channel_label.setStyleSheet(f"color: {DARK_THEME['text_secondary']}; font-size: 12px;")

        self.meta_label = QLabel("Duration: —   •   Views: —")
        self.meta_label.setStyleSheet(f"color: {DARK_THEME['text_muted']}; font-size: 12px;")

        meta.addWidget(self.title_label)
        meta.addWidget(self.channel_label)
        meta.addWidget(self.meta_label)
        meta.addStretch()
        info_layout.addLayout(meta, 1)
        middle.addWidget(self.info_card, 3)

        # Options card
        opt_card = CardFrame()
        opt_layout = QVBoxLayout(opt_card)
        opt_layout.setContentsMargins(18, 16, 18, 16)
        opt_layout.setSpacing(12)

        opt_layout.addWidget(QLabel("Format", styleSheet=f"color:{DARK_THEME['text_secondary']};font-size:12px;font-weight:600;"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Video (MP4)", "Audio only (MP3)", "Audio only (M4A)"])
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        opt_layout.addWidget(self.format_combo)

        opt_layout.addWidget(QLabel("Quality", styleSheet=f"color:{DARK_THEME['text_secondary']};font-size:12px;font-weight:600;"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Best available")
        opt_layout.addWidget(self.quality_combo)

        self.subs_check = QCheckBox("Download subtitles (EN)")
        opt_layout.addWidget(self.subs_check)

        # Save location
        dir_row = QHBoxLayout()
        dir_row.setSpacing(8)
        self.dir_label = QLabel(self._short_path(self._download_dir))
        self.dir_label.setStyleSheet(f"color:{DARK_THEME['text_secondary']};font-size:12px;")
        self.dir_label.setToolTip(self._download_dir)
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondary")
        browse_btn.setFixedHeight(34)
        browse_btn.clicked.connect(self._choose_dir)
        dir_row.addWidget(self.dir_label, 1)
        dir_row.addWidget(browse_btn)
        opt_layout.addLayout(dir_row)
        opt_layout.addStretch()
        middle.addWidget(opt_card, 2)
        layout.addLayout(middle)

        # ── Progress Card ──
        prog_card = CardFrame()
        prog_layout = QVBoxLayout(prog_card)
        prog_layout.setContentsMargins(20, 16, 20, 16)
        prog_layout.setSpacing(10)

        prog_top = QHBoxLayout()
        self.prog_label = QLabel("Ready to download")
        self.prog_label.setStyleSheet(f"color:{DARK_THEME['text_secondary']};font-size:13px;")
        self.speed_label = QLabel("")
        self.speed_label.setStyleSheet(f"color:{DARK_THEME['text_muted']};font-size:12px;")
        self.eta_label = QLabel("")
        self.eta_label.setStyleSheet(f"color:{DARK_THEME['text_muted']};font-size:12px;")
        self.pct_label = QLabel("0%")
        self.pct_label.setStyleSheet(f"color:{DARK_THEME['accent']};font-size:13px;font-weight:700;")
        prog_top.addWidget(self.prog_label, 1)
        prog_top.addWidget(self.speed_label)
        prog_top.addWidget(QLabel("·", styleSheet=f"color:{DARK_THEME['text_muted']};"))
        prog_top.addWidget(self.eta_label)
        prog_top.addWidget(self.pct_label)
        prog_layout.addLayout(prog_top)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        prog_layout.addWidget(self.progress_bar)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.download_btn = GlowButton("⬇  Download")
        self.download_btn.setMinimumHeight(44)
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self._start_download)
        btn_row.addWidget(self.download_btn, 1)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondary")
        self.cancel_btn.setMinimumHeight(44)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_download)
        btn_row.addWidget(self.cancel_btn)

        open_dir_btn = QPushButton("Open Folder")
        open_dir_btn.setObjectName("secondary")
        open_dir_btn.setMinimumHeight(44)
        open_dir_btn.clicked.connect(self._open_download_dir)
        btn_row.addWidget(open_dir_btn)
        prog_layout.addLayout(btn_row)
        layout.addWidget(prog_card)

        # ── Log ──
        log_card = CardFrame()
        log_inner = QVBoxLayout(log_card)
        log_inner.setContentsMargins(14, 10, 14, 10)
        log_inner.setSpacing(6)
        log_hdr = QHBoxLayout()
        log_hdr.addWidget(QLabel("Log", styleSheet=f"color:{DARK_THEME['text_muted']};font-size:11px;font-weight:600;"))
        clr_btn = QPushButton("Clear")
        clr_btn.setObjectName("secondary")
        clr_btn.setFixedSize(50, 22)
        clr_btn.setStyleSheet(f"font-size:11px; padding:2px 6px; border-radius:5px; background:{DARK_THEME['bg_hover']}; color:{DARK_THEME['text_muted']};border:none;")
        clr_btn.clicked.connect(lambda: self.log_area.clear())
        log_hdr.addStretch()
        log_hdr.addWidget(clr_btn)
        log_inner.addLayout(log_hdr)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(90)
        log_inner.addWidget(self.log_area)
        layout.addWidget(log_card)

        return page

    # ── Batch Page ───────────────────────────────────────────

    def _build_batch_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        header = QLabel("Batch Download")
        header.setStyleSheet(f"color:{DARK_THEME['text_primary']};font-size:20px;font-weight:700;")
        layout.addWidget(header)

        sub = QLabel("Add multiple URLs to download them all with the same settings.")
        sub.setStyleSheet(f"color:{DARK_THEME['text_secondary']};font-size:13px;")
        layout.addWidget(sub)

        add_card = CardFrame()
        add_layout = QHBoxLayout(add_card)
        add_layout.setContentsMargins(16, 14, 16, 14)
        add_layout.setSpacing(10)
        self.batch_input = QLineEdit()
        self.batch_input.setPlaceholderText("Paste a YouTube URL…")
        self.batch_input.setMinimumHeight(42)
        self.batch_input.returnPressed.connect(self._add_batch_url)
        add_layout.addWidget(self.batch_input, 1)
        add_btn = GlowButton("Add")
        add_btn.setFixedWidth(80)
        add_btn.setMinimumHeight(42)
        add_btn.clicked.connect(self._add_batch_url)
        add_layout.addWidget(add_btn)
        layout.addWidget(add_card)

        # Batch list
        self.batch_scroll = QScrollArea()
        self.batch_scroll.setWidgetResizable(True)
        self.batch_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.batch_container = QWidget()
        self.batch_vbox = QVBoxLayout(self.batch_container)
        self.batch_vbox.setContentsMargins(0, 0, 0, 0)
        self.batch_vbox.setSpacing(6)
        self.batch_vbox.addStretch()
        self.batch_scroll.setWidget(self.batch_container)
        layout.addWidget(self.batch_scroll, 1)

        # Batch options
        bot_row = QHBoxLayout()
        bot_row.setSpacing(10)
        self.batch_fmt_combo = QComboBox()
        self.batch_fmt_combo.addItems(["Video (MP4)", "Audio only (MP3)", "Audio only (M4A)"])
        self.batch_fmt_combo.setFixedHeight(40)
        bot_row.addWidget(self.batch_fmt_combo, 1)

        self.batch_dl_btn = GlowButton("⬇  Download All")
        self.batch_dl_btn.setFixedHeight(40)
        self.batch_dl_btn.clicked.connect(self._start_batch)
        bot_row.addWidget(self.batch_dl_btn)

        clr_all_btn = QPushButton("Clear All")
        clr_all_btn.setObjectName("secondary")
        clr_all_btn.setFixedHeight(40)
        clr_all_btn.clicked.connect(self._clear_batch)
        bot_row.addWidget(clr_all_btn)
        layout.addLayout(bot_row)

        self.batch_status_label = QLabel("")
        self.batch_status_label.setStyleSheet(f"color:{DARK_THEME['text_secondary']};font-size:13px;")
        layout.addWidget(self.batch_status_label)

        return page

    # ── History Page ─────────────────────────────────────────

    def _build_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("Download History")
        title.setStyleSheet(f"color:{DARK_THEME['text_primary']};font-size:20px;font-weight:700;")
        hdr.addWidget(title, 1)
        clr_btn = QPushButton("Clear History")
        clr_btn.setObjectName("secondary")
        clr_btn.setFixedHeight(36)
        clr_btn.clicked.connect(self._clear_history)
        hdr.addWidget(clr_btn)
        layout.addLayout(hdr)

        self.history_list = QListWidget()
        self.history_list.setSpacing(4)
        self.history_list.setStyleSheet(f"background:{DARK_THEME['bg_primary']};border:none;")
        self.history_empty = QLabel("No downloads yet.\nGo to Download and grab something!")
        self.history_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_empty.setStyleSheet(f"color:{DARK_THEME['text_muted']};font-size:14px;")
        layout.addWidget(self.history_list, 1)
        layout.addWidget(self.history_empty)
        self.history_empty.setVisible(True)
        return page

    # ── Settings Page ────────────────────────────────────────

    def _build_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        title = QLabel("Settings")
        title.setStyleSheet(f"color:{DARK_THEME['text_primary']};font-size:20px;font-weight:700;")
        layout.addWidget(title)

        def section(name):
            l = QLabel(name)
            l.setStyleSheet(f"color:{DARK_THEME['text_muted']};font-size:11px;font-weight:700;letter-spacing:1px;margin-top:8px;")
            layout.addWidget(l)

        section("DOWNLOAD PATH")
        dir_card = CardFrame()
        dir_row = QHBoxLayout(dir_card)
        dir_row.setContentsMargins(16, 12, 16, 12)
        self.settings_dir_label = QLabel(self._download_dir)
        self.settings_dir_label.setStyleSheet(f"color:{DARK_THEME['text_secondary']};font-size:13px;")
        dir_row.addWidget(self.settings_dir_label, 1)
        chg_btn = QPushButton("Change")
        chg_btn.setObjectName("secondary")
        chg_btn.setFixedHeight(34)
        chg_btn.clicked.connect(self._choose_dir)
        dir_row.addWidget(chg_btn)
        layout.addWidget(dir_card)

        section("AUDIO QUALITY")
        aq_card = CardFrame()
        aq_layout = QHBoxLayout(aq_card)
        aq_layout.setContentsMargins(16, 12, 16, 12)
        aq_layout.addWidget(QLabel("MP3 bitrate:", styleSheet=f"color:{DARK_THEME['text_secondary']};font-size:13px;"), 1)
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["320 kbps (best)", "256 kbps", "192 kbps", "128 kbps"])
        self.bitrate_combo.setFixedWidth(160)
        aq_layout.addWidget(self.bitrate_combo)
        layout.addWidget(aq_card)

        section("CONCURRENCY")
        cc_card = CardFrame()
        cc_layout = QHBoxLayout(cc_card)
        cc_layout.setContentsMargins(16, 12, 16, 12)
        cc_layout.addWidget(QLabel("Simultaneous downloads:", styleSheet=f"color:{DARK_THEME['text_secondary']};font-size:13px;"), 1)
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 5)
        self.concurrent_spin.setValue(2)
        self.concurrent_spin.setFixedWidth(60)
        self.concurrent_spin.setStyleSheet(f"background:{DARK_THEME['bg_card']};color:{DARK_THEME['text_primary']};border:1px solid {DARK_THEME['border']};border-radius:6px;padding:4px 8px;")
        cc_layout.addWidget(self.concurrent_spin)
        layout.addWidget(cc_card)

        section("FILE NAMING")
        fn_card = CardFrame()
        fn_layout = QVBoxLayout(fn_card)
        fn_layout.setContentsMargins(16, 12, 16, 12)
        fn_layout.setSpacing(6)
        fn_layout.addWidget(QLabel("Template (yt-dlp syntax):", styleSheet=f"color:{DARK_THEME['text_secondary']};font-size:12px;"))
        self.filename_tmpl = QLineEdit("%(title)s.%(ext)s")
        self.filename_tmpl.setMinimumHeight(38)
        fn_layout.addWidget(self.filename_tmpl)
        fn_layout.addWidget(QLabel("Use %(title)s, %(id)s, %(uploader)s, %(ext)s, etc.", styleSheet=f"color:{DARK_THEME['text_muted']};font-size:11px;"))
        layout.addWidget(fn_card)

        layout.addStretch()

        save_btn = GlowButton("Save Settings")
        save_btn.setFixedWidth(160)
        save_btn.setFixedHeight(42)
        save_btn.clicked.connect(lambda: self._log("✓ Settings saved.", color=DARK_THEME['success']))
        layout.addWidget(save_btn)
        return page

    # ── Style ────────────────────────────────────────────────

    def _apply_style(self):
        self.setStyleSheet(APP_STYLE)

    # ── Helpers ──────────────────────────────────────────────

    def _short_path(self, path):
        home = str(Path.home())
        if path.startswith(home):
            return "~" + path[len(home):]
        return path[:40] + ("…" if len(path) > 40 else "")

    def _choose_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Choose Download Folder", self._download_dir)
        if d:
            self._download_dir = d
            self.dir_label.setText(self._short_path(d))
            self.dir_label.setToolTip(d)
            self.settings_dir_label.setText(d)

    def _open_download_dir(self):
        path = self._download_dir
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])

    def _log(self, msg, color=None):
        ts = datetime.now().strftime("%H:%M:%S")
        c  = color or DARK_THEME['text_secondary']
        self.log_area.append(
            f'<span style="color:{DARK_THEME["text_muted"]}">[{ts}]</span> '
            f'<span style="color:{c}">{msg}</span>'
        )

    def _fmt_duration(self, secs):
        if not secs:
            return "—"
        h, r = divmod(int(secs), 3600)
        m, s = divmod(r, 60)
        return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

    def _fmt_views(self, v):
        if not v:
            return "—"
        if v >= 1_000_000:
            return f"{v/1_000_000:.1f}M"
        if v >= 1_000:
            return f"{v/1_000:.0f}K"
        return str(v)

    # ── Fetch Info ───────────────────────────────────────────

    def _fetch_info(self):
        url = self.url_input.text().strip()
        if not url:
            self._log("⚠  Please enter a URL.", color=DARK_THEME['warning'])
            return
        if self._fetch_worker and self._fetch_worker.isRunning():
            return

        self.status_badge.setStatus('fetching')
        self.status_label.setText("Fetching video information…")
        self.fetch_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self._log(f"⟳  Fetching: {url[:60]}…")

        self._fetch_worker = FetchInfoWorker(url)
        self._fetch_worker.info_ready.connect(self._on_info_ready)
        self._fetch_worker.error_occurred.connect(self._on_fetch_error)
        self._fetch_worker.start()

    def _on_info_ready(self, info):
        self._video_info = info
        is_playlist = info.get('_type') == 'playlist'

        title    = info.get('title', 'Unknown')
        channel  = info.get('uploader') or info.get('channel', '—')
        duration = self._fmt_duration(info.get('duration'))
        views    = self._fmt_views(info.get('view_count'))
        thumb    = info.get('thumbnail', '')

        if is_playlist:
            count = len(info.get('entries', []))
            self.title_label.setText(f"[Playlist] {title}")
            self.meta_label.setText(f"{count} videos")
        else:
            self.title_label.setText(title)
            self.meta_label.setText(f"Duration: {duration}   •   Views: {views}")

        self.channel_label.setText(f"🎙  {channel}")
        self.status_badge.setStatus('ready')
        self.status_label.setText("Ready to download")
        self.fetch_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self._log(f"✓  Loaded: {title[:60]}", color=DARK_THEME['success'])

        # Populate quality combo
        self._populate_quality(info)

        # Load thumbnail
        if thumb and not is_playlist:
            self.thumb_label.setText("…")
            self._thumb_loader = ThumbnailLoader(thumb)
            self._thumb_loader.image_ready.connect(self._set_thumbnail)
            self._thumb_loader.start()

    def _populate_quality(self, info):
        self.quality_combo.clear()
        self._formats = []
        fmts = info.get('formats', [])
        seen = set()
        audio_only = self.format_combo.currentIndex() > 0

        if audio_only:
            self.quality_combo.addItem("Best available (auto)")
            return

        # Collect video-only formats with known resolution
        for f in reversed(fmts):
            h = f.get('height')
            if not h:
                continue
            codec = f.get('vcodec', 'none')
            if codec == 'none':
                continue
            label = f"{h}p"
            if f.get('fps') and f['fps'] > 30:
                label += f" {int(f['fps'])}fps"
            if label not in seen:
                seen.add(label)
                self._formats.append((label, f['format_id']))
                self.quality_combo.addItem(label)

        if not seen:
            self.quality_combo.addItem("Best available (auto)")
        else:
            self.quality_combo.insertItem(0, "Best available (auto)")
            self.quality_combo.setCurrentIndex(0)

    def _on_fetch_error(self, msg):
        self.status_badge.setStatus('error')
        self.status_label.setText("Failed to fetch info")
        self.fetch_btn.setEnabled(True)
        self._log(f"✕  {msg}", color=DARK_THEME['error'])

    def _set_thumbnail(self, px):
        scaled = px.scaled(
            180, 102,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.thumb_label.setPixmap(scaled)
        self.thumb_label.setText("")

    def _on_format_changed(self, idx):
        if self._video_info:
            self._populate_quality(self._video_info)

    # ── Download ─────────────────────────────────────────────

    def _start_download(self):
        if not self._video_info:
            return
        url        = self.url_input.text().strip()
        fmt_idx    = self.format_combo.currentIndex()
        audio_only = fmt_idx > 0
        audio_fmt  = 'mp3' if fmt_idx == 1 else 'm4a'

        # Determine format_id
        q_idx = self.quality_combo.currentIndex()
        format_id = 'bestvideo'
        if not audio_only and q_idx > 0 and q_idx - 1 < len(self._formats):
            _, format_id = self._formats[q_idx - 1]

        tmpl = self.filename_tmpl.text().strip() if hasattr(self, 'filename_tmpl') else "%(title)s.%(ext)s"

        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_badge.setStatus('downloading')
        self.prog_label.setText("Starting download…")
        self._log(f"↓  Downloading {'audio' if audio_only else 'video'}…")

        self._dl_worker = DownloadWorker(
            url, format_id, self._download_dir, tmpl,
            audio_only=audio_only, audio_fmt=audio_fmt,
            download_subs=self.subs_check.isChecked()
        )
        self._dl_worker.progress_update.connect(self._on_progress)
        self._dl_worker.status_update.connect(lambda s: self.prog_label.setText(s))
        self._dl_worker.download_done.connect(self._on_download_done)
        self._dl_worker.error_occurred.connect(self._on_download_error)
        self._dl_worker.start()

    def _on_progress(self, pct, speed, eta):
        self.progress_bar.setValue(int(pct))
        self.pct_label.setText(f"{pct:.1f}%")
        self.speed_label.setText(speed)
        self.eta_label.setText(f"ETA {eta}")
        self.prog_label.setText("Downloading…")

    def _on_download_done(self, filepath):
        self.progress_bar.setValue(100)
        self.pct_label.setText("100%")
        self.status_badge.setStatus('done')
        self.prog_label.setText("Download complete!")
        self.speed_label.setText("")
        self.eta_label.setText("")
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        title = self._video_info.get('title', 'Unknown') if self._video_info else 'Unknown'
        fmt = self.format_combo.currentText()
        self._log(f"✓  Done: {title[:50]}", color=DARK_THEME['success'])
        self._add_to_history(title, self.url_input.text().strip(), fmt, 'done')

    def _on_download_error(self, msg):
        self.status_badge.setStatus('error')
        self.prog_label.setText("Download failed")
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._log(f"✕  Error: {msg}", color=DARK_THEME['error'])
        title = self._video_info.get('title', 'Unknown') if self._video_info else 'Unknown'
        self._add_to_history(title, self.url_input.text().strip(),
                             self.format_combo.currentText(), 'error')

    def _cancel_download(self):
        if self._dl_worker and self._dl_worker.isRunning():
            self._dl_worker.terminate()
            self.status_badge.setStatus('cancelled')
            self.prog_label.setText("Cancelled")
            self.download_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            self._log("○  Download cancelled.", color=DARK_THEME['text_muted'])

    # ── History ──────────────────────────────────────────────

    def _add_to_history(self, title, url, fmt, status):
        ts = datetime.now().strftime("%b %d %H:%M")
        self._history.insert(0, (title, url, fmt, ts, status))
        item = QListWidgetItem(self.history_list)
        widget = DownloadHistoryItem(title, url, fmt, ts, status)
        item.setSizeHint(widget.sizeHint() + QSize(0, 8))
        self.history_list.insertItem(0, item)
        self.history_list.setItemWidget(item, widget)
        self.history_empty.setVisible(False)

    def _clear_history(self):
        self._history.clear()
        self.history_list.clear()
        self.history_empty.setVisible(True)

    # ── Batch ────────────────────────────────────────────────

    def _add_batch_url(self):
        url = self.batch_input.text().strip()
        if not url:
            return
        if any(i.url == url for i in self._batch_items):
            self._log("⚠  URL already in batch list.", color=DARK_THEME['warning'])
            return
        item_widget = BatchURLItem(url)
        item_widget.remove_requested.connect(self._remove_batch_item)
        self._batch_items.append(item_widget)
        self.batch_vbox.insertWidget(self.batch_vbox.count() - 1, item_widget)
        self.batch_input.clear()
        self.batch_status_label.setText(f"{len(self._batch_items)} URL(s) queued")

    def _remove_batch_item(self, widget):
        self._batch_items.remove(widget)
        self.batch_vbox.removeWidget(widget)
        widget.deleteLater()
        self.batch_status_label.setText(f"{len(self._batch_items)} URL(s) queued")

    def _clear_batch(self):
        for w in self._batch_items:
            self.batch_vbox.removeWidget(w)
            w.deleteLater()
        self._batch_items.clear()
        self.batch_status_label.setText("")

    def _start_batch(self):
        if not self._batch_items:
            return
        self._batch_queue = list(self._batch_items)
        self._batch_index = 0
        self._run_next_batch()

    def _run_next_batch(self):
        if self._batch_index >= len(self._batch_queue):
            self.batch_status_label.setText(
                f"✓ All {len(self._batch_queue)} downloads complete!")
            return
        item = self._batch_queue[self._batch_index]
        url  = item.url
        item.setStatus('downloading')
        fmt_idx    = self.batch_fmt_combo.currentIndex()
        audio_only = fmt_idx > 0
        audio_fmt  = 'mp3' if fmt_idx == 1 else 'm4a'
        tmpl = "%(title)s.%(ext)s"
        worker = DownloadWorker(url, 'bestvideo', self._download_dir, tmpl,
                                audio_only=audio_only, audio_fmt=audio_fmt)
        idx = self._batch_index

        def done(fp, i=idx, it=item):
            it.setStatus('done')
            self.batch_status_label.setText(f"Done {i+1}/{len(self._batch_queue)}")
            self._batch_index += 1
            self._run_next_batch()

        def err(msg, i=idx, it=item):
            it.setStatus('error')
            self.batch_status_label.setText(f"Error on item {i+1}")
            self._batch_index += 1
            self._run_next_batch()

        worker.download_done.connect(done)
        worker.error_occurred.connect(err)
        worker.start()
        self._log(f"↓ Batch [{self._batch_index+1}/{len(self._batch_queue)}]: {url[:50]}…")
        self.batch_status_label.setText(
            f"Downloading {self._batch_index+1}/{len(self._batch_queue)}…")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("YTVault")
    app.setApplicationVersion("1.0.0")

    # High-DPI
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    window = YTVaultWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
