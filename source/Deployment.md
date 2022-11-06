# [BOB - automate-cheque-processing](https://www.techgig.com/hackathon/automate-cheque-processing)

## Scope of Work of the PoC

The POC currently is restricted to handling only 
    
    - AI Services to upload a bank cheque both printed and handwritten
    - Cognitive Services to extract structured and unstructured text from the cheques(Azure Computer Vision OCR)
    - Custom Processor Models for each document type trained to extract required entities (Azure Form Recognizer)
    - Signature Detection and Verification using custom model and azure form recognizers
    - Azure translation service to translate cheques
    - Azure WebApps for parallel processing cheques 
    - Masking of text from cheques
    - Azure Storage Containers to store documents/images


Features - 

    1. Image document Identification
    2. Extract structured and unstructured text
    3. Extract required entities
    4. Signature Identification
    5. Signature Verification
    6. Masking of text from KYC documents
    7. Language Detection and Translation

## Pre-requisites from the Bank’s side
1. Azure Account
2. Works with both CPU and GPU
3. Setup & Deployment will not require more than a week.
4. Training new models with good data and Pipeline creation cna take somewhere between 8-10 weeks.

## Infrastructure required for setting up the PoC. 
1. The Images can be uploaded to a container storage.
2. An Azure Webapp to deploy this code and call it using REST API's.
3. Azure Form Recognizers 
4. Azure language translation


## High level PoC Key Performance Indicators (KPIs) 
- Samples Processed are provide in the [images](../images/) directory and Video of execution can be found [here](https://drive.google.com/file/d/1gRcZK0jRq_GusskbYgupXoLXdZ-89Jcg/view?usp=sharing) 

- I have trained around 10 different cheques ( 6 printed and 4 handwritten ) and composed them into one model for use due to cost constraints. This can be scaled up with different form types.

- The Form Recognizer Models Entity confidence score can be found [here](./scripts/BOB.json). 

- For Example Entities Trained & Extracted from PAN CARD Form Recognizer Models
    ```"account_holder_name": 0.5,
        "account_no": 0.995,
        "amount": 0.833,
        "amount_in_words": 0.667,
        "issue_date": 0.667,
        "signature": 0.667
    ```

## Deployment Guide
### Local Deployment
1. [Ghostscript](https://www.ghostscript.com/doc/current/Install.htm)
2. [Poppler](https://poppler.freedesktop.org/)
3. [Imagewick](https://imagemagick.org/script/download.php)
4. [Python](https://www.python.org/downloads/release/python-390/)
4. First Run will install all the required custom models being used.
5. The Credentials and keys provided with this POC will be available till the challenge duration
6. Download best.pt from [here](https://drive.google.com/file/d/1YmR3HqUw1TYmIy6MG8yioX8FWAq9uQvn/view?usp=sharing) and  paste it in source/scripts/yolov5/runs/train/Tobacco-run/weights/best.pt
7. Download vgg16_weights_tf_dim_ordering_tf_kernels.h5 from [here](https://drive.google.com/file/d/1AoXV2KLeMVJPBf9brMQohcpa5c9Sespq/view?usp=share_link) and paste it in source/scripts/vgg16_weights_tf_dim_ordering_tf_kernels.h5
```cmd
pip3 install vitualenv
virtualenv img_ocr
source img_ocr/bin/activate   
pip3 install -r requirements.txt
python index.py
open -> http://0.0.0.0:8050/
```

### Docker Deployment
```cmd
docker build -t cheque .
docker run -d -p 8050:8050 cheque
open -> http://0.0.0.0:8050/
```
