# C3 Time-Machine - Major Updates

## Changes Made

### 1. ✅ Fixed Threading Issues (pill.py)

**Problem:** `QMetaObject.invokeMethod` was causing RuntimeError crashes.

**Solution:** Replaced with PyQt signals for thread-safe communication:
- `capture_complete = pyqtSignal()` - Emitted when capture finishes
- `capture_error = pyqtSignal(str)` - Emitted on errors
- `update_status = pyqtSignal(str)` - Updates UI from background thread

**How it works:**
```python
# Background thread emits signal
self.capture_complete.emit()

# Main thread receives it via slot
self.capture_complete.connect(self._on_capture_complete)
```

### 2. ✅ Added Cancel Functionality (pill.py)

**What's New:**
- **Cancel button (✕)** appears next to GO button during capture
- Click to immediately stop recording and discard capture
- No file is saved when cancelled
- Status shows "⚠ Cancelling..." during cancel operation

**Implementation:**
- `cancel_button` widget (hidden by default, shown during capture)
- `on_cancel_clicked()` method sets `cancel_requested = True`
- `recorder.cancel_capture()` signals recorder to stop
- Background thread checks `cancel_requested` before saving

### 3. ✅ Improved Audio Device Detection (recorder.py)

**Priority Search Order:**
1. **WASAPI Loopback** devices (contains "loopback")
2. **Stereo Mix** devices (contains "stereo mix")
3. **Any Mix** devices (contains "mix")
4. Fallback to default input (microphone) with clear warning

**Enhanced Console Output:**
```
🔍 Searching for system audio capture device...
✓ Found Stereo Mix device: Stereo Mix (Realtek) (ID: 3)

✓ Recording started:
  Sample rate: 16000 Hz
  Channels: 1 (mono)
  Device: Stereo Mix (Realtek)
```

**If no device found:**
- Prints clear instructions for enabling Stereo Mix in Windows
- Lists all available input devices
- Falls back to microphone with warning

### 4. ✅ Added Visual Progress Bar (pill.py)

**New UI Element:**
- `QProgressBar` appears during capture
- Shows progress: "5s / 60s", "30s / 60s", etc.
- Fills up from left to right (red color)
- Hidden when not capturing

**Dimensions:**
- Normal: 170x150px
- During capture: 170x180px (expands to fit progress bar)

### 5. ✅ Pulsing Recording Dot Animation (pill.py)

**What it does:**
- Recording indicator (●) pulses between filled and empty (○)
- Pulses every 800ms when NOT capturing
- Shows the app is alive and recording
- Stops pulsing during capture (shows static ⏺)

**Implementation:**
```python
self.pulse_timer = QTimer()
self.pulse_timer.timeout.connect(self._pulse_dot)
self.pulse_timer.start(800)  # Pulse every 800ms
```

### 6. ✅ Improved Snap-to-Edge (pill.py)

**Enhancements:**
- Reduced margin from 10px to 5px (closer to edges)
- Added `QEasingCurve.Type.OutCubic` for smoother animation
- Prioritizes right edge over left edge
- Only animates when actually snapping (not on every drag release)
- Fixed taskbar margin (45px instead of 50px)

**Snap Priority:**
1. Right edge (if within 50px)
2. Left edge (if within 50px, but not if right edge matched)
3. Top edge (independent check)
4. Bottom edge (independent check, accounts for taskbar)

## New UI Layout

### Normal State (170x150px)
```
┌──────────────────┐
│ ○ Recording...   │  ← Pulsing dot
│                  │
│     ┌────────┐   │
│     │   GO   │   │  ← Red button
│     └────────┘   │
│                  │
│ Buffer: 45s      │
└──────────────────┘
```

### Capturing State (170x180px)
```
┌──────────────────┐
│ ⏺ Recording: 43s │  ← Countdown
│                  │
│  ┌─────────┐ ┌─┐ │
│  │Capturing│ │✕│ │  ← GO (disabled) + Cancel
│  └─────────┘ └─┘ │
│                  │
│ ▓▓▓▓▓▓░░░░░░░░░  │  ← Progress bar (43/60)
│ 43s / 60s        │
│                  │
│ Buffer: 120s     │
└──────────────────┘
```

## Cancel Flow

1. User presses GO button
2. GO button becomes disabled, shows "Capturing..."
3. Cancel button (✕) appears next to it
4. Progress bar appears and starts filling
5. **User clicks Cancel (✕)**
6. `cancel_requested = True`
7. `recorder.cancel_capture()` sets `cancel_flag = True`
8. Background thread stops collecting future chunks
9. Returns `None` instead of audio data
10. No file is saved
11. UI resets to normal state

## Error Handling

**Improved error display:**
- If capture errors (not cancelled): shows "✗ Error!" for 2 seconds
- Then automatically returns to "● Recording..."
- Console shows full traceback for debugging

**Graceful cancel:**
- Shows "⚠ Cancelling..." immediately
- Disables cancel button to prevent double-click
- Resets UI once background thread confirms cancellation

## Testing Checklist

- [ ] **Start app** - Should show pulsing dot (● ↔ ○)
- [ ] **Check console** - Should show device detection messages
- [ ] **Press GO** - Cancel button and progress bar appear
- [ ] **Watch progress** - Bar fills up, countdown decreases
- [ ] **Click Cancel mid-capture** - Should stop immediately, no file saved
- [ ] **Let capture complete** - Should save file to recordings/
- [ ] **Drag to right edge** - Should snap perfectly with 5px margin
- [ ] **Drag to left edge** - Should snap perfectly with 5px margin
- [ ] **Check recordings/** - Verify only completed captures are saved

## Files Changed

1. **c3tm/ui/pill.py** - Complete rewrite with signals, cancel, progress bar, pulse
2. **c3tm/audio/recorder.py** - Improved device detection, cancel support
3. **UPDATES.md** - This file (documentation)

## Known Limitations

- Cancel button appears immediately but capture may take ~100ms to actually stop
- Progress bar updates every 1 second (not smooth sub-second updates)
- Pulsing dot animation is simple (no fade effect, just toggle)
- Snap-to-edge only works on primary monitor (multi-monitor not tested)

## Next Steps

If everything works:
1. Test with real meeting (Teams/Meet/Zoom)
2. Verify Stereo Mix captures meeting audio
3. Test cancel during real capture
4. Verify files are only saved when NOT cancelled

If issues persist:
1. Check console output for error messages
2. Run `test_audio_devices.py` to verify device detection
3. Enable Stereo Mix in Windows Sound settings
4. Try with microphone first to test basic functionality
