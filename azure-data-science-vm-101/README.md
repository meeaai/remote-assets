# Azure Data Science Virtual Machine

This repository contains the scripts and templates to deploy an Azure Data Science Virtual Machine (DSVM) in a resource group. The DSVM is a custom virtual machine image that is published on the Azure marketplace and available for a variety of virtual machine sizes. The DSVM is pre-configured with popular tools for data science and deep learning, including Microsoft R Server, Anaconda Python, Jupyter notebooks, Visual Studio Code, and more.


## When to use the Data Science Virtual Machine?

- **Student Assignments**: If you are a student and need to complete a data science assignment, the DSVM provides a ready-to-use environment with all the tools you need. This can be a time saver provided there is no credit for setting up the environment from scratch.

- **Proof of Concept**: If you are a data scientist or a developer and need to quickly prototype a solution, the DSVM provides a ready-to-use environment with all the tools you need. However, other tools such as Azure Machine Learning Studio or Azure Databricks may be more suitable for some use cases, especially if you need to evaluate the scalability of your solution.

- **Live Training**: If you are a trainer and need to deliver a data science training, the DSVM provides a ready-to-use environment with all the tools you need. 


## How to Deploy the Data Science Virtual Machine?

### Deploying the DSVM from Azure Portal:

1. **Create a Resource Group**: In the Azure portal, create a new resource group. This is a logical container for resources deployed on Azure.

2. **Choose the DSVM Image**: Navigate to the Azure Marketplace and search for the "Data Science Virtual Machine" image.

3. **Configure the Virtual Machine**: Choose the appropriate VM size based on your computational needs. Enter a unique name for the VM, and set the username and password.

4. **Review and Create**: Review your settings and click on "Create" to deploy the DSVM.



#### Deploying the DSVM using Azure CLI and [Bicep](https://learn.microsoft.com/en-us/azure/machine-learning/data-science-virtual-machine/dsvm-tutorial-bicep?view=azureml-api-2&tabs=CLI):

```bash

az group create --name <resource-group-name> --location <location>

az deployment group create --resource-group <resource-group-name> --template-file azuredeploy.bicep --parameters azuredeploy.parameters.json

```

Once the deployment is complete, you can connect to the DSVM using Remote Desktop Protocol (RDP) or Secure Shell (SSH), depending on your operating system.



## Limitations and Considerations

While the DSVM is a powerful tool, it's important to consider the following:

- **Cost**: The DSVM is not free. The cost depends on the VM size and the duration of usage. Be sure to stop or deallocate the VM when not in use to avoid unnecessary charges.

- **Security**: As with any cloud resource, ensure that your DSVM is secure. Use strong passwords and consider implementing additional security measures such as firewalls and network security groups.

- **Maintenance**: The DSVM is a fully-fledged virtual machine, which means it requires regular updates and maintenance. Be prepared to manage and maintain your DSVM to ensure it runs smoothly.

---

# Closing Thoughts

In conclusion, the Azure Data Science Virtual Machine is a versatile tool that can accelerate data science projects by providing a pre-configured environment with a wide array of tools. Whether you're a student, a data scientist, or a trainer, the DSVM can help you focus more on data science and less on setting up your environment. However, it's important to consider the associated costs, security implications, and maintenance requirements.