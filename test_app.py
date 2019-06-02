import application as AP

testex = '''
# App Service on Azure Stack update 1 release notes

*Applies to: Azure Stack integrated systems and Azure Stack Development Kit*

These release notes describe the improvements and fixes in Azure App Service on Azure Stack Update 1 and any known issues. Known issues are divided into issues directly related to the deployment, update process, and issues with the build (post-installation).

> [!IMPORTANT]
> Apply the 1802 update to your Azure Stack integrated system or deploy the latest Azure Stack development kit before deploying Azure App Service.
>
>

## Build reference

The App Service on Azure Stack Update 1 build number is **69.0.13698.9**

### Prerequisites

> [!IMPORTANT]
> New deployments of Azure App Service on Azure Stack now require a [three-subject wildcard certificate](azure-stack-app-service-before-you-get-started.md#get-certificates) due to improvements in the way in which SSO for Kudu is now handled in Azure App Service. The new subject is **\*.sso.appservice.\<region\>.\<domainname\>.\<extension\>**
>
>

Refer to the [Before You Get Started documentation](azure-stack-app-service-before-you-get-started.md) before beginning deployment.

### New features and fixes

Azure App Service on Azure Stack Update 1 includes the following improvements and fixes:

- **High Availability of Azure App Service** - The Azure Stack 1802 update enabled workloads to be deployed across fault domains. Therefore App Service infrastructure is able to be fault tolerant as it will be deployed across fault domains. By default all new deployments of Azure App Service has this capability however for deployments completed prior to Azure Stack 1802 update being applied refer to the [App Service Fault Domain documentation](azure-stack-app-service-before-you-get-started.md )

- **Deploy in existing virtual network** - Customers can now deploy App Service on Azure Stack within an existing virtual network. Deploying in an existing virtual network enables customers to connect to the SQL Server and File Server, required for Azure App Service, over private ports. During deployment, customers can select to deploy in an existing virtual network, however [must create subnets for use by App Service](azure-stack-app-service-before-you-get-started.md#virtual-network) prior to deployment.

- Updates to **App Service Tenant, Admin, Functions portals and Kudu tools**. Consistent with Azure Stack Portal SDK version.
'''

seo = AP.get_top_ten(testex)
print(seo)