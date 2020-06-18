import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import csv


def boxplot_fixed_activities():
    plt.clf()
    df2 = pd.read_csv("hv_concrete.csv")
    n_act = df2.iloc[0]['n_act']
    sns_plot = sns.boxplot(x="n_candidates", y="HV", data=df2, hue="algorithm")
    # plt.title("any title ")
    sns_plot.figure.savefig(f"boxplots/boxplot(activities fixed {n_act}).png")

def boxplot_fixed_candidates():
    plt.clf()
    df1 = pd.read_csv("hv_abstract.csv")
    n_candidates = df1.iloc[0]['n_candidates']
    sns_plot = sns.boxplot(x="n_act", y="HV", data=df1, hue="algorithm")
    plt.title(f"candidates number : {n_candidates} ")
    sns_plot.figure.savefig(f"boxplots/boxplot(candidates fixed {n_candidates}).png")


boxplot_fixed_activities()
# boxplot_fixed_candidates()

#cleaning csv files
with open('hv_abstract.csv', mode='w') as file:
    file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    file_writer.writerow(["algorithm", "n_act", "HV"])

with open('hv_concrete.csv', mode='w') as file:
    file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    file_writer.writerow(["algorithm", "n_candidates", "HV"])
