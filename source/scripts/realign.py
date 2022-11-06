import cv2
import numpy as np

import math
from typing import Tuple, Union
import cv2
import numpy as np
from deskew import determine_skew


def rotate(image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)


def realign_asset(imFilename,outfilename,debug=False):
    if "pdf" in imFilename:
        print("ERROR : PLEASE PROVIDE AN IMAGE!")
        return
    if not outfilename:
        print("ERROR : PLEASE PROVIDE A OUTPUT IMAGE PATH!")
        return
    
    image = cv2.imread(imFilename)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    angle = determine_skew(grayscale)
    rotated = rotate(image, angle, (0, 0, 0))
    stacked = np.hstack([image, rotated])
    
    if debug:
        # show the two output image alignment visualizations
        cv2.imshow("Image Alignment Stacked", stacked)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    cv2.imwrite(outfilename,rotated)

if __name__ == '__main__':
    # Read reference image
    refFilename = "../sample_data/Form-60.jpeg"
    imFilename = "../sample_data/Form-60-rotated.jpeg"

    template = cv2.imread(refFilename)
    image = cv2.imread(imFilename)
    aligned = realign_asset(image, template, debug=True)

    stacked = np.hstack([aligned, template])
    # show the two output image alignment visualizations
    cv2.imshow("Image Alignment Stacked", stacked)
    cv2.waitKey(0)
    cv2.destroyAllWindows()