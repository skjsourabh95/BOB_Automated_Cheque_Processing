from scipy.spatial import distance
from tensorflow.keras import Model
from tensorflow.keras import applications
import cv2
import glob,os

def get_signatures():
    preset_signs = {}
    for pth in glob.glob(os.path.join('./data/signatures','*.png')):
        image = cv2.imread(pth)
        preset_signs[os.path.basename(pth).split(".")[0]]  = get_feature_vector(image)
    return preset_signs

def get_feature_vector(img):
    img1 = cv2.resize(img, (224, 224))
    feature_vector = basemodel.predict(img1.reshape(1, 224, 224, 3))
    return feature_vector

def calculate_similarity(vector1, vector2):
    return 1 - distance.cosine(vector1, vector2)


vgg16 = applications.vgg16.VGG16(weights='./scripts/vgg16_weights_tf_dim_ordering_tf_kernels.h5', include_top=True, pooling='max', input_shape=(224, 224, 3))
basemodel = Model(inputs=vgg16.input, outputs=vgg16.get_layer('fc2').output)
preset_signs = get_signatures()


def verify_signature(path,signature_present,signature_detected,data_extracted,extracted_name,debug = False):
    image = cv2.imread(path)
    signatures_verified = {}
    signature_conf = 0
    signature_name = None
    signature_selected = {}
    for signs in signature_detected:
        x1, y1, x2, y2 = signs['sign_image_cords']
        # bgr = (0, 255, 0)
        # cv2.rectangle(img, (x1, y1), (x2, y2), bgr, 5)
        # cv2.putText(img, f'{classes[int(labels)]}:{round(float(conf), 2)}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        crop_img = image[y1:y2, x1:x2]
        f3 = get_feature_vector(crop_img)
        
        for name,sign in preset_signs.items():
            signature_verification_conf = calculate_similarity(sign, f3)
            if signature_conf < signature_verification_conf:
                signature_conf = signature_verification_conf
                signature_name = name
                signature_selected = signs
    
    # print(signature_selected)
    signatures_verified = { "signature_verification_conf":signature_conf,
                            "verified_signature_name":signature_name,
                            "signature_detection_conf":signature_selected["signature_detection_conf"],
                            "signature_class":signature_selected["signature_class"],
                            "sign_image_cords" :  signature_selected["sign_image_cords"]
                            }
    
    print(signatures_verified)
    
    image = cv2.imread(path)
    if signature_present:
        x1, y1, x2, y2 = data_extracted["labels_coordinates"]["signature"]
    else:
        x1, y1, x2, y2 = signatures_verified['sign_image_cords']
    crop_img = image[y1:y2, x1:x2]
    filename = f"{path.split(os.sep)[-1].split('.')[0]}-signature.jpeg"
    output_path = os.path.join(f"{os.sep}".join(path.split(os.sep)[:-1]),filename)
    
    cv2.imwrite(output_path,crop_img)

    if extracted_name and extracted_name.lower() == " ".join(signature_name.split("_")):
        return True, signatures_verified
    else:
        return False, signatures_verified
    