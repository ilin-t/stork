

# Listing 1
s = '''
a = 5
b = 'text'
def f(x):
    print(x)
    return x
f(5)
'''
c=compile(s, "", "exec")


print(compile("a=5 \na+=1 \nprint(a)", "", "exec"))

