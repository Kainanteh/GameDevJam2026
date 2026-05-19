import os
from PIL import Image

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/godot_splash_native_widescreen_1779203734541.png"
    if not os.path.exists(src_path):
        return
        
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    
    # Let's inspect column x=512 (center) from y=750 to 990 to find where the mountain begins!
    print("CENTER COLUMN (x=512) COLORS:")
    for y in range(750, 990, 5):
        print(f"y={y}: {img.getpixel((512, y))}")

if __name__ == '__main__':
    main()
