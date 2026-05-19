import os
import re
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

def generate_svg(filename, face_color, face_width, eyes_color, eyes_width, pupil_width, godot_color, godot_width, engine_color, engine_width):
    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
  <!-- Background -->
  <rect width="1920" height="1080" fill="#07060a"/>

  <!-- Robot Head Group -->
  <g fill="none" stroke-linejoin="round" stroke-linecap="round" transform="translate(806.4, 180) scale(2.4)">
    <g transform="translate(12.322 12.322)scale(.101)">
      <!-- Face -->
      <path stroke="{face_color}" stroke-width="{face_width}" d="m105 673 152 14q12 1 15 14l4 67 132 10 8-61q2-11 15-15h162q13 4 15 15l8 61 132-10 4-67q3-13 15-14l152-14V427q30-39 56-81-35-59-83-108-43 20-82 47-40-37-88-64 7-51 8-102-59-28-123-42-26 43-46 89-49-7-98 0-20-46-46-89-64 14-123 42 1 51 8 102-48 27-88 64-39-27-82-47-48 49-83 108 26 42 56 81zm0 33v39c0 276 813 276 814 0v-39l-134 12-5 69q-2 10-14 13l-162 11q-12 0-16-11l-10-65H446l-10 65q-4 11-16 11l-162-11q-12-3-14-13l-5-69z"/>
      
      <!-- Mouth -->
      <path stroke="{eyes_color}" stroke-width="{eyes_width}" d="M105 673v33q407 354 814 0v-33z"/>
      
      <!-- Nose -->
      <path stroke="{eyes_color}" stroke-width="{eyes_width}" d="M483 600c0 34 58 34 58 0v-86c0-34-58-34-58 0z"/>
      
      <!-- Eyes -->
      <circle cx="299" cy="526" r="90" stroke="{eyes_color}" stroke-width="{eyes_width}"/>
      <circle cx="725" cy="526" r="90" stroke="{eyes_color}" stroke-width="{eyes_width}"/>
      
      <!-- Pupils (neon rings inside) -->
      <circle cx="307" cy="532" r="40" stroke="{eyes_color}" stroke-width="{pupil_width}"/>
      <circle cx="717" cy="532" r="40" stroke="{eyes_color}" stroke-width="{pupil_width}"/>
    </g>
  </g>

  <!-- Text: GODOT -->
  <text x="960" y="700" 
        font-family="DejaVu Sans, Liberation Sans, Arial, sans-serif" 
        font-weight="900" 
        font-size="90" 
        text-anchor="middle" 
        fill="none" 
        stroke="{godot_color}" 
        stroke-width="{godot_width}" 
        letter-spacing="16">GODOT</text>

  <!-- Text: Game engine -->
  <text x="960" y="800" 
        font-family="DejaVu Sans, Liberation Sans, Arial, sans-serif" 
        font-weight="bold" 
        font-size="34" 
        text-anchor="middle" 
        fill="none" 
        stroke="{engine_color}" 
        stroke-width="{engine_width}" 
        letter-spacing="6">Game engine</text>
</svg>"""

    with open(filename, 'w') as f:
        f.write(svg_template)

def main():
    os.makedirs('scratch', exist_ok=True)
    
    cyan_neon = "#00f3ff"
    pink_neon = "#ff007f"
    white_core = "#ffffff"
    light_cyan = "#e0fbff"
    light_pink = "#ffe8f0"
    
    # 1. Generate the Glow SVG (thick neon outline colored)
    generate_svg('scratch/splash_glow.svg', 
                 face_color=cyan_neon, face_width=80, 
                 eyes_color=pink_neon, eyes_width=80, pupil_width=60,
                 godot_color=cyan_neon, godot_width=16,
                 engine_color=pink_neon, engine_width=8)

    # 2. Generate the Tube SVG (medium thickness colored core)
    generate_svg('scratch/splash_tube.svg', 
                 face_color=cyan_neon, face_width=36, 
                 eyes_color=pink_neon, eyes_width=36, pupil_width=24,
                 godot_color=cyan_neon, godot_width=6,
                 engine_color=pink_neon, engine_width=3)

    # 3. Generate the Core SVG (thin white filament inside)
    generate_svg('scratch/splash_core.svg', 
                 face_color=light_cyan, face_width=10, 
                 eyes_color=light_pink, eyes_width=10, pupil_width=6,
                 godot_color=white_core, godot_width=2,
                 engine_color=white_core, engine_width=1)

    # 4. Rasterize all SVGs to high-quality PNGs
    print("Rasterizing SVGs with rsvg-convert...")
    os.system('rsvg-convert scratch/splash_glow.svg -o scratch/splash_glow.png')
    os.system('rsvg-convert scratch/splash_tube.svg -o scratch/splash_tube.png')
    os.system('rsvg-convert scratch/splash_core.svg -o scratch/splash_core.png')

    # 5. Load rasters in Pillow
    img_glow = Image.open('scratch/splash_glow.png').convert('RGBA')
    img_tube = Image.open('scratch/splash_tube.png').convert('RGBA')
    img_core = Image.open('scratch/splash_core.png').convert('RGBA')

    # 6. Initialize final canvas (Solid #07060a)
    canvas_w = 1920
    canvas_h = 1080
    splash = Image.new('RGBA', (canvas_w, canvas_h), (7, 6, 10, 255))
    draw = ImageDraw.Draw(splash)

    # 7. Draw background stars matching the style of the wallpaper
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
            draw_obj.point((cx-2, cy), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx+2, cy), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx, cy-2), fill=(color[0], color[1], color[2], 60))
            draw_obj.point((cx, cy+2), fill=(color[0], color[1], color[2], 60))

    random.seed(9876)
    for _ in range(40):
        # Left side stars
        cx = random.randint(30, 520)
        cy = random.randint(30, 1050)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)
        
        # Right side stars
        cx = random.randint(1400, 1890)
        cy = random.randint(30, 1050)
        col = random.choice([neon_blue, neon_pink, star_white])
        sz = random.choice([1, 2, 3, 4])
        draw_star(draw, cx, cy, col, sz)

    # 8. Create and composite neon glow/bloom layers
    # Blur the glow PNG with different strengths
    glow_30 = img_glow.filter(ImageFilter.GaussianBlur(32))
    glow_15 = img_glow.filter(ImageFilter.GaussianBlur(16))
    glow_6 = img_glow.filter(ImageFilter.GaussianBlur(6))
    glow_2 = img_glow.filter(ImageFilter.GaussianBlur(2))

    # Apply layers with additive blending
    for glow, opacity in [(glow_30, 0.5), (glow_15, 0.7), (glow_6, 0.9), (glow_2, 1.0)]:
        # Blend each layer onto the background
        splash.alpha_composite(glow)

    # Paste the sharp colored tubes
    splash.alpha_composite(img_tube)

    # Paste the hot white inner cores
    splash.alpha_composite(img_core)

    # 9. Save final splash screen image
    os.makedirs('assets', exist_ok=True)
    splash.save('assets/godot_splash_logo.png', 'PNG')
    print("Successfully generated perfect vector neon splash screen!")

if __name__ == '__main__':
    main()
