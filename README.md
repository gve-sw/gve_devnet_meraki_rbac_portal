#  GVE_Devnet_Meraki_RBAC_Portal
Meraki web portal to allow limited access to organizations and functions based on user roles.

| :exclamation:  External repository notice   |
|:---------------------------|
| This repository is now mirrored at "PLEASE UPDATE HERE - add External repo URL after code review is completed"  Please inform a https://github.com/gve-sw/ organization admin of any changes to mirror them to the external repo |

## Contacts
* Ramona Renner 

## Solution Components
* Cisco Meraki Dashboard API (Cisco Meraki Python Library)
* flask
* python
* javascrpt
* html
* css

# Business Use Case
## IT Manager’s problem to be solved with this use case:

* **Needs:** Limit access to organizations, networks and Meraki functionality based on different user roles.
* **Challenge (WHY?):** The native Meraki Dashboard permissions and access control is not fine granular enough for the customers' scenario with partners and integrators.
* **Solution:** A custom build webapp offers a role-based login based on custom user roles. Hereby, not only the limiting to specific organizations but also meraki functionality is covered.
* **Business Outcomes:** Improved security by limiting unwanted access for partners, integrators and other user roles. Furthermore, decreased possibility for unintended changes from unauthorized users and improved user experience, since every user only sees the options relevant for them.

![Overview of PoV](/IMAGES/high_level_design.PNG)


# High Level Design Demo

![High level design of PoV](/IMAGES/high_level_design2.PNG)

# Getting Started
## Pre-requisites

* Meraki Dashboard API Key (Instructions shared in this document later)
* Min 2 Meraki organizations and their IDs (Instructions shared in this document later)
* Google Chrome, Firefox or Microsoft Edge


## Installation

### 1. Save Project Locally

Create and activate a virtual environment for the project ([Instructions](https://docs.python.org/3/tutorial/venv.html)).

Clone this Github repository:

```python
cd [add name of virtual environment here]
git clone [add github link here]
```


### 2. Obtain and Set Meraki API Key 

This application requires a Meraki API key. Obtain and note the **Meraki API Key** by following the instructions under https://developer.cisco.com/meraki/api/#!authorization/obtaining-your-meraki-api-key.

Afterwards, add the API key in the **.env** file as value for the **MERAKI_API_TOKEN** variable. 
    
> Note: Mac OS hides the .env file in the finder by default. View the demo folder for example with your preferred IDE to make the file visible.

> Note: Windows doesn't download the .env file via the git clone command. Create a new .env file in the project root folder in this case.


### 2. Obtain the Organization IDs

For the definition of the user permissions the organization ID of two or more organizations is required. It will be used in the next section **Define user permissions**.
    

2. To obtain the **Organization ID** execute the following steps: 
    
    2.1 Go to https://developer.cisco.com/meraki/api-v1/#!get-organizations > click **Configuration**
        ![OrganizationIDs](/IMAGES/editor1.png)

    2.2 Add the Meraki Api key from step 1 in the **APIKey in header** field > press **Save**
        ![OrganizationIDs](/IMAGES/editor2.png)

    2.3 Click **Run**   
        ![OrganizationIDs](/IMAGES/editor3.png)
    
    2.4 Find the organization name in the output data > make a note of the **id** of this organization
        ![OrganizationIDs](/IMAGES/editor4.png)


### 3. Define User Permissions and Users

The application requires to assign one or more organization IDs to each user role. Therefore, use the noted IDs from section **Obtain Meraki API Key and Organization IDs** and add them as needed in the **permissions.json** file under the **organizations** key for each role. By doing so, we define the organizations each user role has access to. It is recommended to assign different combinations for demonstrating the limited access to organizations based on the different roles during a demo.
    ![PermissionsDefinition](/IMAGES/permissions.png)

It is also possible to change the access to Meraki functionality for each role by altering the settings under the **permissions** key. 

Furthermore, the user accounts can be changed by adapting the **user.json** file. Each user is defined by a username, password and the role of the user. 
    
![UserDefinition](/IMAGES/users.PNG)


### 4. Install and Run the Application

Install dependencies

```python
cd [add name of virtual environment here]
cd GVE_Devnet_Meraki_RBAC_Portal 
pip install -r requirements.txt
```

Run application

```python
python app.py
```

Access the webapp via http://localhost:5000 and login as different users, defined in the **user.json**, to demonstrate the changing access to organizations, networks and Meraki functionality based on the user role. 
    ![UserDefinition](/IMAGES/login.png)


The available organizations and networks per user can be selected via picker on the top left side.
    ![UserDefinition](/IMAGES/picker.png)


To demonstrate that the available functionality changes for each user role, it is also helpful to refer to the changing menu elements available for the different roles. 


### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
