# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Convert white and near-white areas in an image to a given background colour and resize.

Usage:
    uv run white_to_background.py <image_path> [--colour '#2BD3EC'] [--threshold 240] [--resize 480x720]

The script modifies the image in place, converting pixels that are
close to white (all RGB channels above threshold) to the specified
background colour, then optionally resizes to the specified dimensions.
"""

import argparse
from pathlib import Path

from PIL import Image


def hex_to_rgb(hex_colour: str) -> tuple[int, int, int]:
    """Convert hex colour string (e.g. '#2BD3EC') to RGB tuple."""
    hex_colour = hex_colour.lstrip('#')
    return tuple(int(hex_colour[i:i+2], 16) for i in (0, 2, 4))


# Default slide background: #2BD3EC = RGB(43, 211, 236)
DEFAULT_COLOUR = '#2BD3EC'

# Default slide image size (2:3 ratio)
DEFAULT_SIZE = (480, 720)


def white_to_colour(image_path: str, colour: str = DEFAULT_COLOUR, threshold: int = 240, resize: tuple[int, int] | None = DEFAULT_SIZE) -> None:
    """Convert white/near-white pixels to slide background colour and optionally resize.

    Args:
        image_path: Path to the PNG image to process
        colour: Hex colour string (e.g. '#2BD3EC'). Default '#2BD3EC'.
        threshold: RGB threshold (0-255). Pixels with all channels
                   above this value become the background colour. Default 240.
        resize: Target size as (width, height) tuple. Default (480, 720).
                Pass None to skip resizing.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    bg_rgb = hex_to_rgb(colour)

    # Open and convert to RGB
    img = Image.open(path).convert("RGB")
    data = img.getdata()

    new_data = []
    for pixel in data:
        r, g, b = pixel
        # If pixel is close to white, replace with background colour
        if r > threshold and g > threshold and b > threshold:
            new_data.append(bg_rgb)
        else:
            new_data.append(pixel)

    img.putdata(new_data)

    # Resize if specified
    if resize:
        img = img.resize(resize, Image.Resampling.LANCZOS)
        print(f"Processed: {path} (white -> {colour}, resized to {resize[0]}x{resize[1]})")
    else:
        print(f"Processed: {path} (white -> {colour})")

    img.save(path, "PNG")


def parse_size(value: str) -> tuple[int, int]:
    """Parse size string like '240x360' into (width, height) tuple."""
    try:
        width, height = value.lower().split('x')
        return (int(width), int(height))
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid size format: {value}. Use WIDTHxHEIGHT (e.g., 240x360)")


def main():
    parser = argparse.ArgumentParser(
        description="Convert white backgrounds to a specified colour and resize PNG images"
    )
    parser.add_argument(
        "image_path",
        help="Path to the PNG image to process"
    )
    parser.add_argument(
        "--colour",
        type=str,
        default=DEFAULT_COLOUR,
        help=f"Background colour as hex string (e.g. '#2BD3EC'). Default: {DEFAULT_COLOUR}"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=200,
        help="RGB threshold (0-255). Pixels with all channels above this become the background colour. Default: 200"
    )
    parser.add_argument(
        "--resize",
        type=parse_size,
        default="480x720",
        help="Target size as WIDTHxHEIGHT (e.g., 480x720). Default: 480x720"
    )
    parser.add_argument(
        "--no-resize",
        action="store_true",
        help="Skip resizing (only convert white to background colour)"
    )

    args = parser.parse_args()
    resize = None if args.no_resize else args.resize
    white_to_colour(args.image_path, args.colour, args.threshold, resize)


if __name__ == "__main__":
    main()
