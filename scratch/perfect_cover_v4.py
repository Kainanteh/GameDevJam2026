import os
import random
from PIL import Image, ImageDraw

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_i_was_what_you_are_swapped_1779175615275.png"
    logo_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/logo_titulo_transparent.png"
    
    out_paths = [
        "/home/kainanteh/game-dev-jam-2026/itch_cover.png",
        "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/itch_cover.png"
    ]
    
    if not os.path.exists(src_path):
        print(f"Error: Swapped banner image not found at {src_path}")
        return
    if not os.path.exists(logo_path):
        print(f"Error: Title logo transparent not found at {logo_path}")
        return

    # Load original 1024x1024 swapped banner and the transparent title logo
    img = Image.open(src_path).convert('RGBA')
    logo = Image.open(logo_path).convert('RGBA')
    
    # 1. Crop only the scene area (characters, roots, mountains) below the text (y=300 to 1024)
    # Width is 978 (excluding left/right borders)
    inner_w = 978
    inner_h = 724 # 1024 - 300
    scene_img = img.crop((23, 300, 1001, 1024))
    
    # 2. Create the widescreen 1290x1024 canvas (aspect ratio 1.26:1)
    canvas_w = 1290
    canvas_h = 1024
    canvas = Image.new('RGBA', (canvas_w, canvas_h))
    draw = ImageDraw.Draw(canvas)

    # 3. Render a continuous background sky gradient across the entire 1290x1024 canvas
    # Match the deep starry night sky colors of the cover banner.
    for y in range(0, canvas_h):
        t = y / float(canvas_h)
        if t < 0.75:
            t_sky = t / 0.75
            r = int(5 + (40 - 5) * t_sky)
            g = int(3 + (15 - 3) * t_sky)
            b = int(18 + (55 - 18) * t_sky)
        else:
            r, g, b = 40, 15, 55
        draw.line([(0, y), (canvas_w, y)], fill=(r, g, b, 255))

    # 4. Draw organic mountain extensions on the canvas FIRST (under the pasted image)
    # The mountain color is: (5, 4, 20, 255)
    # Height starts at y=755 (which is the mountain line at the edges)
    
    # Left mountain
    left_mountain = [
        (0, 1024),
        (0, 780),
        (60, 755),
        (130, 770),
        (200, 745),
        (320, 765),
        (320, 1024)
    ]
    draw.polygon(left_mountain, fill=(5, 4, 20, 255))

    # Right mountain
    right_mountain = [
        (960, 1024),
        (960, 765),
        (1060, 745),
        (1130, 765),
        (1200, 735),
        (1290, 770),
        (1290, 1024)
    ]
    draw.polygon(right_mountain, fill=(5, 4, 20, 255))

    # 5. Scatter organic pixel stars in the left/right skies (excluding the title text area)
    random.seed(333)
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

    # Left stars
    for _ in range(25):
        cx = random.randint(20, 260)
        cy = random.randint(20, 720)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3])
        draw_star(draw, cx, cy, col, sz)

    # Right stars
    for _ in range(25):
        cx = random.randint(1030, 1270)
        cy = random.randint(20, 720)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3])
        draw_star(draw, cx, cy, col, sz)

    # 6. Build an alpha blending mask to paste the characters/scene
    # Fade width: 140 pixels. Fade is full-height of the scene (y=0 to 724)
    mask = Image.new('L', (inner_w, inner_h), 255)
    mask_draw = ImageDraw.Draw(mask)
    fade_w = 140
    for y in range(inner_h):
        for x in range(fade_w):
            alpha = int((x / float(fade_w)) * 255)
            mask_draw.point((x, y), fill=alpha)
            mask_draw.point((inner_w - 1 - x, y), fill=alpha)

    # 7. Paste the scene at x=156, y=300 (bottom section)
    # The top 300 pixels remain clean gradient background sky
    paste_x = (canvas_w - inner_w) // 2 # 156
    canvas.paste(scene_img, (paste_x, 300), mask)

    # 8. Scale and paste the transparent title logo in the top clean sky area
    # Original logo is 924x200. Let's make it bigger!
    # Let's scale it up to 1020 width (which is about 80% of canvas width)
    logo_w = 1020
    logo_h = int(logo.height * (logo_w / float(logo.width))) # 1020 * (200 / 924) = 220
    logo_resized = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    
    # Paste logo centered horizontally at y=45
    logo_x = (canvas_w - logo_w) // 2 # 135
    canvas.paste(logo_resized, (logo_x, 45), logo_resized)

    # 9. Draw the new widescreen double-line pixel border
    # Border color matches the original: (58, 44, 80, 255)
    border_color = (58, 44, 80, 255)
    
    # Outer rectangle: x=10..13, y=10..13, width=4
    draw.rectangle([10, 10, canvas_w - 11, canvas_h - 11], outline=border_color, width=4)
    # Inner rectangle: x=18..21, y=18..21, width=4
    draw.rectangle([18, 18, canvas_w - 19, canvas_h - 19], outline=border_color, width=4)

    # 10. Resize the 1290x1024 canvas to exactly Itch.io's required 630x500
    resized_img = canvas.resize((630, 500), Image.Resampling.LANCZOS)
    
    # Save output files
    for path in out_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        resized_img.save(path, "PNG")
        print(f"Saved perfect cover image to: {path}")

if __name__ == '__main__':
    main()
