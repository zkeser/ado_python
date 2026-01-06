from ado_iteration_automation.connection import get_connection
from ado_iteration_automation.read_yaml import read_yaml
from ado_iteration_automation.list_projects import get_project_lists
from ado_iteration_automation.list_work_items import list_classification_nodes
from ado_iteration_automation.update_nodes import add_missing_parents
from pprint import pprint


if __name__ == "__main__":
    add_missing_parents(get_connection())