import os
from PIL import Image

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_i_was_what_you_are_swapped_1779175615275.png"
    if not os.path.exists(src_path):
        return
        
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    
    # We check y from 30 to 100
    for y in range(30, 100, 5):
        row_pixels = [img.getpixel((x, y)) for x in range(100, w - 100, 10)]
        bright_pixels = [p for p in row_pixels if max(p[0], p[1], p[2]) > 100]
        print(f"y={y}: Bright pixel count = {len(bright_pixels)}")

if __name__ == '__main__':
    main()
