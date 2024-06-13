#!/usr/bin/env python3
from config.server_config import ServerDictProps

import json
from jsonpath_ng import parser

import requests
requests.packages.urllib3.disable_warnings()

class MsoSession:
    """
    Represents a session for connecting to the MSO server.

    This class provides methods to authenticate with the MSO server, create and manage API keys, and interact with the server's API.

    Args:
        server (dict): A dictionary containing the server properties such as 'host', 'port', 'certificate', 'user',
            'passwd', 'domain', and 'apiKeyName'. The 'apiKeyName' is the name of the API key to be used.

    Raises:
        ConnectionError: If there is a connection error while establishing a connection with the MSO server.
        AttributeError: If there is an issue with verifying MSO credentials or the MSO API key name.
        NotImplementedError: If any of the methods (create_api_key, update_api_key_name, get_api_key, delete_api_key)
            are called, as they are not yet implemented.

    Attributes:
        host (str): The hostname or IP address of the MSO server.
        port (int): The port number of the MSO server.
        certificate (str): The path to the SSL/TLS certificate file for verifying the server's identity.
        user (str): The username for authentication with the MSO server.
        passwd (str): The password for authentication with the MSO server.
        domain (str): The domain for authentication with the MSO server.
        base_url (str): The base URL of the MSO server, constructed using the host and port.
        api_key_name (str): The name of the API key to be used.
        auth_token (str): The authentication token obtained from the MSO server.
        api_key (str): The API key obtained from the MSO server.

    Methods:
        create_auth_token(): Creates an authentication token by sending a POST request to the MSO server.
        create_api_key(): [Not Implemented] Creates an API key.
        update_api_key_name(): [Not Implemented] Updates the name of the API key.
        get_api_key(): [Not Implemented] Retrieves the API key.
        get_api_key(): Retrieves the API key token by sending a GET request to the MSO server.
        delete_api_key(): [Not Implemented] Deletes the API key.

    Example:
        server_props = {
            'host': 'mso.example.com',
            'port': 443,
            'certificate': false,
            'user': 'admin',
            'passwd': 'password',
            'domain': 'example.com',
            'apiKeyName': 'my-api-key'
        }
        session = MsoSession(server_props)
        session.create_auth_token()
        api_key = session.get_api_key()
    """

    def __init__ (self, server):
        self.host = server['host']
        self.port = server['port']
        self.certificate = server['certificate']
        self.user = server['user']
        self.passwd = server['passwd']
        self.domain = server['domain']
        self.base_url = 'https://' + self.host + ':' + self.port
        self.api_key_name = server['apiKeyName']
        try:
            self.auth_token = self.create_auth_token()
            self.api_key = self.get_api_key()
        except ConnectionError as e:
            raise ConnectionError('Failed to open coneciton with MSO!') from e

    def create_auth_token (self):
        url = self.base_url + '/login'
        payload = json.dumps({
            'userName': self.user,
            'userPasswd': self.passwd,
            'domain': self.domain
        })
        headers = {
            'Content-Type': 'application/json'
        }
        try: 
            response = requests.request('POST', url, headers=headers, data=payload, verify=self.certificate)
            if response.status_code == 200:
                return response.json()['jwttoken']
            else:
                raise AttributeError('Try to verify MSO credentials!')
        except Exception as e:
            raise ConnectionError('Failed to create Auth Token on MSO!') from e
    
    def create_api_key (self):
        raise NotImplementedError('Method not yet implemented.')
    
    def update_api_key_name (self):
        raise NotImplementedError('Method not yet implemented.')
    
    def get_api_key (self):
        raise NotImplementedError('Method not yet implemented.')
    
    def get_api_key (self):
        url = self.base_url + '/api/config/dn/userapikey/local-admin?showPassword=yes'
        payload = json.dumps({})
        headers = {
            'Cookie': 'AuthCookie=' + self.auth_token,
            'Content-Type': 'application/json'
        }
        try:
            key_parser = parser.parse('$.apiKeys[?(@.name=="' + self.api_key_name +'")].key')
            response = requests.request('GET', url, headers=headers, data=payload, verify=self.certificate)
            if response.status_code == 200 and key_parser.find(response.json()):
                return key_parser.find(response.json())[0].value
            else:
                raise AttributeError('Try to verify MSO Api Key Name!')
        except Exception as e:
            raise ConnectionError('Failed to fetch API Key from MSO!') from e

    def delete_api_key (self):
        raise NotImplementedError('Method not yet implemented.')