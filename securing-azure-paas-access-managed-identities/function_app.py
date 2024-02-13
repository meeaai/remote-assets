import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()


def _get_tags_from_vision_api(image: bytes) -> list:
    # This function is a mockup of a function that would call the Azure Vision API
    # to get tags for an image.
    return ["tag1", "tag2", "tag3"]


def _get_tags_from_3rd_party_api(image: bytes) -> list:
    # This function is a mockup of a function that would call a 3rd party API
    # to get tags for an image.
    return ["tag4", "tag5", "tag6"]


@app.function_name(name="BlobTrigger1")
@app.blob_trigger(arg_name="myblob",
                  path="PATH/TO/BLOB",
                  connection="AzureWebJobsStorage")
def test_function(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    blob_content: bytes = myblob.read()
