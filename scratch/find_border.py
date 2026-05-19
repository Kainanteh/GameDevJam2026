import os
from PIL import Image

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/godot_splash_native_widescreen_1779203734541.png"
    if not os.path.exists(src_path):
        return
        
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    
    # We inspect columns across the image at y = 990, 1000, 1008, 1014, 1020 to find the border line
    # The border is usually a dark purple rectangle line (e.g. color (27, 23, 37) or similar).
    # Let's print the colors of a few columns near the center (x = 512) and edges
    for y in range(990, 1024, 2):
        print(f"y={y}: x=100:{img.getpixel((100, y))} | x=512:{img.getpixel((512, y))} | x=900:{img.getpixel((900, y))}")

if __name__ == '__main__':
    main()
