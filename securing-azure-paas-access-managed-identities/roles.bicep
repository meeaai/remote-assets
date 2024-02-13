@description('The name of the managed identity resource.')
param identityName string = 'myuseridentity-001'

@description('The primary location of the managed identity resource.')
param location string = resourceGroup().location

@description('Whether the managed identity has contributor access on the resource group level')
param isRGContributor bool = false

@description('The tags to associate with the managed identity resource.')
param tags object = {
  Environment: 'Demo'
  Contact: 'info@mungana.com'
  Repo: 'https://github.com/rihonegroupdev/remote-assets/securing-azure-paas-access-managed-identities'
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: identityName
  scope: resourceGroup()
}

// Assign automation roles
// Role Definitions Reference: https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
resource resourceGroupAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (isRGContributor) {
  name: guid('${managedIdentity.name}-rg-control-access')
  scope: resourceGroup()
  properties: {
    description: 'Allow identity to perform automated management tasks on the resource group'
    principalType: 'ServicePrincipal'
    principalId: managedIdentity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b24988ac-6180-42a0-ab88-20f7382dd24c')
  }
}

resource storageAccountBlobAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${managedIdentity.name}-storage-blob-access')
  scope: managedIdentity
  properties: {
    description: 'Allow identity to read and write blob data'
    principalType: 'ServicePrincipal'
    principalId: managedIdentity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}

resource storageAccountQueueAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${managedIdentity.name}-storage-queue-access')
  scope: managedIdentity
  properties: {
    description: 'Allow identity to read and write queue messages'
    principalType: 'ServicePrincipal'
    principalId: managedIdentity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88')
  }
}

resource storageAccountTableAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${managedIdentity.name}-storage-table-access')
  scope: managedIdentity
  properties: {
    description: 'Allow identity to read and write table data'
    principalType: 'ServicePrincipal'
    principalId: managedIdentity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3')
  }
}

resource storageAccountFileShareAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${managedIdentity.name}-storage-file-share-access')
  scope: managedIdentity
  properties: {
    description: 'Allow identity to read and write file share data'
    principalType: 'ServicePrincipal'
    principalId: managedIdentity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0c867c2a-1d8c-454a-a3db-ab2ea1bdc8bb')
  }
}

resource cosmosDBDataAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${managedIdentity.name}-cosmosdb-data-access')
  scope: managedIdentity
  properties: {
    description: 'Allow identity to list containers, as well as read and write from CosmosDB'
    principalType: 'ServicePrincipal'
    principalId: managedIdentity.properties.principalId
    // https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-setup-rbac#built-in-role-definitions
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '00000000-0000-0000-0000-000000000002')
  }
}

resource keyVaultSecretsAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${managedIdentity.name}-kv-secrets-access')
  scope: managedIdentity
  properties: {
    description: 'Allow identity to read key vault secrets'
    principalType: 'ServicePrincipal'
    principalId: managedIdentity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
  }
}

resource keyVaultCertsAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${managedIdentity.name}-kv-certificate-access')
  scope: managedIdentity
  properties: {
    description: 'Allow identity to read key vault certificates'
    principalType: 'ServicePrincipal'
    principalId: managedIdentity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'db79e9a7-68ee-4b58-9aeb-b90e7c24fcba')
  }
}

resource keyVaultCryptoAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('${managedIdentity.name}-kv-crypto-access')
  scope: managedIdentity
  properties: {
    description: 'Allow identity to read key vault crypto data'
    principalType: 'ServicePrincipal'
    principalId: managedIdentity.properties.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '12338af0-0e69-4776-bea7-57ae8d297424')
  }
}


output identityName string = managedIdentity.name
output identityPrincipalId string = managedIdentity.properties.principalId
output identityResourceId string = managedIdentity.id
