# python/config/server_config.py
import os
import json
import pathlib
import logging as log

class ServerDictProps():
    """
    Represents a utility class for retrieving server dictionary properties from a configuration file.

    This class provides static methods to access server properties stored in a JSON configuration file. It allows retrieving the entire dictionary of server properties or a specific value based on a key.

    Methods:
        get_values(): Retrieves the server properties dictionary from the configuration file.

            Returns:
                dict or None: The server properties dictionary loaded from the configuration file. Returns None if there is an error.

        get_value(key: str): Retrieves a specific value from the server properties dictionary based on the given key.

            Args:
                key (str): The key corresponding to the value to be retrieved.

            Returns:
                Any or None: The value corresponding to the given key. Returns None if the key does not exist or if there is an error.

    Example:
        # Retrieve the entire server properties dictionary
        server_props = ServerDictProps.get_values()

        # Retrieve a specific value from the server properties dictionary
        host = ServerDictProps.get_value('host')
    """

    __values = None

    @staticmethod
    def get_values(config_file):
        try:
            if ServerDictProps.__values == None:
                conf = os.path.normpath(str(pathlib.Path(__file__).parent.resolve()) + '/' + config_file)
                log.debug('Loading configuration file: %s', conf)
                with open(conf) as f:
                    ServerDictProps.__values = json.load(f)
            return ServerDictProps.__values
        except Exception as e:
            log.error(e)

    @staticmethod
    def get_value(key):
        if ServerDictProps.__values == None: ServerDictProps.get_values()
        return ServerDictProps.__values[key]