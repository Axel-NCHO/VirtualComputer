################################################################################
import random
from util.compute_backend import xp

################################################################################
def hex_to_rgb(hex_code) -> xp.ndarray:
    """
    Convert a hex color string to RGB tuple.
    Supports formats: '#RRGGBB', 'RRGGBB', '#RGB', 'RGB'
    """
    hex_code = hex_code.lstrip('#')

    if len(hex_code) == 3:  # Short format like '#RGB'
        hex_code = ''.join([c * 2 for c in hex_code])

    if len(hex_code) != 6:
        raise ValueError(f"Invalid hex color code: {hex_code}")

    return xp.array((
        int(hex_code[0:2], 16),  # Red
        int(hex_code[2:4], 16),  # Green
        int(hex_code[4:6], 16)  # Blue
    ))

# --------------------------------------------------------------------------------
def random_color_rgb() -> xp.ndarray:
    return xp.array((
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    ))
