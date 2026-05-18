import os
from PIL import Image, ImageDraw

def generate_unified_tile():
    out_dir = "/home/kainanteh/game-dev-jam-2026"
    
    # Crear un azulejo más grande (128x128) para que la repetición no se vea ruidosa
    tile = Image.new("RGBA", (128, 128), (7, 6, 10, 255)) # Color abisal #07060a
    draw = ImageDraw.Draw(tile)
    
    # 1. DIBUJAR LAS LÍNEAS DE LA CUADRÍCULA (GRID SEAMLESS)
    # Rejilla muy tenue morado oscuro
    grid_color = (20, 16, 32, 255) 
    draw.line([(0, 127), (127, 127)], fill=grid_color, width=1) # Horizontal inferior
    draw.line([(127, 0), (127, 127)], fill=grid_color, width=1) # Vertical derecha
    
    # 2. DIBUJAR ESTRELLAS PIXEL-ART (Evitando los bordes para garantizar seamless)
    # Estrella 1: Pequeño diamante de neón azul apagado en (32, 40)
    draw.point((32, 40), fill=(0, 210, 255, 255))
    draw.point((31, 40), fill=(0, 210, 255, 100))
    draw.point((33, 40), fill=(0, 210, 255, 100))
    draw.point((32, 39), fill=(0, 210, 255, 100))
    draw.point((32, 41), fill=(0, 210, 255, 100))
    
    # Estrella 2: Pequeño diamante de neón rosa apagado en (96, 80)
    draw.point((96, 80), fill=(255, 0, 127, 255))
    draw.point((95, 80), fill=(255, 0, 127, 100))
    draw.point((97, 80), fill=(255, 0, 127, 100))
    draw.point((96, 79), fill=(255, 0, 127, 100))
    draw.point((96, 81), fill=(255, 0, 127, 100))
    
    # Puntos de estrellas distantes (1 píxel con opacidad baja)
    draw.point((15, 85), fill=(255, 255, 255, 90))
    draw.point((75, 20), fill=(255, 255, 255, 60))
    draw.point((110, 110), fill=(255, 255, 255, 80))
    draw.point((50, 105), fill=(255, 255, 255, 50))
    
    # 3. GUARDAR EN AMBOS DESTINOS (BACKGROUND Y EMBED BG)
    bg_out = os.path.join(out_dir, "tile_background.png")
    embed_out = os.path.join(out_dir, "tile_embed.png")
    
    bg_brain = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/tile_background.png"
    embed_brain = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/tile_embed.png"
    
    # Guardar en local
    tile.save(bg_out, "PNG")
    tile.save(embed_out, "PNG")
    
    # Guardar en brain
    tile.save(bg_brain, "PNG")
    tile.save(embed_brain, "PNG")
    
    print("¡Textura Starry Cyber-Grid unificada generada con éxito!")

if __name__ == "__main__":
    generate_unified_tile()
