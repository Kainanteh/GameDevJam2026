import os
from PIL import Image

def generate_cover_image():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/itch_header_ancestral_path_1779138400833.png"
    out_path1 = "/home/kainanteh/game-dev-jam-2026/cover.png"
    out_path2 = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/cover.png"
    
    if not os.path.exists(src_path):
        print("Error: Source image not found at:", src_path)
        return
        
    img = Image.open(src_path)
    
    # 630x500 is the recommended size for itch.io game covers
    # The source is 1024x1024 (1:1). 
    # To convert to 630x500 (1.26:1) without stretching:
    # Scale width to 630. Height will be 630.
    img_resized = img.resize((630, 630), Image.Resampling.LANCZOS)
    
    # Crop height from 630 to 500.
    # The text is at the top, characters are at the bottom.
    # Let's crop slightly more from the bottom to protect the top title text and stars.
    # We crop 35 pixels from the top and 95 pixels from the bottom.
    left = 0
    top = 35
    right = 630
    bottom = 535
    
    cover = img_resized.crop((left, top, right, bottom))
    
    # Save the resulting 630x500 image
    cover.save(out_path1, "PNG")
    cover.save(out_path2, "PNG")
    print(f"Successfully generated 630x500 cover image at {out_path1} and {out_path2}")
    print(f"Dimensions: {cover.size}")

if __name__ == "__main__":
    generate_cover_image()
