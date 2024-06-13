from log import initialize_log

import requests
import sys
requests.packages.urllib3.disable_warnings()

from config.server_config import ServerDictProps
from mso_session import MsoSession
from mso_fabric import MsoFabric
from mso_schema import MsoSchema
from csv_to_dict import csv_to_dict
from jsonpath_ng import parser

def create_payload_change(input: dict, fabric: MsoFabric):
    """
    Create the change payload based on the provided input and fabric details.

    Args:
        input (dict): A dictionary containing the input data for the change.
        fabric (MsoFabric): An instance of the MsoFabric class representing the target fabric.

    Returns:
        dict: A dictionary representing the payload to be add in the schema payload.
    """
    return {
        "type": input['intfType'],
        "path": fabric.payload['interfaces'][next((index for index, interface in enumerate(fabric.payload['interfaces']) if interface['name'] == input['intfName']), None)]['dn'],
        "portEncapVlan": int(input['vlan']),
        "deploymentImmediacy": input['deploymentImmediacy'],
        "mode": input['mode']
    }

if __name__ == '__main__':

    # Initialize the application log
    app_log = initialize_log("APP_LOG")

    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file_path> | Note: Use absoluty file path location.")
    else:
        file_input = sys.argv[1]

    # Load inputs from the CSV file
    inputs = csv_to_dict(file_input)
    app_log.info('CSV File loaded.')

    # Establish a session with the MSO server
    mso_session = MsoSession(ServerDictProps.get_values('mso_server_config.json'))
    app_log.info('MSO connection established.')

    # Load MSO schemas based on the input data
    schemas : dict ({ str : MsoSchema }) = {}
    for schema_name in set(schema['schema'] for schema in inputs): schemas.update({schema_name: MsoSchema(schema_name, mso_session)})
    app_log.info('MSO schemas loaded.')

    # Load MSO node interfaces based on the input data
    fabrics : dict ({ tuple : MsoFabric }) = {}
    for site_node in set((node['siteName'], node['podName'], node['nodeName'], node['intfType']) for node in inputs): fabrics.update({site_node: MsoFabric(site_node, mso_session)})
    app_log.info('MSO fabrics loaded.')

    for input in inputs:
        
        # Create the change payload for the input
        change_payload = create_payload_change(input, fabrics.get((input['siteName'], input['podName'], input['nodeName'], input['intfType'])))
        
        # Retrieve the payload for the corresponding schema
        payload = schemas[input['schema']].payload

        # Find the template ID based on the input template name
        template_id = parser.parse('$.templates[?(@.name=="' + input['templateName'] + '")].templateID').find(payload)
        if not len(template_id):
            raise AttributeError('Try to verify Template Name!')
        template_id = template_id[0].value

        # Create references for ANP and EPG based on the input data
        anp_ref = '/schemas/' + payload['id'] + '/templates/' + input['templateName'] +'/anps/' + input['applicationProfileName']
        epg_ref = anp_ref + '/epgs/' + input['epgName']

    	# Find the indices for site, ANP, and EPG in the payload
        site_index = next((index for index, site in enumerate(payload['sites']) if site['siteId'] == fabrics.get((input['siteName'], input['podName'], input['nodeName'], input['intfType'])).site_id and site['templateID'] == template_id), None)
        anp_index = next((index for index, anp in enumerate(payload['sites'][site_index]['anps']) if anp['anpRef'] == anp_ref), None)
        if anp_index is not None:
            epg_index = next((index for index, epg in enumerate(payload['sites'][site_index]['anps'][anp_index]['epgs']) if epg['epgRef'] == epg_ref), None)
            if epg_index is None: raise AttributeError('Try to verify EPG Name!')    
        else: raise AttributeError('Try to verify Application Profile Name!')
        
        # Modified the actual payload and update the schemas payload
        payload['sites'][site_index]['anps'][anp_index]['epgs'][epg_index]['staticPorts'].append(change_payload)
        schemas[input['schema']].update_payload(payload)
    app_log.info('Schemas successfully updated.')

    # Update the modified schemas in the MSO server
    for schema in schemas:
        schemas[schema].update_mso_schema()
        app_log.info('Schema ' + schema + ' updated on MSO!')
    app_log.info('MSO schemas successfully updated.')
