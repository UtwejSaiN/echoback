"""
Generate a simple icon for C3 Time-Machine
Creates a red circular icon with a clock/timer aesthetic
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os

    def create_c3_icon(output_path='c3_icon.ico'):
        """Create a simple red circular icon with C3 branding"""

        # Create multiple sizes for Windows icon
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        images = []

        for size in sizes:
            # Create image with transparency
            img = Image.new('RGBA', size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            width, height = size
            margin = int(width * 0.05)

            # Draw red circle background
            draw.ellipse(
                [margin, margin, width - margin, height - margin],
                fill=(220, 20, 20, 255),  # Red
                outline=(180, 10, 10, 255),  # Darker red border
                width=max(1, int(width * 0.02))
            )

            # Draw white "C3" text in center
            if width >= 32:  # Only draw text for larger sizes
                try:
                    # Try to use a bold font if available
                    font_size = int(width * 0.4)
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        font = ImageFont.truetype("arialbd.ttf", font_size)
                except:
                    # Fallback to default font
                    font = ImageFont.load_default()

                text = "C3"

                # Get text bounding box for centering
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                x = (width - text_width) // 2
                y = (height - text_height) // 2 - int(height * 0.05)

                # Draw text with slight shadow for depth
                shadow_offset = max(1, int(width * 0.01))
                draw.text((x + shadow_offset, y + shadow_offset), text,
                         fill=(0, 0, 0, 128), font=font)  # Shadow
                draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)  # White text

            # Draw small clock hand indicator (optional detail for larger sizes)
            if width >= 48:
                center_x, center_y = width // 2, height // 2
                hand_length = int(width * 0.25)
                hand_width = max(2, int(width * 0.03))

                # Draw clock hand pointing at 2 o'clock (for "2 minutes back")
                import math
                angle = -60  # degrees (0 is up, clockwise)
                rad = math.radians(angle)
                end_x = center_x + int(hand_length * math.sin(rad))
                end_y = center_y - int(hand_length * math.cos(rad))

                draw.line([(center_x, center_y), (end_x, end_y)],
                         fill=(255, 255, 255, 200), width=hand_width)

            images.append(img)

        # Save as ICO file (Windows icon format)
        images[0].save(output_path, format='ICO', sizes=[img.size for img in images])
        print(f"✓ Icon created: {output_path}")
        print(f"  Sizes: {', '.join([f'{w}x{h}' for w, h in sizes])}")

        return output_path

    if __name__ == "__main__":
        icon_path = create_c3_icon()

        # Verify icon was created
        if os.path.exists(icon_path):
            file_size = os.path.getsize(icon_path)
            print(f"  File size: {file_size:,} bytes")
            print("\n✓ Icon ready for PyInstaller!")
        else:
            print("✗ Error: Icon file was not created")

except ImportError:
    print("=" * 60)
    print("ERROR: Pillow (PIL) not installed!")
    print("=" * 60)
    print("\nTo generate the icon, install Pillow:")
    print("  pip install Pillow")
    print("\nAlternatively, you can:")
    print("  1. Skip icon generation (PyInstaller will use default)")
    print("  2. Use an online icon generator")
    print("  3. Provide your own .ico file")
    print("=" * 60)
