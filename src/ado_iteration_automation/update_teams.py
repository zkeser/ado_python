from ado_iteration_automation.list_work_items import list_classification_nodes
from ado_iteration_automation.read_yaml import read_yaml
from azure.devops.v7_1.work.models import TeamContext, TeamSettingsIteration
from pprint import pprint

def assign_iterations_to_teams(connection, teams_data):
    work_client = connection.clients.get_work_client()
    classifications = list_classification_nodes(connection)
    
    # 1. Map ADO IDs (Project -> Name -> ID)
    parent_iteration_ids = {}
    child_iteration_ids = {}

    for project_name, project_node in classifications.items():
        parent_iteration_ids[project_name] = {}
        child_iteration_ids[project_name] = {}
        
        project_objs = project_node.get('children', [])
        for parent in project_objs:
            p_name = parent.get('name', '')
            p_id = parent.get('identifier', '')
            parent_iteration_ids[project_name][p_name] = p_id
            
            for child in parent.get('children', []):
                c_name = child.get('name', '')
                c_id = child.get('identifier', child.get('id')) 
                child_iteration_ids[project_name][c_name] = c_id
    
    # 2. Initialize YAML data inside the function scope
    yaml_parent_names = [p['iteration_name'] for p in read_yaml("ado_iterations_list")]
    
    # Create the dictionary for child iterations
    yaml_child_dict = {}
    yaml_leaf_iterations = read_yaml("ado_child_iterations_list")
    for item in yaml_leaf_iterations:
        yaml_child_dict[item['iteration_name']] = item['parent_iteration_name']

    # 3. Assign iterations to teams
    for team in teams_data:
        team_context = TeamContext(
            project_id=team['project_id'],
            team_id=team['team_id']
        )
        existing_assigned = work_client.get_team_iterations(team_context=team_context)
        assigned_guids = {item.id for item in existing_assigned}
 
        p_name = team['project_name']
        project_id_map = parent_iteration_ids.get(p_name, {})
        project_leaf_map = child_iteration_ids.get(p_name, {}) # Define map for this project

        # --- Parent Iterations ---
        for target_name in yaml_parent_names:
            iteration_guid = project_id_map.get(target_name)
            
            if iteration_guid:
                
                if iteration_guid in assigned_guids:
                    continue

                iteration_obj = TeamSettingsIteration(id=iteration_guid)
               
                try:
                    work_client.post_team_iteration(
                        iteration=iteration_obj,
                        team_context=team_context
                    )
                    print(f"✅ Assigned Parent '{target_name}' to team '{team['team_name']}'")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        continue
                    print(f"❌ Error assigning {target_name}: {e}")
            else:
                print(f"⚠️ Warning: Parent '{target_name}' not found in ADO for project '{p_name}'")

        # --- Leaf Iterations (Moved inside the team loop) ---
        for leaf_name in yaml_child_dict.keys():
            iteration_guid = project_leaf_map.get(leaf_name)
  
            if iteration_guid:
                iteration_obj = TeamSettingsIteration(id=str(iteration_guid))
                if iteration_guid in assigned_guids:
                    continue

                try:
                    work_client.post_team_iteration(
                        iteration=iteration_obj,
                        team_context=team_context
                    )
                    print(f"✅ Assigned Leaf '{leaf_name}' to team '{team['team_name']}'")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        continue
                    print(f"❌ Error assigning leaf {leaf_name}: {e}")
            else:
                print(f"⚠️ Warning: Leaf '{leaf_name}' not found in ADO for project '{p_name}'")
    return
