from pprint import pprint

def get_project_lists(connection):
    core_client = connection.clients.get_core_client()
    get_projects_response = core_client.get_projects()
    return [{"name": p.name, "id": p.id} for p in get_projects_response]