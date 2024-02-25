"""
This module contains an Azure Function App that triggers on blob storage events.
It reads the blob content, detects the language of the text using Azure Text Analytics,
and saves the results to CosmosDB.

Author: Ndamulelo Nemakhavhani <info@rihonegroup.com>
License: MIT License

Copyright (c) 2024 Ndamulelo Nemakhavhani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import uuid
import logging
import time

from datetime import datetime

import azure.functions as func

from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient


app = func.FunctionApp()


def _save_to_cosmosdb(record: dict, cosmos_client: CosmosClient):
    logging.debug(f"Saving record to CosmosDB: {record}")
    container_client = cosmos_client.get_database_client("IdentityDemoDB").get_container_client("mydbcontainer")
    return container_client.upsert_item(body=record)


def __get_kv_secret(kv_endpoint: str, secretName: str, credentials: DefaultAzureCredential):
    client = SecretClient(vault_url=kv_endpoint, credential=credentials)
    retrieved_secret = client.get_secret(secretName)
    return retrieved_secret.value


# TODO: add error handling, retries, etc.
def _detect_language(documents: list[str], azure_ai_language_endpoint: str, azure_ai_lang_credentials) -> list[dict]:
    text_analytics_client = TextAnalyticsClient(
        endpoint=azure_ai_language_endpoint, credential=azure_ai_lang_credentials)

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


@app.function_name(name="TimerTrigger1")
@app.timer_trigger(arg_name="mytimer", schedule="*/10 * * * * *", run_on_startup=True)
def fun1(mytimer: func.TimerRequest):
    logging.info(f"Python timer trigger function executed at: {datetime.now()}")
    return


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
        request_record = {
            "id": str(uuid.uuid4()),
            "fileName": myblob.name,
            "blobPath": myblob.name,
            "fileFormat": myblob.name.split(".")[-1],
            "dateStarted": datetime.datetime.now().isoformat(),
            "status": "Processing"
        }
        request_record = _save_to_cosmosdb(request_record, cosmos_client)

        try:
            api_key = __get_kv_secret(os.environ["KEYVAULT_ENDPOINT"], "language-api-key", credentials)
            detection_outcomes = _detect_language(
                [text], os.environ["AZURE_LANGUAGE_ENDPOINT"], AzureKeyCredential(api_key))
            logging.info(
                f"The primary language detected in the document={myblob.name} is: {detection_outcomes[0]['language']}")

            elapsed = time.perf_counter() - start
            request_record["dateFinished"] = datetime.datetime.now().isoformat()
            request_record["language"] = detection_outcomes[0]["language"]
            request_record["languageCode"] = detection_outcomes[0]["language_code"]
            request_record["metadata"] = {
                "elapsedTime": elapsed
            }
            _save_to_cosmosdb(request_record, cosmos_client)

        except Exception as e:
            logging.exception(f"Error getting tags: {e}\nPlease check the logs and try again.")
            request_record["status"] = "Failed"
            request_record["error"] = str(e)
            request_record["dateFinished"] = datetime.datetime.now().isoformat()
            _save_to_cosmosdb(request_record, cosmos_client)
