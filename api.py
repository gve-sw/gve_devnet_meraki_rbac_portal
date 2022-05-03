""" Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

# Import Section
import meraki
import os
from dotenv import load_dotenv
import sys

# load all environment variables
load_dotenv()

base_url = "https://api.meraki.com/api/v1"

DASHBOARD = meraki.DashboardAPI(
            api_key=os.environ['MERAKI_API_TOKEN'],
            base_url=base_url,
            print_console=False)


#API calls
#Organizations
def getOrganizationID():
    response = DASHBOARD.organizations.getOrganizations()
    return response

#Networks
def getNetworks(orgID):
    response = DASHBOARD.organizations.getOrganizationNetworks(
        orgID, total_pages='all'
    )
    return(response)

#Devices
def getNetworkDevices(networkID):
    response = DASHBOARD.networks.getNetworkDevices(
        networkID
    )
    return(response)

def getNetworkAccessPoints(networkId):
    accessPoints = []

    networkDevices = getNetworkDevices(networkId)

    for device in networkDevices:
        if "MR" in device['model']:
            accessPoints.append(device)

    return accessPoints

def getOrgaDevices(organizationId):
    response = DASHBOARD.organizations.getOrganizationDevices(
        organizationId, total_pages='all'
    )
    return(response)

def claimIntoOrganization(organization_id, serials, orders, licenses):

    response = DASHBOARD.organizations.claimIntoOrganization(
        organization_id, 
        orders=orders, 
        serials=serials, 
        licenses=licenses
    )
    return response
    #https://developer.cisco.com/meraki/api-v1/#!claim-into-organization

def claimNetworkDevices(network_id, serials):
    response = DASHBOARD.networks.claimNetworkDevices(
        network_id, serials
    )
    return response

#Clients
def getNetworkClients(networkId):
    network_devices = DASHBOARD.networks.getNetworkClients(
        networkId, total_pages='all'
    )
    # https://developer.cisco.com/meraki/api-v1/#!get-network-clients 
    #network_devices = get("networks/"+ str(networkId) +"/clients?timespan=86400", {})
    return network_devices

#Group policies
def getGroupPolicies(networkId):
    # https://developer.cisco.com/meraki/api-v1/#!get-network-group-policies
    groupPolicies = DASHBOARD.networks.getNetworkGroupPolicies(
        networkId
    )
    return groupPolicies

def deletePolicy(network_id, policy_id):
    DASHBOARD.networks.deleteNetworkGroupPolicy(
        network_id, policy_id
    )
    #https://developer.cisco.com/meraki/api-v1/#!delete-network-group-policy

def getGroupPolicy(network_id, policy_id):
    groupPolicy = DASHBOARD.networks.getNetworkGroupPolicy(
        network_id, policy_id
    )
    return groupPolicy
    #https://developer.cisco.com/meraki/api-v1/#!get-network-group-policy

def createGroupPolicy(network_id, payload):
    response = DASHBOARD.networks.createNetworkGroupPolicy(
        network_id, payload['name'], 
        #scheduling={'enabled': payload['scheduling']['enabled']}, 
        bandwidth= payload['bandwidth'], 
        splashAuthSettings=payload['splashAuthSettings'], 
        vlanTagging=payload['vlanTagging']
    )
    return response
    #https://developer.cisco.com/meraki/api-v1/#!update-network-group-policy

#Ports
def getAllSwitchPorts(networkId):

    networkDevices = getNetworkDevices(networkId)
    switches = []
    switchesAndPorts = []

    for device in networkDevices:
        if "MS" in device['model']:
            switches.append(device)

    for switch in switches:
        serial = str(switch['serial'])
        response = DASHBOARD.switch.getDeviceSwitchPorts(
            serial
        )
        switchesAndPorts.append({"switchname": switch['name'], "switchserial": switch['serial'], "switchports":response})

    return switchesAndPorts

def updatePort(serial, port_id, payload):

    response = DASHBOARD.switch.updateDeviceSwitchPort(
        serial, port_id, 
        name = payload["name"], 
        enabled=payload["enabled"], 
        type=payload["type"], 
        vlan=payload["vlan"], 
        isolationEnabled=payload["isolationEnabled"], 
        rstpEnabled=payload["rstpEnabled"], 
        stpGuard=payload["stpGuard"], 
        udld=payload["udld"]
    )

    return True

#Adressing and VLAN
def getAddressingAndVlanData(network_id):
    
    vlanDisabledError = False

    applicance_ports = getNetworkAppliancePorts(network_id)
    applicance_static_routes = getNetworkApplianceStaticRoutes(network_id)
    applicance_vlans = getNetworkApplianceVlans(network_id)

    if(applicance_ports == "VLANs are not enabled for this network" or applicance_static_routes == "VLANs are not enabled for this network" or applicance_vlans == "VLANs are not enabled for this network"): 
        vlanDisabledError = True

    return applicance_ports, applicance_static_routes, applicance_vlans, vlanDisabledError

def getNetworkAppliancePorts(network_id):
    
    try:#Handle network with disabled vlans
        response = DASHBOARD.appliance.getNetworkAppliancePorts(network_id)
    except meraki.exceptions.APIError as e: 
        response = e.message['errors'][0]
    return response

def getNetworkApplianceStaticRoutes(network_id):
    response = DASHBOARD.appliance.getNetworkApplianceStaticRoutes(network_id)
    return response

def getNetworkApplianceVlans(network_id):
    try:#Handle network with disabled vlans
        response = DASHBOARD.appliance.getNetworkApplianceVlans(network_id)
    except meraki.exceptions.APIError as e: 
        response = e.message['errors'][0]
    return response

def updateNetworkAppliancePort(network_id, port_id, payload):

    if(payload['dropUntaggedTraffic'] == "1"):
        nat_vlan = 1
        payload['dropUntaggedTraffic'] = False

    if(payload['enabled']=="true" and payload['type'] == "trunk" and payload['dropUntaggedTraffic'] == False):
        response = DASHBOARD.appliance.updateNetworkAppliancePort(
        network_id, port_id, 
        dropUntaggedTraffic=payload['dropUntaggedTraffic'], 
        type=payload['type'], 
        vlan=1,
        allowedVlans=payload['vlan'],
        enabled=payload['enabled'])
    elif(payload['enabled']=="true" and payload['type'] == "trunk" and payload['dropUntaggedTraffic'] == "1"):
        response = DASHBOARD.appliance.updateNetworkAppliancePort(
        network_id, port_id, 
        dropUntaggedTraffic=True, 
        type=payload['type'], 
        allowedVlans=payload['vlan'],
        enabled=payload['enabled'])
    elif(payload['enabled']=="true" and payload['type'] == "access"):
        response = DASHBOARD.appliance.updateNetworkAppliancePort(
        network_id, port_id, 
        type=payload['type'], 
        vlan=nat_vlan,
        enabled=payload['enabled'])   
    else:
        response = DASHBOARD.appliance.updateNetworkAppliancePort(
        network_id, port_id,
        enabled=payload['enabled'])

    return response

def deleteNetworkApplianceVlan(network_id, vlan_id):
    response = DASHBOARD.appliance.deleteNetworkApplianceVlan(
    network_id, vlan_id
    )
    return response

def deleteNetworkApplianceStaticRoute(network_id, static_route_id):
    response = DASHBOARD.appliance.deleteNetworkApplianceStaticRoute(
        network_id, static_route_id
    )
    return response

def createNetworkApplianceVlan(network_id, id_, name, subnet, appliance_ip):
    response = DASHBOARD.appliance.createNetworkApplianceVlan(
        network_id, id_, name, subnet, appliance_ip
    )
    return response

def createNetworkApplianceStaticRoute(network_id, name, subnet, gateway_ip):
    response = DASHBOARD.appliance.createNetworkApplianceStaticRoute(
        network_id, name, subnet, gateway_ip
    )
    return response

