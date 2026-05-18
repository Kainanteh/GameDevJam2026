import os
from PIL import Image

def copy_memento_mori_header():
    src_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_i_was_what_you_are_1779133437293.png"
    dest_path1 = "/home/kainanteh/game-dev-jam-2026/itch_header_ancestral_path.png"
    dest_path2 = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/itch_header_ancestral_path.png"
    
    if not os.path.exists(src_path):
        print("Error: Source banner banner_i_was_what_you_are does not exist!")
        return
        
    # Open the JPEG and save it as PNG to preserve high quality format
    img = Image.open(src_path)
    img.save(dest_path1, "PNG")
    img.save(dest_path2, "PNG")
    print(f"Successfully saved clean Memento Mori header to {dest_path1} and {dest_path2}")

if __name__ == "__main__":
    copy_memento_mori_header()
