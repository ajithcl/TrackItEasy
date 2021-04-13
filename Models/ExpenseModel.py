import pymongo
import datetime
from pymongo import MongoClient
from Models import Common
from datetime import date
import matplotlib
import seaborn as sns
import pandas as pd
import numpy as np

matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import style

# Visualization settings
sns.set_style(style='white')
sns.set(rc={
    'figure.figsize': (10, 6),
    'axes.facecolor': 'white',
    'axes.grid': True,
    'grid.color': '.9',
    'axes.linewidth': 1.0,
    'grid.linestyle': u'-'},
    font_scale=1.5)
custom_colors = ["#3498db", "#95a5a6", "#34495e", "#2ecc71", "#e74c3c"]
sns.set_palette(custom_colors)


class Expense:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.PersonalWebDb
        self.expensedata = self.db.Expense

    def createExpense(self, data):
        result = self.expensedata.insert_one(data)
        return result

    def getCurrentMonthAmount(self, userid=None):
        monthDates = Common.getCurrentMonthStartEndDates()
        strStartDate = str(monthDates["MonthStartDate"])
        strEndDate = str(monthDates["MonthEndDate"])
        results = self.expensedata.find({"UserId": userid,
                                         "ExpenseDate":
                                             {"$gte": datetime.datetime.strptime(strStartDate, "%Y-%m-%d"),
                                              "$lte": datetime.datetime.strptime(strEndDate, "%Y-%m-%d")}})
        totalAmount = 0.0
        if results:
            for row in results:
                totalAmount += int(row["Amount"])

        return totalAmount

    def get_nth_month_amount(self, userid, year_n, month_n):
        month_dates = Common.get_months_start_end_dates(month_n=month_n, year_n=year_n)
        results = self.expensedata.find({"UserId": userid,
                                         "ExpenseDate":
                                             {
                                                 "$gte": month_dates["StartDate"],
                                                 "$lte": month_dates["EndDate"]
                                             }})
        total_amount = 0
        if results:
            for row in results:
                total_amount += int(row["Amount"])

        return total_amount

    def getCurrentMonthExpenseDetails(self, userid=None):
        monthDates = Common.getCurrentMonthStartEndDates()
        strStartDate = str(monthDates["MonthStartDate"])
        strEndDate = str(monthDates["MonthEndDate"])
        results = self.expensedata.find({"UserId": userid,
                                         "ExpenseDate":
                                             {
                                                 "$gte": datetime.datetime.strptime(strStartDate, "%Y-%m-%d"),
                                                 "$lte": datetime.datetime.strptime(strEndDate, "%Y-%m-%d")
                                             }

                                         }).sort('ExpenseDate', pymongo.DESCENDING)
        if results:
            return results
        else:
            return "error"

    def getMonthlyExpenseCategorySplit(self, userid=None):
        monthDates = Common.getCurrentMonthStartEndDates()
        strStartDate = str(monthDates["MonthStartDate"])
        strEndDate = str(monthDates["MonthEndDate"])
        category_list = self.expensedata.distinct("Category")
        output_dict = {}
        for category in category_list:
            result_set = self.expensedata.find({"UserId": userid,
                                                "ExpenseDate":
                                                    {
                                                        "$gte": datetime.datetime.strptime(strStartDate, "%Y-%m-%d"),
                                                        "$lte": datetime.datetime.strptime(strEndDate, "%Y-%m-%d")
                                                    },
                                                "Category": category
                                                })
            total_amount = 0
            for record in result_set:
                total_amount += record["Amount"]
            if total_amount > 0:
                output_dict[category] = total_amount

        return output_dict

    def deleteExpense(self, data):
        pass

    def updateExpense(self, data):
        pass

    def getTodaysExpense(self, userid):
        currentdate = datetime.datetime.now()
        currentdate = datetime.datetime.strftime(currentdate, "%Y-%m-%d")
        currentdate = datetime.datetime.strptime(currentdate, "%Y-%m-%d")
        result = self.expensedata.find({"UserId": userid,
                                        "ExpenseDate": currentdate})
        total_amount = 0
        for record in result:
            total_amount += record["Amount"]
        return total_amount

    def getAverageMonthlyExpense(self, userid):
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        start_date = str(current_year) + "-01-01"
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = str(current_year) + "-" + str(current_month) + "-1"
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        result = self.expensedata.aggregate([{"$match": {"UserId": userid,
                                                         "ExpenseDate": {"$gte": start_date,
                                                                         "$lt": end_date}}},
                                             {"$group": {
                                                 "_id": {"month": {"$month": "$ExpenseDate"}},
                                                 "MonthlyTotal": {"$sum": "$Amount"}
                                             }}
                                             ])
        amount_list = []
        for record in result:
            amount_list.append(record["MonthlyTotal"])

        average_amount = 0
        if len(amount_list) > 0:
            average_amount = sum(amount_list) / len(amount_list)
        return average_amount

    def current_year_total_graph(self, userid):
        current_year = datetime.date.today().year
        start_date = str(current_year) + "-01-01"
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        try:
            result = self.expensedata.aggregate([{"$match": {"UserId": userid, "ExpenseDate": {"$gte": start_date}}},
                                                 {"$group": {"_id": {"month": {"$month": "$ExpenseDate"}},
                                                             "MonthlyTotal": {"$sum": "$Amount"}}}])
            months = []
            amount = []
            graph_input = {}
            for item in result:
                months.append(item["_id"]["month"])
                amount.append(item["MonthlyTotal"])

            for mon, amt in zip(months, amount):
                graph_input[mon] = amt

            dict_items = sorted(graph_input.items())
            x_mon = []
            y_amt = []
            month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            for item in dict_items:
                x_mon.append(month_names[item[0]])
                y_amt.append(item[1])
            # style.use('seaborn-whitegrid')
            plt.plot(x_mon, y_amt)
            plt.ylabel("Amount (Rs)")
            plt.title("Monthly expense " + str(current_year))
            for mon, amt in zip(x_mon, y_amt):
                plt.annotate(amt, xy=(mon, amt))

            plt.savefig("static/temp/expense.png")
            plt.close()
            return "success"
        except:
            return "error"

    def get_all_expense_trend(self, userid):
        # Group the records based on year and then month
        # Calculate monthly sum.
        results = self.expensedata.aggregate([{"$match": {"UserId": userid}},
                                              {"$group": {
                                                  "_id": {"year": {"$year": "$ExpenseDate"},
                                                          "month": {"$month": "$ExpenseDate"}},
                                                  "MonthlyTotal": {"$sum": "$Amount"}}}
                                              ])
        df = pd.DataFrame(columns=['year', 'month', 'MonthlyTotal'], dtype=int)
        if results:
            for row in results:
                df = pd.concat([df,
                                pd.DataFrame(data={'year': row['_id']['year'],
                                                   'month': row['_id']['month'],
                                                   'MonthlyTotal': row['MonthlyTotal']},
                                             index=[0])])
            sns.lineplot(data=df, x='month', y='MonthlyTotal', hue='year', palette='tab10');
            plt.title("Expense trends - Monthwise");
            plt.legend(loc='center', bbox_to_anchor=(1.05, 0.5), title='Year');
            plt.xticks(np.arange(1, 13),
                       labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']);
            plt.xticks(rotation=90);
            img_file="static/temp/expense_trend.png"
            plt.savefig(img_file)
            plt.close()
            return img_file
        else:
            return "error"
