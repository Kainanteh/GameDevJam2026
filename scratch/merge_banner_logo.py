import os
from PIL import Image

def merge_banner_and_logo():
    # Rutas absolutas
    logo_path = "/home/kainanteh/game-dev-jam-2026/Contexto/GameDevTV20206.png"
    banner_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_camino_ancestral_1779133079502.png"
    output_path = "/home/kainanteh/game-dev-jam-2026/itch_header_ancestral_path.png"
    
    if not os.path.exists(logo_path):
        print("El logo de la Jam no existe en la ruta:", logo_path)
        return
        
    if not os.path.exists(banner_path):
        print("El banner generado no existe en la ruta:", banner_path)
        return
        
    # Abrir imágenes
    banner = Image.open(banner_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")
    
    # Redimensionar el logo a una medida proporcional de cabecera (ej: 140px de ancho)
    w_percent = (140 / float(logo.size[0]))
    h_size = int((float(logo.size[1]) * float(w_percent)))
    logo_resized = logo.resize((140, h_size), Image.Resampling.LANCZOS)
    
    # Posicionar en la esquina superior derecha con un margen de 24 píxeles
    margin = 24
    position = (banner.width - logo_resized.width - margin, margin)
    
    # Pegar con canal alfa de transparencia
    banner.paste(logo_resized, position, logo_resized)
    
    # Guardar resultado final
    banner.save(output_path, "PNG")
    print("¡Fusión realizada con éxito! Archivo guardado en:", output_path)

if __name__ == "__main__":
    merge_banner_and_logo()
