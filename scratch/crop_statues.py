from PIL import Image

def crop_image(path):
    im = Image.open(path)
    bbox = im.getbbox()
    if bbox:
        cropped = im.crop(bbox)
        cropped.save(path)
        print(f"Cropped {path} to {cropped.size}")
    else:
        print(f"No bbox found for {path}")

crop_image("assets/estatuaHombre.png")
crop_image("assets/estatuaMujer.png")
