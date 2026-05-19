import os
from PIL import Image

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_i_was_what_you_are_swapped_1779175615275.png"
    if not os.path.exists(src_path):
        return
        
    img = Image.open(src_path).convert('RGBA')
    
    # We inspect values along the top row near x=512, from y=0 to 35
    for y in range(0, 40):
        print(f"y={y}: {img.getpixel((512, y))}")
        
    # We inspect values along the left edge at y=512, from x=0 to 35
    print("\nLEFT EDGE (y=512, x=0..40):")
    for x in range(0, 40):
        print(f"x={x}: {img.getpixel((x, 512))}")

if __name__ == '__main__':
    main()
