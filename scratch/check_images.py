import os
from PIL import Image

def inspect_images():
    brain_dir = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b"
    files = [
        "/home/kainanteh/game-dev-jam-2026/itch_header_ancestral_path.png",
        os.path.join(brain_dir, "banner_i_was_what_you_are_1779133437293.png"),
        os.path.join(brain_dir, "logo_titulo_transparent.png"),
        os.path.join(brain_dir, "logo_titulo.png"),
        os.path.join(brain_dir, "banner_camino_ancestral_1779133079502.png")
    ]
    for f in files:
        if os.path.exists(f):
            img = Image.open(f)
            print(f"Path: {f}")
            print(f"  Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
        else:
            print(f"Path: {f} - DOES NOT EXIST")

if __name__ == "__main__":
    inspect_images()
