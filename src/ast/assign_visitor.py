import ast
import hashlib
import os
import re
import sys
from pathlib import Path

from src.log_modules import util
from src.db_conn.s3_connector import S3Connector
from src.log_modules.log_results import createLogger


class AssignVisitor(ast.NodeVisitor):
    def __init__(self):
        self.pipeline = ""
        self.assignment = {"variable": str, "data_source": [], }
        self.imports= {}
        self.inputs = []
        self.assignments = []
        self.func_definitions = []
        self.datasets = []
        self.datasets_files = []
        self.imports = []
        self.new_inputs = []
        self.new_datasets = []
        self.datasets_urls = []
        self.logger = None
        self.variables = []
        self.read_methods={'raw_string': [], 'variable': [], 'external': []}
        self.datasets_read_methods = {'raw_string': [], 'variable': [], 'external': []}

    def direct_visit(self, parent_object, node, towards):
        try:
            func_name = "visit_" + type(towards).__name__
            func = getattr(parent_object, func_name)
            # print(f"Method {func_name} will be called from node "
            #       f"type {type(node)} from object {type(parent_object)} towards object {type(towards)}.\n")
            output = func(towards)
            return output

        except AttributeError as e:
            if self.logger:
                self.logger.error("visit_" + type(towards).__name__ + " accessed from node type " + type(
                    node).__name__ + " is not defined.\n")
            else:
                print(f"visit_{type(towards).__name__} accessed from node type {type(node).__name__} is not defined.\n"
                      f"error message: {e}")
        except TypeError as e:
            self.logger.error(e)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({"import" : alias.name})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        temp = {"from": node.module, "import": []}
        for alias in node.names:
            temp["import"].append(alias.name)
        self.imports.append({"from": temp})
        self.generic_visit(node)

    def visit_With(self, node):
        # items = self.direct_visit(self, node, node.items)
        # body = self.direct_visit(self, node, node.body)
        for item in node.items:
            args = self.direct_visit(self, node, item)
        for item in node.body:
            body_el = self.direct_visit(self, node, item)

    def visit_withitem(self, node):

        context_expr = self.direct_visit(self, node, node.context_expr)
        optional_vars = self.direct_visit(self, node, node.optional_vars)
        self.assignment["variable"] = optional_vars
        self.assignment["data_source"] = context_expr

        self.assignments.append(self.assignment)

    def visit_FunctionDef(self, node):
        args = self.direct_visit(self, node, node.args)
        function_body = []
        decorator_list = []
        for item in node.body:
            function_body.append(self.direct_visit(self, node, item))

        for element in node.decorator_list:
            decorator_list.append(element)

        func_def = {"function": node.name, "args": args, "data_source": function_body, "decorator_list":decorator_list}
        self.func_definitions.append(func_def)
        return func_def

    def visit_For(self, node):

        target = self.direct_visit(self, node, node.target)
        el_list = self.direct_visit(self, node, node.iter)

        for elt in node.body:
            self.direct_visit(self, node, elt)

    def visit_Try(self, node):
        for elt in node.body:
            self.direct_visit(self, node, elt)

        for handler in node.handlers:
            self.direct_visit(self, node, handler)

        for alternative in node.orelse:
            self.direct_visit(self, node, alternative)

        for elt_fb in node.finalbody:
            self.direct_visit(self, node, elt_fb)

    # TODO Extract values from If Node
    def visit_If(self, node):
        return None

    # TODO Extract values from Expr Node
    def visit_Expr(self, node):
        return None

    def visit_Return(self, node):
        value = self.direct_visit(self, node, node.value)
        return value

    def visit_list(self, node):
        return node

    def visit_Assign(self, node):
        self.assignment = {"variable": str, "data_source": []}
        for target in node.targets:
            self.assignment["variable"] = self.direct_visit(self, node, target)
            self.assignment["data_source"].append(self.direct_visit(parent_object=self, node=node, towards=node.value))
            self.assignment["lineno"] = node.lineno

        self.assignments.append(self.assignment)

    def visit_Call(self, node):
        func_call = self.direct_visit(parent_object=self, node=node, towards=node.func)
        args_names = []
        params = []
        var_flag = False
        for arg in node.args:
            temp = self.get_assignment_value_from_var_name_node(variable=self.direct_visit(self, node, arg), position=arg.lineno)
            if temp:
                args_names.append(temp[0])
                var_flag = True
            else:
                args_names.append(self.direct_visit(parent_object=self, node=node, towards=arg))
        for keyword in node.keywords:
            params.append(self.direct_visit(self, node, keyword))
        try:
            if var_flag:
                args_names = "".join(args_names)
            # print(f"Args_names: {args_names}")
            if type(node.func).__name__ == "Attribute" and self.assignment["data_source"]:
                self.assignment["data_source"].append(
                    {"func_call": func_call, "data_file": args_names, "params": params})
            else:
                return {"func_call": func_call, "data_file": args_names, "params": params}
        except(KeyError, TypeError, AttributeError) as e:
            self.logger.error(e)

    def visit_Attribute(self, node):
        package = self.direct_visit(parent_object=self, node=node, towards=node.value)
        method = node.attr
        if type(node).__name__ == "Call":
            self.assignment["data_source"].append(package)
        else:
            return {"from": package, "method": method}

    def visit_BinOp(self, node):
        right_var_value = self.direct_visit(parent_object=self, node=node, towards=node.right)
        left_var_value = self.direct_visit(parent_object=self, node=node, towards=node.left)

        if isinstance(node.left, ast.Name):
            left_var_value = self.get_assignment_value_from_var_name_node(variable=left_var_value, position=node.lineno)[0]

        if isinstance(node.right, ast.Name):
            right_var_value = self.get_assignment_value_from_var_name_node(variable=right_var_value, position=node.lineno)[0]

        if type(node.op).__name__ == "Add":
            return f"{left_var_value}{right_var_value}"

        # print(f"BinOp for {node.lineno}. Left operand: {left_var_value}, right operand {right_var_value}.")
        return [left_var_value, right_var_value]

    def visit_Subscript(self, node):
        load_var = self.direct_visit(parent_object=self, node=node, towards=node.value)
        filter_criteria = self.direct_visit(parent_object=self, node=node, towards=node.slice)

        return [load_var, filter_criteria]

    def visit_Slice(self, node):
        lower = self.direct_visit(self, node, node.lower)
        upper = self.direct_visit(self, node, node.upper)

        return [lower, upper]

    def visit_Name(self, node):

        return node.id

    def visit_Constant(self, node):
        return node.value

    def visit_keyword(self, node):
        return {node.arg: self.direct_visit(parent_object=self, node=node, towards=node.value)}

    def visit_Compare(self, node):
        left = self.direct_visit(parent_object=self, node=node, towards=node.left)
        operation = node.ops
        right = self.direct_visit(parent_object=self, node=node, towards=node.comparators[0])

        return {"left_op": left, "operator": operation, "right": right}

    def visit_Lambda(self, node):
        args = self.direct_visit(parent_object=self, node=node, towards=node.args)
        func = self.direct_visit(parent_object=self, node=node, towards=node.body)

    def visit_arguments(self, node):
        args = []
        for arg in node.args:
            args.append(self.direct_visit(self, node, arg))
        return args

    def visit_arg(self, node):
        return node.arg

    def visit_List(self, node):
        list_el = []
        var_flag = False
        for element in node.elts:
            temp = self.get_assignment_value_from_var_name_node(variable=self.direct_visit(self, node, element),
                                                                position=element.lineno)
            if temp:
                list_el.append(temp[0])
                var_flag = True
            else:
                list_el.append(self.direct_visit(parent_object=self, node=node, towards=element))
        if var_flag:
            list_el = "".join(list_el)

        return list_el

    #
    def visit_Tuple(self, node):
        tuple_el = []
        var_flag = False
        for element in node.elts:
            temp = self.get_assignment_value_from_var_name_node(variable=self.direct_visit(self, node, element),
                                                                position=element.lineno)
            if temp:
                tuple_el.append(temp[0])
                var_flag = True
            else:
                tuple_el.append(self.direct_visit(parent_object=self, node=node, towards=element))
        if var_flag:
            tuple_el = "".join(tuple_el)

        return tuple_el

    def visit_Dict(self, node):
        content = {}
        for element in node.keys:
            key = self.direct_visit(self, node, element)
            key_index = node.keys.index(element)
            value = self.direct_visit(self, node, node.values[key_index])
            content[key] = value
            # print(f"Key: {key}, Index: {key_index}, Value: {value}")
        # return content

    def visit_ListComp(self, node):
        return 0

    def visit_JoinedStr(self, node):
        string_parts = ""
        for element in node.values:
            variable = self.direct_visit(self, node, element)
            if isinstance(variable, str):
                string_parts = string_parts + variable
            else:
                string_parts = string_parts + variable[0]
            # print(f"STRING PARTS {string_parts}")

        return string_parts

    def visit_FormattedValue(self, node):
        formatted_value = self.direct_visit(self, node, node.value)
        # print(type(node.value).__name__)
        if isinstance(node.value, ast.Name):
            # print(f"YES {formatted_value}")
            var_value = self.get_assignment_value_from_var_name_node(variable=formatted_value, position=node.lineno)
            if var_value:
                self.logger.info(f"Retrieving value for variable: {node.value}. Value: {var_value}")
                # print(f"Retrieving value for variable: {node.value}. Value: {var_value}")
                return var_value
            else:
                return formatted_value
        return formatted_value

    def filter_Assignments(self):
        removed = []
        try:
            for assignment in self.assignments:
                # print("Type of the above assignment: %s" % type(assignment["data_source"]))
                # print(f"Assignment: {assignment}")
                assignment["data_source"] = [i for i in assignment["data_source"] if i is not None]
                for source in assignment["data_source"]:

                    data_file_from_var = self.retrieve_variable_from_assignment(assignment=assignment,
                                                                                assignment_list=self.assignments)
                    # print(f"Data file from variable retrieved: {data_file_from_var}")
                    # print(f"Data file from var: {data_file_from_var}")
                    new_assignment = self.var_assignment_to_input(var_assignment=data_file_from_var,
                                                                  assignment=assignment)
                    # print(f"New assigment: {new_assignment}")
                    if new_assignment and new_assignment not in self.inputs:
                        # print(f"Assignment to be stored as a 'var access': {new_assignment}")
                        self.read_methods['variable'].append(new_assignment)
                        self.inputs.append(new_assignment)
                        break

                    if self.keepDataSource(data_source=source) and assignment not in self.inputs:
                        self.inputs.append(assignment)
                        # print(f"Raw string data assignment: {assignment}")
                        self.read_methods['raw_string'].append(assignment)
                        break
            self.inputs = [assignment for assignment in self.assignments if assignment not in removed]
        except (AttributeError, KeyError, TypeError) as e:
            self.logger.error(e)

        return self.inputs

    def keepDataSource(self, data_source):
        try:
            if type(data_source) is not dict:
                return False
            elif "data_file" not in data_source.keys():
                return False
            elif len(data_source["data_file"]) == 0:
                return False
            elif type(data_source["data_file"][0]) is not str:
                return False
            elif not util.checkDataFile(data_source["data_file"]):
                return False
            else:
                return True
        except (TypeError, AttributeError, KeyError) as e:
            self.logger.error(e)

    def var_assignment_to_input(self, var_assignment, assignment):
        try:
            data_path = var_assignment['data_source']
            for source in assignment['data_source']:
                self.logger.info(
                    f"var_assignment['variable']: {var_assignment['variable']}, source['data_file']: {data_path}, var_assignment: {var_assignment}")
                self.logger.info(
                    f"assignment['variable']: {assignment['variable']}, source['data_file']: {source['data_file']})")
                if self.has_data_file_single_source(source=source) and (
                        var_assignment['variable'] == source['data_file'][0]):
                    source['data_file'] = data_path
                    self.logger.info(f"New assignment: {assignment}")
                    break
        except TypeError as e:
            self.logger.error(e)
        return assignment

    # def get_value_from_var_name_node(self, variable, position):
    #     closest_variable_assignment = self.find_closest_variable_node(variable=variable, position=position)
    #     try:
    #         if closest_variable_assignment:
    #             if self.has_data_file(closest_variable_assignment):
    #                 data_source = closest_variable_assignment["data_source"]
    #                 data_source = [i for i in data_source if i is not None]
    #                 for item in data_source:
    #                     if isinstance(item, dict):
    #                         return item["data_file"]
    #             else:
    #                 return closest_variable_assignment["data_source"]
    #         else:
    #             return None
    #     except KeyError as e:
    #         self.logger.error(e)

    def get_assignment_value_from_var_name_node(self, variable, position):
        try:
            closest_variable_assignment = self.find_closest_variable_node(variable=variable, position=position)
            if isinstance(closest_variable_assignment["data_source"], list):
                for source in closest_variable_assignment["data_source"]:
                    # print(f"SOURCE: {source}")
                    if isinstance(source, dict):
                        data_file = source["data_file"]
                        for item in data_file:
                            if isinstance(item, dict):
                                if 'data_file' in item.keys():
                                    try:
                                        return item['data_file'][0]
                                    except IndexError as e:
                                        self.logger.error(e)

                    else:
                        return closest_variable_assignment["data_source"]
            else:
                return closest_variable_assignment["data_source"]

        except (RecursionError, AttributeError, KeyError, TypeError) as e:
            self.logger.error(e)

    def find_closest_variable_node(self, variable, position):
        diff = sys.maxsize
        closest = None
        destination_line = position
        for item in self.assignments:
            if variable == item["variable"] and destination_line - item['lineno'] < diff:
                diff = destination_line - item['lineno']
                if diff <= 0:
                    break
                closest = item
        return closest

    def retrieve_variable_from_assignment(self, assignment, assignment_list):
        data_file = self.has_data_file(assignment=assignment)

        last_change = None
        try:
            if data_file:
                # print(f"Data file retrieved: {data_file}")
                for item in assignment_list:
                    if data_file[0] == item["variable"]:
                        # print(f"Data file {data_file} matching variable {item}")
                        last_change = self.get_closest_assignment(assignment=item,
                                                                  assignment_list=assignment_list)
                return last_change if last_change else None
        except (NameError, AttributeError, TypeError, KeyError) as e:
            self.logger.error(e)

    # # def retrieve_variable_from_assignment_list(self, assignment_list):
    #     for assignment in assignment_list:
    #         data_file = self.has_data_file(assignment=assignment)
    #         try:
    #             if data_file:
    #                 for item in assignment_list:
    #                     if data_file[0] == item["variable"]:
    #                         last_change = self.get_closest_assignment(assignment=assignment,
    #                                                                   assignment_list=assignment_list)
    #         except (NameError, AttributeError) as e:
    #             self.logger.error(e)

    # def find_closest_assignment(self, assignment, assignment_list):
    #     diff = sys.maxsize
    #     closest = assignment
    #     destination_line = assignment['lineno']
    #     for item in assignment_list:
    #         if destination_line - item['lineno'] < diff:
    #             diff = destination_line - item['lineno']
    #             if diff <= 0:
    #                 break
    #             closest = item
    #     return closest
    #
    def find_closest_variable(self, assignment, variable, position, assignment_list):
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

    def has_data_file_assignment(self, assignment):
        for source in assignment["data_source"]:
            if isinstance(source, dict):
                try:
                    return self.parse_data_file(source["data_file"])
                except KeyError as e:
                    self.logger.error(e)
                    return False

    def has_data_file_source(self, data_source):
        if isinstance(data_source, dict):
            try:
                data_file = self.has_data_file_source(data_source["data_file"])
                if data_file:
                    return self.parse_data_file(data_file["data_file"])
                else:
                    return self.parse_data_file(data_source["data_file"])
            except KeyError as e:
                self.logger.error(e)
                return False

    def parse_data_file(self, data_file):
        if isinstance(data_file, list):
            for item in data_file:
                if isinstance(item, str):
                    return item
                elif isinstance(item, dict):
                    try:
                        if 'data_file' in item.keys():
                            self.parse_data_file(item['data_file'])
                    except KeyError as e:
                        self.logger.error(e)
                        continue
                else:
                    return None

    def get_variable_and_value(self, assignment):
        variable = assignment["variable"]
        value = assignment["data_source"]
        return variable, value

    def get_var_value_in_assignment(self, assignment):
        try:
            if not isinstance(assignment['data_source'], list):
                data_source = assignment['data_source']
                return data_source['data_file']
            elif (not assignment["variable"]) or (len(assignment["data_source"]) > 1):
                data_source = assignment['data_source'][0]
                return data_source['data_file']
            else:
                return assignment["data_source"]
        except (AttributeError, KeyError, TypeError) as e:
            self.logger.error(e)

    def get_value_from_var_name(self, assignment, variable, position, assignment_list):
        try:
            closest_variable_assignment = self.find_closest_variable(assignment=assignment, variable=variable,
                                                                     position=position,
                                                                     assignment_list=assignment_list)
            if closest_variable_assignment and closest_variable_assignment["data_source"]:
                if isinstance(closest_variable_assignment["data_source"], list):
                    for source in closest_variable_assignment["data_source"]:
                        if isinstance(source, dict):
                            data_file = source["data_file"]
                            for item in data_file:
                                if isinstance(item, dict):
                                    if 'data_file' in item.keys():
                                        try:
                                            return item['data_file']
                                        except IndexError as e:
                                            self.logger.error(e)

                else:
                    return closest_variable_assignment["data_source"]
            else:
                return None
        except (RecursionError, AttributeError, KeyError, TypeError) as e:
            self.logger.error(e)

    def replace_variables_in_assignments(self):
        try:
            for assignment in self.assignments:
                if assignment:
                    variable, assignment_var = self.get_variable_and_value(assignment)
                    # print(f"Variable: {variable}, value: {assignment_var}")
                    # data_file = self.get_var_value_in_assignment(assignment)
                    # print(f"Data file: {data_file}")
                    val = self.get_value_from_var_name(assignment=assignment, variable=variable,
                                                       position=assignment['lineno'],
                                                       assignment_list=self.assignments)
                    # print(f"Value: {val}")
                    if val and assignment["data_source"]:
                        for source in assignment["data_source"]:
                            if isinstance(source, dict):
                                if 'data_file' in source.keys():
                                    source['data_file'] = val
                        self.logger.info(f"{assignment}")
        except (AttributeError, KeyError, TypeError) as e:
            self.logger.error(e)

    def get_closest_assignment(self, assignment, assignment_list):
        diff = sys.maxsize
        closest = None
        destination_line = assignment['lineno']
        for item in assignment_list:
            if destination_line - item['lineno'] <= diff:
                diff = destination_line - item['lineno']
                closest = item
                if diff <= 0:
                    break
        return closest

    def has_data_file(self, assignment):
        for source in assignment["data_source"]:
            if isinstance(source, dict):
                try:
                    return source["data_file"]
                except KeyError as e:
                    self.logger.error(e)
                    return False

    def has_data_file_single_source(self, source):
        if isinstance(source, dict):
            try:
                return source["data_file"]
            except KeyError as e:
                self.logger.error(e)
                return False

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

    def getDatasetName(self, dataset_path):
        dataset_path, dataset_name = os.path.split(dataset_path)
        return dataset_name

    # def filter_datasets(self):
    #     processing_steps = []
    #     for assignment in self.inputs:
    #         for i in range(self.inputs.index(assignment) + 1, len(self.inputs)):
    #             if assignment["variable"] in self.inputs[i]["data_source"]["data_file"]:
    #                 processing_steps.append(self.inputs[i])
    #                 # print("%s is a preprocessing step\n" % assignment)
    #             elif assignment["variable"] == self.inputs[i]["variable"]:
    #                 processing_steps.append(self.inputs[i])
    #                 # print("%s alters a previous data input\n" % assignment)
    #             # else:
    #             #     print("%s is a data input\n" % assignment)
    #     self.datasets = [assignment for assignment in self.inputs if assignment not in processing_steps]
    #     print(f"Datasets: {self.datasets}")

    def parseNewInputs(self):
        for input in self.new_inputs:
            if input["new_input"][0] == "":
                input["new_input"] = input["old_input"]
            else:
                continue

    def parsePath(self, data_path):

        pipeline_directory = self.getRepositoryPath()

        if data_path[0] == "/":
            return data_path
        elif data_path[0].isalnum():
            return pipeline_directory[0] + "/" + data_path
        elif data_path[0] == ".":
            if data_path[1] == "/":
                return pipeline_directory[0] + "/" + data_path[2:]
            else:
                parent_dir = Path(pipeline_directory[0]).parent.absolute()
                return str(parent_dir) + "/" + data_path[3:]

    def getRepositoryPath(self):
        pipeline_path = os.path.abspath(self.pipeline)
        pipeline_directory = os.path.split(pipeline_path)

        return pipeline_directory

    def getPipelinePath(self):
        return os.path.dirname(self.pipeline)

    def getRepositoryName(self):
        repository_name = os.path.basename(self.getPipelinePath())
        return repository_name

    def parseRepoName(self, repo_name):
        if len(repo_name) > 30:
            repo_name = repo_name[0:29]
            # print(repo_name)

        bucket_name = re.sub(r'[\W_]+', '-', repo_name) + "-" + str(hashlib.md5(repo_name.encode()).hexdigest())
        # print(len(bucket_name))
        return bucket_name.lower()

    # def addInputsToDatasets(self):
    #     self.new_datasets = self.datasets
    #     for input in self.new_inputs:
    #         if input["new_input"] != "":
    #             self.new_datasets[self.new_inputs.index(input)]["data_source"]["data_file"][0] = input["new_input"]
    #         else:
    #             continue

    # def transformScript(self, script, new_script):
    #     temp = self.datasets_urls
    #
    #     with open(new_script, "w") as new:
    #         with open(script, "r") as old:
    #             row_old = iter(old)
    #             for row in row_old:
    #                 for source in temp:
    #                     dataset_name = self.getDatasetName(source['dataset_name'])
    #                     if source['dataset_name'] in row:
    #                         row = row.replace(source['dataset_name'], source['url'])
    #                         temp.remove(source)
    #                     elif dataset_name in row:
    #                         # for i in range(0, len(source["dataset"])):
    #                         matches = re.search(f".[=]{dataset_name}", row)
    #                         # print(f"Matches: {matches.string}")
    #                         # row = row.replace(re.search(f".{dataset_name}, source["url"])
    #                         temp.remove(source)
    #
    #                 new.write(row)
    #             old.close()
    #         new.close()

    def transformScript(self, script, new_script, datasets_urls):
        temp = datasets_urls

        with open(new_script, "w") as new:
            with open(script, "r") as old:
                row_old = iter(old)
                for row in row_old:
                    # row_parts = row.strip().split("=")
                    for source in temp:
                        dataset_name = source['dataset_name']
                        if isinstance(source['variable'], dict):
                            source['variable'] = f"{source['variable']['from']}.{source['variable']['method']}"
                        if (source['variable'] in row and dataset_name in row):
                            row = row.replace(source['dataset_name'], source['url'])
                            temp.remove(source)
                        elif dataset_name in row:
                            row = row.replace(source['dataset_name'], source["url"])
                            temp.remove(source)
                    new.write(row)
                old.close()
            new.close()


    def getDatasetsFromInputs(self):
        for member in self.inputs:
            try:
                for source in member["data_source"]:
                    for dataset in source["data_file"]:
                        if util.checkFileExtension(dataset):
                            self.datasets.append({'variable': member['variable'], 'dataset': dataset, 'lineno': member['lineno']})

            except (TypeError, KeyError) as e:
                self.logger.error(e)

        return self.datasets

    def getDatasetsFromReadMethods(self):
        for key in self.read_methods.keys():
            for member in self.read_methods[key]:
                try:
                    for dataset in self.datasets:
                        if member['variable'] == dataset['variable'] and dataset not in self.datasets_read_methods[key]:
                            self.datasets_read_methods[key].append(dataset)

                except (TypeError, KeyError) as e:
                    self.logger.error(e)

        return self.datasets_read_methods



    # def uploadDatasets(self, bucket):
    #     for dataset in self.datasets:
    #         self.connector.uploadFile(path=dataset, bucket=bucket)
    #         filename = os.path.split(dataset)[1]
    #         self.assignVisitor.inputs.append(self.connector.getObjectUrl(filename))

    # def createDatasetUrlInBucket(self, dataset, bucket):
    #     dataset_name = self.getDatasetName(self.parsePath(dataset))
    #     self.datasets_urls.append({"dataset_name": dataset,
    #                                "url": S3Connector.getObjectUrl(key=dataset_name, bucket=bucket)})

    def setPipeline(self, pipeline):
        self.pipeline = pipeline

    def getPipeline(self):
        return self.pipeline

    def getPipelineName(self):
        pipeline_path, pipeline_name = os.path.split(self.pipeline)
        return pipeline_name

    def setVariables(self):
        self.variables = [{'variable': assignment["variable"], 'lineno': assignment["lineno"]} for assignment in
                          self.assignments]

    def getVariables(self):
        return self.variables

    def setLoggerConfig(self, logger, project, level):
        self.logger = createLogger(filename=logger, project_name=project, level=level)

    def setLogger(self, logger):
        self.logger = logger

    def clearAssignments(self):
        self.assignments = []

    def clearDatasets(self):
        self.datasets = []

    def clearInputs(self):
        self.inputs = []

    def clearDatasetUrls(self):
        self.datasets_urls = []

    def clearDatasetReadMethods(self):
        self.datasets_read_methods = {'raw_string': [], 'variable': [], 'external': []}

    def clearReadMethods(self):
        self.read_methods = {'raw_string': [], 'variable': [], 'external': []}
