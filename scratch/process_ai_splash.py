import os
import random
from PIL import Image, ImageDraw, ImageFilter

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/godot_splash_logo_ai_1779203086072.png"
    
    if not os.path.exists(src_path):
        print(f"Error: AI generated image not found at {src_path}")
        return

    # Load AI image
    ai_img = Image.open(src_path).convert('RGBA')
    
    # 1. Crop out the original border (which is square)
    # The border is roughly 24 pixels thick from edges
    crop_box = (25, 25, 999, 999) # 974x974 area
    inner_img = ai_img.crop(crop_box)
    inner_w, inner_h = inner_img.size # 974, 974

    # 2. Create the 1920x1080 canvas
    canvas_w = 1920
    canvas_h = 1080
    
    # Base background color matching the abyssal black of the game
    bg_color = (7, 6, 10, 255)
    splash = Image.new('RGBA', (canvas_w, canvas_h), bg_color)
    draw = ImageDraw.Draw(splash)

    # 3. Paste the cropped logo/illustration in the center
    paste_x = (canvas_w - inner_w) // 2 # (1920 - 974) // 2 = 473
    paste_y = (canvas_h - inner_h) // 2 # (1080 - 974) // 2 = 53
    
    # Before pasting, let's create a soft purple glow on the sides to blend seamlessly
    # Draw a gradient or nebula glow
    nebula = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    n_draw = ImageDraw.Draw(nebula)
    # Drawing large soft radial purple glows on the bottom left and bottom right
    # to blend with the mountains and purple sky in the center
    def draw_radial_glow(img_draw, cx, cy, radius, color):
        for r in range(radius, 0, -8):
            alpha = int((1.0 - (r / radius) ** 1.5) * color[3] * 0.15)
            if alpha > 0:
                img_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(color[0], color[1], color[2], alpha))

    draw_radial_glow(n_draw, 960, 800, 600, (60, 20, 90, 100)) # Center bottom glow
    draw_radial_glow(n_draw, 300, 900, 400, (30, 10, 50, 80))  # Left bottom glow
    draw_radial_glow(n_draw, 1620, 900, 400, (30, 10, 50, 80)) # Right bottom glow
    
    # Blur the nebula to make it extremely smooth
    nebula = nebula.filter(ImageFilter.GaussianBlur(40))
    splash.alpha_composite(nebula)

    # Now paste the inner image
    splash.alpha_composite(inner_img, (paste_x, paste_y))

    # 4. Draw extended mountains on the left and right margins to blend with the center illustration
    # Let's read the mountain heights from the left and right edges of the cropped image
    # For a clean transition, we define the mountain ridge coordinates.
    # At paste_x = 473, the mountain height in the cropped image is around y = 840 (relative to canvas, which is 53 + 787).
    # At paste_x + inner_w = 1447, the mountain height is around y = 850 (relative to canvas, which is 53 + 797).
    
    # Left mountain silhouette (from x=0 to x=473)
    left_mountain = [
        (0, 1080),
        (0, 880),
        (80, 850),
        (160, 870),
        (250, 820),
        (330, 840),
        (400, 810),
        (473, 840), # Connects to center illustration
        (473, 1080)
    ]
    # Draw dark purple mountain background
    draw.polygon(left_mountain, fill=(19, 15, 28, 255))
    
    # Right mountain silhouette (from x=1447 to x=1920)
    right_mountain = [
        (1447, 1080),
        (1447, 850), # Connects to center illustration
        (1520, 820),
        (1600, 840),
        (1680, 800),
        (1760, 830),
        (1840, 810),
        (1920, 840),
        (1920, 1080)
    ]
    draw.polygon(right_mountain, fill=(19, 15, 28, 255))

    # Draw foreground darker mountain layer for depth
    left_fg_mountain = [
        (0, 1080),
        (0, 920),
        (120, 890),
        (220, 910),
        (310, 870),
        (420, 890),
        (473, 875),
        (473, 1080)
    ]
    draw.polygon(left_fg_mountain, fill=(11, 9, 18, 255))

    right_fg_mountain = [
        (1447, 1080),
        (1447, 885),
        (1550, 860),
        (1650, 890),
        (1750, 850),
        (1850, 880),
        (1920, 870),
        (1920, 1080)
    ]
    draw.polygon(right_fg_mountain, fill=(11, 9, 18, 255))

    # 5. Scatter retro pixel stars in the left and right skies
    random.seed(42)
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

    # Spawn 30 stars in the left sky area
    for _ in range(30):
        cx = random.randint(30, 440)
        cy = random.randint(30, 750)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)

    # Spawn 30 stars in the right sky area
    for _ in range(30):
        cx = random.randint(1480, 1890)
        cy = random.randint(30, 750)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)

    # 6. Draw the elegant double-line pixel frame around the entire 1920x1080 canvas
    border_color = (32, 28, 44, 255) # Sleek retro dark purple border
    
    # Outer frame
    draw.rectangle([12, 12, 1908, 1068], outline=border_color, width=2)
    # Inner frame
    draw.rectangle([20, 20, 1900, 1060], outline=border_color, width=2)
    
    # Corner decoration (dots and notches)
    corners = [
        # Top-left
        [15, 15, 17, 17],
        # Top-right
        [1903, 15, 1905, 17],
        # Bottom-left
        [15, 1063, 17, 1065],
        # Bottom-right
        [1903, 1063, 1905, 1065]
    ]
    for c in corners:
        draw.rectangle(c, fill=border_color)

    # Save to output assets path
    os.makedirs('assets', exist_ok=True)
    splash.save('assets/godot_splash_logo.png', 'PNG')
    print("Successfully processed AI-generated image into a perfect 16:9 pixel-art splash screen!")

if __name__ == '__main__':
    main()
