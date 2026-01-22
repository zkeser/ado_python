from  pprint import pprint
from ado_iteration_automation.read_yaml import read_yaml

def get_teams(connection):
    core_client = connection.clients.get_core_client()
    get_teams_response = core_client.get_all_teams()

    extracted_teams = []
    blacklisted_projects = read_yaml("ado_project_blacklist")
    blacklisted_teams = read_yaml("ado_team_blacklist")
    
    for team in get_teams_response:
        url_parts = team.url.rstrip('/').split('/')
        organization = url_parts[-6]
        project_id = url_parts[-3]
        team_id = url_parts[-1]
        if project_id not in blacklisted_projects and team_id not in blacklisted_teams:
            extracted_teams.append({
                "organization": organization,
                "project_id": project_id,
                "project_name": team.project_name,
                "team_id": team_id,
                "team_name": team.name
            })  
    return extracted_teams

