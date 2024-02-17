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
- Perimissions to create & assign permissions on a Resource Group or Subscription level - For this example, the user is assigned the `
Role Based Access Control Administrator` role.

## Deployment

1. [Optional] Create a resource group if you do not have one already

   ```bash
   az group create --name identity-demo2024-rg --location westeurope
   ```

2. Deploy bicep template

   ```bash

   az deployment group create --resource-group identity-demo2024-rg --template-file ./main.bicep --confirm-with-what-if

   # Note: We are not using the `--parameters` flag as the template has default values for the parameters. You could create a parameters file or enter the values directly in the command line if you want to override the default values.
   ```

3. If all well, you should now be able to try the example workflow described in the next section.


## Example workflow

- To illustrate the benefits of using a user-assigned managed identity, we will an example of an Event-driven serverless workflow 
that will automatically tag product images using [Azure Vision API](https://azure.microsoft.com/en-us/products/ai-services/ai-vision) for a fictitious e-commerce platform. The process flow is as follows:

  1. A new product image is uploaded to a storage account
  2. A blob trigger function is triggered by the new image
  3. The function sends the image to the Azure Vision API for analysis
  4. The function tags the image with the results of the analysis
  5. The function creates a new record in a CosmosDB database with the image URL and the tags
  6. (Optional) Instead of using [Azure Vision API](https://azure.microsoft.com/en-us/products/ai-services/ai-vision), you can use a vision model from other providers like Google Cloud Vision API, AWS Rekognition, etc. Store 
    the API keys in Azure Key Vault and use the managed identity to access the keys.



## Cleanup

- If you do not intend to keep the resources, you can delete the resource group to remove all the resources created in this demo.

  ```bash
  az group delete --name identity-demo2024-rg --yes --no-wait
  ```

  <br/>
  <br/>


# Troubleshooting

   * **Deployment permissions**: If you encounter an  Authorization error during deployment, ensure that you have the necessary permissions to create and assign permissions on a Resource Group or Subscription level. Note that having Contributor permissions on a Resource Group does not automatically grant you the ability to assign permissions to a managed identity.


   * **...role definition with ID '00000000000000000000000000000002' does not exist": If you ecnounter this error while deploying the template, try using the Azure CLI to assign the role to the managed identity instead

   ```bash 
   resourceGroupName='<myResourceGroup>'
   accountName='<myCosmosAccount>'
   readOnlyRoleDefinitionId = '00000000-0000-0000-0000-000000000002' # This is the ID of the Cosmos DB Built-in Data contributor role definition
   principalId = "<replace me>" # This is the object ID of the managed identity.

   az cosmosdb sql role assignment create --account-name $accountName \ 
      --resource-group $resourceGroupName \
      --scope "/" \
      --principal-id $principalId \
      --role-definition-id $readOnlyRoleDefinitionId
   ```

   * Better yet, you could define a custom role with the necessary permissions and assign it to the managed identity. This will give you more control over the permissions granted to the managed identity. For example:

   ```json 
   // custom-role.json
   {
      "Name": "CosmosDBDataContributor",
      "IsCustom": true,
      "Description": "Can read and write all data in the Cosmos DB account",
      "Actions": [
            "Microsoft.DocumentDB/databaseAccounts/readMetadata",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/*",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/*"
      ],
      "NotActions": [],
      "DataActions": [],
      "NotDataActions": [],
      "AssignableScopes": [
         "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.DocumentDB/databaseAccounts/{databaseAccountName}"
      ]
   }
   ```

   * Create the custom role using Azure CLI

   ```bash
   az cosmosdb sql role definition create --account-name $accountName \
      --resource-group $resourceGroupName \
      --body custom-role.json
   ```

   * Assign the custom role to the managed identity

   ```bash
   az cosmosdb sql role assignment create --account-name $accountName \
      --resource-group $resourceGroupName \
      --scope "/" \
      --principal-id $principalId \
      --role-definition-id $roleDefinitionId
   ```