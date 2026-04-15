from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLabel, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, pyqtSignal, QEasingCurve
from PyQt6.QtGui import QFont, QGuiApplication
import threading

class PillWidget(QWidget):
    """
    Minimal pill-shaped window with GO button.
    Always on top, draggable, semi-transparent.
    """

    # Signals for thread-safe communication
    capture_complete = pyqtSignal()
    capture_error = pyqtSignal(str)
    update_status = pyqtSignal(str)

    def __init__(self, recorder, saver):
        super().__init__()
        self.recorder = recorder
        self.saver = saver

        # Window flags
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )

        # Semi-transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 20px;
            }
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QPushButton#cancel_button {
                background-color: #666666;
                font-size: 12px;
                padding: 5px 10px;
                border-radius: 10px;
            }
            QPushButton#cancel_button:hover {
                background-color: #888888;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                background-color: #2a2a2a;
                text-align: center;
                color: white;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #ff4444;
                border-radius: 4px;
            }
        """)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)

        # Status label with pulsing dot
        self.status_label = QLabel("● Recording...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Button container (GO + Cancel)
        button_container = QHBoxLayout()
        button_container.setSpacing(5)

        # GO button
        self.go_button = QPushButton("GO")
        self.go_button.setFixedSize(100, 50)
        self.go_button.clicked.connect(self.on_go_clicked)
        button_container.addWidget(self.go_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Cancel button (hidden initially)
        self.cancel_button = QPushButton("✕")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setFixedSize(30, 30)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.cancel_button.hide()
        button_container.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(button_container)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 60)  # 60 seconds
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(15)
        self.progress_bar.setFormat("%vs / 60s")
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Buffer status
        self.buffer_label = QLabel("Buffer: 0s")
        self.buffer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.buffer_label)

        self.setLayout(layout)

        # Position (top-right corner initially)
        self.setGeometry(100, 100, 170, 150)

        # Dragging support
        self.drag_position = None

        # Connect signals to slots
        self.capture_complete.connect(self._on_capture_complete)
        self.capture_error.connect(self._on_capture_error)
        self.update_status.connect(self._on_update_status)

        # Update buffer status every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_buffer_status)
        self.timer.start(1000)  # 1 second

        # Pulsing animation for recording dot
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse_dot)
        self.pulse_timer.start(800)  # Pulse every 800ms
        self.pulse_state = False

        # Capturing state
        self.is_capturing = False
        self.cancel_requested = False
        self.countdown_timer = None
        self.capture_thread = None

    def _pulse_dot(self):
        """Animate the recording dot to show it's alive"""
        if not self.is_capturing:
            current_text = self.status_label.text()
            if "●" in current_text:
                # Alternate between filled and empty circle
                if self.pulse_state:
                    new_text = current_text.replace("●", "○")
                else:
                    new_text = current_text.replace("○", "●")
                self.status_label.setText(new_text)
                self.pulse_state = not self.pulse_state

    def on_go_clicked(self):
        """Handle GO button press"""
        if self.is_capturing:
            print("Already capturing, please wait...")
            return

        self.is_capturing = True
        self.cancel_requested = False
        self.go_button.setEnabled(False)
        self.go_button.setText("Capturing...")

        # Show cancel button and progress bar
        self.cancel_button.show()
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        # Adjust window size to accommodate progress bar
        self.setGeometry(self.x(), self.y(), 170, 180)

        # Start countdown timer for progress bar
        self.countdown_seconds = 60
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self._update_countdown)
        self.countdown_timer.start(1000)  # Update every second

        # Trigger capture in background thread
        self.capture_thread = threading.Thread(target=self._capture_thread, daemon=True)
        self.capture_thread.start()

    def on_cancel_clicked(self):
        """Handle Cancel button press"""
        print("Capture cancelled by user")
        self.cancel_requested = True
        self.recorder.cancel_capture()  # Signal recorder to stop
        self.status_label.setText("⚠ Cancelling...")
        self.cancel_button.setEnabled(False)

    def _update_countdown(self):
        """Update countdown display and progress bar during future capture"""
        self.countdown_seconds -= 1
        elapsed = 60 - self.countdown_seconds

        # Update progress bar
        self.progress_bar.setValue(elapsed)

        if self.countdown_seconds > 0:
            self.status_label.setText(f"⏺ Recording: {self.countdown_seconds}s")
        else:
            self.status_label.setText("💾 Saving...")
            if self.countdown_timer:
                self.countdown_timer.stop()

    def _capture_thread(self):
        """Background thread for capture (blocks for 60 seconds)"""
        try:
            # Get 2 min past + 1 min future
            print("Starting capture: 2 min past + 1 min future...")

            # Now capture (this blocks for 60 seconds or until cancelled)
            audio_data = self.recorder.trigger_capture()

            # Check if cancelled
            if self.cancel_requested or audio_data is None or len(audio_data) == 0:
                print("Capture was cancelled, not saving file")
                self.capture_error.emit("Capture cancelled")
                return

            # Update status via signal
            self.update_status.emit("💾 Saving...")

            # Save to file
            filename = self.saver.save_capture(audio_data)
            print(f"Capture complete: {filename}")

            # Signal completion
            self.capture_complete.emit()

        except Exception as e:
            print(f"Capture error: {e}")
            import traceback
            traceback.print_exc()
            self.capture_error.emit(str(e))

    def _on_capture_complete(self):
        """Handle capture completion (runs on main thread)"""
        self._reset_ui()
        print("✓ Capture saved successfully!")

    def _on_capture_error(self, error_msg):
        """Handle capture error (runs on main thread)"""
        self._reset_ui()
        if "cancel" not in error_msg.lower():
            self.status_label.setText("✗ Error!")
            QTimer.singleShot(2000, lambda: self.status_label.setText("● Recording..."))

    def _on_update_status(self, text):
        """Update status label from background thread (runs on main thread)"""
        self.status_label.setText(text)

    def _reset_ui(self):
        """Reset UI after capture (called on main thread)"""
        self.is_capturing = False
        self.cancel_requested = False
        self.go_button.setEnabled(True)
        self.go_button.setText("GO")
        self.status_label.setText("● Recording...")
        self.cancel_button.hide()
        self.cancel_button.setEnabled(True)
        self.progress_bar.hide()

        if self.countdown_timer:
            self.countdown_timer.stop()

        # Shrink window back to original size
        self.setGeometry(self.x(), self.y(), 170, 150)

    def update_buffer_status(self):
        """Update buffer status label"""
        if not self.is_capturing:  # Don't update during capture
            stats = self.recorder.buffer.get_stats()
            duration = stats['buffer_duration_seconds']
            self.buffer_label.setText(f"Buffer: {int(duration)}s / 120s")

    # Dragging support with magnetic snap-to-edge
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Snap to edge when drag is released"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._snap_to_edge()
            event.accept()

    def _snap_to_edge(self):
        """Magnetic snap to screen edges"""
        # Get current screen geometry
        screen = QGuiApplication.primaryScreen().geometry()
        widget_rect = self.geometry()

        snap_threshold = 50  # pixels

        # Current position
        x = widget_rect.x()
        y = widget_rect.y()
        snapped = False

        # Snap to right edge (priority)
        if abs((x + widget_rect.width()) - screen.width()) < snap_threshold:
            x = screen.width() - widget_rect.width() - 5  # 5px margin
            snapped = True

        # Snap to left edge
        elif abs(x - screen.left()) < snap_threshold:
            x = screen.left() + 5
            snapped = True

        # Snap to top edge
        if abs(y - screen.top()) < snap_threshold:
            y = screen.top() + 5
            snapped = True

        # Snap to bottom edge
        elif abs((y + widget_rect.height()) - screen.height()) < snap_threshold:
            y = screen.height() - widget_rect.height() - 45  # Account for taskbar
            snapped = True

        # Only animate if actually snapping
        if snapped:
            animation = QPropertyAnimation(self, b"pos")
            animation.setDuration(200)  # 200ms smooth snap
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.setStartValue(self.pos())
            animation.setEndValue(QPoint(x, y))
            animation.start()

            # Store animation to prevent garbage collection
            self._snap_animation = animation
