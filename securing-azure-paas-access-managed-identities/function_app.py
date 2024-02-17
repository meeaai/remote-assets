import os
import uuid
import azure.functions as func
import datetime
import time
import logging

app = func.FunctionApp()
USE_3RD_PARTY_API = os.environ.get("USE_3RD_PARTY_API", "False").lower() == "true"


def _get_tags_from_vision_api(image: bytes) -> list:
    # This function is a mockup of a function that would call the Azure Vision API
    # to get tags for an image.
    return ["tag1", "tag2", "tag3"]


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
    tags = _get_tags_from_vision_api(blob_content) if not USE_3RD_PARTY_API else _get_tags_from_3rd_party_api(blob_content)
    logging.info(f"Tags: {tags}")
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
    