from PIL import Image, ImageDraw
import os


color = (0, 165, 255) #BGR

def mask_documents(path,cords,debug=False):
    # print(cords)
    mask = Image.open(path)
    draw = ImageDraw.Draw(mask)
    for label in ["account_no","account_holder_name"]:
        if label in cords and len(cords[label]) > 0:
            (x1, y1, x2, y2) = cords[label]
            draw.rectangle(((x1, y1), (x2, y2)), fill = True)
    
    if debug:
        mask.show()

    filename = f"{path.split(os.sep)[-1].split('.')[0]}-masked.jpeg"
    output_path = os.path.join(f"{os.sep}".join(path.split(os.sep)[:-1]),filename)
    print(output_path)
    if mask.mode in ("RGBA", "P"): 
        mask = mask.convert("RGB")
    mask.save(output_path)
   
