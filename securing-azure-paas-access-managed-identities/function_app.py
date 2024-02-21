import os
import uuid
import azure.functions as func
import datetime
import time
import logging

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.credentials import AzureKeyCredential
from azure.cosmos import CosmosClient
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures, ImageAnalysisResult

app = func.FunctionApp()
USE_3RD_PARTY_API = os.environ.get("USE_3RD_PARTY_API", "False").lower() == "true"
IDENTITY_CLIENT_ID = os.environ['AZURE_CLIENT_ID']
VAULT_ENDPOINT = os.environ['VAULT_ENDPOINT']
IS_DEVELOPMENT = os.environ.get('IS_DEVELOPMENT', "False").lower() == "true"
COMPUTER_VISION_REGION = os.environ.get('COMPUTER_VISION_REGION', 'westeurope')
COMPUTER_VISION_ENDPOINT = os.environ.get(
    'COMPUTER_VISION_ENDPOINT', f"https://{COMPUTER_VISION_REGION}.api.cognitive.microsoft.com/")
DB_ENDPOINT = os.environ['DB_ENDPOINT']


# TODO: Add retries etc
def __get_kv_secret(endpoint: str, secretName: str, credentials: DefaultAzureCredential):
    client = SecretClient(vault_url=endpoint, credential=credentials)
    retrieved_secret = client.get_secret(secretName)
    return retrieved_secret.value


def _get_tags_from_vision_api(image: bytes, api_key: str, endpoint: str) -> list:
    logging.info(f"Getting tags from vision API")
    start = time.perf_counter()
    client = ImageAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))
    image_analysis_res: ImageAnalysisResult = client._analyze_from_image_data(image_content=image,
                                                                              visual_features=[VisualFeatures.TAGS],
                                                                              language="en")
    model = image_analysis_res.model_version
    has_tags = image_analysis_res.tags is not None and len(image_analysis_res.tags.list) > 0
    elapsed = round(time.perf_counter() - start, 4)
    image_tags = [tag.name for tag in image_analysis_res.tags.list] if has_tags else []
    logging.info(f"Finished getting ${len(image_tags)} tags from vision API using Model={model}, Duration={elapsed}s")
    return image_tags


def __save_to_cosmos_db(record: dict, cosmos_client: CosmosClient):
    logging.debug(f"Saving record to CosmosDB: {record}")
    container_client = cosmos_client.get_database_client("IdentityDemoDB").get_container_client("mydbcontainer")
    return container_client.upsert_item(body=record)


def _get_tags_from_3rd_party_api(image: bytes) -> list:
    # This function is a placeholder of a function that would call a 3rd party API
    # to get tags for an image.
    return ["tag4", "tag5", "tag6"]


@app.function_name(name="BlobTrigger1")
@app.blob_trigger(arg_name="myblob",
                  path="myblobcontainer/{name}",
                  connection="AzureWebJobsStorage")
def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Name from binding: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    start = time.perf_counter()
    blob_content: bytes = myblob.read()

    # Authenticate with user managed identity to acess PAAS services
    credentials = DefaultAzureCredential(managed_identity_client_id=IDENTITY_CLIENT_ID) if not IS_DEVELOPMENT else \
        DefaultAzureCredential()
    cosmos_client = CosmosClient(url=DB_ENDPOINT,
                                 credential=credentials)

    request_record = {
        "id": str(uuid.uuid4()),
        "fileName": myblob.name,
        "blobPath": myblob.name,
        "fileFormat": myblob.name.split(".")[-1],
        "Is3rdPartyAPI": USE_3RD_PARTY_API,
        "dateStarted": datetime.datetime.now().isoformat(),
        "status": "Processing"
    }
    request_record = __save_to_cosmos_db(request_record, cosmos_client)

    try:
        vision_api_key = __get_kv_secret(VAULT_ENDPOINT, "vision-api-key", credentials)
        tags = _get_tags_from_vision_api(api_key=vision_api_key, image=blob_content, endpoint=COMPUTER_VISION_ENDPOINT) if not USE_3RD_PARTY_API \
            else _get_tags_from_3rd_party_api(blob_content)
        logging.info(f"Tags: {tags}")
    except Exception as e:
        logging.exception(f"Error getting tags: {e}\nPlease check the logs and try again.")
        request_record["status"] = "Failed"
        request_record["error"] = str(e)
        request_record["dateFinished"] = datetime.datetime.now().isoformat()
        __save_to_cosmos_db(request_record, cosmos_client)
        return

    elapsed = time.perf_counter() - start
    request_record["dateFinished"] = datetime.datetime.now().isoformat()
    request_record["status"] = "Completed"
    request_record["tags"] = tags
    request_record["duration"] = round(elapsed, 4)
    logging.info(f"Finished tagging image in {elapsed:0.4f}s")
    __save_to_cosmos_db(request_record, cosmos_client)
