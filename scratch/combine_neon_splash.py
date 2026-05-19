import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

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
    w, h = tube_mask.size
    
    # Glow layer
    tube_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    tube_img.paste(color, (0, 0), tube_mask)
    
    glow_30 = tube_img.filter(ImageFilter.GaussianBlur(24))
    glow_12 = tube_img.filter(ImageFilter.GaussianBlur(10))
    glow_4 = tube_img.filter(ImageFilter.GaussianBlur(3))
    glow_1 = tube_img.filter(ImageFilter.GaussianBlur(1))
    
    for glow, opacity in [(glow_30, 0.4), (glow_12, 0.6), (glow_4, 1.0), (glow_1, 1.0)]:
        glow_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        glow_layer.paste(glow, position, glow)
        canvas.alpha_composite(glow_layer)
        
    # Core layer
    core_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    core_img.paste(core_color, (0, 0), core_mask)
    
    core_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    core_layer.paste(core_img, position, core_mask)
    canvas.alpha_composite(core_layer)

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/godot_splash_widescreen_1779203197995.png"
    
    if not os.path.exists(src_path):
        print(f"Error: Widescreen AI image not found at {src_path}")
        return

    # Load widescreen AI image
    ai_img = Image.open(src_path).convert('RGBA')
    
    # Crop out border
    inner_img = ai_img.crop((25, 25, 999, 999)) # 974x974
    bg_1080 = inner_img.resize((1080, 1080), Image.Resampling.LANCZOS)
    
    # 1. Clean the center of the 1080x1080 background to remove the blurry robot and text
    # We paint a smooth vertical gradient matching the sky in the center
    # Center bounds: x = 280 to 800
    bg_draw = ImageDraw.Draw(bg_1080)
    
    # Paint sky gradient in the center
    # Top color: (8, 6, 12, 255), Bottom sky color (above mountains): (24, 15, 34, 255)
    for y in range(0, 800):
        t = y / 800.0
        r = int(8 + (24 - 8) * t)
        g = int(6 + (15 - 6) * t)
        b = int(12 + (34 - 12) * t)
        bg_draw.line([(280, y), (800, y)], fill=(r, g, b, 255))
        
    # Paint extended mountains over the center (y = 800 to 1080)
    # The mountain ridge connects at x=280 (y=830) and x=800 (y=820)
    # Background mountain layer
    bg_mountain = [
        (280, 1080),
        (280, 830),
        (380, 810),
        (480, 840),
        (580, 790),
        (680, 825),
        (800, 820),
        (800, 1080)
    ]
    bg_draw.polygon(bg_mountain, fill=(19, 15, 28, 255))
    
    # Foreground mountain layer
    fg_mountain = [
        (280, 1080),
        (280, 870),
        (350, 890),
        (450, 860),
        (550, 880),
        (650, 850),
        (750, 865),
        (800, 855),
        (800, 1080)
    ]
    bg_draw.polygon(fg_mountain, fill=(11, 9, 18, 255))

    # Apply soft blur to the painted gradients and mountains in the center to match AI texture
    center_patch = bg_1080.crop((270, 0, 810, 1080))
    center_patch_blurred = center_patch.filter(ImageFilter.GaussianBlur(1))
    bg_1080.paste(center_patch_blurred, (270, 0))

    # 2. Expand to 1920x1080 canvas
    canvas_w = 1920
    canvas_h = 1080
    splash = Image.new('RGBA', (canvas_w, canvas_h))
    
    # Paste cleaned background in the center
    paste_x = 420
    splash.paste(bg_1080, (paste_x, 0))
    
    # Fill left margin (x = 0 to 420) using background slice without the robot (e.g. x = 420 to 730 on the canvas)
    # This range has NO robot, so mirroring it produces a clean background with no ghost robots!
    left_slice = splash.crop((paste_x, 0, paste_x + 310, canvas_h)) # width 310
    left_flipped = left_slice.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    splash.paste(left_flipped, (paste_x - 310, 0)) # Paste from x = 110 to 420
    
    # Fill the remaining x = 0 to 110
    left_edge_slice = left_flipped.crop((0, 0, 110, canvas_h))
    left_edge_flipped = left_edge_slice.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    splash.paste(left_edge_flipped, (0, 0))

    # Fill right margin (x = 1500 to 1920) using background slice without the robot (e.g. x = 1190 to 1500 on the canvas)
    right_slice = splash.crop((1500 - 310, 0, 1500, canvas_h)) # width 310
    right_flipped = right_slice.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    splash.paste(right_flipped, (1500, 0)) # Paste from x = 1500 to 1810
    
    # Fill the remaining x = 1810 to 1920
    right_edge_slice = right_flipped.crop((200, 0, 310, canvas_h)) # width 110
    right_edge_flipped = right_edge_slice.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    splash.paste(right_edge_flipped, (1810, 0))

    # 3. Render Razor-Sharp Vector Robot Head (Cyan and Pink Neon)
    # Generate high-res 512x512 PNG of the head
    print("Rasterizing SVG robot outlines...")
    os.system('rsvg-convert -w 512 -h 512 scratch/icon_head_512.svg -o scratch/icon_head_512.png')
    
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
            if r > 200 and g > 200 and b > 200:
                em_px[x, y] = 255
            elif r < 100 and g < 100 and b < 100:
                pass
            else:
                fm_px[x, y] = 255

    # Face outlines (Cyan)
    face_tube = get_outline_thick(face_mask, thickness=8)
    face_core = get_outline_thick(face_mask, thickness=2)
    
    # Eyes outlines (Pink)
    eyes_tube = get_outline_thick(eyes_mask, thickness=5)
    eyes_core = get_outline_thick(eyes_mask, thickness=1.5)
    
    # Paste neon robot head in center
    head_x = (canvas_w - h_w) // 2
    head_y = 150 # Shifted slightly up to match layout
    
    cyan_glow = (0, 210, 255, 255)
    cyan_core = (230, 252, 255, 255)
    pink_glow = (255, 0, 127, 255)
    pink_core = (255, 230, 240, 255)

    draw_neon_sign(splash, face_tube, face_core, cyan_glow, cyan_core, (head_x, head_y))
    draw_neon_sign(splash, eyes_tube, eyes_core, pink_glow, pink_core, (head_x, head_y))

    # 4. Render Razor-Sharp Custom Text "GODOT" with Gradient Fill
    # We draw geometric letters G-O-D-O-T onto a mask using custom lines
    text_mask = Image.new('L', (canvas_w, 200), 0)
    tm_draw = ImageDraw.Draw(text_mask)
    
    start_x = 712
    start_y = 30
    
    letters = {
        'G': [(80, 8), (20, 8), (8, 20), (8, 76), (20, 88), (80, 88), (80, 48), (46, 48)],
        'O': [(20, 8), (60, 8), (72, 20), (72, 76), (60, 88), (20, 88), (8, 76), (8, 20), (20, 8)],
        'D': [(8, 8), (56, 8), (72, 24), (72, 70), (56, 88), (8, 88), (8, 8)],
        'T': [((8, 8), (72, 8)), ((40, 8), (40, 88))]
    }
    
    def draw_path(draw_obj, path, ox, oy, width=14):
        scaled = [(x + ox, y + oy) for x, y in path]
        draw_obj.line(scaled, fill=255, width=width, joint="curve")

    draw_path(tm_draw, letters['G'], start_x, start_y)
    draw_path(tm_draw, letters['O'], start_x + 104, start_y)
    draw_path(tm_draw, letters['D'], start_x + 208, start_y)
    draw_path(tm_draw, letters['O'], start_x + 312, start_y)
    draw_path(tm_draw, letters['T'][0], start_x + 416, start_y)
    draw_path(tm_draw, letters['T'][1], start_x + 416, start_y)

    # Get outline masks
    text_tube = get_outline_thick(text_mask, thickness=6)
    text_core = get_outline_thick(text_mask, thickness=2)
    
    # We render the text with a gorgeous gradient (Cyan to Pink) just like the AI image!
    # Create gradient image
    grad_img = Image.new('RGBA', (canvas_w, 200))
    g_draw = ImageDraw.Draw(grad_img)
    for y in range(200):
        t = y / 200.0
        r = int(0 + (255 - 0) * t)
        g = int(210 + (0 - 210) * t)
        b = int(255 + (127 - 255) * t)
        g_draw.line([(0, y), (canvas_w, y)], fill=(r, g, b, 255))
        
    # Apply gradient to tube glow
    tube_grad = Image.new('RGBA', (canvas_w, 200))
    tube_grad.paste(grad_img, (0, 0), text_tube)
    
    glow_30_t = tube_grad.filter(ImageFilter.GaussianBlur(24))
    glow_12_t = tube_grad.filter(ImageFilter.GaussianBlur(10))
    glow_4_t = tube_grad.filter(ImageFilter.GaussianBlur(3))
    
    for glow, opacity in [(glow_30_t, 0.4), (glow_12_t, 0.6), (glow_4_t, 1.0)]:
        glow_layer = Image.new('RGBA', splash.size, (0, 0, 0, 0))
        glow_layer.paste(glow, (0, 680), glow)
        splash.alpha_composite(glow_layer)
        
    # Paste core
    core_img = Image.new('RGBA', (canvas_w, 200), (0, 0, 0, 0))
    core_img.paste(cyan_core, (0, 0), text_core)
    core_layer = Image.new('RGBA', splash.size, (0, 0, 0, 0))
    core_layer.paste(core_img, (0, 680), text_core)
    splash.alpha_composite(core_layer)

    # 5. Render stylized "Game engine" text (Pink Neon)
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
    
    draw_neon_sign(splash, engine_tube, engine_core, pink_glow, pink_core, (0, 800))

    # 6. Draw elegant double-line border
    border_color = (27, 23, 37, 255)
    draw_border = ImageDraw.Draw(splash)
    draw_border.rectangle([12, 12, 1908, 1068], outline=border_color, width=2)
    draw_border.rectangle([20, 20, 1900, 1060], outline=border_color, width=2)
    
    corners = [
        [15, 15, 17, 17],
        [1903, 15, 1905, 17],
        [15, 1063, 17, 1065],
        [1903, 1063, 1905, 1065]
    ]
    for c in corners:
        draw_border.rectangle(c, fill=border_color)

    # Save to output assets path
    os.makedirs('assets', exist_ok=True)
    splash.save('assets/godot_splash_logo.png', 'PNG')
    print("Successfully generated perfect vector hybrid neon splash screen!")

if __name__ == '__main__':
    main()
