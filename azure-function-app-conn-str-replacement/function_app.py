import os
import logging
import time

import azure.functions as func

from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

app = func.FunctionApp()


def _save_to_cosmosdb(record: dict, cosmos_client: CosmosClient):
    logging.debug(f"Saving record to CosmosDB: {record}")
    container_client = cosmos_client.get_database_client("IdentityDemoDB").get_container_client("mydbcontainer")
    return container_client.upsert_item(body=record)


def _detect_language(documents: list[str], azure_ai_language_endpoint: str, azure_ai_lang_credentials) -> list[dict]:
    endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    result = text_analytics_client.detect_language(documents)
    reviewed_docs = [doc for doc in result if not doc.is_error]
    outcomes = []
    for idx, doc in enumerate(reviewed_docs):
        outcomes.append({
            "id": idx,
            "language": doc.primary_language.name,
            "language_code": doc.primary_language.iso6391_name
        })
    return outcomes


@app.function_name(name="BlobTrigger1")
@app.blob_trigger(arg_name="myblob",
                  path="myblobcontainer/{name}",
                  connection="AzureWebJobsStorage")
def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    start = time.perf_counter()
    blob_content: bytes = myblob.read()
    text = blob_content.decode("utf-8")
    if len(text) < 100:  # This is arbitrary
        logging.warning(f"Text is too short: {text}")
        return

    # Authenticate with managed identity to acess PAAS services
    # If you are using a System managed identity, you can use the DefaultAzureCredential class to authenticate
    if 'USER_IDENTITY_CLIENT_ID' not in os.environ:
        credentials = DefaultAzureCredential()
    else:
        credentials = DefaultAzureCredential(managed_identity_client_id=os.environ['USER_IDENTITY_CLIENT_ID'])

    # Authenticate with managed identity to access Cosmos DB client
    with CosmosClient(url=os.environ['COSMOSDB_ENDPOINT'], credential=credentials) as cosmos_client:
        pass
    
    elapsed = time.perf_counter() - start
