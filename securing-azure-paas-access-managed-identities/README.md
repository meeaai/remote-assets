# Azure User-Assigned Managed Identity - Demo

* **Author**: [Ndamulelo Nemakhavhani](https://blog.ndamulelo.co.za/about)
* **Article**: [Securing Azure PaaS Access Using Managed Identities](https://blog.ndamulelo.co.za/azure-user-assigned-managed-identity-demo)
* **Issues**: [info@rihonegroup.com](mailto:info@info@rihonegroup.com)
* **Date**: 2024-02-14

> **Azure Managed Identities** provide a secure and simple way to access Azure resources **without the need to store credentials** in code or configuration files. This  demo illustrated the benefits of using a user-assigned managed identity on a serverless workflow for tagging product images using **Azure Vision API**.



 ![Azure User-Assigned Managed Identity - Demo](./azure-managed-identity-template.png)


## Prerequisites

- Azure subscription
- Azure CLI
- Perimissions to create & assign permissions on a Resource Group or Subscription level

## Deployment

1. [Optional] Create a resource group

   ```bash
   az group create --name identity-demo2024-rg --location westeurope
   ```

2. Deploy bicep template

   ```bash

   az deployment group create --resource-group identity-demo2024-rg --template-file ./main.bicep
   ```

3. If all well, you should now be able to try the example workflow described in the next section.


## Example workflow

- To illustrate the benefits of using a user-assigned managed identity, we will an example of an Event-driven serverless workflow 
that will automatically tag product images using [Azure Vision API]() for a fictitious e-commerce platform. The process flow is as follows:

  1. A new product image is uploaded to a storage account
  2. A blob trigger function is triggered by the new image
  3. The function sends the image to the Azure Vision API for analysis
  4. The function tags the image with the results of the analysis
  5. The function creates a new record in a CosmosDB database with the image URL and the tags
  6. (Optional) Instead of using [Azure Vision API](), you can use a vision model from other providers like Google Cloud Vision API, AWS Rekognition, etc. Store 
    the API keys in Azure Key Vault and use the managed identity to access the keys.