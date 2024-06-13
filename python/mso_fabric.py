# python/mso_fabric.py
from mso_session import MsoSession

from jsonpath_ng.ext import parser

import requests
requests.packages.urllib3.disable_warnings()

class MsoFabric:
    """
    Represents a fabric in the MSO (Multi-Site Orchestrator) system.

    This class provides methods to interact with fabrics in the MSO system. It allows retrieving the site ID, node DN, and fabric interface payload from the MSO API.

    Args:
        site_node (tuple): A tuple containing the site name and node name of the fabric.
        session (MsoSession): An instance of the MsoSession class representing the MSO server session.

    Raises:
        ConnectionError: If there is a connection error while establishing a connection with the MSO system.
        AttributeError: If there is an issue with the MSO site name or node name.

    Attributes:
        session (MsoSession): An instance of the MsoSession class representing the MSO server session.
        site (str): The name of the site associated with the fabric.
        site_id (str): The unique identifier of the site in the MSO system.
        node (str): The name of the fabric node within the site.
        node_dn (str): The distinguished name (DN) of the fabric node.
        type (str): The type of fabric, typically set to 'physical'.
        payload (dict): The payload containing fabric interface information retrieved from the MSO API.

    Methods:
        get_site_id(): Retrieves the unique identifier of the site from the MSO system.

            Returns:
                str: The ID of the site.

        get_node_dn(): Retrieves the distinguished name (DN) of the fabric node from the MSO API.

            Returns:
                str: The DN of the fabric node.

        get_if_payload(): Retrieves the fabric interface payload from the MSO API.

            Returns:
                dict: The payload of the fabric interfaces.

    Example:
        # Create an instance of MsoSession
        session = MsoSession(server_props)

        # Create an instance of MsoFabric
        site_node = ('MySite', 'MyNode')
        fabric = MsoFabric(site_node, session)

        # Retrieve the site ID
        site_id = fabric.get_site_id()

        # Retrieve the node DN
        node_dn = fabric.get_node_dn()

        # Retrieve the fabric interface payload
        interface_payload = fabric.get_if_payload()

        # Access fabric attributes or perform operations on the payload as needed.
    """
    
    def __init__ (self, site_node: tuple, session: MsoSession):
        self.session = session
        self.site = site_node[0]
        self.pod = site_node[1]
        self.node = site_node[2]
        self.intf_type = site_node[3]
        self.site_id = self.get_site_id()
        self.node_dn = self.get_node_dn()
        self.payload = self.get_intf_payload()

    def get_site_id (self):
        url = self.session.base_url + '/mso/api/v1/sites?X-Nd-Apikey=' + self.session.api_key + '&X-Nd-Username=' + self.session.user
        headers = {
            'Cookie': 'AuthCookie=' + self.session.auth_token,
            'Content-Type': 'application/json'
        }
        try:
            key_parser = parser.parse('$.sites[?(@.name=="' + self.site + '")].id')
            response = requests.request("GET", url, headers=headers, verify=self.session.certificate)
            if response.status_code == 200 and key_parser.find(response.json()):
                return key_parser.find(response.json())[0].value
            else:
                raise AttributeError('Try to verify MSO Site Name!')
        except Exception as e:
            raise ConnectionError('Failed to fetch Site ID from MSO!') from e
        
    def get_node_dn (self):
        if self.intf_type == 'vpc': return f'topology/{self.pod}/{self.node}'
        url = self.session.base_url + '/mso/api/v1/aci/sites/' + self.site_id + '/nodes?X-Nd-Apikey=' + self.session.api_key + '&X-Nd-Username=' + self.session.user
        headers = {
            'Cookie': 'AuthCookie=' + self.session.auth_token,
            'Content-Type': 'application/json'
        }
        try:
            key_parser = parser.parse('$.nodes[?(@.name=="' + self.node + '")].dn')
            response = requests.request("GET", url, headers=headers, verify=self.session.certificate)
            if response.status_code == 200 and key_parser.find(response.json()):
                return key_parser.find(response.json())[0].value
            else:
                raise AttributeError('Try to verify Node Name!')
        except Exception as e:
            raise ConnectionError('Failed to fetch Node DN from MSO!') from e
    
    def get_intf_payload (self):
        inft_type = 'physical' if self.intf_type == 'port' else self.intf_type
        url = self.session.base_url + '/mso/api/v1/aci/sites/' + self.site_id + '/nodes/interfaces?node=' + self.node_dn + '&type=' + inft_type + '&X-Nd-Apikey=' + self.session.api_key + '&X-Nd-Username=' + self.session.user
        headers = {
            'Cookie': 'AuthCookie=' + self.session.auth_token,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request("GET", url, headers=headers, verify=self.session.certificate)
            if response.json()["interfaces"]:
                return response.json()
            else:
                raise ConnectionError(f'The Frabic Interface list received is empty from Node {self.node_dn}')
        except Exception as e:
            raise ConnectionError('Failed to fetch Frabic Interfaces from MSO!') from e
