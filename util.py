import ast


def direct_visit(parent_object, node, towards):
    try:
        func_name = "visit_" + type(towards).__name__
        func = getattr(parent_object, func_name)
        # print("Method %s will be called from node "
        #       "type %s from object %s.\n" % (func_name, type(node), type(parent_object)))
        output = func(towards)
        return output
    except AttributeError:
        print(
            "visit_" + type(towards).__name__ +
            " accessed from node type " + type(node).__name__ + " is not defined.\n")


def getAst(pipeline):
    with open(pipeline, "r") as source:
        return ast.parse(source.read() + "\n")
