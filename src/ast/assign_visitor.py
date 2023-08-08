import ast
import hashlib
import os
import re
import sys
from pathlib import Path

from src.log_modules import util
from src.db_conn.s3_connector import S3Connector


# from src.ast.variable_crawler import retrieve_variable_from_assignment


class AssignVisitor(ast.NodeVisitor):
    def __init__(self):
        self.pipeline = ""
        self.assignment = {"variable": str, "data_source": []}
        self.inputs = []
        self.assignments = []
        self.datasets = []
        self.imports = []
        self.new_inputs = []
        self.new_datasets = []
        self.datasets_urls = []
        self.logger = None
        self.variables = []

    def direct_visit(self, parent_object, node, towards):
        try:
            func_name = "visit_" + type(towards).__name__
            func = getattr(parent_object, func_name)
            # print("Method %s will be called from node "
            #       "type %s from object %s.\n" % (func_name, type(node), type(parent_object)))
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
            if self.logger:
                self.logger.error(e)
            else:
                print(e)

    # WIP, not tested
    def visit_FunctionDef(self, node):
        args = self.direct_visit(self, node, node.args)
        function_body = []
        decorator_list = []
        for item in node.body:
            function_body.append(self.direct_visit(self, node, item))

        for element in decorator_list:
            function_body.append(element)

        return {"function": node.name, "data_source": function_body}
        # return None

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

    #
    def visit_Call(self, node):
        func_call = self.direct_visit(parent_object=self, node=node, towards=node.func)
        args_names = []
        params = []
        for arg in node.args:
            args_names.append(self.direct_visit(self, node, arg))
        for keyword in node.keywords:
            params.append(self.direct_visit(self, node, keyword))

        # print(type(node.func).__name__)
        if type(node.func).__name__ == "Attribute":
            self.assignment["data_source"].append({"func_call": func_call, "data_file": args_names, "params": params})
        else:
            return {"func_call": func_call, "data_file": args_names, "params": params}

    def visit_Attribute(self, node):
        package = self.direct_visit(parent_object=self, node=node, towards=node.value)
        method = node.attr
        if type(node).__name__ == "Call":
            self.assignment["data_source"].append(package)
        else:
            return {"from": package, "method": method}

    def visit_BinOp(self, node):
        left = self.direct_visit(parent_object=self, node=node, towards=node.left)
        right = self.direct_visit(parent_object=self, node=node, towards=node.right)

        if type(node.op).__name__ == "Add":
            if type(left) == str and type(right) == str:
                return str(left + "+" + right)
        return [left, right]

    def visit_Subscript(self, node):
        load_var = self.direct_visit(parent_object=self, node=node, towards=node.value)
        filter_criteria = self.direct_visit(parent_object=self, node=node, towards=node.slice)

        return [load_var, filter_criteria]

    # TODO Check other AST nodes and what properties they carry.
    # TODO Adapt for subscripts,
    #  they are most commonly used for data filtering

    def visit_Name(self, node):
        return node.id

    def visit_Constant(self, node):
        return node.value

    def visit_keyword(self, node):
        return {node.arg: self.direct_visit(parent_object=self, node=node, towards=node.value)}

    # The methods below are necessary for parsing the filter operators and preprocessing operations

    def visit_Compare(self, node):
        left = self.direct_visit(parent_object=self, node=node, towards=node.left)
        operation = node.ops
        right = self.direct_visit(parent_object=self, node=node, towards=node.comparators[0])

        return {"left_op": left, "operator": operation, "right": right}

    def visit_Lambda(self, node):
        args = self.direct_visit(parent_object=self, node=node, towards=node.args)
        func = self.direct_visit(parent_object=self, node=node, towards=node.body)

        # print("Args: %s, func: %s" % (args, func))

    def visit_arguments(self, node):
        args = []
        for arg in node.args:
            args.append(self.direct_visit(self, node, arg))
        # print(args)
        return args

    def visit_arg(self, node):
        return node.arg

    def visit_List(self, node):
        list_el = []
        for element in node.elts:
            list_el.append(self.direct_visit(self, node, element))

        return list_el

    #
    def visit_Tuple(self, node):
        tuple_el = []
        for element in node.elts:
            tuple_el.append(self.direct_visit(self, node, element))

        return tuple(tuple_el)

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
        for element in node.values:
            variable = self.direct_visit(self, node, element)
            retrieve_variable_from_assignment

    def filter_Assignments(self):
        removed = []
        for assignment in self.assignments:
            # print("Type of the above assignment: %s" % type(assignment["data_source"]))
            assignment["data_source"] = [i for i in assignment["data_source"] if i is not None]
            # print(assignment["data_source"])
            for source in assignment["data_source"]:
                if self.keepDataSource(data_source=source) and assignment not in self.inputs:
                    self.inputs.append(assignment)
                data_file_from_var = self.retrieve_variable_from_assignment(assignment=assignment,
                                                                            assignment_list=self.assignments)
                new_assignment = self.var_assignment_to_input(var_assignment=data_file_from_var, assignment=assignment)
                if new_assignment:
                    self.inputs.append(new_assignment)
                # print(f"New assignment: {new_assignment}")

                # TODO: Clean commented code
                # to_keep = False
                # print(source)
                # if type(source) is not dict:
                #     removed.append(source)
                # elif "data_file" not in source.keys():
                #     removed.append(source)
                # elif len(source["data_file"]) == 0:
                #     removed.append(source)
                # elif type(source["data_file"][0]) is not str:
                #     removed.append(source)
                # elif not util.checkDataFile(source["data_file"]):
                #     removed.append(source)
                # else:
                #     # self.inputs.append(assignment)
                #     to_keep = True
                #     # print("didn't remove\n")

                # if to_keep and assignment not in self.inputs:
                #     self.inputs.append(assignment)

        # self.inputs = [assignment for assignment in self.assignments if assignment not in removed]

        # print(f"Inputs length: {len(self.inputs)}")
        return self.inputs

    def keepDataSource(self, data_source):
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

    def var_assignment_to_input(self, var_assignment, assignment):
        try:
            data_path = var_assignment['data_source']
            for source in assignment['data_source']:
                print(
                    f"var_assignment['variable']: {var_assignment['variable']}, source['data_file']: {source['data_file']})")
                if self.has_data_file_single_source(source=source) and (
                        var_assignment['variable'] == source['data_file'][0]):
                    print("Yes")
                    source['data_file'] = data_path
                    print(f"New assignment: {assignment}")
                    break
        except TypeError as e:
            print(e)
        return assignment

    # TODO
    # def is_concatenated(self, string):
    #     if os.path.isfile(string):
    #         return False
    #     else:
    #
    #         for variable in self.variables:
    #             # if variable in string:
    #
    #
    #
    # def get_string_value(self, data_file):
    #     return data_file['data_source']
    #
    #
    # def find_variable(self, string):



    def retrieve_variable_from_assignment(self, assignment, assignment_list):
        print(f"method call, length of assignments: {len(assignment_list)}")
        data_file = self.has_data_file(assignment=assignment)
        last_change = None
        try:
            if data_file:
                for item in assignment_list:
                    # print(f"Item: {item}")
                    if data_file[0] == item["variable"]:
                        # print(f"Assignment: {item}")
                        # print(f"Path to dataset from variable {item['variable']}: {item['data_source'][0]}")
                        last_change = self.get_closest_assignment(assignment=assignment,
                                                                  assignment_list=assignment_list)
                        print(f"Closest variable: {last_change}, to the assignment: {assignment}")

                return last_change if last_change else None
        except (NameError, AttributeError) as e:
            print(e)

    def retrieve_variable_from_assignment_list(self, assignment_list):
        print(f"method call, length of assignments: {len(assignment_list)}")
        for assignment in assignment_list:
            data_file = self.has_data_file(assignment=assignment)
            try:
                if data_file:
                    for item in assignment_list:
                        # print(f"Item: {item}")
                        if data_file[0] == item["variable"]:
                            # print(f"Assignment: {item}")
                            # print(f"Path to dataset from variable {item['variable']}: {item['data_source'][0]}")
                            last_change = self.get_closest_assignment(assignment=assignment,
                                                                      assignment_list=assignment_list)
                            print(f"Closest variable: {last_change}, to the assignment: {assignment}")
            except (NameError, AttributeError) as e:
                print(e)

    def get_closest_assignment(self, assignment, assignment_list):
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

    def has_data_file(self, assignment):
        for source in assignment["data_source"]:
            if isinstance(source, dict):
                try:
                    return source["data_file"]
                except KeyError as e:
                    print(e)
                    return False

    def has_data_file_single_source(self, source):
        if isinstance(source, dict):
            try:
                return source["data_file"]
            except KeyError as e:
                print(e)
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
        # print(f"Pipeline directory: {pipeline_directory}")

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
        # print(f"Len repository name: {len(repo_name)}")
        if len(repo_name) > 30:
            repo_name = repo_name[0:29]
            print(len(repo_name))

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

    def transformScript(self, script, new_script):
        temp = self.datasets_urls

        with open(new_script, "w") as new:
            with open(script, "r") as old:
                row_old = iter(old)
                for row in row_old:
                    for source in temp:
                        if source["dataset_name"] in row:
                            # for i in range(0, len(source["dataset"])):
                            row = row.replace(source["dataset_name"], source["url"])
                            temp.remove(source)

                    new.write(row)
                old.close()
            new.close()

    def getDatasetsFromInputs(self):
        for member in self.inputs:
            # print(f"variable: {member['variable']}")
            for source in member["data_source"]:
                # print(f"source: {source}")
                try:
                    # print(f"source['data_file']: {source['data_file']}")
                    for dataset in source["data_file"]:
                        if util.checkFileExtension(dataset):
                            # print(f"dataset:{dataset}")
                            # if log_modules.checkDataFile(dataset):
                            abs_path_dataset = self.parsePath(dataset)
                            # print(f"Source data file:{abs_path_dataset}")
                            self.datasets.append(abs_path_dataset)

                            # dataset_name = self.getDatasetName(abs_path_dataset)

                            # print(f"Url: {self.connector.getObjectUrl(key=dataset_name, bucket=bucket_name)}")

                            # self.assignVisitor.datasets_urls.append({"dataset_name": dataset,
                            #                                          "url": self.connector.getObjectUrl(
                            #                                              key=dataset_name, bucket=bucket_name)})

                            # self.connector.uploadFile(path=abs_path_dataset, bucket=bucket_name)

                except TypeError as e:
                    self.logger.error(e)
                    # print(e)

                except KeyError as e:
                    self.logger.error(e)
                    # print(e)
        # print(f"Datasets: {self.datasets}")
        return self.datasets

    # def uploadDatasets(self, bucket):
    #     for dataset in self.datasets:
    #         self.connector.uploadFile(path=dataset, bucket=bucket)
    #         filename = os.path.split(dataset)[1]
    #         self.assignVisitor.inputs.append(self.connector.getObjectUrl(filename))

    def createDatasetUrlInBucket(self, dataset, bucket):
        dataset_name = self.getDatasetName(self.parsePath(dataset))
        self.datasets_urls.append({"dataset_name": dataset,
                                   "url": S3Connector.getObjectUrl(key=dataset_name, bucket=bucket)})

    def setPipeline(self, pipeline):
        self.pipeline = pipeline

    def getPipeline(self):
        return self.pipeline

    def setVariables(self):
        self.variables = [{'variable': assignment["variable"], 'lineno': assignment["lineno"]} for assignment in
                          self.assignments]

    def getVariables(self):
        return self.variables

    def setLogger(self, logger):
        self.logger = logger
