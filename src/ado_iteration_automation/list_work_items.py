from pprint import pprint
from ado_iteration_automation.read_yaml import read_yaml
from ado_iteration_automation.connection import get_connection
from ado_iteration_automation.list_projects import get_project_lists

def list_classification_nodes(connection):
    wit_client = connection.clients.get_work_item_tracking_client()
    
    projects = get_project_lists(connection)
    all_data = {}
    blacklist = read_yaml("ado_project_blacklist")


    for project in projects:
        if project['id'] not in blacklist:
        # while project['id'] not in read_yaml("./data/ado_project_blacklist.yml"):
            try:
                print(f"Fetching iterations for: {project['name']}...")
                node_response = wit_client.get_classification_node(
                    project=project["id"],
                    structure_group="iterations",
                    depth=5
                )
                
                if node_response:
                    all_data[project["name"]] = node_response.as_dict()
                else:
                    all_data[project["name"]] = "No nodes found"

            except Exception as e:
                print(f"❌ Failed to fetch {project['name']}: {e}")
                all_data[project['name']] = f"Error: {str(e)}"
    
    # pprint(all_data['AZ-400 Playground']['children']["name"])
    # pprint(all_data['AZ-400 Playground']['attributes'])
    return all_data