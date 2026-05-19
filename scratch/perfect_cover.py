import os
import random
from PIL import Image, ImageDraw, ImageFilter

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_i_was_what_you_are_swapped_1779175615275.png"
    out_paths = [
        "/home/kainanteh/game-dev-jam-2026/itch_cover.png",
        "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/itch_cover.png"
    ]
    
    if not os.path.exists(src_path):
        print(f"Error: Swapped banner image not found at {src_path}")
        return

    # Load original 1024x1024 swapped banner image
    img = Image.open(src_path).convert('RGBA')
    
    # 1. Crop out the borders to get the pure illustration (978x978)
    # The borders are at indices 10-13 and 18-22, so we crop starting at 23
    inner_w, inner_h = 978, 978
    inner_img = img.crop((23, 23, 1001, 1001))
    
    # 2. Create the widescreen 1290x1024 canvas (which maintains Itch.io's 1.26:1 ratio)
    canvas_w = 1290
    canvas_h = 1024
    canvas = Image.new('RGBA', (canvas_w, canvas_h))
    draw = ImageDraw.Draw(canvas)

    # 3. Render a continuous background sky gradient across the entire 1290x1024 canvas
    # Matching the dark indigo/purple night sky of the cover image.
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

    # 4. Build an alpha blending mask to paste the center image
    # Fade width: 120 pixels
    mask = Image.new('L', (inner_w, inner_h), 255)
    mask_draw = ImageDraw.Draw(mask)
    fade_w = 120
    for y in range(inner_h):
        for x in range(fade_w):
            alpha = int((x / float(fade_w)) * 255)
            mask_draw.point((x, y), fill=alpha)
            mask_draw.point((inner_w - 1 - x, y), fill=alpha)

    # Paste the center illustration (1:1 native scale, absolutely sharp!)
    paste_x = (canvas_w - inner_w) // 2 # 156
    paste_y = (canvas_h - inner_h) // 2 # 23
    canvas.paste(inner_img, (paste_x, paste_y), mask)

    # 5. Draw organic mountain extensions on the left/right margins ON TOP of the pasted image
    # The mountain color matches the cover silhouette: (5, 4, 20, 255) -> #050414
    # Starts inside the solid area of the pasted image (x=300 on the left, x=990 on the right)
    
    # Left mountain
    left_mountain = [
        (0, 1024),
        (0, 780),
        (60, 755),
        (130, 770),
        (200, 745),
        (300, 778), # Overlaps inside center image
        (300, 1024)
    ]
    draw.polygon(left_mountain, fill=(5, 4, 20, 255))

    # Right mountain
    right_mountain = [
        (990, 1024),
        (990, 778), # Overlaps inside center image
        (1060, 745),
        (1130, 765),
        (1200, 735),
        (1290, 770),
        (1290, 1024)
    ]
    draw.polygon(right_mountain, fill=(5, 4, 20, 255))

    # 6. Scatter organic pixel stars in the left/right skies
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
        cx = random.randint(20, 280)
        cy = random.randint(20, 720)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3])
        draw_star(draw, cx, cy, col, sz)

    # Right stars
    for _ in range(25):
        cx = random.randint(1000, 1270)
        cy = random.randint(20, 720)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3])
        draw_star(draw, cx, cy, col, sz)

    # 7. Draw the new widescreen double-line pixel border
    # Purple border color: (58, 44, 80, 255)
    border_color = (58, 44, 80, 255)
    
    # Outer rectangle: x=10..13, y=10..13
    draw.rectangle([10, 10, canvas_w - 11, canvas_h - 11], outline=border_color, width=4)
    # Inner rectangle: x=18..21, y=18..21
    draw.rectangle([18, 18, canvas_w - 19, canvas_h - 19], outline=border_color, width=4)

    # 8. Resize the 1290x1024 canvas to exactly Itch.io's required 630x500
    resized_img = canvas.resize((630, 500), Image.Resampling.LANCZOS)
    
    # Save output files
    for path in out_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        resized_img.save(path, "PNG")
        print(f"Saved perfect cover image to: {path}")

if __name__ == '__main__':
    main()
