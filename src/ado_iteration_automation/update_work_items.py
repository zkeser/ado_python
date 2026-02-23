from pprint import pprint
from ado_iteration_automation.read_yaml import read_yaml
from ado_iteration_automation.connection import get_connection
from ado_iteration_automation.list_projects import get_project_lists
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation, Wiql



def wiql_query(connection):
    wit_client = connection.clients.get_work_item_tracking_client()
    yaml_projects = read_yaml("ado_project_blacklist")
    epics = {}
    for project in get_project_lists(connection):
        if project["id"] not in yaml_projects:
            project_name =  project["name"]
            wiql = Wiql( 
                query=f""" 
                SELECT [System.Id], 
                    [System.WorkItemType], 
                    [System.Title], 
                    [System.State] 
                FROM workitems 
                WHERE [System.TeamProject] = "{project_name}"
                ORDER BY [System.Id] 
                """ 
                )
            
            query_result = wit_client.query_by_wiql(wiql)
            ids= [x.id for x in query_result.work_items]
            for id in ids:

                work_item = wit_client.get_work_item(id=id)
                work_type = work_item.as_dict()["fields"]["System.WorkItemType"]
                work_title = work_item.as_dict()["fields"]["System.Title"]
                work_item_id = work_item.as_dict()["id"]
                
                if  work_type == "Epic":
                     epics[work_title] = work_item_id
    return epics

def rename_work_item_epic(connection):
    yaml_work_item_changes = read_yaml("ado_work_item_updates")
    epics = wiql_query(connection)
    epic_names = set(epics.keys())
    for array in yaml_work_item_changes:
        old_name, new_name= array.values()
        if old_name in epic_names:
            epic_id = epics[old_name]
         
            patch = [JsonPatchOperation(
                op="add",
                path="/fields/System.Title",
                value=new_name
            )   ]

            wit_client = connection.clients.get_work_item_tracking_client()
            wit_client.update_work_item(
                id=epic_id,
                document=patch
            )
            print(f"✅ Updated work item {old_name} title to {new_name} based on YAML configuration.")
    return 
   
