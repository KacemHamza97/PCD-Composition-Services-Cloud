import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import csv


def boxplot(algorithm):
    plt.clf()
    df1 = pd.read_csv("hv_abstract.csv")
    print(df1)
    df1 = df1.loc[df1['algorithm'] == algorithm]
    print(df1)
    sns_plot = sns.boxplot(x="n_act", y="HV", data=df1)
    plt.title(algorithm)
    sns_plot.figure.savefig(f"boxplots/boxplot(candidates_50_{algorithm}).png")

    plt.clf()
    df = pd.read_csv("hv_concrete.csv")
    df1 = df[['algorithm', 'n_candidates', 'HV']]
    df1 = df1.loc[df['algorithm'] == algorithm]
    print(df1)
    sns_plot = sns.boxplot(x="n_candidates", y="HV", data=df1)
    plt.title(algorithm)
    sns_plot.figure.savefig(f"boxplots/boxplot(activities_20_{algorithm}).png")


boxplot("moabc_spea2")
boxplot("nsga2")
boxplot("nsga2_r")
boxplot("moabc")
boxplot("spea2")

# cleaning csv files
with open('hv_abstract.csv', mode='w') as file:
    file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    file_writer.writerow(["algorithm", "n_act", "HV"])

with open('hv_concrete.csv', mode='w') as file:
    file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    file_writer.writerow(["algorithm", "n_candidates", "HV"])
