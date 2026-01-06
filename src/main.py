from ado_iteration_automation.connection import get_connection
from ado_iteration_automation.read_yaml import read_blacklisted_yaml
from ado_iteration_automation.list_projects import get_project_lists
from ado_iteration_automation.list_work_items import list_classification_nodes
from pprint import pprint


if __name__ == "__main__":
    # print(get_project_lists(get_connection()))
    print(list_classification_nodes(get_connection()))
    # read_blacklisted_yaml()