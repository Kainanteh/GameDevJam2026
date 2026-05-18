import os
from PIL import Image

def crop_new_logo():
    new_banner_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_i_was_what_you_are_1779133437293.png"
    logo_out = "/home/kainanteh/game-dev-jam-2026/logo_camino_ancestral.png"
    logo_out_brain = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/logo_camino_ancestral.png"
    
    if os.path.exists(new_banner_path):
        banner = Image.open(new_banner_path)
        # Recortar el bloque del texto del título (y = 80 a y = 260)
        # Ancho completo (0 a 1024), con un margen horizontal cómodo
        logo_crop = banner.crop((50, 80, banner.width - 50, 270))
        logo_crop.save(logo_out, "PNG")
        logo_crop.save(logo_out_brain, "PNG")
        print("¡Logotipo memento mori recortado con éxito!")
    else:
        print("No se encontró el nuevo banner para recortar.")

if __name__ == "__main__":
    crop_new_logo()
