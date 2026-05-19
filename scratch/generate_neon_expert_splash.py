import os
import re
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

def get_outline_thick(mask, thickness=8):
    size = int(thickness * 2)
    if size % 2 == 0:
        size += 1
    if size < 3:
        size = 3
    dilated = mask.filter(ImageFilter.MaxFilter(size))
    eroded = mask.filter(ImageFilter.MinFilter(size))
    return ImageChops.difference(dilated, eroded)

def draw_neon_sign(canvas, tube_mask, core_mask, color, core_color, position):
    # tube_mask: thick outline mask
    # core_mask: thin core mask
    # color: neon glow color (R, G, B, A)
    # core_color: neon tube core color (R, G, B, A)
    # position: (x, y)
    
    w, h = tube_mask.size
    
    # Create colored tube layer
    tube_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    tube_img.paste(color, (0, 0), tube_mask)
    
    # Generate bloom glow layers
    glow_30 = tube_img.filter(ImageFilter.GaussianBlur(25))
    glow_15 = tube_img.filter(ImageFilter.GaussianBlur(12))
    glow_5 = tube_img.filter(ImageFilter.GaussianBlur(4))
    glow_2 = tube_img.filter(ImageFilter.GaussianBlur(1))
    
    # Composite glows with additive-like opacity (layering multiple times)
    for glow, opacity in [(glow_30, 0.4), (glow_15, 0.6), (glow_5, 1.0), (glow_2, 1.0)]:
        glow_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        glow_layer.paste(glow, position, glow)
        canvas.alpha_composite(glow_layer)
        
    # Core inner tube (bright white core)
    core_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    core_img.paste(core_color, (0, 0), core_mask)
    
    # Paste core onto canvas
    core_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    core_layer.paste(core_img, position, core_mask)
    canvas.alpha_composite(core_layer)

def main():
    # 1. Rasterize SVG to a high-res 512x512 image
    with open('icon.svg', 'r') as f:
        svg_content = f.read()

    svg_no_rect = re.sub(r'<rect[^>]*>', '', svg_content)
    os.makedirs('scratch', exist_ok=True)
    with open('scratch/icon_head_512.svg', 'w') as f:
        f.write(svg_no_rect)

    print("Rasterizing SVG to 512x512...")
    os.system('rsvg-convert -w 512 -h 512 scratch/icon_head_512.svg -o scratch/icon_head_512.png')

    # 2. Load the head and extract masks
    head_raw = Image.open('scratch/icon_head_512.png').convert('RGBA')
    h_w, h_h = head_raw.size
    raw_px = head_raw.load()

    face_mask = Image.new('L', (h_w, h_h), 0)
    eyes_mask = Image.new('L', (h_w, h_h), 0)
    
    fm_px = face_mask.load()
    em_px = eyes_mask.load()

    for y in range(h_h):
        for x in range(h_w):
            r, g, b, a = raw_px[x, y]
            if a < 30:
                continue
            
            # Map colors
            if r > 200 and g > 200 and b > 200:
                em_px[x, y] = 255
            elif r < 100 and g < 100 and b < 100:
                pass # Transparent pupil
            else:
                fm_px[x, y] = 255

    # 3. Create high-quality outline and core masks for the face and eyes/mouth
    # Face (Cyan Neon):
    # Tube: 10px thick, Core: 3px thick
    face_tube = get_outline_thick(face_mask, thickness=8)
    face_core = get_outline_thick(face_mask, thickness=2)
    
    # Eyes/Mouth (Pink Neon):
    # Tube: 6px thick, Core: 2px thick
    eyes_tube = get_outline_thick(eyes_mask, thickness=5)
    eyes_core = get_outline_thick(eyes_mask, thickness=1.5)

    # 4. Initialize the 1920x1080 canvas
    canvas_w = 1920
    canvas_h = 1080
    splash = Image.new('RGBA', (canvas_w, canvas_h), (7, 6, 10, 255))
    draw = ImageDraw.Draw(splash)

    # 5. Seed stars matching the background artwork exactly
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

    random.seed(1337)
    for _ in range(40):
        # Left side
        cx = random.randint(30, 550)
        cy = random.randint(30, 1050)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)
        
        # Right side
        cx = random.randint(1370, 1890)
        cy = random.randint(30, 1050)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)

    # 6. Render the Glowing Neon Robot Head (Centred)
    head_x = (canvas_w - h_w) // 2
    head_y = 180
    
    cyan_glow = (0, 210, 255, 255)
    cyan_core = (230, 252, 255, 255)
    
    pink_glow = (255, 0, 127, 255)
    pink_core = (255, 230, 240, 255)

    # Render Face
    draw_neon_sign(splash, face_tube, face_core, cyan_glow, cyan_core, (head_x, head_y))
    # Render Eyes & Mouth
    draw_neon_sign(splash, eyes_tube, eyes_core, pink_glow, pink_core, (head_x, head_y))

    # 7. Render Custom Retro-Futuristic Stencil/Arcade text "GODOT"
    # We draw geometric letters G-O-D-O-T onto a mask using custom lines
    text_mask = Image.new('L', (canvas_w, 200), 0)
    tm_draw = ImageDraw.Draw(text_mask)
    
    # Design coordinate lines for letters
    # Bounding Box of each letter: width = 80, height = 96
    # Width = 80, Height = 96, Spacing = 24
    # G-O-D-O-T: 5 letters. Total width = 5 * 80 + 4 * 24 = 400 + 96 = 496.
    # Start X = (1920 - 496) // 2 = 712
    start_x = 712
    start_y = 30
    
    letters = {
        'G': [
            (80, 8), (20, 8), (8, 20), (8, 76), (20, 88), (80, 88), (80, 48), (46, 48)
        ],
        'O': [
            (20, 8), (60, 8), (72, 20), (72, 76), (60, 88), (20, 88), (8, 76), (8, 20), (20, 8)
        ],
        'D': [
            (8, 8), (56, 8), (72, 24), (72, 70), (56, 88), (8, 88), (8, 8)
        ],
        'T': [
            # Drawn as two paths
            ((8, 8), (72, 8)),
            ((40, 8), (40, 88))
        ]
    }
    
    def draw_path(draw_obj, path, ox, oy, width=14):
        scaled = [(x + ox, y + oy) for x, y in path]
        draw_obj.line(scaled, fill=255, width=width, joint="curve")

    # Render "G"
    draw_path(tm_draw, letters['G'], start_x, start_y)
    
    # Render "O"
    draw_path(tm_draw, letters['O'], start_x + 104, start_y)
    
    # Render "D"
    draw_path(tm_draw, letters['D'], start_x + 208, start_y)
    
    # Render "O"
    draw_path(tm_draw, letters['O'], start_x + 312, start_y)
    
    # Render "T"
    draw_path(tm_draw, letters['T'][0], start_x + 416, start_y)
    draw_path(tm_draw, letters['T'][1], start_x + 416, start_y)

    # Get outline masks for custom text
    text_tube = get_outline_thick(text_mask, thickness=6)
    text_core = get_outline_thick(text_mask, thickness=2)
    
    # Render GODOT custom text on canvas (y = 700)
    draw_neon_sign(splash, text_tube, text_core, cyan_glow, cyan_core, (0, 710))

    # 8. Render stylized "Game engine" text
    # Let's render "Game engine" using NotoSans-Bold size 32, make outline, and render it in neon pink
    font_path_bold = '/usr/share/fonts/noto/NotoSans-Bold.ttf'
    text_engine = "Game engine"
    engine_mask = Image.new('L', (canvas_w, 100), 0)
    em_draw = ImageDraw.Draw(engine_mask)
    font_engine = ImageFont.truetype(font_path_bold, 36)
    
    box_engine = em_draw.textbbox((0, 0), text_engine, font=font_engine)
    engine_w = box_engine[2] - box_engine[0]
    engine_x = (canvas_w - engine_w) // 2
    
    em_draw.text((engine_x, 20), text_engine, fill=255, font=font_engine)
    
    engine_tube = get_outline_thick(engine_mask, thickness=4)
    engine_core = get_outline_thick(engine_mask, thickness=1)
    
    draw_neon_sign(splash, engine_tube, engine_core, pink_glow, pink_core, (0, 830))

    # 9. Save final splash screen image
    splash.save('assets/godot_splash_logo.png', 'PNG')
    print("Successfully generated expert neon splash screen in assets/godot_splash_logo.png!")

if __name__ == '__main__':
    main()
