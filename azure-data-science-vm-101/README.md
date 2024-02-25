# Getting started with Azure Data Science Virtual Machines

This repository contains the scripts and templates to deploy an [Azure Data Science Virtual Machine (DSVM)](https://learn.microsoft.com/en-us/azure/machine-learning/data-science-virtual-machine/overview?view=azureml-api-2) in a resource group. The DSVM is a custom virtual machine image that is published on the Azure marketplace and available for a variety of virtual machine sizes. The DSVM is pre-configured with popular tools for data science and deep learning, including Microsoft R Server, Anaconda Python, Jupyter notebooks, Visual Studio Code, and more.

## When to use the Data Science Virtual Machine?

- **Proof of Concept**: If you are a data scientist or a developer and need to quickly prototype a solution, the DSVM provides a ready-to-use environment with all the tools you need. However, other tools such as Azure Machine Learning Studio or Azure Databricks may be more suitable for some use cases, especially if you need to evaluate the scalability of your solution.

- **Adhoc Long Running Training Jobs**: DSVM can also be useful for running on-demand model training jobs which require GPU or CPU intensive computations. The convenience of having a pre-configured environment can sometimes outweigh the cost of running the VM.

- **Live Training**: If you are a trainer and need to deliver a data science training, the DSVM provides a ready-to-use environment with all the tools you need.

- **Student Assignments**: If you are a student and need to complete a data science assignment, the DSVM provides a ready-to-use environment with all the tools you need. This can be a time saver provided there is no credit for setting up the environment from scratch.

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

## Security Considerations

When deploying the DSVM, it's important to consider the following security best practices:

- **Private Network**: Deploy the DSVM in a virtual network and use network security groups to control inbound and outbound traffic. You can then use a VPN or Azure Bastion to connect to the DSVM without exposing it to the public internet. This helps to reduce the attack surface and protect the DSVM from unauthorized access, especially for sensitive workloads involving proprietary or personal data.

- **Identity and Access Management**: Use Azure Active Directory (AAD) to manage user identities and access to the DSVM. This allows you to enforce multi-factor authentication, role-based access control, and conditional access policies to protect the DSVM from unauthorized access.

- **Security In Depth**: Implement additional security measures such as Disk Encryption, endpoint protection, firewalls, Azure Defender for Cloud and Security Monitoring to protect the DSVM from malware, data breaches, and other security threats.

## Similar Services on Other Cloud Providers

- **Amazon Web Services (AWS)**: AWS offers a similar service called the [Deep Learning AMI](https://docs.aws.amazon.com/dlami/latest/devguide/what-is-dlami.html) which is a pre-configured environment for deep learning. It includes popular deep learning frameworks such as TensorFlow, PyTorch, and MXNet.

- **Google Cloud Platform (GCP)**: GCP offers a similar service called [Deep Learning VM](https://cloud.google.com/deep-learning-vm/docs/introduction) which is a pre-configured environment for deep learning. It includes popular deep learning frameworks such as TensorFlow, PyTorch, and Keras.

---

# Closing Thoughts

In conclusion, the Azure Data Science Virtual Machine is a versatile tool that can accelerate data science projects by providing a pre-configured environment with a wide array of tools. Whether you're a student, a data scientist, or a trainer, the DSVM can help you focus more on data science and less on setting up your environment. However, it's important to consider the associated costs, security implications, and maintenance requirements.
