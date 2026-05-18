import os
from PIL import Image

def apply_new_header():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/itch_header_ancestral_path_1779138400833.png"
    dest_path1 = "/home/kainanteh/game-dev-jam-2026/itch_header_ancestral_path.png"
    dest_path2 = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/itch_header_ancestral_path.png"
    
    if not os.path.exists(src_path):
        print("Error: Source image not found at:", src_path)
        return
        
    img = Image.open(src_path)
    img.save(dest_path1, "PNG")
    img.save(dest_path2, "PNG")
    print(f"Successfully applied the updated header image to {dest_path1} and {dest_path2}")

if __name__ == "__main__":
    apply_new_header()
