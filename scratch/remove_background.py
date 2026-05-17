from PIL import Image
import os

def make_white_and_transparent(image_path):
    if not os.path.exists(image_path):
        print(f"File {image_path} does not exist!")
        return
        
    img = Image.open(image_path).convert("RGBA")
    datas = img.getdata()
    
    new_data = []
    for item in datas:
        r, g, b, a = item
        # If the pixel is very dark (close to black background)
        if r < 15 and g < 15 and b < 15:
            # Make it fully transparent black
            new_data.append((0, 0, 0, 0))
        else:
            # Convert any non-transparent pixel to pure white while preserving its original alpha (glow)
            new_data.append((255, 255, 255, a))
            
    img.putdata(new_data)
    img.save(image_path, "PNG")
    print(f"Successfully processed {image_path} to white with alpha")

make_white_and_transparent("assets/mujer.png")
make_white_and_transparent("assets/hombre.png")
