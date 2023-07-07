# +

s1 = 'Apple'
s2 = 'Pie'
s3 = 'Sauce'

s4 = s1 + s2 + s3


# Join

s1 = 'Hello'
s2 = 'World'

print('Concatenated String using join() =', "".join([s1, s2]))

# %

s1 = 'Hello'
s2 = 'World'

s3 = "%s %s" % (s1, s2)
print('String Concatenation using % Operator =', s3)

# Format

s1 = 'Hello'
s2 = 'World'

s3 = "{}-{}".format(s1, s2)
print('String Concatenation using format() =', s3)

s3 = "{in1} {in2}".format(in1=s1, in2=s2)
print('String Concatenation using format() =', s3)


#  F String

s1 = 'Hello'
s2 = 'World'

s3 = f'{s1} {s2}'
print('String Concatenation using f-string =', s3)

