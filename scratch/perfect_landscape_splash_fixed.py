import os
import random
from PIL import Image, ImageDraw, ImageFilter

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/godot_splash_native_widescreen_1779203734541.png"
    
    if not os.path.exists(src_path):
        print(f"Error: Widescreen AI image not found at {src_path}")
        return

    # Load original AI image (1024x1024)
    ai_img = Image.open(src_path).convert('RGBA')
    
    # 1. Crop out the border to get the pure illustration (974x974)
    inner_w, inner_h = 974, 974
    inner_img = ai_img.crop((25, 25, 999, 999))
    
    # 2. Create the final 1920x1080 canvas
    canvas_w = 1920
    canvas_h = 1080
    splash = Image.new('RGBA', (canvas_w, canvas_h))
    draw = ImageDraw.Draw(splash)

    # 3. Render a continuous background sky gradient across the entire 1920x1080 canvas
    # Top color: (8, 6, 12, 255), Mid color: (16, 10, 24, 255), Bottom sky color: (24, 15, 34, 255)
    for y in range(0, canvas_h):
        t = y / float(canvas_h)
        if t < 0.9:
            t_sky = t / 0.9
            r = int(8 + (24 - 8) * t_sky)
            g = int(6 + (15 - 6) * t_sky)
            b = int(12 + (34 - 12) * t_sky)
        else:
            r, g, b = 24, 15, 34
        draw.line([(0, y), (canvas_w, y)], fill=(r, g, b, 255))

    # 4. Build an alpha blending mask to paste the center image
    # The mask has 1.0 (255) opacity in the middle, and fades to 0 on the left/right edges for the sky.
    # For the mountain area at the bottom (y > 900), we do NOT fade (alpha is solid 255) to avoid semi-transparent mountain seams.
    mask = Image.new('L', (inner_w, inner_h), 255)
    mask_draw = ImageDraw.Draw(mask)
    
    fade_w = 120
    for y in range(inner_h):
        if y < 900:
            # Sky area: fade left and right edges
            for x in range(fade_w):
                alpha = int((x / float(fade_w)) * 255)
                mask_draw.point((x, y), fill=alpha)
                mask_draw.point((inner_w - 1 - x, y), fill=alpha)
        else:
            # Mountain area: solid opacity to keep the mountain opaque
            for x in range(inner_w):
                mask_draw.point((x, y), fill=255)

    # Paste the center illustration (1:1 native scale, absolutely sharp!) using the blending mask
    paste_x = (canvas_w - inner_w) // 2 # 473
    paste_y = (canvas_h - inner_h) // 2 # 53
    splash.paste(inner_img, (paste_x, paste_y), mask)

    # 5. Draw organic multi-layered mountains on the left/right margins ON TOP of the pasted image
    # This overlaps the boundaries and prevents any cut-off seams.
    # Mountain colors:
    # Far background: (36, 24, 60, 255), Highlight: (60, 40, 85, 255)
    # Midground: (27, 18, 46, 255), Highlight: (45, 30, 65, 255)
    # Foreground: (16, 11, 28, 255), Highlight: (30, 20, 45, 255)

    def draw_mountain_layer(draw_obj, points, color, highlight_color):
        # Draw the main filled polygon
        draw_obj.polygon(points, fill=color)
        # Draw the top ridge highlight (excluding the bottom and side boundary lines)
        ridge = points[1:-2]
        for i in range(len(ridge) - 1):
            draw_obj.line([ridge[i], ridge[i+1]], fill=highlight_color, width=2)

    # Far background mountains
    left_far = [
        (0, 1080),
        (0, 970),
        (80, 990),
        (180, 960),
        (280, 990),
        (380, 980),
        (450, 1020),
        (485, 1043), # Connects to center mountain peak
        (485, 1080)
    ]
    draw_mountain_layer(draw, left_far, (36, 24, 60, 255), (60, 40, 85, 255))

    right_far = [
        (1435, 1080),
        (1435, 1043),
        (1480, 1010),
        (1560, 980),
        (1660, 950),
        (1760, 990),
        (1860, 970),
        (1920, 980),
        (1920, 1080)
    ]
    draw_mountain_layer(draw, right_far, (36, 24, 60, 255), (60, 40, 85, 255))

    # Midground mountains
    left_mid = [
        (0, 1080),
        (0, 1000),
        (60, 1015),
        (160, 995),
        (260, 1020),
        (360, 1010),
        (440, 1035),
        (485, 1053),
        (485, 1080)
    ]
    draw_mountain_layer(draw, left_mid, (27, 18, 46, 255), (45, 30, 65, 255))

    right_mid = [
        (1435, 1080),
        (1435, 1053),
        (1490, 1030),
        (1580, 1005),
        (1680, 980),
        (1780, 1010),
        (1880, 995),
        (1920, 1005),
        (1920, 1080)
    ]
    draw_mountain_layer(draw, right_mid, (27, 18, 46, 255), (45, 30, 65, 255))

    # Foreground mountains
    left_fg = [
        (0, 1080),
        (0, 1035),
        (140, 1020),
        (240, 1040),
        (340, 1030),
        (430, 1050),
        (485, 1063),
        (485, 1080)
    ]
    draw_mountain_layer(draw, left_fg, (16, 11, 28, 255), (30, 20, 45, 255))

    right_fg = [
        (1435, 1080),
        (1435, 1063),
        (1500, 1045),
        (1600, 1025),
        (1700, 1035),
        (1800, 1015),
        (1920, 1025),
        (1920, 1080)
    ]
    draw_mountain_layer(draw, right_fg, (16, 11, 28, 255), (30, 20, 45, 255))

    # 6. Scatter organic pixel stars in the left/right skies
    random.seed(888)
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
        cx = random.randint(30, 440)
        cy = random.randint(30, 900)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)

    # Spawn stars in the right sky margin
    for _ in range(35):
        cx = random.randint(1480, 1890)
        cy = random.randint(30, 900)
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
    print("Successfully generated seamless landscape splash screen with perfect mountain heights!")

if __name__ == '__main__':
    main()
