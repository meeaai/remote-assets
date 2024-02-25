#!/bin/bash
set -e
## This is a convenience script to zip the package of the function app project and 
## upload it to a storage container for deployment.
storageAccountName=${1:-myblobstorehbf3keghjkav2}
containerName=${2:-myblobcontainer}
echo "$(date) Packaging and uploading to storage account: $storageAccountName"

mkdir -p bin
zip bin/functionapp.zip requirements.txt function_app.py host.json README.md
echo "$(date) Package zip created"

## Uncomment login command if you are not logged in to azcop
# azcopy login --tenant-id <tenant-id>
azcopy cp "$PWD/bin/functionapp.zip" "https://${storageAccountName}.blob.core.windows.net/${containerName}/deployments/functionapp.zip" --overwrite=true
rm bin/functionapp.zip

echo "$(date) Package uploaded to https://${storageAccountName}.blob.core.windows.net/${containerName}/deployments/functionapp.zip"