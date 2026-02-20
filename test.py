print("Hello PaisaPal 🚀")
import pandas as pd

# Read CSV file
df = pd.read_csv("transactions.csv")

print("Here is your data:")
print(df)

# Calculate totals
total_income = df[df["Amount"] > 0]["Amount"].sum()
total_expense = df[df["Amount"] < 0]["Amount"].sum()

print("\nTotal Income:", total_income)
print("Total Expense:", total_expense)
print("Net Cashflow:", total_income + total_expense)
