"""
Simple python wrapper script to use ghoscript function to compress PDF files.
Compression levels:
    0: default
    1: prepress
    2: printer
    3: ebook
    4: screen
Dependency: Ghostscript.
"""

import subprocess
import os.path
import sys
import shutil
from PIL import Image
import os



def compress_pdf(input_file_path, output_file_path, power=0):
    """Function to compress PDF via Ghostscript command line interface"""
    quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }

    # Basic controls
    # Check if valid path
    if not os.path.isfile(input_file_path):
        print("Error: invalid path for input PDF file")
        sys.exit(1)

    # Check if file is a PDF by extension
    if input_file_path.split('.')[-1].lower() != 'pdf':
        print("Error: input file is not a PDF")
        sys.exit(1)

    gs = get_ghostscript_path()
    print("Compress PDF...")
    initial_size = os.path.getsize(input_file_path)
    print("Original Size {0:.1f}MB".format(initial_size / 100000))
    subprocess.call([gs, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS={}'.format(quality[power]),
                    '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    '-sOutputFile={}'.format(output_file_path),
                     input_file_path]
    )
    final_size = os.path.getsize(output_file_path)
    ratio = 1 - (final_size / initial_size)
    print("Compression by {0:.0%}.".format(ratio))
    print("Final file size is {0:.1f}MB".format(final_size / 1000000))
    print("Done.")
    return "Final file size is {0:.1f}MB".format(final_size / 1000000)

def get_ghostscript_path():
    gs_names = ['gs', 'gswin32', 'gswin64']
    for name in gs_names:
        if shutil.which(name):
            return shutil.which(name)
    raise FileNotFoundError(f'No GhostScript executable was found on path ({"/".join(gs_names)})')


def compress_images(image_loc,new_image_loc,resize=False,same_res=True):
    image = Image.open(image_loc)
    print("BEFORE:",image.format, image.size, image.mode, os.stat(image_loc).st_size)

    # resizing and optimization
    if resize:
        new_image = image.resize((500,500), resample=1)
        new_image.save(new_image_loc)
        print("AFTER:",new_image.format, new_image.size, new_image.mode, os.stat(new_image_loc).st_size)
        print("Reduction Ratio: {0:.1f} %".format(((os.stat(image_loc).st_size - os.stat(new_image_loc).st_size)/os.stat(image_loc).st_size)*100))

    # no resulution change
    if same_res:
        image.save(new_image_loc,optimize=True, quality=35)
        print("AFTER:",image.format, image.size, image.mode, os.stat(new_image_loc).st_size)
        print("Reduction Ratio: {0:.1f} %".format(((os.stat(image_loc).st_size - os.stat(new_image_loc).st_size)/os.stat(image_loc).st_size)*100))
    
    return "Reduction_Ratio: {0:.1f} %".format(((os.stat(image_loc).st_size - os.stat(new_image_loc).st_size)/os.stat(image_loc).st_size)*100)
    

def compress_asset(inp,out):
    if "pdf" in inp.lower():
        reduction = compress_pdf(inp, out, power=4)
        return reduction
    else:
        reduction = compress_images(inp,out)
        return reduction