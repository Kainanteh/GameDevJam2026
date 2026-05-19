import os
import random
from PIL import Image, ImageDraw, ImageFilter

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/godot_splash_no_border_1779203949567.png"
    
    if not os.path.exists(src_path):
        print(f"Error: Widescreen AI image not found at {src_path}")
        return

    # Load original borderless AI image (1024x1024)
    ai_img = Image.open(src_path).convert('RGBA')
    
    # 2. Create the final 1920x1080 canvas
    canvas_w = 1920
    canvas_h = 1080
    splash = Image.new('RGBA', (canvas_w, canvas_h))
    draw = ImageDraw.Draw(splash)

    # 3. Render a continuous background sky gradient across the entire 1920x1080 canvas
    # This matches the deep purple/indigo space gradient of the AI image.
    for y in range(0, canvas_h):
        t = y / float(canvas_h)
        if t < 0.85:
            t_sky = t / 0.85
            r = int(12 + (60 - 12) * t_sky)
            g = int(5 + (10 - 5) * t_sky)
            b = int(25 + (90 - 25) * t_sky)
        else:
            r, g, b = 60, 10, 90
        draw.line([(0, y), (canvas_w, y)], fill=(r, g, b, 255))

    # 4. Build an alpha blending mask to paste the center image
    # The mask has 1.0 (255) opacity in the middle, and fades to 0 on the left/right edges.
    # We fade across the entire height of the image to blend both sky and mountain transitions smoothly.
    mask = Image.new('L', (1024, 1024), 255)
    mask_draw = ImageDraw.Draw(mask)
    
    fade_w = 140
    for y in range(1024):
        for x in range(fade_w):
            alpha = int((x / float(fade_w)) * 255)
            mask_draw.point((x, y), fill=alpha)
            mask_draw.point((1024 - 1 - x, y), fill=alpha)

    # Paste the center illustration (1:1 native scale, absolutely sharp!) using the blending mask
    paste_x = (canvas_w - 1024) // 2 # 448
    paste_y = (canvas_h - 1024) // 2 # 28
    splash.paste(ai_img, (paste_x, paste_y), mask)

    # 5. Draw organic multi-layered mountains on the left/right margins ON TOP of the pasted image
    # We start drawing INSIDE the center image (x=600 on the left, x=1320 on the right) where it is fully opaque.
    # This completely covers the faded boundaries and makes the mountains 100% solid and continuous!
    # Mountain color matches the AI silhouette: (25, 5, 58, 255)
    # Highlight color: (110, 25, 150, 255)

    def draw_mountain_layer(draw_obj, points, color, highlight_color):
        # Draw the main filled polygon
        draw_obj.polygon(points, fill=color)
        # Draw the top ridge highlight (excluding the vertical boundary lines)
        ridge = points[1:-2]
        for i in range(len(ridge) - 1):
            draw_obj.line([ridge[i], ridge[i+1]], fill=highlight_color, width=2)

    # Left mountain (x = 0 to 600)
    # Starts at x=600, y=930 inside the solid area of the center image
    left_mountain = [
        (0, 1080),
        (0, 930),
        (80, 910),
        (160, 935),
        (260, 890),
        (350, 915),
        (420, 900),
        (500, 925),
        (600, 932), # Starts deep inside the center image's mountain
        (600, 1080)
    ]
    draw_mountain_layer(draw, left_mountain, (25, 5, 58, 255), (110, 25, 150, 255))

    # Right mountain (x = 1320 to 1920)
    # Starts at x=1320, y=900 inside the solid area of the center image
    right_mountain = [
        (1320, 1080),
        (1320, 900), # Starts deep inside the center image's mountain
        (1400, 875),
        (1500, 850),
        (1580, 880),
        (1680, 830),
        (1760, 860),
        (1840, 845),
        (1920, 875),
        (1920, 1080)
    ]
    draw_mountain_layer(draw, right_mountain, (25, 5, 58, 255), (110, 25, 150, 255))

    # 6. Scatter organic pixel stars in the left/right skies
    random.seed(999)
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

    # Spawn stars in the left sky margin
    for _ in range(35):
        cx = random.randint(30, 420)
        cy = random.randint(30, 850)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)

    # Spawn stars in the right sky margin
    for _ in range(35):
        cx = random.randint(1500, 1890)
        cy = random.randint(30, 800)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)

    # 7. Draw the new double-line pixel border around the screen
    border_color = (27, 23, 37, 255)
    draw.rectangle([12, 12, 1908, 1068], outline=border_color, width=2)
    draw.rectangle([20, 20, 1900, 1060], outline=border_color, width=2)
    
    corners = [
        [15, 15, 17, 17],
        [1903, 15, 1905, 17],
        [15, 1063, 17, 1065],
        [1903, 1063, 1905, 1065]
    ]
    for c in corners:
        draw.rectangle(c, fill=border_color)

    # Save to output assets path
    os.makedirs('assets', exist_ok=True)
    splash.save('assets/godot_splash_logo.png', 'PNG')
    print("Successfully generated seamless widescreen splash screen v4!")

if __name__ == '__main__':
    main()
