import cv2
import torch
import matplotlib.pyplot as plt

yolo_path = "./scripts/yolov5"
model_path='./scripts/yolov5/runs/train/Tobacco-run/weights/best.pt'
model = torch.hub.load(yolo_path, 'custom', path=model_path, source='local',device='cpu',_verbose=False)
print("Model Loaded")

def detect_signature(path,debug = False):
    classes = model.names
    image = cv2.imread(path)
    results = model(image)
    labels, cord, conf = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-2], results.xyxyn[0][:, -2]
    
    signatures_detected = []
    for i in range(len(labels)):
        row = cord[i]
        x_shape, y_shape = image.shape[1], image.shape[0]
        x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
        # bgr = (0, 255, 0)
        # cv2.rectangle(img, (x1, y1), (x2, y2), bgr, 5)
        # cv2.putText(img, f'{classes[int(labels)]}:{round(float(conf), 2)}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        if debug:
            crop_img = image[y1:y2, x1:x2]
            fig, ax = plt.subplots(figsize=(3, 1))
            ax.imshow(crop_img)
            ax.set_axis_off()
            plt.tight_layout()
            plt.show()
        
        signatures_detected.append({"signature_detection_conf":conf[i].item(),
                                    "signature_class":classes[int(labels[i])],
                                    "sign_image_cords" :  (x1, y1, x2, y2)
                                    })
        
    print(signatures_detected)

    if len(signatures_detected) > 0:
        return True,signatures_detected
    return False,[]
    
        