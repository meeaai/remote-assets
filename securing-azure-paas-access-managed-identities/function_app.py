import os
import uuid
import azure.functions as func
import datetime
import time
import logging

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

app = func.FunctionApp()
USE_3RD_PARTY_API = os.environ.get("USE_3RD_PARTY_API", "False").lower() == "true"
IDENTITY_CLIENT_ID = os.environ['AZURE_CLIENT_ID']
VAULT_ENDPOINT = os.environ['VAULT_ENDPOINT']
COMPUTER_VISION_REGION = os.environ.get('COMPUTER_VISION_REGION', 'westeurope')


# TODO: Add retries etc
def __get_kv_secret(endpoint: str, secretName: str, credentials: DefaultAzureCredential):
    client = SecretClient(vault_url=endpoint, credential=credentials)
    retrieved_secret = client.get_secret(secretName)
    return retrieved_secret.value


def _get_tags_from_vision_api(image: bytes, api_key: str, region: str = COMPUTER_VISION_REGION) -> list:
    # This function is a mockup of a function that would call the Azure Vision API
    # to get tags for an image.
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Broadway_and_Times_Square_by_night.jpg/450px-Broadway_and_Times_Square_by_night.jpg"
    client = ComputerVisionClient(
        endpoint=f"https://{region}.api.cognitive.microsoft.com/",
        credentials=CognitiveServicesCredentials(api_key)
    )
    image_analysis_response = client.analyze_image(url, visual_features=[VisualFeatureTypes.tags])
    image_analysis_response.response.raise_for_status()
    image_tags = [tag.name for tag in image_analysis_response.tags]
    return image_tags


def _get_tags_from_3rd_party_api(image: bytes) -> list:
    # This function is a mockup of a function that would call a 3rd party API
    # to get tags for an image.
    return ["tag4", "tag5", "tag6"]


def _write_results_to_db(result_record: dict):
    # This function is a mockup of a function that would write the results to a database.
    return result_record


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
    kv_credentials = DefaultAzureCredential(managed_identity_client_id=IDENTITY_CLIENT_ID)

    try:
        vision_api_key = __get_kv_secret(VAULT_ENDPOINT, "vision-api-key", kv_credentials)
        tags = _get_tags_from_vision_api(api_key=vision_api_key, image=blob_content) if not USE_3RD_PARTY_API \
            else _get_tags_from_3rd_party_api(blob_content)
        logging.info(f"Tags: {tags}")
    except Exception as e:
        logging.exception(f"Error getting tags: {e}\nPlease check the logs and try again.")
        return

    result_record = {
        "id": str(uuid.uuid4()),
        "fileName": myblob.name,
        "fileFormat": myblob.name.split(".")[-1],
        "tags": tags,
        "Is3rdPartyAPI": USE_3RD_PARTY_API,
        "dateCreated": datetime.datetime.now().isoformat()
    }
    _write_results_to_db(result_record)
    logging.debug(f"Result record: {result_record}")
    elapsed = time.perf_counter() - start
    logging.info(f"Finished tagging image in {elapsed:0.4f}s")
