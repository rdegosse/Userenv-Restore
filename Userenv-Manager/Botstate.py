#!/usr/bin/env python
"""Botstate.

Python wrappers for FarmBot bostate API.

rdegosse
"""
import os
import json
from functools import wraps
import requests

debug_dev = False

def farmware_api_url():
    """Return the correct Farmware API URL according to FarmBot OS version."""
    major_version = int(os.getenv('FARMBOT_OS_VERSION', '0.0.0')[0])
    if debug_dev:
        base_url = 'http://192.168.x.x:27347/'
        return base_url + 'api/v1/'
    else:
        base_url = os.environ['FARMWARE_URL']
        return base_url + 'api/v1/' if major_version > 5 else base_url
    


def _print_json(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        """Send Botstate or return the JSON string.

        Boststate is sent by sending an HTTP GET request to /bot/state
        using the url in the `FARMWARE_URL` environment variable.
        """
        try:
            if not debug_dev: os.environ['FARMWARE_URL']
        except KeyError:
            # Not running as a Farmware: return JSON
            return function(*args, **kwargs)
        else:
            # Running as a Farmware:
            if debug_dev:
                farmware_token = 'eyJhbGciOiJSUzI1.......'
            else:
                farmware_token = os.environ['FARMWARE_TOKEN']
            headers = {'Authorization': 'bearer {}'.format(farmware_token),
                       'content-type': "application/json"}
            payload = json.dumps(function(*args, **kwargs))
            ret = requests.get(farmware_api_url() + 'bot/state',
                          data=payload, headers=headers)
            return ret.json()
    return wrapper


@_print_json
def get_bot_state():
    return {}
 
def get_user_env():
    return get_bot_state()['user_env']

