#!/usr/bin/env python3
"""
Generate a simple icon for the application if one isn't available.

This script creates a basic icon file using PIL/Pillow that can be used
as a fallback if no custom icon is provided.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

def generate_icon(output_path, size=256, bg_color=(0, 102, 204), text="KPI", text_color=(255, 255, 255)):
    """Generate a simple icon with text."""
    # Create a new image with the given background color
    img = Image.new('RGB', (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font
    try:
        # Try to use a built-in font
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Use default font
        font = None
    
    # Draw text in the center
    text_width, text_height = draw.textsize(text, font=font) if font else (size // 2, size // 3)
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save in different sizes for icon
    img.save(output_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    
    print(f"Icon generated: {output_path}")

if __name__ == "__main__":
    # Get output path from command line or use default
    output_path = sys.argv[1] if len(sys.argv) > 1 else "icon.ico"
    
    # Generate icon
    generate_icon(output_path)
