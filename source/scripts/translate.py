import requests
import json

def detect_language(text, key, region, endpoint):
    # Use the Translator detect function
    path = '/detect'
    url = endpoint + path
    # Build the request
    params = {
        'api-version': '3.0'
    }
    headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': region,
    'Content-type': 'application/json'
    }
    body = [{
        'text': text
    }]
    # Send the request and get response
    request = requests.post(url, params=params, headers=headers, json=body)
    response = request.json()
    print(response)
    # Get language
    language = response[0]["language"]
    # Return the language
    return language

def translate(text, source_language, target_language, key, region, endpoint):
    # Use the Translator translate function
    url = endpoint + '/translate'
    # Build the request
    params = {
        'api-version': '3.0',
        'from': source_language,
        'to': target_language
    }
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json'
    }
    body = [{
        'text': text
    }]
    # Send the request and get response
    request = requests.post(url, params=params, headers=headers, json=body)
    response = request.json()
    # Get translation
    translation = response[0]["translations"][0]["text"]
    # Return the translation
    return translation



target_lang = ["en"]
with open('./scripts/azure_config.json','r') as f:
    config = json.load(f)

def translate_cheque(data):
    translated_text = {}
    if "data_extracted" in data:
        if "identified_labels" in data["data_extracted"]:
            for k,v in data["data_extracted"]["identified_labels"].items():
                lang = detect_language(v['value'], config['TRANSLATE_KEY'], config['LOCATION'], config['TRANSLATE_ENDPOINT'])
                translated_text[k] = {"value":translate(v['value'], lang, target_lang, config['TRANSLATE_KEY'], config['LOCATION'], config['TRANSLATE_ENDPOINT']),
                                      "confidence": v['confidence']}
    data['translated_text'] = translated_text
    return translated_text
    