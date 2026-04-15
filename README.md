# Echoback

**Never miss an important meeting moment again.** Echoback is a Windows desktop application that continuously records the last 2 minutes of system audio in memory. When something important happens, press the GO button to save the past 2 minutes plus the next 1 minute—giving you perfect 3-minute captures with full context.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![Contributions](https://img.shields.io/badge/contributions-welcome-brightgreen)

---

## ✨ Features

- **🔄 Retroactive Recording** - Capture audio that already happened (last 2 minutes)
- **⏱️ Smart Buffering** - Always-on circular buffer keeps only 2 minutes in memory
- **🎯 One-Click Capture** - Press GO to save 2 min past + 1 min future (3 minutes total)
- **📊 Visual Feedback** - Progress bar and countdown timer show capture status
- **❌ Cancel Anytime** - Stop recording mid-capture without saving
- **🎤 System Audio** - Captures meeting participants' voices, not just your microphone
- **📍 Snap-to-Edge** - Pill UI magnetically snaps to screen edges
- **💾 Local Storage** - All recordings saved locally (WAV format, 16kHz mono)
- **🔒 Privacy First** - Manual trigger required, no automatic recording
- **🖥️ System Tray** - Minimize to tray, always ready when you need it

---

## 🎥 How It Works

```
Timeline:
├──────────────────────────┼──────────────────┤
│   Past (buffered)        │  Future (live)   │
│   2 minutes              │  1 minute        │
└──────────────────────────┴──────────────────┘
                           ↑
                        Press GO
                        
Result: 3-minute audio file with full context
```

1. **Echoback runs in background** - Continuously buffers last 2 minutes
2. **Important moment happens** - Someone says something critical
3. **You press GO** - Immediately after hearing it
4. **Echoback captures** - 2 minutes before + 1 minute after
5. **File saved** - Perfect 3-minute recording in `recordings/` folder

---

## 🚀 Coming Soon

We're actively developing these exciting features:

### 📱 Management UI
- **Browse recordings** - Visual timeline of all your captures
- **Built-in player** - Play audio directly in the app
- **Search & filter** - Find recordings by date, duration, or tags
- **Export options** - Share recordings easily (email, cloud, etc.)

### 📝 Contextual Notes
- **Add notes while capturing** - Describe what's happening in real-time
- **Edit later** - Add context to recordings after the fact
- **Tags & labels** - Organize with custom categories
- **Transcription** - Automatic speech-to-text (coming soon)

### 📸 Screen Capture
- **Screenshot on GO** - Automatically capture your screen when you press GO
- **Screen recording option** - Record video alongside audio
- **Multi-monitor support** - Choose which screen to capture
- **Synchronized playback** - View screenshots synced with audio timeline

### 🤝 Want to Help Build These?

**We're looking for collaborators!** Whether you're interested in:
- UI/UX design for the management interface
- Audio processing and transcription
- Screen capture implementation
- Cloud storage integration
- Or any other feature ideas

**Check out our [Contributing](#-contributing) section below to get started!**

---

## 📥 Download & Installation

### Option 1: Pre-built Executable (Recommended)

1. Download `Echoback_v1.0.0.zip` from [Releases](../../releases)
2. Extract the ZIP file
3. Run `Echoback.exe`
4. Follow first-run setup if prompted

**No Python installation required!**

### Option 2: Run from Source

```bash
# Clone repository
git clone https://github.com/UtwejSaiN/echoback.git
cd echoback

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python -m echoback.main
```

---

## ⚙️ First-Time Setup

### Enable System Audio Capture

Echoback needs to capture system audio (what you hear in meetings) rather than just your microphone.

**If you see a setup dialog on first launch, follow these steps:**

1. Right-click the **Speaker icon** in Windows taskbar (bottom-right)
2. Select **"Sounds"** from menu
3. Click the **"Recording"** tab
4. Right-click in empty space → **"Show Disabled Devices"**
5. Right-click **"Stereo Mix"** → **"Enable"**
6. Right-click **"Stereo Mix"** again → **"Set as Default Device"**
7. Click **OK**
8. Restart Echoback

**After this one-time setup**, Echoback will automatically capture meeting audio.

---

## 🎯 Usage

### Basic Operation

1. **Launch Echoback** - Double-click `Echoback.exe` or run from source
2. **Wait for buffer** - Let it fill for ~30-60 seconds (shows "Buffer: Xs / 120s")
3. **Join your meeting** - Teams, Google Meet, Zoom, etc.
4. **Listen normally** - Echoback runs in background, buffering audio
5. **Important moment?** - Press the **GO** button immediately
6. **Wait 60 seconds** - Progress bar fills, countdown shows remaining time
7. **Recording saved!** - Check `recordings/` folder for your WAV file

### UI Overview

```
┌──────────────────┐
│ ○ Recording...   │  ← Status (pulses to show it's alive)
│                  │
│     ┌────────┐   │
│     │   GO   │   │  ← Press when important moment happens
│     └────────┘   │
│                  │
│ Buffer: 45s      │  ← Shows how much audio is buffered
└──────────────────┘
```

**During capture:**
```
┌──────────────────┐
│ ⏺ Recording: 43s │  ← Countdown timer
│  ┌─────────┐ ┌─┐ │
│  │Capturing│ │✕│ │  ← GO button disabled + Cancel button
│  └─────────┘ └─┘ │
│ ▓▓▓▓▓▓░░░░░░░░░  │  ← Visual progress bar
│ 43s / 60s        │
│ Buffer: 120s     │
└──────────────────┘
```

### System Tray

- **Close window** → Minimizes to system tray (stays running)
- **Double-click tray icon** → Restores window
- **Right-click tray icon** → Menu (Show/Hide/About/Quit)

---

## 📁 File Structure

```
Echoback/
├── Echoback.exe            # Main application
├── echoback_icon.ico       # Application icon
├── config/
│   └── default_config.json # Default settings
└── recordings/             # Your saved captures
    ├── 2026-04-15_143022.wav
    ├── 2026-04-15_143022.json
    └── ...
```

**Each recording includes:**
- `.wav` file - Audio (16kHz mono, ~6 MB per 3 minutes)
- `.json` file - Metadata (timestamp, duration, file size)

---

## ⚡ Keyboard & Mouse

| Action | Effect |
|--------|--------|
| **Click GO** | Start capture (2 min past + 1 min future) |
| **Click ✕** | Cancel capture mid-recording |
| **Drag pill** | Move window anywhere |
| **Release near edge** | Snap to screen edge (magnetic) |
| **Close window** | Minimize to system tray |
| **Double-click tray** | Restore window |

---

## 🔧 Configuration

Edit `config/default_config.json` to customize:

```json
{
  "buffer_duration": 120,      // Past audio buffer (seconds)
  "future_duration": 60,        // Future recording length (seconds)
  "sample_rate": 16000,         // Audio quality (Hz)
  "channels": 1,                // 1 = mono, 2 = stereo
  "recordings_dir": "recordings"
}
```

**Common adjustments:**
- **3-minute buffer**: Change `buffer_duration` to `180`
- **Longer future**: Change `future_duration` to `90` (1.5 minutes)
- **Higher quality**: Change `sample_rate` to `44100` (CD quality)

---

## 🛠️ Building from Source

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for complete guide.

**Quick build:**
```bash
# Install build dependencies
pip install pyinstaller Pillow

# Generate icon
python generate_icon.py

# Build executable
python build_product.py

# Output: dist/Echoback.exe
```

---

## 🤝 Contributing

**We warmly welcome contributions!** Echoback is open source and built by the community.

### 🌟 Ways to Contribute

1. **Code contributions**
   - Implement features from the [Coming Soon](#-coming-soon) list
   - Fix bugs and improve performance
   - Add tests and documentation

2. **Design contributions**
   - UI/UX mockups for management interface
   - App icon redesign
   - User flow diagrams

3. **Documentation**
   - Improve README or guides
   - Create video tutorials
   - Write blog posts about Echoback

4. **Feature ideas**
   - Open an issue with your idea
   - Discuss on GitHub Discussions
   - Create a prototype

### 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/echoback.git
   cd echoback
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/management-ui
   # or
   git checkout -b feature/screen-capture
   # or
   git checkout -b feature/contextual-notes
   ```

4. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Test thoroughly on Windows

5. **Commit and push**
   ```bash
   git add .
   git commit -m "Add: Management UI with recording browser"
   git push origin feature/management-ui
   ```

6. **Open a Pull Request**
   - Describe what you built
   - Reference any related issues
   - Add screenshots if UI changes

### 💡 Feature Priorities

**High Priority (Help Wanted!):**
- 📱 **Management UI** - PyQt6 interface for browsing/playing recordings
- 📝 **Contextual Notes** - Add text input for recording descriptions
- 📸 **Screen Capture** - Screenshot on GO button press

**Medium Priority:**
- 🔊 **MP3 Compression** - Reduce file sizes
- 🔍 **Search & Filter** - Find recordings quickly
- ☁️ **Cloud Sync** - Optional Dropbox/Google Drive integration

**Nice to Have:**
- 🗣️ **Transcription** - Speech-to-text via Whisper API
- 🎨 **Themes** - Dark/light mode
- ⌨️ **Global Hotkeys** - Keyboard shortcuts for GO button
- 📊 **Analytics** - Recording statistics and insights

### 📋 Code Style

- Follow PEP 8 for Python code
- Use type hints where helpful
- Add docstrings to functions/classes
- Keep functions focused and small
- Write self-documenting code

### 🐛 Reporting Bugs

Found a bug? Please open an issue with:
- **Description** - What happened vs. what you expected
- **Steps to reproduce** - How to trigger the bug
- **Environment** - Windows version, Python version
- **Screenshots** - If applicable

### 💬 Questions?

- **GitHub Discussions** - Ask questions, share ideas
- **GitHub Issues** - Report bugs, request features
- **Email** - utwejnalluri@gmail.com

---

## 🐛 Troubleshooting

### No meeting audio captured (only microphone)

**Cause:** Stereo Mix not enabled or not set as default

**Fix:**
1. Windows Settings → Sound → Recording tab
2. Enable "Stereo Mix"
3. Set as **Default Device** (not just enabled)
4. Restart Echoback

### App crashes when pressing GO

**Cause:** Audio device disconnected or driver issue

**Fix:**
1. Check Windows Sound settings
2. Ensure audio device is working
3. Try restarting Echoback

### Empty or corrupted recordings

**Cause:** Buffer not filled yet, or disk full

**Fix:**
1. Wait 2+ minutes after launch before first GO press
2. Check available disk space
3. Try recording again

### Antivirus flags the EXE

**Cause:** PyInstaller executables sometimes trigger false positives

**Fix:**
1. Submit file to antivirus vendor as false positive
2. Add exception for Echoback.exe
3. Download directly from GitHub Releases (trusted source)

---

## 💡 Tips & Best Practices

- **Wait for full buffer** - Best results after 2+ minutes running
- **Press GO immediately** - Don't wait, the moment already happened
- **Watch the countdown** - Avoid talking sensitive info during the next 60 seconds
- **Keep window open during meetings** - Or minimize to tray
- **Organize recordings** - Rename WAV files with descriptive names
- **Test before important meetings** - Practice with test audio

---

## 🔒 Privacy & Security

- **Local only** - All recordings stored on your computer
- **Manual trigger** - No automatic recording or cloud upload
- **No telemetry** - App doesn't send any data anywhere
- **Easy deletion** - Just delete files from `recordings/` folder
- **Temporary buffer** - Only last 2 minutes kept in memory

---

## 📊 System Requirements

- **OS:** Windows 10 or Windows 11
- **RAM:** 2 GB minimum (50 MB used by app)
- **Disk:** 100 MB for app + storage for recordings (~6 MB per capture)
- **Audio:** Sound card with Stereo Mix or WASAPI loopback support
- **Python:** Not required for pre-built EXE

---

## 🌟 Contributors

Thank you to everyone who has contributed to Echoback!

<!-- Contributors list will be automatically generated -->

**Want to see your name here?** Check out our [Contributing](#-contributing) guide!

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙋 Support

- **Issues:** [GitHub Issues](../../issues)
- **Discussions:** [GitHub Discussions](../../discussions)
- **Email:** utwejnalluri@gmail.com

---

## 📜 Changelog

### v1.0.0 (2026-04-15)
- Initial release
- Retroactive 2-minute audio buffer
- GO button capture (3 minutes total)
- Visual progress bar and countdown
- Cancel functionality
- System tray integration
- First-run setup wizard
- Snap-to-edge UI
- WAV format recordings with metadata

---

## 🙏 Acknowledgments

Built with:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [sounddevice](https://python-sounddevice.readthedocs.io/) - Audio capture
- [NumPy](https://numpy.org/) - Audio processing
- [PyInstaller](https://pyinstaller.org/) - Executable packaging

---

**Made with ❤️ by Utwej Sai Nalluri**

⭐ **Star this repo if you find it useful!**  
🤝 **Contributions welcome - let's build something amazing together!**
