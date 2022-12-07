import ast

from src.util import util
from src.util.util import direct_visit


class AssignVisitor(ast.NodeVisitor):
    def __init__(self):
        self.assignment = None
        self.inputs = []
        self.assignments = []
        self.datasets = []
        self.imports = []
        self.new_inputs = []
        self.new_datasets = []
        self.datasets_urls = []

    def visit_FunctionDef(self, node):
        args = direct_visit(self, node, node.args)
        function_body = []
        decorator_list = []
        for item in node.body:
            function_body.append(direct_visit(self, node, item))

        for element in decorator_list:
            function_body.append(element)

        return {"function": node.name, "data_source": function_body}




    def visit_Return(self, node):
        value = direct_visit(self, node, node.value)
        return value

    def visit_list(self, node):
        return node

    def visit_Assign(self, node):
        self.assignment = {"variable": str, "data_source": []}
        for target in node.targets:
            self.assignment["variable"] = direct_visit(self, node, target)
            self.assignment["data_source"].append(direct_visit(parent_object=self, node=node, towards=node.value))

        print(f"Length of data_source: {len(self.assignment['data_source'])}")
        self.assignments.append(self.assignment)

    #
    def visit_Call(self, node):
        func_call = direct_visit(parent_object=self, node=node, towards=node.func)
        args_names = []
        params = []
        for arg in node.args:
            args_names.append(direct_visit(self, node, arg))
        for keyword in node.keywords:
            params.append(direct_visit(self, node, keyword))

        print(type(node.func).__name__)
        if type(node.func).__name__ == "Attribute":
            self.assignment["data_source"].append({"func_call": func_call, "data_file": args_names, "params": params})
        else:
            return {"func_call": func_call, "data_file": args_names, "params": params}

    def visit_Attribute(self, node):
        package = direct_visit(parent_object=self, node=node, towards=node.value)
        method = node.attr
        if type(node).__name__ == "Call":
            self.assignment["data_source"].append(package)
        else:
            return {"from": package, "method": method}

    def visit_BinOp(self, node):
        left = direct_visit(parent_object=self, node=node, towards=node.left)
        # print(node.op)
        right = direct_visit(parent_object=self, node=node, towards=node.right)
        # print(node.left._fields[0] + "  ", type(node.op).__name__ +
        #       " " + node.right._fields[1])

        if type(node.op).__name__ == "Add":
            if type(left) == str and type(right) == str:
                return str(left + "+" + right)
        return [left, right]

    def visit_Subscript(self, node):
        load_var = direct_visit(parent_object=self, node=node, towards=node.value)
        filter_criteria = direct_visit(parent_object=self, node=node, towards=node.slice)

        return [load_var, filter_criteria]

    # TODO Check other AST nodes and what properties they carry.
    # TODO Adapt for subscripts,
    #  they are most commonly used for data filtering

    def visit_Name(self, node):
        return node.id

    def visit_Constant(self, node):
        return node.value

    def visit_keyword(self, node):
        return {node.arg: direct_visit(parent_object=self, node=node, towards=node.value)}

    # The methods below are necessary for parsing the filter operators and preprocessing operations

    def visit_Compare(self, node):
        left = direct_visit(parent_object=self, node=node, towards=node.left)
        operation = node.ops
        right = direct_visit(parent_object=self, node=node, towards=node.comparators[0])

        # print("Left op: %s, \n operator: %s, \n right: %s" % (left, operation, right))

        return {"left_op": left, "operator": operation, "right": right}

    def visit_Lambda(self, node):
        args = direct_visit(parent_object=self, node=node, towards=node.args)
        func = direct_visit(parent_object=self, node=node, towards=node.body)

        # print("Args: %s, func: %s" % (args, func))

    def visit_arguments(self, node):
        args = []
        for arg in node.args:
            args.append(direct_visit(self, node, arg))
        # print(args)
        return args

    def visit_arg(self, node):
        # print("arg: %s" % node.arg)
        return node.arg

    def visit_List(self, node):
        list_el = []
        for element in node.elts:
            list_el.append(direct_visit(self, node, element))

        # print(list_el)
        return list_el

    #
    def visit_Tuple(self, node):
        tuple_el = []
        for element in node.elts:
            tuple_el.append(direct_visit(self, node, element))

        # print(tuple(tuple_el))
        return tuple(tuple_el)

    def visit_Dict(self, node):
        content = {}
        for element in node.keys:
            key = direct_visit(self, node, element)
            key_index = node.keys.index(element)
            value = direct_visit(self, node, node.values[key_index])
            content[key] = value
            print(f"Key: {key}, Index: {key_index}, Value: {value}")
        # print(f"Content: {content}")
        # return content

    # TODO Define visit Dict method

    def visit_ListComp(self, node):
        return 0

    def filter_Assignments(self):
        removed = []
        for assignment in self.assignments:
            print("Type of the above assignment: %s" % type(assignment["data_source"]))
            to_keep = False
            assignment["data_source"] = [i for i in assignment["data_source"] if i is not None]
            print(assignment["data_source"])
            for source in assignment["data_source"]:
                to_keep = False
                # print(source)
                if type(source) is not dict:
                    removed.append(source)
                    # print("removed\n")
                elif "data_file" not in source.keys():
                    removed.append(source)
                    # print("removed\n")
                elif len(source["data_file"]) == 0:
                    removed.append(source)
                    # print("removed\n")
                elif type(source["data_file"][0]) is not str:
                    removed.append(source)
                    # print("removed\n")
                elif not util.checkDataFile(source["data_file"]):
                    removed.append(source)
                    # print("Type of the above data_file: %s" % type(source["data_file"][0]))
                    # print("removed\n")
                else:
                    # self.inputs.append(assignment)
                    # print(f"Assignment: {assignment}")
                    to_keep = True
                    print("didn't remove\n")
                if to_keep and assignment not in self.inputs:
                    self.inputs.append(assignment)
            # if type(assignment["data_source"]) is not (dict or list):
            #     removed.append(assignment)
            #     print("removed\n")
            # elif "data_file" not in assignment["data_source"].keys():
            #     removed.append(assignment)
            #     print("removed\n")
            # elif len(assignment["data_source"]["data_file"]) == 0:
            #     removed.append(assignment)
            #     print("removed\n")
            # elif type(assignment["data_source"]["data_file"][0]) is not str:
            #     removed.append(assignment)
            #     print("Type of the above data_file: %s" % type(assignment["data_source"]["data_file"][0]))
            #     print(f"data_file = {assignment['data_source']['data_file'][0]}")
            #     print("removed\n")
            # elif not self.checkDataFile(assignment["data_source"]["data_file"]):
            #     removed.append(assignment)
            #     print("Type of the above data_file: %s" % type(assignment["data_source"]["data_file"][0]))
            #     print("removed\n")
            # elif type(assignment["data_source"]["data_file"][0][0]) is not str:
            #     removed.append(assignment)
            #     print("Type of the above data_file: %s" % type(assignment["data_source"]["data_file"][0][0]))
            #     print("removed\n")

        # self.inputs = [assignment for assignment in self.assignments if assignment not in removed]

        print(f"Inputs length: {len(self.inputs)}")
        return self.inputs

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

    # def addInputsToDatasets(self):
    #     self.new_datasets = self.datasets
    #     for input in self.new_inputs:
    #         if input["new_input"] != "":
    #             self.new_datasets[self.new_inputs.index(input)]["data_source"]["data_file"][0] = input["new_input"]
    #         else:
    #             continue

    def transformScript(self, script, new_script):
        temp = self.datasets_urls
        # print("From transformScript\n")
        # print(temp)
        # print("From transformScript\n")
        # print(self.new_inputs)

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
