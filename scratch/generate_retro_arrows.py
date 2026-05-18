from PIL import Image
import os

# Narrower and smaller 10x6 gothic caret perfectly centered in the 16x16 canvas
up_grid = [
    "................", # 0
    "................", # 1
    "................", # 2
    "................", # 3
    "................", # 4
    ".......BB.......", # 5
    "......BGGB......", # 6
    ".....BGGGGB.....", # 7
    "....BGGbBGGB....", # 8
    "...BGGb..BGGB...", # 9
    "...BB......BB...", # 10
    "................", # 11
    "................", # 12
    "................", # 13
    "................", # 14
    "................"  # 15
]

def make_image_from_grid(grid, color_map, filename):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for r in range(16):
        for c in range(16):
            char = grid[r][c]
            # Convert 'b' or 'B' to black outline
            if char in ('B', 'b'):
                color = color_map['B']
            elif char == 'G':
                color = color_map['G']
            else:
                color = color_map['.']
            img.putpixel((c, r), color)
            
    # Scale up to 64x64 using Nearest Neighbor to keep it crisp and pixel-art styled
    scaled_img = img.resize((64, 64), Image.NEAREST)
    
    dest_path = os.path.join("assets", filename)
    scaled_img.save(dest_path, "PNG")
    print(f"Generated {dest_path}")

# Core Color Map
# 'G' = Glowing Gold/Amber
# 'B' = Pure Black Border
# '.' = Transparent
color_map = {
    'G': (229, 178, 37, 255),
    'B': (0, 0, 0, 255),
    '.': (0, 0, 0, 0)
}

# 1. Generate UP Arrow
make_image_from_grid(up_grid, color_map, "icon_arrow_up.png")

# 2. Generate DOWN Arrow (Vertical Flip of UP Grid)
down_grid = []
for r in range(16):
    down_grid.append(up_grid[15 - r])
make_image_from_grid(down_grid, color_map, "icon_arrow_down.png")

# 3. Generate LEFT Arrow (Rotated 90 degrees CCW - Mathematically Perfectly Centered)
left_grid = []
for r in range(16):
    row_chars = []
    for c in range(16):
        row_chars.append(up_grid[c][15 - r])
    left_grid.append("".join(row_chars))
make_image_from_grid(left_grid, color_map, "icon_back_arrow.png")
