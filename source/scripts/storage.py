from azure.cosmos import CosmosClient, exceptions, PartitionKey
import json
import random

with open('./scripts/azure_config.json','r') as f:
    config = json.load(f)

client = CosmosClient(config['STORAGE_ENDPOINT'], credential=config['STORAGE_KEY'])
DATABASE_NAME = 'bob'
try:
    database = client.create_database(DATABASE_NAME)
except exceptions.CosmosResourceExistsError:
    database = client.get_database_client(DATABASE_NAME)

CONTAINER_NAME = 'cheque'
try:
    container = database.create_container(id=CONTAINER_NAME, partition_key=PartitionKey(path="/account_no"))
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(CONTAINER_NAME)
except exceptions.CosmosHttpResponseError:
    raise


def insert_data(data):
    record = {}
    record['id'] = str(int(random.uniform(1,100)))
    record['account_no'] = data['data_extracted']['identified_labels']['account_no']['value']
    record['account_holder_name'] = data['data_extracted']['identified_labels']['account_holder_name']['value']
    record['amount_in_words'] = data['data_extracted']['identified_labels']['amount_in_words']['value']
    record['amount'] = data['data_extracted']['identified_labels']['amount']['value']
    record['issue_date'] = data['data_extracted']['identified_labels']['issue_date']['value']
    record['signature'] = data['data_extracted']['identified_labels']['signature']['value']
    if data['signature_present']:
        record['signature_present'] = str(data['signature_present']).lower()
        record['signatures_verified'] = str(data['signatures_verified']).lower()
        record['signature_verification_conf'] = str(data['signature_verification_conf'])
        record['verified_signature_name'] = data['verified_signature_name']
        record['signature_detection_conf'] = str(data['signature_detection_conf'])
    else:
        record['signature_present'] = str(data['signature_present']).lower()
        record['signatures_verified'] = 'False'
        record['signature_verification_conf'] = '0.0'
        record['verified_signature_name'] = "False"
        record['signature_detection_conf'] = '0.0'
    
    container.upsert_item(body = record)

def get_all():
    item_list = list(container.read_all_items(max_item_count=10))
    return item_list