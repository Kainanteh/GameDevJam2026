import os
from PIL import Image

def process_sharp_logo():
    new_banner_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_i_was_what_you_are_swapped_1779175615275.png"
    
    out_paths = [
        "/home/kainanteh/game-dev-jam-2026/logo_titulo_transparent.png",
        "/home/kainanteh/game-dev-jam-2026/logo_titulo.png",
        "/home/kainanteh/game-dev-jam-2026/logo_camino_ancestral.png",
        "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/logo_titulo_transparent.png",
        "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/logo_titulo.png"
    ]
    
    if not os.path.exists(new_banner_path):
        print("Error: No se encontró el banner de origen.")
        return
        
    banner = Image.open(new_banner_path)
    
    # Recortar el texto del título de forma limpia y apaisada
    logo_crop = banner.crop((50, 75, banner.width - 50, 295)).convert("RGBA")
    
    datas = logo_crop.getdata()
    new_data = []
    
    for item in datas:
        r, g, b, a = item
        brightness = max(r, g, b)
        
        if brightness < 140:
            new_data.append((0, 0, 0, 0)) # Transparencia absoluta y limpia
        else:
            new_data.append((r, g, b, 255)) # Letras pixel-art sólidas y nítidas
            
    logo_crop.putdata(new_data)
    
    # Guardar en todos los destinos
    for path in out_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logo_crop.save(path, "PNG")
        print(f"Guardado transparente nítido en: {path}")

if __name__ == "__main__":
    process_sharp_logo()
