import dis
import sys
from examples.sample_pipelines import bytecode_test


random_path = "/home/ilint/data"

a = 5
# print(getattr(sys.modules[__name__], 'a'))
a = a + 3

print(getattr(sys.modules[__name__], 'random_path'))
print(f"From {bytecode_test}, a = {getattr(bytecode_test, 'a')}")

# print(sys.modules.keys())
print(len(sys.modules.keys()))
print(sys.modules[__name__])

def f():
    global a
    return a - 5

dis.dis(f)

exec(f.__code__, {'__lltrace__': 'foo', 'a': 10})
