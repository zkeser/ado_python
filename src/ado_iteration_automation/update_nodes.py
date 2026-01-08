from pprint import pprint
from ado_iteration_automation.read_yaml import read_yaml
from ado_iteration_automation.list_work_items import list_classification_nodes
from ado_iteration_automation.connection import get_connection
from azure.devops.v7_1.work_item_tracking.models import WorkItemClassificationNode
    

def create_update_missing_parents(connection):
    wit_client=connection.clients.get_work_item_tracking_client()
    classifications = list_classification_nodes(get_connection())

    # Build lookup from YAML
    parent_list = read_yaml("ado_iterations_list")
    yaml_lookup = {item['iteration_name']: {"startDate": item["iteration_start_date"], "finishDate": item["iteration_end_date"]} for item in parent_list}
    yaml_names = set(yaml_lookup.keys())

    #Update existing parents that have no dates with dates from YAML
    classifications = list_classification_nodes(get_connection())
    for classification in classifications.values():
        for child in classification['children']:
            if "attributes" not in child:
                posted_node = WorkItemClassificationNode(
                    attributes={
                        "startDate": yaml_lookup[child['name']]['startDate'],
                        "finishDate": yaml_lookup[child['name']]['finishDate']
                    }
                )
                try:
                    wit_client.update_classification_node(posted_node, project=classification['name'], structure_group="iterations", path=child['name'])
                    print(f"Updated parent iteration {child['name']} in project {classification['name']} with dates.")

                except Exception as e:
                    print(f"Error updating iteration {child['name']} in project {classification['name']}: {e}")


    #Look for missing parents from YAML and create with attributes
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
            print(f"No missing parent iterations in project {project_name}")
        
    return


# Create the remaining leaf iterations under their respective parents as needed
def update_missing_leaf_nodes(connection):
    wit_client=connection.clients.get_work_item_tracking_client()
    leaf_list = read_yaml("ado_child_iterations_list")
    leaf_yaml_lookup = {item['iteration_name']: {"startDate": item["iteration_start_date"], "finishDate": item["iteration_end_date"]} for item in leaf_list}
    

    #Update existing leafs that have no dates with dates from YAML
    classifications = list_classification_nodes(get_connection())
    for classification in classifications.values():
        for child in classification['children']:
            parent_name = child['name']
            for leaf in child.get('children', []):
                leaf_name = leaf['name']
                if ("attributes" not in leaf or 
                    leaf['attributes'].get("startDate") != leaf_yaml_lookup[leaf['name']]["startDate"] or 
                    leaf['attributes'].get("finishDate") != leaf_yaml_lookup[leaf['name']]["finishDate"]):
                    posted_node = WorkItemClassificationNode(
                        attributes={
                            "startDate": leaf_yaml_lookup[leaf['name']]['startDate'],
                            "finishDate": leaf_yaml_lookup[leaf['name']]["finishDate"]
                        }
                    )
                    try:
                        full_path = f"{parent_name}/{leaf_name}"
                        wit_client.update_classification_node(posted_node, project=classification['name'], structure_group="iterations", path=full_path)
                        print(f"Updated leaf iteration {leaf['name']} in project {classification['name']} with dates.")

                    except Exception as e:
                        print(f"Error updating iteration {leaf['name']} in project {classification['name']}: {e}")


    #Add remaining leaf iterations from YAML
def create_missing_leaf_nodes(connection):
    wit_client=connection.clients.get_work_item_tracking_client()
    classifications = list_classification_nodes(get_connection())
    leaf_list = read_yaml("ado_child_iterations_list")
    leaf_yaml_lookup = {item['iteration_name']: {"startDate": item["iteration_start_date"], "finishDate": item["iteration_end_date"]} for item in leaf_list}
    leaf_yaml_names = {item['iteration_name'] for item in leaf_list}
    # leaf_yaml_names = set(leaf_yaml_lookup.keys())

    
    classifications = list_classification_nodes(connection)
    missing_by_project = {}

    for project_name, data in classifications.items():
        existing_leaf_names = set()
        for parent in data.get('children', []):
            for leaf in parent.get('children', []):
                leaf_name = leaf['name']
                existing_leaf_names.add(leaf['name'])
    
        missing_in_project = leaf_yaml_names - existing_leaf_names

        if missing_in_project:
            missing_by_project[project_name] = list(missing_in_project)
            for missing_leaf in list(missing_in_project):
                missing_leaf_obj = [item for item in leaf_list if item['iteration_name'] == missing_leaf]
                for leaf_info in missing_leaf_obj:

                    posted_node = WorkItemClassificationNode(
                        name=leaf_info['iteration_name'],
                        attributes={
                            "startDate": leaf_yaml_lookup[leaf_info['iteration_name']]['startDate'],
                            "finishDate": leaf_yaml_lookup[leaf_info['iteration_name']]["finishDate"]
                            }
                            )
                    
                    try:
                        
                        wit_client.create_or_update_classification_node(posted_node, project=project_name, structure_group="iterations", path=leaf_info['parent_iteration_name'])
                        print(f"Created missing leaf iterations in project {project_name}: {missing_in_project}")
                    except Exception as e:
                        print(f"Error creating leaf node {missing_leaf} in project {project_name}: {e}")
           
        else:
            print(f"No missing leaf iterations in project {project_name}")

    return 
