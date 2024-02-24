# Azure Functions Runtime Managed Identity Authentication

- **Author**: [Ndamulelo Nemakhavhani](https://blog.ndamulelo.co.za/about)
- **Article**: [Azure Functions Runtime with Managed Identity Authentication]()
- **Issues**: [info@rihonegroup.com](mailto:info@info@rihonegroup.com)
- **Date**: 2024-02-24

> **Azure Managed Identities** provide a secure and simple way to access Azure resources **without the need to store credentials** in code or configuration files. This demo illustrated the benefits of using a managed identity in place of the `AzureWebJobsStorage` connection string in an Azure Functions app.


Managed Identities offer a lot of benefits, inculding
- Reduced security risk: No need to store credentials in code or configuration files which can be misused or leaked.
- Auditing and compliance: It might be easier to track and audit the use of managed identities in your environment compared to connection strings.
- Simplified management: You no longer need to manage and rotate credentials for the storage account.


## Prerequisites

- Azure subscription
- Azure CLI
- Azure Bicep
- Azure Functions Core Tools

## Deployment

- Please note that to deploy the resources in this demo, you will need to have the necessary permissions to create and assign permissions on a Resource Group or Subscription level. For this example, the user is assigned the `Role Based Access Control Administrator` role.

<br/>

1. [Optional] Create a resource group if you do not have one already

   ```bash
   az group create --name fn-app-identity-rg --location westeurope
   ```

2. Deploy bicep template

   ```bash

   az deployment group create --resource-group fn-app-identity-rg  --template-file ./main.bicep --confirm-with-what-if

   # Note: We are not using the `--parameters` flag as the template has default values for the parameters. You could create a parameters file or enter the values directly in the command line if you want to override the default values.
   ```

3. Managed Identity roles

- At minimum, the identity used by your function app runtime must have the `Storage Blob Data Owner` role, however, more roles may be required based on the types of bindings used in your function app. You can learn more about this [here](https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial)

## Example workflow

- To illustrate the benefits of using managed identities in an Azure Functions app, we will create a use a simple workflow to detect the language of
  a text document using the [Azure AI Language](https://azure.microsoft.com/en-us/services/cognitive-services/language/) service. The process flow is as follows:

  1. A new text document is uploaded to a storage account
  2. A blob trigger function is triggered by the new document
  3. The function sends the document to the Azure AI Language service for analysis
  4. The function creates a new record in a CosmosDB database with the document URL and the language detected
  5. (Optional) Instead of using [Azure AI Language](https://azure.microsoft.com/en-us/services/cognitive-services/language/), you can use a language model from other providers like Google Cloud Natural Language API, AWS Comprehend, etc.

## Cleanup

- If you do not intend to keep the resources, you can delete the resource group to remove all the resources created in this demo.

  ```bash
  az group delete --name fn-app-identity-rg  --yes --no-wait
  ```


## Limitations

While the use of managed identities is a secure and convenient way to access Azure resources, there are some limitations to be aware of:

1. Some services do not [support managed identities](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/managed-identities-status). For example, you cannot use a managed identity to access Azure SMB file shares. Fortunately this can be easily solved by using a service like Azure Key Vault to store the credentials and then use a managed identity to access the Key Vault.

2. Managed Identities are only available in Azure and for services that utilise [Microsoft Entra ID RBAC (Role Based Access Control)](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/services-id-authentication-support). If your services are hosted on other cloud providers or on-premises, you will need to use other methods to manage access.

3. Managed Identities are not available in all regions. You can check the availability of managed identities in your region [here](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview#availability)

  <br/>
  <br/>

# Troubleshooting

- **Deployment permissions**: If you encounter an Authorization error during deployment, ensure that you have the necessary permissions to create and assign permissions on a Resource Group or Subscription level. Note that having Contributor permissions on a Resource Group does not automatically grant you the ability to assign permissions to a managed identity.

- \*\*...role definition with ID '00000000000000000000000000000002' does not exist": If you ecnounter this error while deploying the template, try using the Azure CLI to assign the role to the managed identity instead

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

- Better yet, you could define a custom role with the necessary permissions and assign it to the managed identity. This will give you more control over the permissions granted to the managed identity. For example:

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

- Create the custom role using Azure CLI

```bash
az cosmosdb sql role definition create --account-name $accountName \
   --resource-group $resourceGroupName \
   --body custom-role.json
```

- Assign the custom role to the managed identity

```bash
az cosmosdb sql role assignment create --account-name $accountName \
   --resource-group $resourceGroupName \
   --scope "/" \
   --principal-id $principalId \
   --role-definition-id $roleDefinitionId
```

---

# Related Links

- [Azure AI Language RBAC](https://learn.microsoft.com/en-za/azure/ai-services/language-service/concepts/role-based-access-control)
- [Azure Function Runtime Keyless Authentication - Tutorial](https://learn.microsoft.com/en-us/azure/azure-functions/functions-identity-based-connections-tutorial)
- [Securing Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/security-concepts?tabs=v4#secret-repositories)
