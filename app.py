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
from flask import Flask, render_template, request, Response, redirect
import datetime
import requests
import json
from dotenv import load_dotenv
import os
from pprint import pprint
#File with meraki sdk api call functions
import api


# load all environment variables
load_dotenv()

#Global variables
app = Flask(__name__)

#Content for menu dropdowns with organizations and networks
dropdownContent = {}
#Filtered dropdown content based on the role and thereby permissions of a user
dropdownContentPermissionBased = []
#By user selected organization and network
selectedElements = {'organization': None, 'network_id': None}
#Valid logged in user
validUser = {}
#Permissions that apply to valid logged in user
appliedPermissions = {}

#Ports that were chosen by user to do an action on
selectedPort = ""
selectedAppliancePort = {}

#Methods
#Returns location and time of accessing device
def getSystemTimeAndLocation():
    #request user ip
    userIPRequest = requests.get('https://get.geojs.io/v1/ip.json')
    userIP = userIPRequest.json()['ip'] 

    #request geo information based on ip
    geoRequestURL = 'https://get.geojs.io/v1/ip/geo/' + userIP + '.json'
    geoRequest = requests.get(geoRequestURL)
    geoData = geoRequest.json()

    #create info string
    location = geoData['country']
    timezone = geoData['timezone']
    current_time=datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    timeAndLocation = "System Information: {}, {} (Timezone: {})".format(location, current_time, timezone)
    
    return timeAndLocation

#Read json file and return json
def get_json(filepath):
	with open(filepath, 'r') as f:
		jsondata = json.loads(f.read())
		f.close()
	return jsondata

#Check username and password combination and return valid user and associated permissions on correct credentials
def loginToRightsMapping(username, password):

    global dropdownContentPermissionBased, appliedPermissions, validUser 
    appliedPermissions = {}
    validUser = {}

    permissions = get_json('permission.json')
    users = get_json('user.json')
    
    #Check credentials
    for user in users:
        if user['name'] == username and user['pw'] == password:
            validUser = user
            break
    
    #Set permissions and orga picker content based on role of valid user and 
    if validUser:
        for permission in permissions:
            if permission['role'] == validUser['role']:
                appliedPermissions = permission
                
                for orga in dropdownContent: 
                    if orga['id'] in permission['organizations']:
                        dropdownContentPermissionBased.append(orga)

    return (validUser and appliedPermissions)

#Sets the context (organization and network) based on user input
def setContext():

    global selectedElements

    orgaId = request.form.get("organizations_select")
    networkId = request.form.get("network_select")
    selectedElements.update([('organization', orgaId),('network_id', networkId)])   

def contextSelected():
    return (selectedElements['organization'] and selectedElements['network_id'])

#Routes
@app.route('/', methods=['GET', 'POST'])
def login():

    global dropdownContentPermissionBased, selectedElements, validUser

    if request.method == 'GET':

        #Reset user, permissions and context
        dropdownContentPermissionBased = []
        selectedElements = {'organization': None, 'network_id': None}
        validUser = {}
        
        return render_template('login.html', hiddenLinks=True, user = validUser, timeAndLocation=getSystemTimeAndLocation(), error=False, errormessage="", errorcode=200)


    if request.method == 'POST':

        #Read user input
        username = request.form.get("login-name")
        password = request.form.get("input-type-password")

        loginSuccessful = loginToRightsMapping(username, password)
        
        if(loginSuccessful):
            return redirect('/home')                   
        else:
            return render_template('login.html', hiddenLinks=True, user = validUser, timeAndLocation=getSystemTimeAndLocation(), error=True, errormessage="Wrong credentials.", errorcode=200)


@app.route('/home', methods=['GET', 'POST'])
def home():

    global selectedElements, validUser

    if request.method == 'POST':
        setContext()

    return render_template('home.html', hiddenLinks=False, user = validUser, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, permissions = appliedPermissions, timeAndLocation=getSystemTimeAndLocation())


@app.route('/clients', methods=['GET', 'POST'])
def clients():

    global selectedElements

    if request.method == 'GET':

        if(contextSelected()):
            networkDevices = api.getNetworkClients(selectedElements['network_id'])
        else:
            networkDevices = []

    if request.method == 'POST':
            
            setContext()
            networkDevices = api.getNetworkClients(selectedElements['network_id'])

    return render_template('clients.html', hiddenLinks=False, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, permissions = appliedPermissions, network_device_list = networkDevices, user = validUser,  timeAndLocation=getSystemTimeAndLocation())


@app.route('/groupPolicies', methods=['GET', 'POST'])
def groupPolicies():

    global selectedElements

    if request.method == 'GET':

        if(contextSelected()):
            groupPolicies = api.getGroupPolicies(selectedElements['network_id'])
        else:
            groupPolicies = []

    if request.method == 'POST':
        
            setContext()

            groupPolicies = api.getGroupPolicies(selectedElements['network_id'])

            #Retrieve action user executed and ID if needed as value
            new_action = request.form.get("add_new_policy")
            delete_action = request.form.get("delete_policy")
            
            #User pressed "New Policy" button
            if(new_action):
                return render_template('newPolicy.html', hiddenLinks=False, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, groupPolicies = groupPolicies, permissions = appliedPermissions,  user = validUser,   timeAndLocation=getSystemTimeAndLocation())

            #User pressed "Delete Policy" button. delete_action var contains ID of policy to delete.
            if(delete_action):
                api.deletePolicy(selectedElements['network_id'], delete_action)
                return redirect('/groupPolicies')

    return render_template('groupPolicies.html', hiddenLinks=False, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, groupPolicies = groupPolicies, permissions = appliedPermissions,  user = validUser,   timeAndLocation=getSystemTimeAndLocation())


@app.route('/newPolicy', methods=['GET','POST'])
def newPolicy():
    
    global selectedElements

    if request.method == 'POST':
        
        setContext()

        #Retrieve action user executed and ID if needed as value
        save_action = request.form.get("new_policy") 
        #Retrieve values user chose
        policy_name = request.form.get("policy_name")
        bandwidth = request.form.get("bandwidth")
        splash = request.form.get("splash")
        vlan = request.form.get("vlan")
        bw_limit_down = request.form.get("bw_limit_down")
        bw_limit_up = request.form.get("bw_limit_up")
        vlan_number =request.form.get("vlan_number")

        #Create payload json for api create request
        payload = {"name":policy_name, "bandwidth": {"settings": bandwidth, 'bandwidthLimits': {'limitUp': bw_limit_up, 'limitDown': bw_limit_down}}, "splashAuthSettings":splash, "vlanTagging":{'settings': vlan, 'vlanId': vlan_number}}
        
        if(save_action):
            api.createGroupPolicy(selectedElements['network_id'], payload)
    
        return redirect('/groupPolicies')    

    return render_template('newPolicy.html', hiddenLinks=False, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, groupPolicies = groupPolicies, permissions = appliedPermissions,  user = validUser,  timeAndLocation=getSystemTimeAndLocation())
   

@app.route('/devices', methods=['GET', 'POST'])
def addDevice():
    global selectedElements, dropdownContentPermissionBased
  
    if request.method == 'GET':
        
        if(contextSelected()):
            orgaDevices = api.getNetworkDevices(selectedElements['network_id'])
        else:
            orgaDevices = []

    if request.method == 'POST':
        
        setContext()

        orgaDevices = api.getNetworkDevices(selectedElements['network_id'])
    
    return render_template('devices.html', hiddenLinks=False, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, orgaDevices = orgaDevices, permissions = appliedPermissions, user = validUser, timeAndLocation=getSystemTimeAndLocation(), error=True, errormessage="", errorcode=200)


@app.route('/accessPoints', methods=['GET','POST'])
def accessPoints():
    global selectedElements, dropdownContentPermissionBased

    if request.method == 'GET':
        
        if(contextSelected()):
            accessPoints = api.getNetworkAccessPoints(selectedElements['network_id'])
        else:
            accessPoints = []
    
    if request.method == 'POST':
        
        setContext()

        accessPoints = api.getNetworkAccessPoints(selectedElements['network_id'])

    return render_template('accessPoints.html', hiddenLinks=False, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, networkDevicesAP = accessPoints, permissions = appliedPermissions,  user = validUser,  timeAndLocation=getSystemTimeAndLocation())
   
@app.route('/switchPort', methods=['GET','POST'])
def switchPort():

    global selectedElements, dropdownContentPermissionBased, selectedPort

    selectedPort = {}

    if request.method == 'GET':
        
        if(contextSelected()):
            switchPorts = api.getAllSwitchPorts(selectedElements['network_id'])
        else:
            switchPorts = []
    
    if request.method == 'POST':
        
        setContext()

        switchPorts = api.getAllSwitchPorts(selectedElements['network_id'])

        #Retrieve action user executed and ID if needed as value
        editToPort = request.form.get("edit_port")

        if(editToPort):

            #Read values for Port to edit
            switchname = editToPort.split("/")[0]
            portId = editToPort.split("/")[1]

            #Retrieve data for port to edit based on name and port ID
            for switch in switchPorts:
                if switch['switchname'] == switchname:
                    for port in switch['switchports']:
                        if port["portId"] == portId:
                            #global var selectedPort is set and used by next route /editPort
                            selectedPort = {"switchname": switch['switchname'], "switchserial": switch['switchserial'], "port":port}
            
            return redirect('/editPort')    

    return render_template('switchPort.html', hiddenLinks=False, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, switches = switchPorts, permissions = appliedPermissions,  user = validUser,  timeAndLocation=getSystemTimeAndLocation())
   

@app.route('/editPort', methods=['GET','POST'])
def editPort():
    
    global selectedPort, selectedElements, dropdownContentPermissionBased

    if request.method == 'POST':
        
        setContext()

        #Retrieve action user executed and ID if needed as value
        editToPort = request.form.get("save_port_edit")

        #Read values user chose
        save_and_switch_serial = request.form.get("save_port_edit")
        port_name = request.form.get("port_name")
        port_tags = request.form.get("port_tags")
        port_enabled = request.form.get("port_enabled")
        port_type = request.form.get("port_type")
        port_vlan = request.form.get("port_vlan")
        port_allowed_vlans = request.form.get("port_allowed_vlans")
        port_rstp = request.form.get("port_rstp")
        port_stp = request.form.get("port_stp")
        port_isolation = request.form.get("port_isolation")
        port_udld = request.form.get("port_udld")

        #Create payload json for api create request
        payload = {"name": port_name, "tags": port_tags, "enabled": port_enabled, "type": port_type, "vlan": port_vlan, "allowedVlans": port_allowed_vlans, "isolationEnabled": port_isolation, "rstpEnabled": port_rstp, "stpGuard": port_stp, "udld": port_udld}

        if(editToPort):
            api.updatePort(save_and_switch_serial, selectedPort['port']['portId'], payload)

        return redirect('/switchPort')  

    return render_template('editPort.html', hiddenLinks=False, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, selectedPort = selectedPort, permissions = appliedPermissions,  user = validUser, error=True, errormessage="CUSTOMIZE: Add custom message here.", errorcode=200, timeAndLocation=getSystemTimeAndLocation())


@app.route('/addressingAndVlan', methods=['GET','POST'])
def addressingAndVlan():
    
    global selectedElements, dropdownContentPermissionBased, selectedAppliancePort

    selectedAppliancePort = {}
    vlanDisabledError = False

    if request.method == 'GET':
        
        if(contextSelected()): 
            applicance_ports, applicance_static_routes, applicance_vlans, vlanDisabledError = api.getAddressingAndVlanData(selectedElements['network_id'])
        else:
            applicance_ports = []
            applicance_static_routes = []
            applicance_vlans = []

    
    if request.method == 'POST':
        
        setContext()

        applicance_ports, applicance_static_routes, applicance_vlans, vlanDisabledError = api.getAddressingAndVlanData(selectedElements['network_id'])
                    
        #Retrieve action user executed and ID if needed as value         
        edit_appliance_port =  request.form.get("edit_appliance_port")
        delete_appliance_subnet = request.form.get("delete_appliance_subnet")
        add_route = request.form.get("add_route")
        add_vlan = request.form.get("add_vlan")
        delete_appliance_route =  request.form.get("delete_appliance_route")
        
        #Doing based on user action
        if(edit_appliance_port):
            
            #Retrieve port data for port to edit and set it globally for next route /editAppliancePort
            for port in applicance_ports:
                if port['number'] == int(edit_appliance_port):
                    selectedAppliancePort = port
                    break
            return redirect('/editAppliancePort') 

        elif(delete_appliance_subnet):
            
            api.deleteNetworkApplianceVlan(selectedElements['network_id'], delete_appliance_subnet)
            return redirect('/addressingAndVlan')

        elif(add_vlan):
            
            return redirect('/addVlan') 

        elif(add_route):
            
            return redirect('/addRoute')

        elif(delete_appliance_route):
            
            api.deleteNetworkApplianceStaticRoute(selectedElements['network_id'], delete_appliance_route)
            return redirect('/addressingAndVlan') 

    return render_template('addressingAndVlan.html', hiddenLinks=False, applicance_ports = applicance_ports, applicance_static_routes = applicance_static_routes, applicance_vlans = applicance_vlans,  vlanDisabledError= vlanDisabledError, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, permissions = appliedPermissions,  user = validUser,  timeAndLocation=getSystemTimeAndLocation())


@app.route('/editAppliancePort', methods=['GET','POST'])
def editAppliancePort():

    global selectedElements, dropdownContentPermissionBased, selectedAppliancePort

    if request.method == 'POST':

        setContext()

        #Retrieve action user executed and ID if needed as value         
        save_app_port_edit =  request.form.get("save_app_port_edit")

        if(save_app_port_edit):

            #Read values user chose
            port_enabled = request.form.get("port_enabled")
            port_type = request.form.get("port_type")
            port_native_vlan = request.form.get("port_native_vlan")
            port_vlan = request.form.get("port_vlan")
            
            #Create payload json for api create request
            payload = {"enabled": port_enabled, "type": port_type, "vlan": port_vlan, "dropUntaggedTraffic": port_native_vlan }

            api.updateNetworkAppliancePort(selectedElements['network_id'], save_app_port_edit, payload)
        
        return redirect('/addressingAndVlan')  

    return render_template('editAppliancePort.html', hiddenLinks=False, selected_appliance_port = selectedAppliancePort, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, permissions = appliedPermissions,  user = validUser,  timeAndLocation=getSystemTimeAndLocation())

@app.route('/addRoute', methods=['GET','POST'])
def addRoute():

    global selectedElements, dropdownContentPermissionBased, selectedAppliancePort

    if request.method == 'POST':
        
        setContext()

        #Retrieve action user executed and ID if needed as value         
        add_route = request.form.get("add_route")

        if(add_route):

            #Read values user chose
            route_name = request.form.get("route_name")
            subnet_ip = request.form.get("subnet_ip")
            hop_ip = request.form.get("hop_ip")
 
            api.createNetworkApplianceStaticRoute(selectedElements['network_id'], route_name, subnet_ip, hop_ip)

        return redirect('/addressingAndVlan') 

    return render_template('addRoute.html', hiddenLinks=False, selected_appliance_port = selectedAppliancePort, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, permissions = appliedPermissions,  user = validUser,  timeAndLocation=getSystemTimeAndLocation())


'''@app.route('/addVlan', methods=['GET','POST'])
def addVlan():

    global selectedElements, dropdownContentPermissionBased, selectedAppliancePort

    if request.method == 'POST':
        
        setContext()

        #Retrieve action user executed and ID if needed as value         
        add_vlan = request.form.get("add_vlan")

        if(add_vlan):

            #Read values user chose
            vlan_name = request.form.get("vlan_name")
            subnet_ip = request.form.get("subnet_ip")
            mx_ip = request.form.get("mx_ip")
            vlan_id = int(request.form.get("vlan_id"))
            api.createNetworkApplianceVlan(selectedElements['network_id'], vlan_id, vlan_name, subnet_ip, mx_ip)
        
        return redirect('/addressingAndVlan') 

    return render_template('addVlan.html', hiddenLinks=False, selected_appliance_port = selectedAppliancePort, dropdown_content = dropdownContentPermissionBased, selected_elements = selectedElements, permissions = appliedPermissions,  user = validUser,  timeAndLocation=getSystemTimeAndLocation())
'''


#Main Function
if __name__ == "__main__":

    #Create json with all organizations and associated network for the menu dropdowns
    dropdownContent = api.getOrganizationID()
    
    for orga in dropdownContent:
        orgaID = orga['id']
        orga.update([("networks", api.getNetworks(orgaID))])

    app.run(host='0.0.0.0', debug=True)

