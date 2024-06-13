#!/usr/bin/env python3
from mso_session import MsoSession

import json
from jsonpath_ng.ext import parser

import requests
requests.packages.urllib3.disable_warnings()

class MsoSchema:
    """
    Represents a schema in the MSO server.

    This class provides methods to interact with schemas in the MSO server. It allows retrieving the schema ID and payload, updating the payload, and updating the MSO schema with the updated payload.

    Args:
        name (str): The name of the schema.
        session (MsoSession): An instance of the MsoSession class representing the MSO server session.

    Raises:
        ConnectionError: If there is a connection error while establishing a connection with the MSO server.
        AttributeError: If there is an issue with MSO schema name.

    Attributes:
        session (MsoSession): An instance of the MsoSession class representing the MSO server session.
        name (str): The name of the schema.
        id (str): The ID of the schema retrieved from the MSO server.
        payload (dict): The payload of the schema retrieved from the MSO server.

    Methods:
        get_schema_id(): Retrieves the ID of the schema from the MSO server.

            Returns:
                str: The ID of the schema.

        get_schema_payload(): Retrieves the payload of the schema from the MSO server.

            Returns:
                dict: The payload of the schema.

        update_payload(payload: dict): Updates the payload of the schema.

            Args:
                payload (dict): The updated payload of the schema.

        update_mso_schema(): Updates the MSO schema with the updated payload.

            Raises:
                ConnectionError: If there is an error finding the Schema Update URL on the MSO server.
                AttributeError: If the update operation fails and displays the reponse body.

    Example:
        # Create an instance of MsoSession
        session = MsoSession(server_props)

        # Create an instance of MsoSchema
        schema = MsoSchema('MySchema', session)

        # Retrieve the schema ID
        schema_id = schema.get_schema_id()

        # Retrieve the schema payload
        schema_payload = schema.get_schema_payload()

        # Update the schema payload
        updated_payload = {...}
        schema.update_payload(updated_payload)

        # Update the MSO schema with the updated payload
        schema.update_mso_schema()
    """

    def __init__ (self, name: str, session: MsoSession):
        self.session = session
        self.name = name
        self.id = self.get_schema_id()
        self.payload = self.get_schema_payload()

    def get_schema_id (self):
        url = self.session.base_url + '/mso/api/v1/schemas?X-Nd-Apikey=' + self.session.api_key + '&X-Nd-Username=' + self.session.user
        headers = {
            'Cookie': 'AuthCookie=' + self.session.auth_token,
            'Content-Type': 'application/json'
        }
        try:
            key_parser = parser.parse('$.schemas[?(@.displayName=="' + self.name + '")].id')
            response = requests.request("GET", url, headers=headers, verify=self.session.certificate)
            if response.status_code == 200 and key_parser.find(response.json()):
                return key_parser.find(response.json())[0].value
            else:
                raise AttributeError('Try to verify MSO Schema Name!')
        except Exception as e:
            raise ConnectionError('Failed to fetch Schema ID from MSO!') from e
        
    def get_schema_payload (self):
        url = self.session.base_url + '/mso/api/v1/schemas?X-Nd-Apikey=' + self.session.api_key + '&X-Nd-Username=' + self.session.user
        headers = {
            'Cookie': 'AuthCookie=' + self.session.auth_token,
            'Content-Type': 'application/json'
        }
        try:
            key_parser = parser.parse('$.schemas[?(@.id=="' + self.id + '")]')
            response = requests.request("GET", url, headers=headers, verify=self.session.certificate)
            if response.status_code == 200 and key_parser.find(response.json()):
                return key_parser.find(response.json())[0].value
            else:
                raise AttributeError('Try to verify MSO Schema Name!')
        except Exception as e:
            raise ConnectionError('Failed to fetch Schema Payload from MSO!') from e
        
    def update_payload (self, payload):
        self.payload = payload

    def update_mso_schema (self):
        url = self.session.base_url + '/mso/api/v1/schemas/' + self.id + '?X-Nd-Apikey=' + self.session.api_key + '&X-Nd-Username=' + self.session.user
        headers = {
            'Cookie': 'AuthCookie=' + self.session.auth_token,
            'Content-Type': 'application/json'
        }
        try: 
            response = requests.request("PUT", url, headers=headers, data=json.dumps(self.payload), verify=self.session.certificate)
        except:
            raise ConnectionError('Failed to find Schema Update URL on MSO!')
        if not response.status_code == 201:
            e = Exception(f"Request Body:\n{response.json()}")
            raise AttributeError('Failed to update MSO Schema ' + self.name + '!') from e