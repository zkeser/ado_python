from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import os
from pprint import pprint

def get_connection():
    token = os.getenv("ADO_TOKEN")
    org = os.getenv("ADO_ORG")
    organization_url = f"https://dev.azure.com/{org}"
    credentials = BasicAuthentication('', token)
    return Connection(base_url=organization_url, creds=credentials)