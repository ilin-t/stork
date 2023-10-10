import sys
import time

from assign_visitor import AssignVisitor
from src.log_modules.util import getAst
from src.stork_main import Stork
from src.log_modules.parse_repos import unzip


def retrieve_variable_from_assignment(assignment, assignment_list):
    data_file = has_data_file_assignment(assignment=assignment)
    last_change = None
    try:
        if data_file:
            for item in assignment_list:
                if data_file[0] == item["variable"]:
                    last_change = find_closest_assignment(assignment=assignment,
                                                          assignment_list=assignment_list)
            return last_change if last_change else None
    except (NameError, AttributeError) as e:
        print(e)


def retrieve_variable_from_assignment_list(assignment_list):
    mappings = {}

    for assignment in assignment_list:
        data_file = has_data_file_assignment(assignment=assignment)
        try:
            if data_file:
                for item in assignment_list:
                    if data_file[0] == item["variable"]:
                        last_change = find_closest_assignment(assignment=assignment, assignment_list=assignment_list)
                        mappings[assignment["variable"]] = last_change["data_source"]
        except (NameError, AttributeError) as e:
            print(e)
    return mappings


def find_closest_assignment(assignment, assignment_list):
    diff = sys.maxsize
    closest = None
    destination_line = assignment['lineno']
    for item in assignment_list:
        if destination_line - item['lineno'] < diff:
            diff = destination_line - item['lineno']
            if diff <= 0:
                break
            closest = item
    return closest


def find_closest_variable(assignment, variable, position, assignment_list):
    diff = sys.maxsize
    closest = assignment
    destination_line = position
    for item in assignment_list:
        if variable == item["variable"] and destination_line - item['lineno'] < diff:
            diff = destination_line - item['lineno']
            if diff <= 0:
                break
            closest = item
    return closest


def has_data_file_assignment(assignment):
    for source in assignment["data_source"]:
        if isinstance(source, dict):
            try:
                return parse_data_file(source["data_file"])
            except KeyError as e:
                print(e)
                return False


def has_data_file_source(data_source):
    if isinstance(data_source, dict):
        try:
            data_file = has_data_file_source(data_source["data_file"])
            if data_file:
                return parse_data_file(data_file["data_file"])
            else:
                return parse_data_file(data_source["data_file"])
        except KeyError as e:
            print(e)
            return False


def parse_data_file(data_file):
    if isinstance(data_file, list):
        for item in data_file:
            if isinstance(item, str):
                return item
            elif isinstance(item, dict):
                try:
                    if 'data_file' in item.keys():
                        parse_data_file(item['data_file'])
                except KeyError as e:
                    print(f"KeyError: {e}")
                    continue
            else:
                print("i enter here")
                return None


def get_variable_and_value(assignment):
    variable = assignment["variable"]
    value = assignment["data_source"]
    return variable, value


def get_var_value_in_assignment(assignment):
    if not isinstance(assignment['data_source'], list):
        data_source = assignment['data_source']
        return data_source['data_file']
    elif not assignment["variable"] or len(assignment["data_source"]) > 1:
        data_source = assignment['data_source'][0]
        return data_source['data_file']
    else:
        return assignment["data_source"]


def get_value_from_var_name(assignment, variable, position, assignment_list):
    closest_variable_assignment = find_closest_variable(assignment=assignment, variable=variable, position=position,
                                                        assignment_list=assignment_list)
    print(f"closest {closest_variable_assignment}")
    if closest_variable_assignment and closest_variable_assignment["data_source"]:
        if isinstance(closest_variable_assignment["data_source"], list):
            for source in closest_variable_assignment["data_source"]:
                if isinstance(source, dict):
                    data_file = source["data_file"]
                    for item in data_file:
                        if isinstance(item, dict):
                            if 'data_file' in item.keys():
                                return item['data_file'][0]
        else:
            return closest_variable_assignment["data_source"]
    else:
        return None


def replace_variables_in_assignments(assignment_list):
    for assignment in assignment_list:
        if assignment:
            variable, assignment_var = get_variable_and_value(assignment)
            # print(f"variable {variable}, assignment_var: {assignment_var}")
            data_file = get_var_value_in_assignment(assignment)
            # print(f"print data_file: {data_file}")
            val = get_value_from_var_name(assignment=assignment, variable=variable, position=assignment['lineno'],
                                          assignment_list=assignments)
            if val:
                for source in assignment["data_source"]:
                    if isinstance(source, dict):
                        if 'data_file' in source.keys():
                            source['data_file'] = val
                print(f"{assignment}")


#
# # TODO Check duplicates in the variable list. When having duplicates, a full pass
# #  of the assignment list needs to be finished. REVISIT
#
# # def check_duplicates(variables):
# #     duplicate = False
# #     for variable in variables:
# #         for item in variables:
# #             if variable['variable'] == item['variable']:
# #                 duplicate = True
#

if __name__ == '__main__':
    stork = Stork(config_path=r"../db_conn/config_s3.ini")
    repo_path = "/home/ilint/HPI/repos/stork/examples/data/table_ocr.zip"
    unzip(repo_path=repo_path)
    pipeline = f"{repo_path[:-4]}/table_ocr-master/Evaluations/Tablebank/evaluation.py"

    stork.setClient(stork.access_key, stork.secret_access_key)
    stork.assignVisitor = AssignVisitor()
    tree = getAst(pipeline=pipeline)
    stork.assignVisitor.setPipeline(pipeline=pipeline)
    stork.assignVisitor.visit(tree)

    assignments = stork.assignVisitor.assignments
    replace_variables_in_assignments(assignments)

