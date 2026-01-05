import yaml, os
from pprint import pprint

def read_blacklisted_yaml():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(current_dir, "data", "ado_project_blacklist.yml")
    with open (default_path, 'r') as file:
        try:
            data = yaml.load(file, Loader=yaml.SafeLoader)
            blacklist = data.get("ado_project_blacklist", [])
            # print(blacklist)
            return blacklist
        except yaml.YAMLError as e:
            print(f"Error parsing YAML {e}")