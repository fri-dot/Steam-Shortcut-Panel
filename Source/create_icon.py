#!/usr/bin/env python
"""Create a blue leaf icon for the Steam Shortcut Panel."""

from PIL import Image, ImageDraw
import os

def create_blue_leaf_icon(output_path: str = "icon.ico"):
    """Generate a simple blue leaf icon."""
    # Create a new image with transparency
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a simple leaf shape (upside-down teardrop)
    # Center and size
    center_x, center_y = size // 2, size // 2
    leaf_width = 80
    leaf_height = 120
    
    # Main leaf body (blue gradient effect using filled polygon)
    leaf_points = [
        (center_x, center_y - leaf_height // 2),           # Top point
        (center_x + leaf_width // 2, center_y + 20),       # Right
        (center_x + leaf_width // 3, center_y + leaf_height // 2),  # Bottom right
        (center_x, center_y + leaf_height // 2 - 10),      # Bottom
        (center_x - leaf_width // 3, center_y + leaf_height // 2),  # Bottom left
        (center_x - leaf_width // 2, center_y + 20),       # Left
    ]
    
    # Draw main leaf in bright blue
    draw.polygon(leaf_points, fill=(0, 150, 255, 255), outline=(0, 100, 200, 255))
    
    # Draw vein details in darker blue
    vein_color = (0, 100, 180, 200)
    
    # Center vein
    draw.line([
        (center_x, center_y - leaf_height // 2),
        (center_x, center_y + leaf_height // 2)
    ], fill=vein_color, width=2)
    
    # Side veins
    for i in range(3):
        offset = 20 + (i * 20)
        # Right veins
        draw.line([
            (center_x + offset, center_y - leaf_height // 2 + offset),
            (center_x + offset // 2, center_y + leaf_height // 2 - 20)
        ], fill=vein_color, width=1)
        # Left veins
        draw.line([
            (center_x - offset, center_y - leaf_height // 2 + offset),
            (center_x - offset // 2, center_y + leaf_height // 2 - 20)
        ], fill=vein_color, width=1)
    
    # Save as ICO
    image.save(output_path, format='ICO', sizes=[(256, 256)])
    print(f"✓ Icon created: {output_path}")

if __name__ == "__main__":
    create_blue_leaf_icon()
