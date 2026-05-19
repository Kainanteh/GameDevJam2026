import os
from PIL import Image, ImageDraw, ImageFilter

def main():
    # Use the latest generated widescreen image
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/godot_splash_widescreen_1779203197995.png"
    
    if not os.path.exists(src_path):
        print(f"Error: Widescreen AI image not found at {src_path}")
        return

    # Load image
    ai_img = Image.open(src_path).convert('RGBA')
    
    # 1. Crop out the original border (25px from each edge)
    crop_box = (25, 25, 999, 999) # 974x974 area
    inner_img = ai_img.crop(crop_box)
    
    # 2. Resize to 1080x1080 to match screen height
    # We use LANCZOS for high quality scaling, but we will sharpen it to make the pixel art crisp
    center_img = inner_img.resize((1080, 1080), Image.Resampling.LANCZOS)
    
    # Apply a high-quality sharpening filter to make the robot and text super sharp
    # We use UnsharpMask to enhance contrast on the pixel boundaries without adding noise
    center_img = center_img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=160, threshold=2))

    # 3. Create the 1920x1080 canvas
    canvas_w = 1920
    canvas_h = 1080
    splash = Image.new('RGBA', (canvas_w, canvas_h))

    # 4. Paste the center image at x = 420
    paste_x = 420
    splash.paste(center_img, (paste_x, 0))

    # 5. Fill left margin (x = 0 to 420) by mirroring the adjacent section of the center image
    # We take the slice from x = 420 to 840 (width 420) of the canvas, flip it, and paste it at x = 0
    left_slice = splash.crop((paste_x, 0, paste_x + paste_x, canvas_h))
    left_flipped = left_slice.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    splash.paste(left_flipped, (0, 0))

    # 6. Fill right margin (x = 1500 to 1920) by mirroring the adjacent section of the center image
    # We take the slice from x = 1080 to 1500 (width 420) of the canvas, flip it, and paste it at x = 1500
    right_slice = splash.crop((1500 - paste_x, 0, 1500, canvas_h))
    right_flipped = right_slice.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    splash.paste(right_flipped, (1500, 0))

    # 7. Draw a new double-line pixel frame around the entire 1920x1080 canvas
    # Sample color from the original border: #1b1725
    border_color = (27, 23, 37, 255)
    draw = ImageDraw.Draw(splash)
    
    # Outer frame
    draw.rectangle([12, 12, 1908, 1068], outline=border_color, width=2)
    # Inner frame
    draw.rectangle([20, 20, 1900, 1060], outline=border_color, width=2)
    
    # Corner decoration (dots and notches matching retro pixel art)
    corners = [
        [15, 15, 17, 17],
        [1903, 15, 1905, 17],
        [15, 1063, 17, 1065],
        [1903, 1063, 1905, 1065]
    ]
    for c in corners:
        draw.rectangle(c, fill=border_color)

    # 8. Save the final splash screen
    os.makedirs('assets', exist_ok=True)
    splash.save('assets/godot_splash_logo.png', 'PNG')
    print("Successfully created a perfectly unified, razor-sharp 16:9 pixel-art splash screen!")

if __name__ == '__main__':
    main()
