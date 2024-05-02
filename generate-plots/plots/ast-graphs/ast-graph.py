import ast
from astmonkey import visitors, transformers


code="train_data_1 = pd.read_csv('train_data1.csv')"

node = ast.parse(code)
node = transformers.ParentChildNodeTransformer().visit(node)
visitor = visitors.GraphNodeVisitor()
visitor.visit(node)

visitor.graph.write_svg('graph.svg')