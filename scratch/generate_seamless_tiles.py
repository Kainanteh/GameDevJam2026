import os
import random
from PIL import Image, ImageDraw

def generate_itch_assets():
    # Directorio de salida
    out_dir = "/home/kainanteh/game-dev-jam-2026"
    
    # 1. RECORTAR EL LOGOTIPO DEL BANNER GENERADO
    banner_path = "/home/kainanteh/.gemini/antigravity/brain/63aa44c6-0eab-45be-a406-ba2aecfa9f7b/banner_camino_ancestral_1779133079502.png"
    logo_out = os.path.join(out_dir, "logo_camino_ancestral.png")
    
    if os.path.exists(banner_path):
        banner = Image.open(banner_path)
        # Recortar la parte superior de la cabecera que contiene el logotipo (coordenadas estimadas del logo)
        # El logo se encuentra centrado arriba. Recortamos aproximadamente y = 90 a y = 350.
        logo_crop = banner.crop((40, 70, banner.width - 40, 340))
        logo_crop.save(logo_out, "PNG")
        print("1. Logotipo del juego recortado y guardado en:", logo_out)
    else:
        print("El banner para recortar no fue encontrado.")

    # 2. GENERAR EL FONDO GENERAL EN MOSAICO (General Background Seamless Tile)
    # Crearemos un azulejo de 64x64 que forme una rejilla tecnológica oscura (estilo Cyber-Grid)
    bg_tile = Image.new("RGBA", (64, 64), (7, 6, 10, 255)) # Color #07060a
    draw_bg = ImageDraw.Draw(bg_tile)
    
    # Dibujar líneas de cuadrícula muy tenues en los bordes para formar una rejilla seamless
    grid_color = (23, 20, 36, 255) # Morado sumamente oscuro y discreto
    draw_bg.line([(0, 63), (63, 63)], fill=grid_color, width=1) # Línea horizontal inferior
    draw_bg.line([(63, 0), (63, 63)], fill=grid_color, width=1) # Línea vertical derecha
    
    # Añadir sutiles motas neón apagadas como estrellas/nodos lejanos (1% de opacidad)
    # Nodo azul
    draw_bg.rectangle([12, 12, 13, 13], fill=(0, 210, 255, 30))
    # Nodo rosa
    draw_bg.rectangle([48, 36, 49, 37], fill=(255, 0, 127, 25) )
    
    bg_out = os.path.join(out_dir, "tile_background.png")
    bg_tile.save(bg_out, "PNG")
    print("2. Textura de cuadrícula de fondo (Seamless General BG) guardada en:", bg_out)

    # 3. GENERAR EL FONDO DEL EMBED EN MOSAICO (Embed BG Seamless Tile)
    # Un mosaico con scanlines sutiles para la zona del reproductor del juego
    embed_tile = Image.new("RGBA", (64, 64), (20, 17, 30, 255)) # Color #14111e (ligeramente más claro)
    draw_embed = ImageDraw.Draw(embed_tile)
    
    # Dibujar scanlines horizontales alternas sumamente tenues
    scanline_color = (28, 24, 43, 255)
    for y in range(0, 64, 4):
        draw_embed.line([(0, y), (63, y)], fill=scanline_color, width=1)
        
    embed_out = os.path.join(out_dir, "tile_embed.png")
    embed_tile.save(embed_out, "PNG")
    print("3. Textura de scanlines del reproductor (Seamless Embed BG) guardada en:", embed_out)

if __name__ == "__main__":
    generate_itch_assets()
