import subprocess
import cv2
import numpy as np


def remove_whitespaces(filename,outputfilename):
    # https://github.com/abarker/pdfCropMargins
    if 'pdf' in filename:
        cmd = f"pdf-crop-margins -v -s -p 5 {filename} -o {outputfilename}"
        proc = subprocess.Popen(cmd.split())
        proc.wait()
        
    else:
        # Load image, convert to grayscale, Gaussian blur, Otsu's threshold
        image = cv2.imread(filename)
        original = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3,3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Obtain bounding rectangle and extract ROI
        x,y,w,h = cv2.boundingRect(thresh)
        cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)
        ROI = original[y:y+h, x:x+w]

        # Add alpha channel
        b,g,r = cv2.split(ROI)
        alpha = np.ones(b.shape, dtype=b.dtype) * 50
        ROI = cv2.merge([b,g,r,alpha])

        # cv2.imshow('thresh', thresh)
        # cv2.imshow('image', image)
        # cv2.imshow('ROI', ROI)
        # cv2.waitKey()
        cv2.imwrite(outputfilename,ROI)