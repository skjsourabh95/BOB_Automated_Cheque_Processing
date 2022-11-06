import os
from tqdm import tqdm
from pdf2image import convert_from_path

def extract_image(pdf_path):
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    new_path = f"./tmp/temp.jpeg"
    pages = convert_from_path(pdf_path, 120)
    pages[0].save(new_path, 'JPEG')
    return new_path


def extract_images(pdf_path):
    images = []
    pages = convert_from_path(pdf_path, 120)
    for i,page in tqdm(enumerate(pages)):
        image_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        image_filename = '{}-{}.jpeg'.format(image_filename, i)
        image_filename = os.path.join("./tmp", image_filename)
        page.save(image_filename, 'JPEG')
        images.append(image_filename)
    return images