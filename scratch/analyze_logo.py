import os
from PIL import Image

def analyze_logo():
    logo_path = "/home/kainanteh/game-dev-jam-2026/logo_titulo.png"
    if not os.path.exists(logo_path):
        print("El logo no existe.")
        return
        
    img = Image.open(logo_path).convert("RGBA")
    width, height = img.size
    
    # Muestrear píxeles para ver el rango de la nebulosa vs las letras
    stats = {}
    for y in range(height):
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            brightness = max(r, g, b)
            # Agrupar por tramos de brillo para ver la distribución
            bucket = (brightness // 10) * 10
            stats[bucket] = stats.get(bucket, 0) + 1
            
    print("Distribución de brillo en los píxeles del logo:")
    for bucket in sorted(stats.keys()):
        print(f"Brillo {bucket}-{bucket+9}: {stats[bucket]} píxeles")

if __name__ == "__main__":
    analyze_logo()
