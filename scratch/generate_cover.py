import os
from PIL import Image

def generate_itch_cover():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_i_was_what_you_are_swapped_1779175615275.png"
    out_paths = [
        "/home/kainanteh/game-dev-jam-2026/itch_cover.png",
        "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/itch_cover.png"
    ]
    
    if not os.path.exists(src_path):
        print("Error: Swapped banner image does not exist!")
        return
        
    img = Image.open(src_path)
    width, height = img.size
    
    # We want a 630x500 ratio (1.26:1)
    # Let's crop a rectangle from the 1024x1024 image.
    # To keep the border and content nicely framed without squishing:
    # A box of width 1024 and height 812.7 (rounded to 812) centered vertically
    crop_height = 812
    y_start = (height - crop_height) // 2 # (1024 - 812) // 2 = 106
    
    cropped_img = img.crop((0, y_start, width, y_start + crop_height))
    
    # Resize to exactly 630x500 using LANCZOS for high quality
    resized_img = cropped_img.resize((630, 500), Image.Resampling.LANCZOS)
    
    for path in out_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        resized_img.save(path, "PNG")
        print(f"Saved cover image (630x500) to: {path}")

if __name__ == "__main__":
    generate_itch_cover()
