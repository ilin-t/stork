import ast
from src.log_modules.util import getAst
from src.ast.assign_visitor import AssignVisitor


def direct_visit(parent_object, node, towards):
    func_name = "visit_" + type(towards).__name__
    func = getattr(parent_object, func_name)
    print(f"Method {func_name} will be called from node "
          f"type {type(node)} from object {type(parent_object)} towards object {type(towards)}.\n")
    output = func(towards)
    return output

def filter_pipeline(input_pipeline):
    ast_visitor = ast.NodeVisitor()
    tree = getAst(pipeline=input_pipeline)

    print(tree.body)

    for node in tree.body:
        if isinstance(node, ast.If):
            print("If condition")
            print(node.test)
            test = node.test
            print(test.comparators[0].value)

        elif isinstance(node, ast.FunctionDef):
            print("Function definition")

        elif isinstance(node, ast.ClassDef):
            print("Class definition")




if __name__ == '__main__':
    filter_pipeline(input_pipeline="../examples/sample_pipelines/executable-pipelines/with_main.py")
