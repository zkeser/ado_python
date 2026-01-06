from pprint import pprint
from ado_iteration_automation.read_yaml import read_yaml
from ado_iteration_automation.list_work_items import list_classification_nodes
from ado_iteration_automation.connection import get_connection
from azure.devops.v7_1.work_item_tracking.models import WorkItemClassificationNode

def add_missing_parents(connection):
    wit_client=connection.clients.get_work_item_tracking_client()
    classifications = list_classification_nodes(get_connection())

    # Delete any parents missing dates
    for project_name, classification_data in classifications.items():
        nodes_w_missing_attrs = [node for node in classification_data.get('children', []) if 'attributes' not in node or 'startDate' not in node['attributes'] or 'finishDate' not in node['attributes']]
        # print(nodes_w_missing_attrs)
        # print(nodes_w_missing_attrs[0]['name'])
        if nodes_w_missing_attrs:
            try:
                wit_client.delete_classification_node(project=project_name, structure_group="iterations", path=nodes_w_missing_attrs[0]['name'])
            except Exception as e:
                print(f"Error deleting node {nodes_w_missing_attrs[0]['name']} in project {project_name}: {e}")
        else:
            print(f"No nodes with missing attributes in project {project_name}")

    #Look for missing parents from YAML and create with attributes
    parent_list = read_yaml("ado_iterations_list")
    yaml_lookup = {item['iteration_name']: {"startDate": item["iteration_start_date"], "finishDate": item["iteration_end_date"]} for item in parent_list}
    yaml_names = set(yaml_lookup.keys())
    classifications = list_classification_nodes(get_connection())
    for project_name, classification_data in classifications.items():
        ado_children = classification_data.get('children', [])
        ado_names = {node['name'] for node in ado_children}
        missing_in_ado = yaml_names - ado_names

        if missing_in_ado:
            for missing_name in missing_in_ado:
                dates = yaml_lookup[missing_name]
                posted_node = WorkItemClassificationNode(
                    name=missing_name,
                    attributes={    
                        "startDate": dates['startDate'],
                        "finishDate": dates['finishDate']
                        }
                )
                try:
                    wit_client.create_or_update_classification_node(posted_node, project_name, "iterations")
                    print(f"Created missing node {missing_name} in project {project_name}")
                
                except Exception as e:
                    print(f"Error creating node {missing_name} in project {project_name}: {e}")
        else:
            print(f"No missing parent nodes in project {project_name}")
        


    # Create the remaining leaf nodes under their respective parents as needed
    leaf_list = read_yaml("ado_child_iterations_list")
    return