import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def main():
    # 1. Read original icon.svg
    with open('icon.svg', 'r') as f:
        svg_content = f.read()

    # 2. Modify SVG content
    # Remove the background rectangle
    svg_no_rect = re.sub(r'<rect[^>]*>', '', svg_content)
    # Replace blue face color #478cbf with neon cyan #00f3ff
    svg_neon = svg_no_rect.replace('fill="#478cbf"', 'fill="#00f3ff"')
    # Replace pupils color #414042 with dark background #07060a
    svg_neon = svg_neon.replace('fill="#414042"', 'fill="#07060a"')

    # Save modified SVG to scratch
    os.makedirs('scratch', exist_ok=True)
    with open('scratch/icon_head_neon.svg', 'w') as f:
        f.write(svg_neon)

    # 3. Rasterize SVG to a high-res PNG (160x160)
    print("Rasterizing SVG...")
    os.system('rsvg-convert -w 160 -h 160 scratch/icon_head_neon.svg -o scratch/icon_head_neon.png')

    # 4. Load the head image
    head = Image.open('scratch/icon_head_neon.png').convert('RGBA')

    # Create the glow effect behind the head
    glow_padding = 24
    glow_size = (head.width + glow_padding * 2, head.height + glow_padding * 2)
    glow_img = Image.new('RGBA', glow_size, (0, 0, 0, 0))
    # Paste head into the center of the glow image
    glow_img.paste(head, (glow_padding, glow_padding), head)

    # Separate alpha channel of the head and blur it to make a soft neon pink/magenta glow
    alpha = glow_img.split()[3]
    blurred_alpha = alpha.filter(ImageFilter.GaussianBlur(8))
    
    # Create solid magenta color layer (#ff007f)
    magenta_glow = Image.new('RGBA', glow_size, (255, 0, 127, 255))
    # Apply blurred alpha as mask
    glow_final = Image.new('RGBA', glow_size, (0, 0, 0, 0))
    glow_final.paste(magenta_glow, (0, 0), blurred_alpha)

    # Paste the original clean head on top of the magenta glow
    glow_final.paste(head, (glow_padding, glow_padding), head)

    # 5. Create the final splash canvas (800 x 480)
    canvas_w = 800
    canvas_h = 480
    # Our black color is #07060a
    splash = Image.new('RGBA', (canvas_w, canvas_h), (7, 6, 10, 255))

    # Paste the glowing head in the center
    head_x = (canvas_w - glow_final.width) // 2
    head_y = 60
    splash.paste(glow_final, (head_x, head_y), glow_final)

    # 6. Render stylized text below the logo
    draw = ImageDraw.Draw(splash)

    font_path_bold = '/usr/share/fonts/noto/NotoSans-Bold.ttf'
    font_path_reg = '/usr/share/fonts/noto/NotoSans-Regular.ttf'

    font_godot = ImageFont.truetype(font_path_bold, 40)
    font_engine = ImageFont.truetype(font_path_reg, 18)

    # Text strings
    text_godot = "GODOT"
    text_engine = "Game engine"

    # Draw GODOT text with a subtle cyan glow
    # Get text size
    box_godot = draw.textbbox((0, 0), text_godot, font=font_godot)
    godot_w = box_godot[2] - box_godot[0]
    godot_h = box_godot[3] - box_godot[0]
    godot_x = (canvas_w - godot_w) // 2
    godot_y = 285

    # Draw cyan glow layer for text
    text_glow_canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    tg_draw = ImageDraw.Draw(text_glow_canvas)
    tg_draw.text((godot_x, godot_y), text_godot, fill=(0, 243, 255, 255), font=font_godot)
    
    # Blur text glow
    text_glow_blurred = text_glow_canvas.filter(ImageFilter.GaussianBlur(4))
    splash.paste(text_glow_blurred, (0, 0), text_glow_blurred)

    # Draw solid white text on top
    draw.text((godot_x, godot_y), text_godot, fill=(255, 255, 255, 255), font=font_godot)

    # Draw "Game engine" text in a clean greyish-cyan
    box_engine = draw.textbbox((0, 0), text_engine, font=font_engine)
    engine_w = box_engine[2] - box_engine[0]
    engine_x = (canvas_w - engine_w) // 2
    engine_y = 345
    draw.text((engine_x, engine_y), text_engine, fill=(130, 134, 148, 255), font=font_engine)

    # 7. Save the final image to assets/godot_splash_logo.png
    os.makedirs('assets', exist_ok=True)
    splash.save('assets/godot_splash_logo.png', 'PNG')
    print("Successfully generated assets/godot_splash_logo.png!")

if __name__ == '__main__':
    main()
