"""
Quick test script to list available audio devices.
Run this before starting C3 to verify WASAPI loopback availability.
"""

try:
    import sounddevice as sd

    print("=" * 60)
    print("AUDIO DEVICES DETECTED")
    print("=" * 60)

    devices = sd.query_devices()

    print(f"\nTotal devices found: {len(devices)}\n")

    for idx, device in enumerate(devices):
        print(f"Device {idx}: {device['name']}")
        print(f"  Input channels: {device['max_input_channels']}")
        print(f"  Output channels: {device['max_output_channels']}")
        print(f"  Default sample rate: {device['default_samplerate']}")

        # Highlight loopback devices
        if 'loopback' in device['name'].lower():
            print(f"  ⭐ LOOPBACK DEVICE DETECTED ⭐")
        elif 'stereo mix' in device['name'].lower():
            print(f"  ⭐ STEREO MIX DETECTED ⭐")

        print()

    # Check default devices
    try:
        default_input = sd.default.device[0]
        default_output = sd.default.device[1]

        print("=" * 60)
        print(f"Default input device: {default_input}")
        print(f"  Name: {devices[default_input]['name']}")
        print()
        print(f"Default output device: {default_output}")
        print(f"  Name: {devices[default_output]['name']}")
        print("=" * 60)

    except Exception as e:
        print(f"Error getting default devices: {e}")

    # Recommendations
    print("\n📋 RECOMMENDATIONS:")

    loopback_found = any('loopback' in d['name'].lower() for d in devices)
    stereo_mix_found = any('stereo mix' in d['name'].lower() for d in devices)

    if loopback_found:
        print("✓ WASAPI loopback device found!")
        print("  C3 will automatically use this to capture system audio.")
    elif stereo_mix_found:
        print("✓ Stereo Mix device found!")
        print("  Make sure it's enabled and set as default input device.")
    else:
        print("⚠ No loopback or Stereo Mix device found!")
        print("\nTo capture meeting audio, you need to:")
        print("1. Open Windows Sound settings")
        print("2. Go to Recording tab")
        print("3. Right-click → Show Disabled Devices")
        print("4. Enable 'Stereo Mix'")
        print("5. Set it as default recording device")

    print("\n✓ Test complete! You can now run: python -m c3tm.main")

except ImportError:
    print("Error: sounddevice not installed!")
    print("Run: pip install -r requirements.txt")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
