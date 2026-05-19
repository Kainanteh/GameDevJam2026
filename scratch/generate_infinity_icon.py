import os
import math
from PIL import Image, ImageDraw, ImageFilter

def draw_lemniscate(draw_obj, center, a, color, width):
    points = []
    # We iterate t from 0 to 2*pi with small steps
    steps = 200
    for i in range(steps + 1):
        t = (i / float(steps)) * 2 * math.pi
        denom = 1 + math.sin(t)**2
        x = (a * math.cos(t)) / denom
        y = (a * math.sin(t) * math.cos(t)) / denom
        points.append((center[0] + x, center[1] + y))
    
    # Draw connected line segments
    for j in range(len(points) - 1):
        draw_obj.line([points[j], points[j+1]], fill=color, width=width, joint="round")

def main():
    out_path = "/home/kainanteh/game-dev-jam-2026/assets/icon_infinity.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Create 72x72 canvas
    img = Image.new("RGBA", (72, 72), (0, 0, 0, 0))
    
    # We will draw on a larger canvas and downscale to get beautiful anti-aliasing
    scale = 4
    large_size = 72 * scale
    large_img = Image.new("RGBA", (large_size, large_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(large_img)
    
    center = (large_size // 2, large_size // 2)
    a = 24 * scale # Radius/scale of lemniscate
    
    # 1. Draw neon outer glow (wide orange-gold stroke)
    draw_lemniscate(draw, center, a, (255, 140, 0, 80), width=9*scale)
    
    # Apply a soft blur to the glow layer
    glow_img = large_img.filter(ImageFilter.GaussianBlur(radius=2*scale))
    
    # Create a new drawing context on the blurred glow layer to draw the sharp layers
    draw_sharp = ImageDraw.Draw(glow_img)
    
    # 2. Draw outer border/gold base (medium gold stroke)
    draw_lemniscate(draw_sharp, center, a, (255, 200, 0, 255), width=5*scale)
    
    # 3. Draw inner neon core (thin bright yellow/white stroke)
    draw_lemniscate(draw_sharp, center, a, (255, 255, 240, 255), width=2*scale)
    
    # 4. Add some small cross-sparkles (stars) on the loops to make it look "flashy gold"
    def draw_sparkle(draw_ctx, cx, cy, radius):
        draw_ctx.line([(cx - radius, cy), (cx + radius, cy)], fill=(255, 255, 255, 255), width=1*scale)
        draw_ctx.line([(cx, cy - radius), (cx, cy + radius)], fill=(255, 255, 255, 255), width=1*scale)
        # Small diagonal points
        draw_ctx.point((cx - 1*scale, cy - 1*scale), fill=(255, 220, 100, 200))
        draw_ctx.point((cx + 1*scale, cy - 1*scale), fill=(255, 220, 100, 200))
        draw_ctx.point((cx - 1*scale, cy + 1*scale), fill=(255, 220, 100, 200))
        draw_ctx.point((cx + 1*scale, cy + 1*scale), fill=(255, 220, 100, 200))

    # Sparkle on left loop apex
    draw_sparkle(draw_sharp, center[0] - 16*scale, center[1] - 5*scale, 4*scale)
    # Sparkle on right loop apex
    draw_sparkle(draw_sharp, center[0] + 16*scale, center[1] + 5*scale, 4*scale)
    
    # Downscale to 72x72
    final_img = glow_img.resize((72, 72), Image.Resampling.LANCZOS)
    final_img.save(out_path, "PNG")
    print(f"Generated golden infinity icon at: {out_path}")

if __name__ == "__main__":
    main()
