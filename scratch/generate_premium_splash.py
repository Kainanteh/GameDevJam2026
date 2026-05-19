import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def main():
    # 1. Read original icon.svg
    with open('icon.svg', 'r') as f:
        svg_content = f.read()

    # 2. Modify SVG to keep only head and use original colors
    svg_no_rect = re.sub(r'<rect[^>]*>', '', svg_content)
    
    os.makedirs('scratch', exist_ok=True)
    with open('scratch/icon_head_highres.svg', 'w') as f:
        f.write(svg_no_rect)

    # 3. Rasterize to a high-resolution 300x300 image
    print("Rasterizing SVG to 300x300...")
    os.system('rsvg-convert -w 300 -h 300 scratch/icon_head_highres.svg -o scratch/icon_head_highres.png')

    # 4. Load the head image
    head_raw = Image.open('scratch/icon_head_highres.png').convert('RGBA')
    h_w, h_h = head_raw.size
    raw_px = head_raw.load()

    # Create pixel-perfect color-mapped head at 300x300
    head = Image.new('RGBA', (h_w, h_h), (0, 0, 0, 0))
    h_px = head.load()

    for y in range(h_h):
        for x in range(h_w):
            r, g, b, a = raw_px[x, y]
            if a < 10:
                continue
            
            # Map colors based on distance to original colors:
            # 1. White parts (eyes, mouth)
            if r > 200 and g > 200 and b > 200:
                h_px[x, y] = (255, 255, 255, a) # Keep white but preserve antialiased alpha
            # 2. Pupils (dark grey #414042)
            elif r < 100 and g < 100 and b < 100:
                h_px[x, y] = (7, 6, 10, a) # Deep dark #07060a background color
            # 3. Face (blue #478cbf)
            else:
                # Colorize to neon cyan #00d2ff
                h_px[x, y] = (0, 210, 255, a)

    # 5. Create a high-res outline mask
    # We want a sharp 4-pixel solid fucsia border (#ff007f) around the head
    border_thickness = 4
    head_with_border = Image.new('RGBA', (h_w + border_thickness * 2, h_h + border_thickness * 2), (0, 0, 0, 0))
    
    # Draw the border by pasting the head shifted in multiple directions
    fucsia_color = (255, 0, 127, 255)
    fucsia_solid = Image.new('RGBA', (h_w, h_h), fucsia_color)
    
    # Create the outline on head_with_border
    for dy in range(-border_thickness, border_thickness + 1):
        for dx in range(-border_thickness, border_thickness + 1):
            if dx*dx + dy*dy <= border_thickness*border_thickness:
                head_with_border.paste(fucsia_solid, (border_thickness + dx, border_thickness + dy), head)
                
    # Paste the clean cyan head in the center
    head_with_border.paste(head, (border_thickness, border_thickness), head)

    # 6. Create the final 1920x1080 Canvas (Solid #07060a)
    canvas_w = 1920
    canvas_h = 1080
    splash = Image.new('RGBA', (canvas_w, canvas_h), (7, 6, 10, 255))
    draw = ImageDraw.Draw(splash)

    # Paste the head in the center of the canvas
    head_x = (canvas_w - head_with_border.width) // 2
    head_y = 260
    splash.paste(head_with_border, (head_x, head_y), head_with_border)

    # 7. Render high-resolution text
    font_path_bold = '/usr/share/fonts/noto/NotoSans-Bold.ttf'
    font_path_reg = '/usr/share/fonts/noto/NotoSans-Regular.ttf'

    font_godot = ImageFont.truetype(font_path_bold, 80)
    font_engine = ImageFont.truetype(font_path_reg, 32)

    text_godot = "GODOT"
    text_engine = "Game engine"

    # Draw GODOT text centered with a solid 3px fucsia outline/shadow
    box_godot = draw.textbbox((0, 0), text_godot, font=font_godot)
    godot_w = box_godot[2] - box_godot[0]
    godot_x = (canvas_w - godot_w) // 2
    godot_y = 620

    # Draw solid outline shadow for text
    shadow_offset = 3
    # Draw fucsia outline
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]:
        draw.text((godot_x + dx, godot_y + dy), text_godot, fill=(255, 0, 127, 255), font=font_godot)
        
    # Draw main white text on top
    draw.text((godot_x, godot_y), text_godot, fill=(255, 255, 255, 255), font=font_godot)

    # Draw "Game engine" centered
    box_engine = draw.textbbox((0, 0), text_engine, font=font_engine)
    engine_w = box_engine[2] - box_engine[0]
    engine_x = (canvas_w - engine_w) // 2
    engine_y = 740
    draw.text((engine_x, engine_y), text_engine, fill=(142, 147, 166, 255), font=font_engine)

    # 8. Save to assets/godot_splash_logo.png
    os.makedirs('assets', exist_ok=True)
    splash.save('assets/godot_splash_logo.png', 'PNG')
    print("Successfully generated high-resolution assets/godot_splash_logo.png!")

if __name__ == '__main__':
    main()
