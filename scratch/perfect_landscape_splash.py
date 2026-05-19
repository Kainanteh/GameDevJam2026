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
    # The border is roughly 25px wide
    inner_w, inner_h = 974, 974
    inner_img = ai_img.crop((25, 25, 999, 999))
    
    # 2. Create the final 1920x1080 canvas
    canvas_w = 1920
    canvas_h = 1080
    splash = Image.new('RGBA', (canvas_w, canvas_h))
    draw = ImageDraw.Draw(splash)

    # 3. Render a continuous background sky gradient across the entire 1920x1080 canvas
    # Top color: (8, 6, 12, 255), Mid color: (16, 10, 24, 255), Bottom sky color (above mountains): (24, 15, 34, 255)
    # We render this gradient from y=0 to y=850 (where the sky meets the mountains)
    for y in range(0, canvas_h):
        t = y / float(canvas_h)
        if t < 0.8:
            # Sky gradient
            t_sky = t / 0.8
            r = int(8 + (24 - 8) * t_sky)
            g = int(6 + (15 - 6) * t_sky)
            b = int(12 + (34 - 12) * t_sky)
        else:
            # Bottom mountain base fill
            r, g, b = 24, 15, 34
        draw.line([(0, y), (canvas_w, y)], fill=(r, g, b, 255))

    # 4. Draw a beautiful, organic multi-layered mountain range on the left and right margins
    # The mountain heights connect to the edges of the center cropped image:
    # Left edge (x=473): height is y=880 (relative to canvas, which is 53 + 827)
    # Right edge (x=1447): height is y=860 (relative to canvas, which is 53 + 807)
    
    # Colors sampled from AI mountains:
    # Far background mountains: (36, 24, 60, 255) -> #24183c
    # Midground mountains: (27, 18, 46, 255) -> #1b122e
    # Foreground mountains: (16, 11, 28, 255) -> #100b1c

    # Helper function to generate a jagged mountain path
    def make_mountain_path(x_start, x_end, y_start, y_end, seed_val, min_h, max_h):
        random.seed(seed_val)
        points = [(x_start, 1080)]
        curr_x = x_start
        curr_y = y_start
        points.append((curr_x, curr_y))
        
        step = 16
        while curr_x < x_end - step:
            curr_x += step
            # Generate organic jagged steps
            dy = random.randint(-12, 12)
            curr_y = max(min_h, min(max_h, curr_y + dy))
            points.append((curr_x, curr_y))
            
        points.append((x_end, y_end))
        points.append((x_end, 1080))
        return points

    # Left Far background mountains (x = 0 to 473)
    left_far_path = make_mountain_path(0, 473, 830, 830, 101, 800, 860)
    draw.polygon(left_far_path, fill=(36, 24, 60, 255))
    
    # Right Far background mountains (x = 1447 to 1920)
    right_far_path = make_mountain_path(1447, 1920, 810, 820, 102, 790, 850)
    draw.polygon(right_far_path, fill=(36, 24, 60, 255))

    # Left Midground mountains (x = 0 to 473)
    left_mid_path = make_mountain_path(0, 473, 870, 875, 201, 840, 900)
    draw.polygon(left_mid_path, fill=(27, 18, 46, 255))
    
    # Right Midground mountains (x = 1447 to 1920)
    right_mid_path = make_mountain_path(1447, 1920, 865, 860, 202, 830, 890)
    draw.polygon(right_mid_path, fill=(27, 18, 46, 255))

    # Left Foreground mountains (x = 0 to 473)
    left_fg_path = make_mountain_path(0, 473, 910, 915, 301, 880, 950)
    draw.polygon(left_fg_path, fill=(16, 11, 28, 255))
    
    # Right Foreground mountains (x = 1447 to 1920)
    right_fg_path = make_mountain_path(1447, 1920, 905, 910, 302, 870, 940)
    draw.polygon(right_fg_path, fill=(16, 11, 28, 255))

    # 5. Build an alpha blending mask to paste the center image without seams or bands
    # The mask is 974x974. It has 1.0 (255) opacity in the middle, and fades to 0 (gradient) on the left/right edges.
    # We fade over a 120-pixel wide border at the left and right sides of the cropped image.
    mask = Image.new('L', (inner_w, inner_h), 255)
    mask_draw = ImageDraw.Draw(mask)
    
    # Left edge gradient fade
    for x in range(120):
        alpha = int((x / 120.0) * 255)
        mask_draw.line([(x, 0), (x, inner_h)], fill=alpha)
        
    # Right edge gradient fade
    for x in range(120):
        alpha = int(((120 - x) / 120.0) * 255)
        mask_draw.line([(inner_w - 120 + x, 0), (inner_w - 120 + x, inner_h)], fill=alpha)

    # Paste the center illustration (1:1 native scale, absolutely sharp!) using the blending mask
    paste_x = (canvas_w - inner_w) // 2 # 473
    paste_y = (canvas_h - inner_h) // 2 # 53
    splash.paste(inner_img, (paste_x, paste_y), mask)

    # 6. Scatter beautiful, high-quality organic pixel-art stars in the left/right skies
    # We use a variety of sizes and neon glow colors to match the center sky
    random.seed(777)
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
    for _ in range(40):
        cx = random.randint(30, 420)
        cy = random.randint(30, 780)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)

    # Spawn stars in the right sky margin
    for _ in range(40):
        cx = random.randint(1500, 1890)
        cy = random.randint(30, 780)
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
    print("Successfully generated seamless, native-sharp hybrid splash screen with no scaling blur and no bands!")

if __name__ == '__main__':
    main()
