
#CUSTOMER SEGMENTATION USING RFM


# BUSINESS PROBLEM: An e-commerce company wants to segment its
# customers and determine marketing strategies according to these segments.

# DATASET STORY: There is Online Retail II, 2010-2011 sheet file as dataset.
# Products sold are mostly souvenirs and most of the customers are corporates.




# Importing necessary libraries and setting display options

import numpy as np
import datetime as dt
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

df_ = pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

# Descriptive statistics of the dataset
def check_df(dataframe):
    print("##################### Head #####################")
    print(dataframe.head(10))
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Info #####################")
    print(dataframe.info())
    print("####################### NA ######################")
    print(dataframe.isnull().sum())
    print("################### Quantiles ###################")
    print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)
check_df(df)


# Deleting nan values

df.dropna(inplace=True)


# Removing Invoices starting with "C" as they represent canceled purchase.

df = df[~df["Invoice"].str.contains("C",na=False)]


# Numerical column descriptive analysis

num_cols = ["Quantity", "Price"]

def num_summary(dataframe, numerical_col, histogram=False, boxplot=False):
    quantiles = [0.05, 0.10, 0.50, 0.95, 0.99]
    print(dataframe[numerical_col].describe(quantiles).T)

    if histogram:
        dataframe[numerical_col].hist(bins=20)
        plt.xlabel(numerical_col)
        plt.ylabel("frequency")
        plt.title(numerical_col)
        plt.show()

    if boxplot:
        sns.boxplot(x=dataframe[numerical_col])
        plt.xlabel(numerical_col)
        plt.show()

for col in num_cols:
    num_summary(df, col, True, True)


# Creating TotalPrice variable as total revenue per quantity bought.

df["TotalPrice"] = df["Quantity"] * df["Price"]


# Calculating RFM metrics

# Last date registered in InvoiceDate variable
df["InvoiceDate"].max()  #2011,12,09 12:50:00 - last registered date

today_date = dt.datetime(2011, 12, 11)  # today_date set as 11th of December as 9th December
#                                         date isn't full date time (meaning 24h)

#RECENCY - Day difference between today_date and customer's last "purchase"
#FREQUENCY - Customer's lifetime purchase frequency
#MONETARY - Customer's monetary return

rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     "Invoice": lambda Invoice: Invoice.nunique(),
                                     "TotalPrice": lambda TotalPrice: TotalPrice.sum()})


# Renaming rfm dataframe's columns as follows:
rfm.columns = ["recency", "frequency", "monetary"]

# Setting monetary variable as higher than 0.
rfm = rfm[(rfm['monetary'] > 0)]


# Creating RFM scores from recency, frequency & monetary variables.

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])

rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))





# Setting RFM scores as segment with segmentation map

seg_map = {r'[1-2][1-2]': 'hibernating',
           r'[1-2][3-4]': 'at_Risk',
           r'[1-2]5': 'cant_loose',
           r'3[1-2]': 'about_to_sleep',
           r'33': 'need_attention',
           r'[3-4][4-5]': 'loyal_customers',
           r'41': 'promising',
           r'51': 'new_customers',
           r'[4-5][2-3]': 'potential_loyalists',
           r'5[4-5]': 'champions'}

rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)

graph1 = rfm.groupby("segment")["monetary"].mean().sort_values(ascending=False)
graph1.plot(kind='barh', color="r")
plt.tight_layout()
plt.show()


pareto = rfm.groupby("segment")["monetary"].sum().sort_values(ascending=False)
pareto = pareto.to_frame()
pareto["monetary_ratio"] = (pareto["monetary"] / pareto["monetary"].sum()) * 100
pareto["number"] = rfm["segment"].value_counts()
pareto["number_ratio"] = (pareto["number"] / pareto["number"].sum()) * 100
pareto




