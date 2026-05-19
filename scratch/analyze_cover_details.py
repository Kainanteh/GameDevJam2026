import os
from PIL import Image

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_i_was_what_you_are_swapped_1779175615275.png"
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found")
        return
        
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    
    # Let's inspect column x=40 (just inside the border) from y=750 to 1024 to find mountain heights
    print("LEFT COLUMN (x=40) COLORS:")
    for y in range(750, 1024, 10):
        print(f"y={y}: {img.getpixel((40, y))}")
        
    print("\nRIGHT COLUMN (x=980) COLORS:")
    for y in range(750, 1024, 10):
        print(f"y={y}: {img.getpixel((980, y))}")

    # Let's find the border color at the top (x=512, y=15)
    print(f"\nTOP BORDER COLOR (x=512, y=15): {img.getpixel((512, 15))}")
    print(f"TOP BORDER COLOR (x=512, y=25): {img.getpixel((512, 25))}")

if __name__ == '__main__':
    main()
