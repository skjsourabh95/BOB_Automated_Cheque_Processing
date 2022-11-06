import cv2
import matplotlib.pyplot as plt
import os

def draw_box(path,response,debug=False):
    img = cv2.imread(path)
    
    bgr = (0, 255, 0)
    for name,data,cord in zip(response['data_extracted']['identified_labels'].keys(),response['data_extracted']['identified_labels'].values(),response['data_extracted']['labels_coordinates'].values()):
        # print(data['value'],data['confidence'],cord)
        if len(cord) > 0:
            x1, y1, x2, y2 = cord
            if name == "signature" and not response['signature_present']:
                continue
            cv2.rectangle(img, (x1-10, y1-10), (x2+10, y2), bgr, 5)
            cv2.putText(img, f"{name}:{round(float(data['confidence']),  1)}", (x1-10, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    if debug:
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.imshow(img)
        ax.set_axis_off()
        plt.tight_layout()
        plt.show()

    filename = f"{path.split(os.sep)[-1].split('.')[0]}-labelled.jpeg"
    output_path = os.path.join(f"{os.sep}".join(path.split(os.sep)[:-1]),filename)
    
    cv2.imwrite(output_path,img)