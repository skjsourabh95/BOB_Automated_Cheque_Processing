
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient


def extract_information(formUrl,config):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=config["FORM_ENDPOINT"], credential=AzureKeyCredential(config["FORM_KEY"])
    )

    # Make sure your document's type is included in the list of document types the custom model can analyze
    poller = document_analysis_client.begin_analyze_document_from_url(config["MODEL_ID"], formUrl)
    result = poller.result()
    indentified_document = {}
    identified_keys = {}
    for idx, document in enumerate(result.documents):
        print("Document has type {}".format(document.doc_type))
        print("Document has confidence {}".format(document.confidence))
        print("Document was analyzed by model with ID {}".format(result.model_id))
        indentified_document[document.doc_type] = document.confidence
        for name, field in document.fields.items():
            identified_keys[name] = {"value":field.value if field.value else field.content,
                                    "confidence":field.confidence
                                    }

    labels_coordinates = {}
    for idx, document in enumerate(result.documents):
        for name, field in document.fields.items():
            try:
                labels_coordinates[name] = [int(field.bounding_regions[0].polygon[0].x),int(field.bounding_regions[0].polygon[0].y),int(field.bounding_regions[0].polygon[2].x),int(field.bounding_regions[0].polygon[2].y)]
            except:
                labels_coordinates[name] = []
    
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
        "document_detected":indentified_document,
        "identified_labels":identified_keys,
        "labels_coordinates":labels_coordinates,
        "unstructured_data":unstructured_data_extracted,
        "structured_data":structured_data
        }
    
