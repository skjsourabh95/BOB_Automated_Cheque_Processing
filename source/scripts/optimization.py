import numpy as np
from scripts.compress import compress_asset
from scripts.realign import realign_asset
from scripts.whitespace import remove_whitespaces
import cv2
import os

def optimize(path,compress=True,trim=True,realign=True,debug=True):
    output_path = "./data/tmp/"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    
    output_path = os.path.join(output_path,os.path.basename(path))

    if compress:
        print("INFO: STARTING COMPRESSION")
        reduction = compress_asset(path,output_path)
    if trim:
        print("INFO: STARTING WHITESPACE REDUCTION AND CORRECTION")
        remove_whitespaces(output_path,output_path)
    if realign:
        print("INFO: STARTING ALIGNMENT CORRECTION")
        realign_asset(output_path,output_path)

        
    template = cv2.imread(path)
    image = cv2.imread(output_path)
    
    h1, w1 = template.shape[:2]
    h2, w2 = image.shape[:2]


    #create empty matrix
    vis = np.zeros((max(h1, h2), w1+w2,3), np.uint8)

    #combine 2 images
    vis[:h1, :w1,:3] = template
    vis[:h2, w1:w1+w2,:3] = image
    
    if debug:
        # show the two output image alignment visualizations
        cv2.imshow("Image Processed", vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    filename = f"{output_path.split(os.sep)[-1].split('.')[0]}-optimized.jpeg"
    out_path = os.path.join(f"{os.sep}".join(output_path.split(os.sep)[:-1]),filename)
    
    cv2.imwrite(out_path,vis)

    return output_path,reduction
        