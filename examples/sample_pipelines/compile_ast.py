import ast
from ast import *
import pandas as pd

python_string = """
# user_root = "/home/ilint/"
data_file = "/home/ilint/occurrences-2018.csv"

df1 = f"{user_root}occurrences-2019.csv"

print(df1)
"""

try:
    compiled_python = compile(python_string, "../../examples/sample_pipelines/var_retrieval/data_read_test.py", mode='exec')
    # exec(compiled_python)

except NameError as e:
    print(e)

ast_string = """
Module(
   body=[
      Import(
         names=[
            alias(name='pandas', asname='pd')]),
      Import(
         names=[
            alias(name='sys')]),
      ImportFrom(
         module='sklearn.preprocessing',
         names=[
            alias(name='OneHotEncoder'),
            alias(name='label_binarize'),
            alias(name='StandardScaler')],
         level=0),
      ImportFrom(
         module='sklearn.compose',
         names=[
            alias(name='ColumnTransformer')],
         level=0),
      ImportFrom(
         module='sklearn.linear_model',
         names=[
            alias(name='SGDClassifier')],
         level=0),
      ImportFrom(
         module='sklearn.feature_extraction.text',
         names=[
            alias(name='HashingVectorizer')],
         level=0),
      ImportFrom(
         module='sklearn.pipeline',
         names=[
            alias(name='Pipeline')],
         level=0),
      Assign(
         targets=[
            Name(id='path', ctx=Store())],
         value=Constant(value='datasets/amazon-reviews/')),
      Assign(
         targets=[
            Name(id='reviews', ctx=Store())],
         value=Call(
            func=Attribute(
               value=Name(id='pd', ctx=Load()),
               attr='read_csv',
               ctx=Load()),
            args=[
               JoinedStr(
                  values=[
                     FormattedValue(
                        value=Name(id='path', ctx=Load()),
                        conversion=-1),
                     Constant(value='reviews.csv.gz')])],
            keywords=[
               keyword(
                  arg='compression',
                  value=Constant(value='gzip')),
               keyword(
                  arg='index_col',
                  value=Constant(value=0))])),
      Assign(
         targets=[
            Name(id='products', ctx=Store())],
         value=Call(
            func=Attribute(
               value=Name(id='pd', ctx=Load()),
               attr='read_csv',
               ctx=Load()),
            args=[
               JoinedStr(
                  values=[
                     FormattedValue(
                        value=Name(id='path', ctx=Load()),
                        conversion=-1),
                     Constant(value='products.csv')])],
            keywords=[
               keyword(
                  arg='index_col',
                  value=Constant(value=0))])),
      Assign(
         targets=[
            Name(id='categories', ctx=Store())],
         value=Call(
            func=Attribute(
               value=Name(id='pd', ctx=Load()),
               attr='read_csv',
               ctx=Load()),
            args=[
               JoinedStr(
                  values=[
                     FormattedValue(
                        value=Name(id='path', ctx=Load()),
                        conversion=-1),
                     Constant(value='categories.csv')])],
            keywords=[
               keyword(
                  arg='index_col',
                  value=Constant(value=0))])),
      Assign(
         targets=[
            Name(id='ratings', ctx=Store())],
         value=Call(
            func=Attribute(
               value=Name(id='pd', ctx=Load()),
               attr='read_csv',
               ctx=Load()),
            args=[
               JoinedStr(
                  values=[
                     FormattedValue(
                        value=Name(id='path', ctx=Load()),
                        conversion=-1),
                     Constant(value='ratings.csv')])],
            keywords=[
               keyword(
                  arg='index_col',
                  value=Constant(value=0))]))],
   type_ignores=[])
"""

parsed_tree = ast.parse(ast_string)

print(parsed_tree.body)