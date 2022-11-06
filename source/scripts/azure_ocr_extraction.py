from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient


def extract_information_unknown(formUrl,config):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=config["FORM_ENDPOINT"], credential=AzureKeyCredential(config["FORM_KEY"])
    )
    poller = document_analysis_client.begin_analyze_document_from_url(
        "prebuilt-document", formUrl)

    result = poller.result()

    identified_keys = {}
    for kv_pair in result.key_value_pairs:
        if kv_pair.key and kv_pair.value:
            identified_keys[kv_pair.key.content] = kv_pair.value.content
    
    labels_coordinates = {}
    for idx, document in enumerate(result.documents):
        for name, field in document.fields.items():
            labels_coordinates[name] = [int(field.bounding_regions[0].polygon[0].x),int(field.bounding_regions[0].polygon[0].y),int(field.bounding_regions[0].polygon[2].x),int(field.bounding_regions[0].polygon[2].y)]
    
    
    unstructured_data_extracted = {}
    for page in result.pages:
        temp  = []
        for line in page.lines:
            temp.append(line.content.encode('utf-8').decode())
        
        unstructured_data_extracted[page.page_number] = temp
    
    structured_data = {}
    for i, table in enumerate(result.tables):
        temp = []
        for cell in table.cells:
            temp.append([cell.row_index, cell.column_index, cell.content.encode('utf-8').decode()])
        structured_data[i+1] = temp

    return {
        "identified_labels":identified_keys,
        "labels_coordinates":labels_coordinates,
        "unstructured_data":unstructured_data_extracted,
        "structured_data":structured_data
        }