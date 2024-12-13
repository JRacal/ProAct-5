from webexteamssdk import WebexTeamsAPI
from ncclient import manager
import xml.dom.minidom #use to change the xml output to prettify format.

WEBEX_BOT_TOKEN = "MmM5ODQwMjYtYzNhYi00ZTExLWFiZjEtODUwMzU1ZjM0YjZiYTFjMjY5OGMtMDA2_P0A1_856a32b6-339b-4d3d-89fb-dabbd25aff7b"
WEBEX_ROOM_ID = "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vMDg4MWJlODAtYjk2OS0xMWVmLWIwNmQtZjU4YzY5NmY4ZDIx"

def send_webex_notification(message):
    api = WebexTeamsAPI(access_token=WEBEX_BOT_TOKEN)
    api.messages.create(roomId=WEBEX_ROOM_ID, text=message)
    print("Notification sent to WebEx Teams.")

send_webex_notification("Program Running.")

DEVICE = {
    "host": "192.168.166.128",
    "port": 830,
    "username": "cisco",
    "password": "cisco123!"
}
#Connect to the Server
def connect_to_device():
    return manager.connect(
        host=DEVICE['host'],
        port=DEVICE['port'],
        username=DEVICE['username'],
        password=DEVICE['password'],
        hostkey_verify=False
    )
# filter out to ietf-interaces only
def get_running_config(netconf_manager):
    filter = '''
    <filter>
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"/>
    </filter>
    '''
    config = netconf_manager.get_config(source="running", filter=filter).xml
    print("Running configuration retrieved:")
    print(xml.dom.minidom.parseString(config).toprettyxml())
    return config
#change the running-config
def edit_config(netconf_manager, interface_name, new_description):
    config = f'''
    <config>
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <interface>
                <GigabitEthernet>
                    <name>{interface_name}</name>
                    <description>{new_description}</description>
                </GigabitEthernet>
            </interface>
        </native>
    </config>
    '''
    response = netconf_manager.edit_config(target="running", config=config)
    if response.ok:
        print(f"Configuration for {interface_name} updated to: {new_description}")
        return True
    else:
        print("Failed to update configuration.")
        return False

#display the updated running-config
def validate_changes(netconf_manager, interface_name, expected_description):
    updated_config = get_running_config(netconf_manager)
    if updated_config and expected_description in updated_config:
        print(f"Validation successful: Interface {interface_name} description updated.")
    else:
        print(f"Validation failed: Interface {interface_name} description not updated.")

def automate_network_change(interface_name, new_description):
    try:
        # Step 1: Connect to the server
        with connect_to_device() as netconf_manager:
            print("Connected to the NETCONF server.")

            # Step 2: Retrieve current configuration
            current_config = get_running_config(netconf_manager)

            # Step 3: Apply configuration changes
            if edit_config(netconf_manager, interface_name, new_description):
                print("Configuration updated successfully.")

                # Step 4: Validate the changes
                validate_changes(netconf_manager, interface_name, new_description)

                # Step 5: Send WebEx notification
                message = f"Interface {interface_name} description updated to '{new_description}'."
                send_webex_notification(message)

    except Exception as e:
        print(f"An error occurred: {e}")
        send_webex_notification(f"Automation task failed: {e}")

if __name__ == "__main__":
    interface = "1"
    description = "Test2 Updated via Automation"
    automate_network_change(interface, description)