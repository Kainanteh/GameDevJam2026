import os
from PIL import Image

def main():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_i_was_what_you_are_swapped_1779175615275.png"
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found")
        return
        
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    
    # Let's erase the text area from y=50 to y=300
    for y in range(50, 305):
        # Sample background colors from the left and right margins (where there is no text)
        bg_left = img.getpixel((35, y))
        bg_right = img.getpixel((980, y))
        
        for x in range(40, 985):
            current = img.getpixel((x, y))
            # Calculate distance to left and right background colors
            dist_l = sum(abs(c1 - c2) for c1, c2 in zip(current[:3], bg_left[:3]))
            dist_r = sum(abs(c1 - c2) for c1, c2 in zip(current[:3], bg_right[:3]))
            
            # If the pixel is significantly different from the background, it's part of the neon text!
            if dist_l > 45 and dist_r > 45:
                # Interpolate background color based on x position to blend smoothly from left to right margins
                t = (x - 35) / float(980 - 35)
                r = int(bg_left[0] * (1 - t) + bg_right[0] * t)
                g = int(bg_left[1] * (1 - t) + bg_right[1] * t)
                b = int(bg_left[2] * (1 - t) + bg_right[2] * t)
                img.putpixel((x, y), (r, g, b, 255))
                
    img.save("/home/kainanteh/game-dev-jam-2026/scratch/erased_banner.png")
    print("Saved text-erased banner to scratch/erased_banner.png")

if __name__ == '__main__':
    main()
