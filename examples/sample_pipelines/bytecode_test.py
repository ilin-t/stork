# import dis
# import sys
# import measurement_scripts.pd_to_sql
# from measurement_scripts import pd_to_sql, test
# from src.log_modules import random

# def showMeByte(name):
#     return "hello " + name + " !!!"
#
#
# dis.dis(showMeByte)
# bytecode = dis.code_info(showMeByte)
# print(bytecode)
#
# bytecode = dis.Bytecode(showMeByte)
# print(bytecode)
#
# for i in bytecode:
#     print(i)

a = 5

a = a +3

# print(a)



# print(getattr(sys.modules[__name__], "random_path"))
# print(getattr(pd_to_sql, "lineitem_cols"))
# print(getattr(random, "db_config"))
# print(getattr(test, "lineitem_cols"))

# print(showMeByte("amit kumra"))
# print(showMeByte.__code__.co_code)
# print(showMeByte.__code__.co_consts)
# print(showMeByte.__code__.co_stacksize)
# print(showMeByte.__code__.co_varnames)
# print(showMeByte.__code__.co_flags)
# print(showMeByte.__code__.co_name)
# print(showMeByte.__code__.co_names)