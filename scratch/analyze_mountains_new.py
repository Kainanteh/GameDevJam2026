import os
from PIL import Image

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/godot_splash_no_border_1779203949567.png"
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found")
        return
        
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    
    print("LEFT EDGE (x=0) COLORS:")
    for y in range(750, 1024, 10):
        print(f"y={y}: {img.getpixel((0, y))}")
        
    print("\nRIGHT EDGE (x=1023) COLORS:")
    for y in range(750, 1024, 10):
        print(f"y={y}: {img.getpixel((1023, y))}")

if __name__ == '__main__':
    main()
