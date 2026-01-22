from ado_iteration_automation.connection import get_connection
from ado_iteration_automation.read_yaml import read_yaml
from ado_iteration_automation.list_projects import get_project_lists
from ado_iteration_automation.list_work_items import list_classification_nodes
from ado_iteration_automation.update_nodes import create_update_missing_parents, update_leaf_nodes, create_missing_leaf_nodes
from ado_iteration_automation.get_teams import get_teams
from ado_iteration_automation.update_teams import assign_iterations_to_teams  
from pprint import pprint


if __name__ == "__main__":
    create_update_missing_parents(get_connection())
    update_leaf_nodes(get_connection())
    create_missing_leaf_nodes(get_connection())
    assign_iterations_to_teams(get_connection(), get_teams(get_connection()))
    # pprint(get_teams(get_connection()), indent = 2)
    # pprint(len(get_teams(get_connection())))
    # pprint(get_project_lists(get_connection()), indent =2)   