from PIL import Image
import os

def autocrop_image(image_path):
    if not os.path.exists(image_path):
        print(f"File {image_path} does not exist!")
        return
        
    img = Image.open(image_path).convert("RGBA")
    
    # getbbox() encuentra el rectángulo exacto que contiene píxeles con opacidad > 0
    bbox = img.getbbox()
    if bbox:
        # Recortar la imagen al tamaño exacto de la silueta
        cropped_img = img.crop(bbox)
        
        # Opcional: Hacerla perfectamente cuadrada añadiendo un mínimo de padding si es necesario,
        # pero para TextureRect con STRETCH_KEEP_ASPECT_CENTERED, recortarla a su tamaño real ya es perfecto!
        cropped_img.save(image_path, "PNG")
        print(f"Successfully autocropped {image_path} to bounding box {bbox}")
    else:
        print(f"No active pixels found in {image_path} to crop!")

autocrop_image("assets/mujer.png")
autocrop_image("assets/hombre.png")
