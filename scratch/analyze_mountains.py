import os
from PIL import Image

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/godot_splash_native_widescreen_1779203734541.png"
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found")
        return
        
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    
    # We want to analyze the column x = 25 (left edge of cropped image) 
    # and x = 999 (right edge of cropped image) to find the mountain layer transitions.
    # The sky is dark, the mountains are solid dark colors.
    # Let's print the colors along those columns from y = 600 to 1024.
    
    print("LEFT COLUMN (x=25) COLORS:")
    for y in range(700, 1024, 10):
        print(f"y={y}: {img.getpixel((25, y))}")
        
    print("\nRIGHT COLUMN (x=999) COLORS:")
    for y in range(700, 1024, 10):
        print(f"y={y}: {img.getpixel((999, y))}")

if __name__ == '__main__':
    main()
