import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
from echoback.audio.buffer import CircularAudioBuffer
from echoback.audio.recorder import AudioRecorder
from echoback.audio.saver import SaveManager
from echoback.ui.pill import PillWidget
from echoback.utils.logger import setup_logging
from echoback.utils.config import load_config
import sounddevice as sd

# Import version info
try:
    from version import __version__, __app_name__, __author__
except ImportError:
    __version__ = "1.0.0"
    __app_name__ = "C3 Time-Machine"
    __author__ = "Utwej Sai Nalluri"


def check_audio_device():
    """
    Check if a loopback or Stereo Mix device is available.
    Returns (found, device_name)
    """
    devices = sd.query_devices()

    # Check for loopback
    for device in devices:
        device_name = device['name'].lower()
        if 'loopback' in device_name and device['max_input_channels'] > 0:
            return True, device['name']

    # Check for Stereo Mix
    for device in devices:
        device_name = device['name'].lower()
        if 'stereo mix' in device_name and device['max_input_channels'] > 0:
            return True, device['name']

    # Check for any mix device
    for device in devices:
        device_name = device['name'].lower()
        if 'mix' in device_name and device['max_input_channels'] > 0:
            return True, device['name']

    return False, None


def show_first_run_dialog(parent=None):
    """
    Show first-run dialog with instructions for enabling Stereo Mix
    """
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("Audio Setup Required")
    msg.setText("<b>System Audio Capture Not Available</b>")
    msg.setInformativeText(
        "C3 needs to capture system audio (meeting voices) but no suitable device was found.\n\n"
        "<b>To enable Stereo Mix:</b>"
    )

    detailed_text = """
1. Right-click the Speaker icon in your Windows taskbar (bottom-right)
2. Select "Sounds" from the menu
3. Click the "Recording" tab
4. Right-click in the empty space → "Show Disabled Devices"
5. You should see "Stereo Mix" appear
6. Right-click "Stereo Mix" → Click "Enable"
7. Right-click "Stereo Mix" again → Click "Set as Default Device"
8. Click "OK" to close the window
9. Restart C3 Time-Machine

After following these steps, C3 will capture meeting audio (what you hear in your speakers/headphones) instead of just your microphone.

If "Stereo Mix" doesn't appear, your audio driver may not support it. You can:
- Update your audio drivers (Realtek, etc.)
- Use a virtual audio cable (VB-Audio Cable)
- Or use C3 with your microphone as a fallback
"""
    msg.setDetailedText(detailed_text)

    # Add buttons
    msg.setStandardButtons(
        QMessageBox.StandardButton.Ok |
        QMessageBox.StandardButton.Ignore
    )
    msg.setDefaultButton(QMessageBox.StandardButton.Ok)

    # Custom button text
    ok_button = msg.button(QMessageBox.StandardButton.Ok)
    ok_button.setText("I'll Set It Up Now")

    ignore_button = msg.button(QMessageBox.StandardButton.Ignore)
    ignore_button.setText("Continue Anyway (Use Microphone)")

    result = msg.exec()

    return result == QMessageBox.StandardButton.Ok


class C3Application:
    """Main application class with system tray support"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(__app_name__)
        self.app.setApplicationVersion(__version__)
        self.app.setOrganizationName(__author__)

        # Set application icon if available
        icon_path = Path("c3_icon.ico")
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))

        self.recorder = None
        self.pill = None
        self.tray_icon = None

    def setup_directories(self):
        """Ensure config and recordings directories exist"""
        Path("config").mkdir(exist_ok=True)
        Path("recordings").mkdir(exist_ok=True)

    def initialize_audio(self, config):
        """Initialize audio components"""
        print("Initializing audio buffer...")
        buffer = CircularAudioBuffer(
            duration_seconds=config['buffer_duration'],
            sample_rate=config['sample_rate'],
            channels=config['channels']
        )

        print("Initializing audio recorder...")
        recorder = AudioRecorder(
            buffer=buffer,
            sample_rate=config['sample_rate'],
            channels=config['channels']
        )

        print("Initializing save manager...")
        saver = SaveManager(recordings_dir=config['recordings_dir'])

        return recorder, saver, buffer

    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("Warning: System tray not available on this system")
            return

        self.tray_icon = QSystemTrayIcon(self.app)

        # Set icon
        icon_path = Path("c3_icon.ico")
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            # Use default icon
            self.tray_icon.setIcon(self.app.style().standardIcon(
                self.app.style().StandardPixmap.SP_MediaPlay
            ))

        # Create menu
        menu = QMenu()

        # Show/Hide action
        show_action = QAction("Show C3", self.app)
        show_action.triggered.connect(self.show_pill)
        menu.addAction(show_action)

        hide_action = QAction("Hide C3", self.app)
        hide_action.triggered.connect(self.hide_pill)
        menu.addAction(hide_action)

        menu.addSeparator()

        # About action
        about_action = QAction(f"About {__app_name__}", self.app)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)

        menu.addSeparator()

        # Quit action
        quit_action = QAction("Quit", self.app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip(f"{__app_name__} v{__version__}")

        # Double-click to show
        self.tray_icon.activated.connect(self.on_tray_activated)

        self.tray_icon.show()
        print("✓ System tray icon active")

    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_pill()

    def show_pill(self):
        """Show the pill widget"""
        if self.pill:
            self.pill.show()
            self.pill.raise_()
            self.pill.activateWindow()

    def hide_pill(self):
        """Hide the pill widget"""
        if self.pill:
            self.pill.hide()

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self.pill,
            f"About {__app_name__}",
            f"<h2>{__app_name__}</h2>"
            f"<p><b>Version:</b> {__version__}</p>"
            f"<p><b>Developer:</b> {__author__}</p>"
            f"<hr>"
            f"<p>Retroactive meeting audio capture utility.</p>"
            f"<p>Captures the last 2 minutes + next 1 minute of audio when you press GO.</p>"
            f"<p><small>Built with Python, PyQt6, and ❤️</small></p>"
        )

    def quit_app(self):
        """Quit the application"""
        if self.recorder:
            print("\nShutting down...")
            self.recorder.stop()

        if self.tray_icon:
            self.tray_icon.hide()

        self.app.quit()

    def run(self):
        """Main application loop"""
        # Setup logging
        setup_logging()
        print("=" * 50)
        print(f"{__app_name__} v{__version__}")
        print(f"by {__author__}")
        print("=" * 50)

        # Ensure directories exist
        self.setup_directories()

        # Load configuration
        config = load_config()

        # Check for audio device (first-run experience)
        device_found, device_name = check_audio_device()

        if not device_found:
            print("\n⚠ No system audio capture device found")
            print("  Showing first-run setup dialog...\n")

            # Show dialog before initializing audio
            should_setup = show_first_run_dialog()

            if should_setup:
                # User wants to set it up - show instructions and exit
                print("User will configure audio device. Please restart after setup.")
                sys.exit(0)
            else:
                # User wants to continue with microphone
                print("Continuing with default input device (microphone)")
        else:
            print(f"✓ System audio device found: {device_name}")

        # Initialize audio components
        self.recorder, saver, buffer = self.initialize_audio(config)

        # Start recording
        print("Starting continuous recording...")
        self.recorder.start()

        # Create and show pill widget
        print("Launching UI...")
        self.pill = PillWidget(self.recorder, saver)

        # Override close event to minimize to tray instead of quitting
        original_close_event = self.pill.closeEvent

        def close_event_override(event):
            if self.tray_icon and self.tray_icon.isVisible():
                event.ignore()
                self.pill.hide()
                self.tray_icon.showMessage(
                    __app_name__,
                    "C3 is still running in the background.\nDouble-click tray icon to show.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            else:
                original_close_event(event)
                self.quit_app()

        self.pill.closeEvent = close_event_override

        self.pill.show()

        # Setup system tray
        self.setup_system_tray()

        print("✓ C3 Time-Machine is ready!")
        print("  - Press GO button to capture moment (2 min past + 1 min future)")
        print("  - Recordings saved to:", config['recordings_dir'])
        print("  - Close window to minimize to system tray")
        print()

        # Run application
        exit_code = self.app.exec()

        # Cleanup
        if self.recorder:
            print("\nGoodbye!")

        sys.exit(exit_code)


def main():
    """Main entry point for C3 Time-Machine"""
    app = C3Application()
    app.run()


if __name__ == "__main__":
    main()
