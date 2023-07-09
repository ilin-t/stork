from matplotlib import pyplot as plt
import pandas as pd

df = pd.read_csv(filepath_or_buffer="occurences.csv", header=0)
# print(df)

print(df["library"])
print(df["count"])

plt.bar(x=df["library"], height=df["count"])
plt.ylim(0, max(df["count"])+2)
plt.yticks(range(0, max(df["count"])+2, 2))
plt.show()
