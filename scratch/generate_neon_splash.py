import os
import re
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

def get_outline(mask, thickness=2):
    # Dilate and Erode to get outline
    dilated = mask.filter(ImageFilter.MaxFilter(thickness * 2 + 1))
    eroded = mask.filter(ImageFilter.MinFilter(thickness * 2 + 1))
    return ImageChops.difference(dilated, eroded)

def draw_neon_glow(canvas, mask, color, core_color, position):
    # mask is a L image (0 or 255)
    # color: tuple (R, G, B, A)
    # core_color: tuple (R, G, B, A)
    # position: tuple (x, y)
    
    w, h = mask.size
    
    # Create canvas for glow layers
    glow_canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_canvas)
    
    # Paint mask with the saturated neon color
    glow_canvas.paste(color, (0, 0), mask)
    
    # Generate blur passes
    glow_15 = glow_canvas.filter(ImageFilter.GaussianBlur(12))
    glow_6 = glow_canvas.filter(ImageFilter.GaussianBlur(5))
    glow_2 = glow_canvas.filter(ImageFilter.GaussianBlur(2))
    
    # Composite glow layers onto the main canvas
    # Soft wide glow (opacity 0.4)
    soft_glow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    soft_glow.paste(glow_15, position, glow_15)
    canvas.alpha_composite(soft_glow)
    
    # Medium glow (opacity 0.7)
    med_glow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    med_glow.paste(glow_6, position, glow_6)
    canvas.alpha_composite(med_glow)
    
    # Sharp close glow (opacity 1.0)
    sharp_glow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    sharp_glow.paste(glow_2, position, glow_2)
    canvas.alpha_composite(sharp_glow)
    
    # Core tube (sharp light line)
    core_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    core_img.paste(core_color, (0, 0), mask)
    
    # Paste core
    canvas.paste(core_img, position, mask)

def main():
    # 1. Read original icon.svg
    with open('icon.svg', 'r') as f:
        svg_content = f.read()

    # Remove rectangle
    svg_no_rect = re.sub(r'<rect[^>]*>', '', svg_content)
    
    os.makedirs('scratch', exist_ok=True)
    with open('scratch/icon_head_highres.svg', 'w') as f:
        f.write(svg_no_rect)

    # 2. Rasterize to a high-res 360x360 image
    print("Rasterizing SVG to 360x360...")
    os.system('rsvg-convert -w 360 -h 360 scratch/icon_head_highres.svg -o scratch/icon_head_highres.png')

    # 3. Load the rasterized head
    head_raw = Image.open('scratch/icon_head_highres.png').convert('RGBA')
    h_w, h_h = head_raw.size
    raw_px = head_raw.load()

    # Separate into Face Mask and Eyes/Mouth Mask
    face_mask = Image.new('L', (h_w, h_h), 0)
    eyes_mask = Image.new('L', (h_w, h_h), 0)
    
    fm_px = face_mask.load()
    em_px = eyes_mask.load()

    for y in range(h_h):
        for x in range(h_w):
            r, g, b, a = raw_px[x, y]
            if a < 30:
                continue
            
            # Map colors:
            # 1. White parts (eyes, mouth)
            if r > 200 and g > 200 and b > 200:
                em_px[x, y] = 255
            # 2. Pupils (dark grey #414042)
            elif r < 100 and g < 100 and b < 100:
                pass # Treat as transparent inside pupils for the neon look
            # 3. Face (blue #478cbf)
            else:
                fm_px[x, y] = 255

    # 4. Get outlines for face and eyes/mouth
    face_outline = get_outline(face_mask, thickness=2)
    eyes_outline = get_outline(eyes_mask, thickness=1)

    # 5. Create final 1920x1080 canvas
    canvas_w = 1920
    canvas_h = 1080
    splash = Image.new('RGBA', (canvas_w, canvas_h), (7, 6, 10, 255))
    draw = ImageDraw.Draw(splash)

    # 6. Seed stars to match the wallpaper style
    neon_blue = (0, 210, 255, 255)
    neon_pink = (255, 0, 127, 255)
    star_white = (255, 255, 255, 220)
    
    def draw_star(draw_obj, cx, cy, color, size):
        if size == 1:
            draw_obj.point((cx, cy), fill=color)
        elif size == 2:
            draw_obj.point((cx, cy), fill=color)
            draw_obj.point((cx+1, cy), fill=color)
        elif size == 3:
            draw_obj.point((cx, cy), fill=color)
            draw_obj.point((cx-1, cy), fill=(color[0], color[1], color[2], 120))
            draw_obj.point((cx+1, cy), fill=(color[0], color[1], color[2], 120))
            draw_obj.point((cx, cy-1), fill=(color[0], color[1], color[2], 120))
            draw_obj.point((cx, cy+1), fill=(color[0], color[1], color[2], 120))
        elif size == 4:
            draw_obj.point((cx, cy), fill=star_white)
            draw_obj.point((cx-1, cy), fill=color)
            draw_obj.point((cx+1, cy), fill=color)
            draw_obj.point((cx, cy-1), fill=color)
            draw_obj.point((cx, cy+1), fill=color)
            draw_obj.point((cx-2, cy), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx+2, cy), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx, cy-2), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx, cy+2), fill=(color[0], color[1], color[2], 60))

    # Scatter stars only on left and right margins
    random.seed(42)
    for _ in range(35):
        # Left side
        cx = random.randint(20, 520)
        cy = random.randint(20, 1060)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)
        
        # Right side
        cx = random.randint(1400, 1900)
        cy = random.randint(20, 1060)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)

    # 7. Render Glowing Neon Robot Head
    head_x = (canvas_w - h_w) // 2
    head_y = 200
    
    # Face -> Cyan neon
    cyan_glow = (0, 210, 255, 255)
    cyan_core = (200, 245, 255, 255)
    draw_neon_glow(splash, face_outline, cyan_glow, cyan_core, (head_x, head_y))
    
    # Eyes/Mouth -> Pink/magenta neon
    pink_glow = (255, 0, 127, 255)
    pink_core = (255, 210, 230, 255)
    draw_neon_glow(splash, eyes_outline, pink_glow, pink_core, (head_x, head_y))

    # 8. Render Glowing Neon Text
    font_path_bold = '/usr/share/fonts/noto/NotoSans-Bold.ttf'
    font_path_reg = '/usr/share/fonts/noto/NotoSans-Regular.ttf'

    font_godot = ImageFont.truetype(font_path_bold, 84)
    font_engine = ImageFont.truetype(font_path_reg, 32)

    text_godot = "GODOT"
    text_engine = "Game engine"

    # Draw GODOT text outlines
    # We first render solid text to a temporary black-and-white mask, get outline, then neon-glow render it
    temp_text_img = Image.new('L', (canvas_w, 200), 0)
    tt_draw = ImageDraw.Draw(temp_text_img)
    
    box_godot = tt_draw.textbbox((0, 0), text_godot, font=font_godot)
    godot_w = box_godot[2] - box_godot[0]
    godot_x = (canvas_w - godot_w) // 2
    
    # Draw solid text to mask
    tt_draw.text((godot_x, 20), text_godot, fill=255, font=font_godot)
    
    # Extract outline of GODOT text
    godot_outline = get_outline(temp_text_img, thickness=2)
    
    # Draw GODOT as neon cyan
    draw_neon_glow(splash, godot_outline, cyan_glow, cyan_core, (0, 580))

    # Draw "Game engine" text outlines
    temp_engine_img = Image.new('L', (canvas_w, 100), 0)
    te_draw = ImageDraw.Draw(temp_engine_img)
    
    box_engine = te_draw.textbbox((0, 0), text_engine, font=font_engine)
    engine_w = box_engine[2] - box_engine[0]
    engine_x = (canvas_w - engine_w) // 2
    
    # Draw solid text to mask
    te_draw.text((engine_x, 10), text_engine, fill=255, font=font_engine)
    
    # Extract outline of "Game engine" text
    engine_outline = get_outline(temp_engine_img, thickness=1)
    
    # Draw "Game engine" as neon pink
    draw_neon_glow(splash, engine_outline, pink_glow, pink_core, (0, 720))

    # 9. Save final splash screen image
    splash.save('assets/godot_splash_logo.png', 'PNG')
    print("Successfully generated true neon splash screen in assets/godot_splash_logo.png!")

if __name__ == '__main__':
    main()
