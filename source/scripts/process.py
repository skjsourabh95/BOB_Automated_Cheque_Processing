from scripts.form_recognizer import extract_information
from scripts.azure_ocr_extraction import extract_information_unknown
from scripts.masking_kyc import mask_documents
from scripts.signature_detection import detect_signature
from scripts.utility import upload_blob,check_signature_from_azure
from scripts.optimization import optimize
from scripts.extract_image_from_pdf import extract_image
from scripts.signature_verification import verify_signature
from scripts.draw_bboxes import draw_box
import json,os
from scripts.storage import insert_data

with open('./scripts/azure_config.json','r') as f:
    config = json.load(f)

detection_threshold = 0.10

def process_cheque(path):
    try:
        response = {}
        
        if 'pdf' in path.lower():
            print("INFO: EXTRACTING IMAGES FROM PDF!")
            path = extract_image(path,debug=False)
            print()
        
        print("INFO: STARTING OPTIMIZATION")
        path,reduction = optimize(path,debug=False)
        print()

        print("INFO : UPLOADING FILE TO AZURE BLOB")
        upload_url = upload_blob(path,config["container_name"],config["connect_str"])
        print()

        print("INFO : EXTRACTING DATA FROM THE DOCUMENT UPLOADED!")
        data_extracted = extract_information(upload_url,config)
        if data_extracted['document_detected'] and float(list(data_extracted['document_detected'].values())[0]) <= detection_threshold:
            print("INFO : DOCUMENT CONFIDENCE LOW IN TRAINED MODEL -> USING GENERIC MODEL!")
            data_extracted = extract_information_unknown(upload_url,config)
        else:
            print("INFO : DOCUMENT TRAINED IN FORM RECOGNIZER CHANGING DETECTED DOCUMENT!")
        print("INFO : DATA EXTRACTED :",list(data_extracted.keys()))
        print("INFO : LABELS DETECTED :",data_extracted['identified_labels'])
        print()
        try:
            name = data_extracted['identified_labels'].get('account_holder_name',None).get("value",None)
        except:
            name = None

        print("NAME DETECTED:",name)
       
        print("INFO : DETECTING SIGNATURE IN THE DOCUMENT UPLOADED!")
        signature_present,signatures_detected = detect_signature(path,debug = False)
        print("INFO : SIGNATURE DETECTED FROM LOCAL MODEL :",signature_present)
        signature_present = check_signature_from_azure(data_extracted["identified_labels"])
        print("INFO : SIGNATURE DETECTED FROM AZURE :",signature_present)
        print("INFO : SIGNATURE DETECTED FINAL :",signature_present)
        print()
        signatures_verified = False
        verified_details = {}
        if signature_present:
            print("INFO : VERIFYING SIGNATURE IN THE DOCUMENT UPLOADED WITH THE NAME EXTRACTED!")
            signatures_verified,verified_details = verify_signature(path,signature_present,signatures_detected,data_extracted,name,debug = False)
            print("INFO : SIGNATURE VERIFICATION:",signatures_verified)
            print()


        response = {
            "local_path":path,
            "blob_url":upload_url,
            "signature_present":signature_present,
            "signatures_verified":signatures_verified,
            "data_extracted":data_extracted
        }
        response.update(verified_details)
        print()
        print("INFO : MASKING IMAGE DATA")
        mask_documents(path,data_extracted['labels_coordinates'])
        print("INFO : MASKING DONE")
        print()


        draw_box(path,response)

        # save records
        insert_data(response)
        filename = path.split(os.sep)[-1].split(".")[0] + ".json"

        print("INFO : SAVING RESPONSE")
        output_path = os.path.join(f"{os.sep}".join(path.split(os.sep)[:-1]),filename)
        with open(output_path, "w") as f:
            json.dump(response,f,indent=4)
        print("INFO : OUTPUT FILE SAVED AT: ",output_path)
        print("INFO : PROCESS COMPLETED!")

        return reduction
    except Exception as e:
        print("ERROR : ",str(e))

if __name__ == "__main__":  
    # path = "../data/sample_data/cheque (1).png"
    # path = "../data/sample_data/cheque_sign.png"
    # path = "../data/sample_data/cheque-hindi.png"
    path = "../data/sample_data/cheque-eng.png"
    # path = "../data/sample_data/cheque copy.png"
    process_cheque(path)
