import os
import random
from PIL import Image, ImageDraw

def generate_itch_backgrounds():
    logo_path = "/home/kainanteh/game-dev-jam-2026/Contexto/GameDevTV20206.png"
    out_dir = "/home/kainanteh/game-dev-jam-2026"
    
    # Official color #07060a
    bg_color = (7, 6, 10, 255)
    
    # Colors matching the theme stars
    neon_blue = (0, 210, 255, 255)
    neon_pink = (255, 0, 127, 255)
    star_white = (255, 255, 255, 220)
    
    # Helper to draw a pixel-art star with glow
    def draw_star(draw_obj, cx, cy, color, size):
        if size == 1:
            draw_obj.point((cx, cy), fill=color)
        elif size == 2:
            draw_obj.point((cx, cy), fill=color)
            draw_obj.point((cx+1, cy), fill=color)
        elif size == 3:
            # Star with 4-way bloom
            draw_obj.point((cx, cy), fill=color)
            draw_obj.point((cx-1, cy), fill=(color[0], color[1], color[2], 120))
            draw_obj.point((cx+1, cy), fill=(color[0], color[1], color[2], 120))
            draw_obj.point((cx, cy-1), fill=(color[0], color[1], color[2], 120))
            draw_obj.point((cx, cy+1), fill=(color[0], color[1], color[2], 120))
        elif size == 4:
            # Large star with extended bloom
            draw_obj.point((cx, cy), fill=star_white)
            draw_obj.point((cx-1, cy), fill=color)
            draw_obj.point((cx+1, cy), fill=color)
            draw_obj.point((cx, cy-1), fill=color)
            draw_obj.point((cx, cy+1), fill=color)
            draw_obj.point((cx-2, cy), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx+2, cy), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx, cy-2), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx, cy+2), fill=(color[0], color[1], color[2], 60))

    random.seed(42) # Fixed seed for reproducible beautiful sky

    # =========================================================================
    # 1. GENERATE THE WIDESCREEN BACKGROUND (tile_background.png - 1920x1080)
    # =========================================================================
    bg_w, bg_h = 1920, 1080
    bg_img = Image.new("RGBA", (bg_w, bg_h), bg_color) # Solid #07060a
    draw_bg = ImageDraw.Draw(bg_img)

    # Scatter a high density of stars in the left/right margins
    # Left margin: x=0 to 420
    for _ in range(120):
        x = random.randint(15, 410)
        y = random.randint(15, 1060)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
        draw_star(draw_bg, x, y, col, sz)
        
    # Right margin: x=1500 to 1920
    for _ in range(120):
        x = random.randint(1510, 1905)
        y = random.randint(15, 1060)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
        draw_star(draw_bg, x, y, col, sz)

    # Paste the Jam logo on the right side if it exists
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        w_target = 260
        h_target = int(logo.height * (w_target / float(logo.width)))
        logo_resized = logo.resize((w_target, h_target), Image.Resampling.LANCZOS)
        bg_img.paste(logo_resized, (1600, 360), logo_resized)
        print("Pasted GameDev.tv Jam logo on the right margin of background.")

    # Save wallpaper backgrounds
    bg_out = os.path.join(out_dir, "tile_background.png")
    bg_brain = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/tile_background.png"
    bg_img.save(bg_out, "PNG")
    bg_img.save(bg_brain, "PNG")
    print(f"Saved widescreen background (1920x1080) to {bg_out}")

    # =========================================================================
    # 2. GENERATE THE EMBED BG (tile_embed.png - 1152x648)
    # =========================================================================
    embed_w, embed_h = 1152, 648
    embed_img = Image.new("RGBA", (embed_w, embed_h), bg_color) # Solid #07060a
    draw_embed = ImageDraw.Draw(embed_img)
        
    # Scatter stars across the ENTIRE embed viewport area
    for _ in range(160):
        x = random.randint(15, embed_w - 15)
        y = random.randint(15, embed_h - 15)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choices([1, 2, 3, 4], weights=[65, 23, 9, 3])[0]
        draw_star(draw_embed, x, y, col, sz)

    # Save embed backgrounds
    embed_out = os.path.join(out_dir, "tile_embed.png")
    embed_brain = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/tile_embed.png"
    embed_img.save(embed_out, "PNG")
    embed_img.save(embed_brain, "PNG")
    print(f"Saved starry embed background (1152x648) to {embed_out}")

if __name__ == "__main__":
    generate_itch_backgrounds()
