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
    # We match the deep purple/indigo space gradient of the new AI image.
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
    # The mask has 1.0 (255) opacity in the middle, and fades to 0 on the left/right edges for the sky.
    # For the mountain area at the bottom (y > 800), we do NOT fade (alpha is solid 255) to avoid semi-transparent mountain seams.
    mask = Image.new('L', (1024, 1024), 255)
    mask_draw = ImageDraw.Draw(mask)
    
    fade_w = 140
    for y in range(1024):
        if y < 800:
            # Sky area: fade left and right edges
            for x in range(fade_w):
                alpha = int((x / float(fade_w)) * 255)
                mask_draw.point((x, y), fill=alpha)
                mask_draw.point((1024 - 1 - x, y), fill=alpha)
        else:
            # Mountain area: solid opacity to keep the mountain opaque
            for x in range(1024):
                mask_draw.point((x, y), fill=255)

    # Paste the center illustration (1:1 native scale, absolutely sharp!) using the blending mask
    paste_x = (canvas_w - 1024) // 2 # 448
    paste_y = (canvas_h - 1024) // 2 # 28
    splash.paste(ai_img, (paste_x, paste_y), mask)

    # 5. Draw organic multi-layered mountains on the left/right margins ON TOP of the pasted image
    # This overlaps the boundaries and prevents any cut-off seams.
    # Color matches the AI mountain silhouette: (25, 5, 58, 255) -> #19053a
    # Highlight color: (110, 25, 150, 255) -> purple ridge highlight

    def draw_mountain_layer(draw_obj, points, color, highlight_color):
        # Draw the main filled polygon
        draw_obj.polygon(points, fill=color)
        # Draw the top ridge highlight
        ridge = points[1:-2]
        for i in range(len(ridge) - 1):
            draw_obj.line([ridge[i], ridge[i+1]], fill=highlight_color, width=2)

    # Left mountain (x = 0 to 465)
    # Starts at x=465, y=943 (connecting perfectly to the mountain at the left edge of the pasted image)
    left_mountain = [
        (0, 1080),
        (0, 930),
        (80, 910),
        (160, 935),
        (260, 890),
        (350, 915),
        (420, 900),
        (465, 943), # Seamless connection point
        (465, 1080)
    ]
    draw_mountain_layer(draw, left_mountain, (25, 5, 58, 255), (110, 25, 150, 255))

    # Right mountain (x = 1455 to 1920)
    # Starts at x=1455, y=868 (connecting perfectly to the mountain at the right edge of the pasted image)
    right_mountain = [
        (1455, 1080),
        (1455, 868), # Seamless connection point
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
    print("Successfully generated perfect seamless widescreen splash screen with new borderless AI image!")

if __name__ == '__main__':
    main()
