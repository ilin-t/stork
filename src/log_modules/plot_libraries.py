from matplotlib import pyplot as plt
import pandas as pd


def addlabels(x, y):
    for i in range(0, len(x)):
        # print(y.iloc[i])
        plt.text(x=i, y=y.iloc[i], s=y.iloc[i], ha="center")


packages_root = "/mnt/fs00/rabl/ilin.tolovski/stork/packages/"

df = pd.read_csv(filepath_or_buffer=f"{packages_root}occurences.csv", header=0)
# print(df)

df.sort_values(by="count", ascending=False, inplace=True)
subset = df.iloc[:15][:]
print(subset)
plt.bar(x=subset["library"], height=subset["count"])
addlabels(x=subset["library"], y=subset["count"])
plt.ylim(0, max(subset["count"]) + 10)
plt.xticks(rotation=60)
plt.yticks(range(0, max(df["count"]) + 2, 40))
plt.tight_layout()
plt.show()
