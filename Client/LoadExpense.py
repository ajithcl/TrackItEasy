# This program will read the excel file and load the data into the database via api call.
# The excel file should have the following columns: Category, Amount
import json

import pandas as pd
import requests
from datetime import date


file_name = input("Enter file name: ")
df = pd.read_excel(file_name)

required_columns = ['Category', 'Amount']
if not all(column in df.columns for column in required_columns):
    print(f"Error: The file must contain the following columns: {', '.join(required_columns)}")
    exit(1)

print (df)

currentdate = date.today().strftime("%Y-%m-%d")


for index, row in df.iterrows():
    data = {
        "UserId": "John",
        "Category": row['Category'],
        "Amount": row['Amount'],
        "ExpenseDate": currentdate,
        "Description": row['Description'] if 'Description' in row else ""
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post("http://127.0.0.1:5000/api/expense/create", json=data, headers=headers)
    if response.status_code == 201:
        print(f"Expense created successfully for row {index}")
    else:
        print(f"Failed to create expense for row {index}: {response.text}")

    df.loc[index, 'Status'] = response.status_code
    df.loc[index, 'Response'] = response.text

df.to_excel(file_name, index=False)