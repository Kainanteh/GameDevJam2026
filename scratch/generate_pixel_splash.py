import os
import re
from PIL import Image, ImageDraw, ImageFont

def main():
    # 1. Read original icon.svg
    with open('icon.svg', 'r') as f:
        svg_content = f.read()

    # 2. Modify SVG to keep only head and use clean colors
    svg_no_rect = re.sub(r'<rect[^>]*>', '', svg_content)
    # Use solid white fill for the head so we can colorize it pixel-by-pixel easily
    svg_white = svg_no_rect.replace('fill="#478cbf"', 'fill="#ffffff"')
    
    os.makedirs('scratch', exist_ok=True)
    with open('scratch/icon_head_white.svg', 'w') as f:
        f.write(svg_white)

    # 3. Rasterize to a small 40x40 image for retro pixelation
    print("Rasterizing SVG to 40x40...")
    os.system('rsvg-convert -w 40 -h 40 scratch/icon_head_white.svg -o scratch/icon_head_white.png')

    # 4. Load the head image
    head_raw = Image.open('scratch/icon_head_white.png').convert('RGBA')

    # Convert to 1-bit alpha and colorize the face/eyes/mouth/pupils
    head_px = head_raw.load()
    head = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
    head_draw = ImageDraw.Draw(head)
    
    # We want:
    # Face (originally #478cbf, which is now #ffffff): colorize to neon cyan #00f3ff
    # Eyes/mouth (originally #ffffff): keep #ffffff
    # Pupils (originally #414042): colorize to #07060a
    # We can detect this based on the original SVG colors, but since we rasterized:
    # Let's rasterize two versions or just colorize the white head:
    # Actually, let's look at the rasterized pixels. Since the mouth/eyes are white, and the face is white, they are both white in head_raw!
    # Ah! If they are both white, we can't distinguish them if we make them both white in the SVG.
    # So let's keep the original colors in the SVG, rasterize it, and then map the colors!
    # Original SVG colors:
    # Face: #478cbf (RGB: 71, 140, 191)
    # Eyes/mouth: #ffffff (RGB: 255, 255, 255)
    # Pupils: #414042 (RGB: 65, 64, 66)
    
    with open('scratch/icon_head_colored.svg', 'w') as f:
        f.write(svg_no_rect)
        
    os.system('rsvg-convert -w 40 -h 40 scratch/icon_head_colored.svg -o scratch/icon_head_colored.png')
    head_colored = Image.open('scratch/icon_head_colored.png').convert('RGBA')
    hc_px = head_colored.load()

    # Create pixel-perfect color-mapped head
    head = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
    h_px = head.load()

    for y in range(40):
        for x in range(40):
            r, g, b, a = hc_px[x, y]
            if a < 128:
                continue # Transparent
            
            # Map colors:
            # 1. White parts (eyes, mouth): r, g, b close to 255
            if r > 200 and g > 200 and b > 200:
                h_px[x, y] = (255, 255, 255, 255) # Pure white
            # 2. Pupils (dark grey #414042)
            elif r < 100 and g < 100 and b < 100:
                h_px[x, y] = (7, 6, 10, 255) # Dark background color
            # 3. Face (blue #478cbf)
            else:
                h_px[x, y] = (0, 243, 255, 255) # Neon Cyan

    # 5. Create low-res canvas (200 x 120)
    low_w = 200
    low_h = 120
    low_canvas = Image.new('RGBA', (low_w, low_h), (7, 6, 10, 255))
    low_draw = ImageDraw.Draw(low_canvas)

    # 6. Draw neon pink outline for the head
    # Create mask of the head (where it's not transparent)
    outline_mask = Image.new('L', (40, 40), 0)
    om_px = outline_mask.load()
    for y in range(40):
        for x in range(40):
            if h_px[x, y][3] > 0:
                om_px[x, y] = 255

    # Draw neon pink outline (#ff007f) on low_canvas by shifting mask
    head_x = (low_w - 40) // 2
    head_y = 12
    
    # 1-pixel shift outline in 4 directions
    pink_color = (255, 0, 127, 255)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        # Create a temp outline image
        temp_outline = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        to_px = temp_outline.load()
        for y in range(40):
            for x in range(40):
                if om_px[x, y] > 0:
                    to_px[x, y] = pink_color
        low_canvas.paste(temp_outline, (head_x + dx, head_y + dy), temp_outline)

    # Paste the clean head on top of the outline
    low_canvas.paste(head, (head_x, head_y), head)

    # 7. Draw low-res text
    font_path_bold = '/usr/share/fonts/noto/NotoSans-Bold.ttf'
    font_path_reg = '/usr/share/fonts/noto/NotoSans-Regular.ttf'

    # Low-res font sizes
    font_godot = ImageFont.truetype(font_path_bold, 11)
    font_engine = ImageFont.truetype(font_path_reg, 5)

    text_godot = "GODOT"
    text_engine = "Game engine"

    # Draw GODOT with a 1-pixel neon cyan (#00f3ff) shadow/outline for a glow effect
    box_godot = low_draw.textbbox((0, 0), text_godot, font=font_godot)
    godot_w = box_godot[2] - box_godot[0]
    godot_x = (low_w - godot_w) // 2
    godot_y = 65

    # Cyan text outline
    cyan_color = (0, 243, 255, 255)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        low_draw.text((godot_x + dx, godot_y + dy), text_godot, fill=cyan_color, font=font_godot)

    # Draw main white text
    low_draw.text((godot_x, godot_y), text_godot, fill=(255, 255, 255, 255), font=font_godot)

    # Draw "Game engine" in small retro font
    box_engine = low_draw.textbbox((0, 0), text_engine, font=font_engine)
    engine_w = box_engine[2] - box_engine[0]
    engine_x = (low_w - engine_w) // 2
    engine_y = 86
    low_draw.text((engine_x, engine_y), text_engine, fill=(150, 155, 170, 255), font=font_engine)

    # 8. Upscale the entire canvas to 800 x 480 (4x) using NEAREST NEIGHBOR
    final_canvas = low_canvas.resize((800, 480), Image.NEAREST)

    # Save to assets/godot_splash_logo.png
    final_canvas.save('assets/godot_splash_logo.png', 'PNG')
    print("Successfully generated retro-pixel assets/godot_splash_logo.png!")

if __name__ == '__main__':
    main()
