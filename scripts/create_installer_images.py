"""
Script to create placeholder BMP images for the Handyman KPI installer.

This script generates two BMP images required by the Inno Setup installer:
- wizard-image.bmp: Small wizard image (55x58 pixels)
- wizard-image-large.bmp: Large wizard image (164x314 pixels)

The images will be saved in the resources/images directory.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

def create_small_wizard_image(output_path):
    """Create a small wizard image (55x58 pixels)."""
    # Create an RGB image with blue background
    img = Image.new('RGB', (55, 58), color=(30, 144, 255))
    
    # Add some basic graphics
    draw = ImageDraw.Draw(img)
    draw.rectangle([(5, 5), (50, 53)], outline=(255, 255, 255), width=2)
    
    try:
        # Try to add text (will use default font if specified font is unavailable)
        try:
            font = ImageFont.truetype("arial.ttf", 10)
        except IOError:
            font = ImageFont.load_default()
        
        draw.text((10, 20), "KPI", fill=(255, 255, 255), font=font)
    except Exception as e:
        print(f"Warning: Could not add text to image: {e}")
    
    # Save the image
    img.save(output_path, "BMP")
    print(f"Created small wizard image: {output_path}")

def create_large_wizard_image(output_path):
    """Create a large wizard image (164x314 pixels)."""
    # Create an RGB image with blue background
    img = Image.new('RGB', (164, 314), color=(30, 144, 255))
    
    # Add some basic graphics
    draw = ImageDraw.Draw(img)
    draw.rectangle([(10, 10), (154, 304)], outline=(255, 255, 255), width=2)
    
    try:
        # Try to add text (will use default font if specified font is unavailable)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
            font = ImageFont.load_default()
            
        draw.text((28, 100), "Handyman", fill=(255, 255, 255), font=font)
        draw.text((48, 130), "KPI", fill=(255, 255, 255), font=font)
        draw.text((25, 160), "System", fill=(255, 255, 255), font=font)
        
        # Add some decorative elements
        draw.line([(20, 200), (144, 200)], fill=(255, 255, 255), width=1)
        
        # Add a small wrench icon representation
        draw.line([(82, 240), (102, 260)], fill=(255, 255, 255), width=4)
        draw.ellipse([(70, 225), (85, 240)], outline=(255, 255, 255), width=2)
    except Exception as e:
        print(f"Warning: Could not add text to image: {e}")
    
    # Save the image
    img.save(output_path, "BMP")
    print(f"Created large wizard image: {output_path}")

def create_app_icon(output_path):
    """Create a basic app icon (48x48 pixels)."""
    # Create an RGB image with blue background
    img = Image.new('RGB', (48, 48), color=(30, 144, 255))
    
    # Add some basic graphics
    draw = ImageDraw.Draw(img)
    draw.rectangle([(4, 4), (44, 44)], outline=(255, 255, 255), width=2)
    
    try:
        # Try to add text
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font = ImageFont.load_default()
            
        draw.text((14, 16), "KPI", fill=(255, 255, 255), font=font)
    except Exception as e:
        print(f"Warning: Could not add text to image: {e}")
    
    # Save the image as ICO
    img.save(output_path, "ICO")
    print(f"Created app icon: {output_path}")

def main():
    """Main function."""
    # Get the base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create directories if they don't exist
    images_dir = os.path.join(base_dir, "resources", "images")
    icons_dir = os.path.join(base_dir, "resources", "icons")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(icons_dir, exist_ok=True)
    
    # Create the wizard images
    small_wizard_path = os.path.join(images_dir, "wizard-image.bmp")
    large_wizard_path = os.path.join(images_dir, "wizard-image-large.bmp")
    app_icon_path = os.path.join(icons_dir, "handyman_kpi.ico")
    
    create_small_wizard_image(small_wizard_path)
    create_large_wizard_image(large_wizard_path)
    create_app_icon(app_icon_path)
    
    print("\nInstaller images created successfully!")
    print(f"Small wizard image: {small_wizard_path}")
    print(f"Large wizard image: {large_wizard_path}")
    print(f"App icon: {app_icon_path}")

if __name__ == "__main__":
    main()
