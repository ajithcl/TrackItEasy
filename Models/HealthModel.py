import traceback

import pymongo
from pymongo import MongoClient
import datetime
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

# Get the current date
current_date = datetime.datetime.strftime(datetime.date.today(), "%Y-%m-%d")
current_date = datetime.datetime.strptime(current_date, "%Y-%m-%d")


class Health:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.PersonalWebDb
        self.HealthCollection = self.db.Health

    def get_exercise_status(self, userid, record_date=current_date):
        output = "error"
        try:
            result_set = self.HealthCollection.find_one({"UserId": userid,
                                                         "RecordDate": record_date})
            if result_set:
                output = result_set["ExerciseStatus"]
            else:
                output = "?"
        except Exception as ex:
            # traceback.print_exc()
            output = "error"
        return output

    def update_exercise_status(self, userid, exercise_status, record_date=current_date):
        result = self.HealthCollection.update({"UserId": userid,
                                               "RecordDate": record_date},
                                              {"$set": {"ExerciseStatus": exercise_status}},
                                              upsert=True)
        return result

    def get_current_year_graphics(self, userid):
        current_year = datetime.date.today().year
        start_date = str(current_year) + "-01-01"
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = str(current_year) + "-12-31"
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        try:
            result_set = self.HealthCollection.aggregate([{"$match": {"UserId": userid,
                                                                      "RecordDate": {"$gte": start_date,
                                                                                     "$lte": end_date},
                                                                      "ExerciseStatus": True}},
                                                          {"$group": {"_id": {"month": {"$month": "$RecordDate"}},
                                                                      "MonthlyCount": {"$sum": 1}}}])
            months = []
            count = []
            graph_input = {}
            for item in result_set:
                months.append(item["_id"]["month"])
                count.append(item["MonthlyCount"])
            for mon, cnt in zip(months, count):
                graph_input[mon] = cnt
            dict_items = sorted(graph_input.items())
            x_mon = []
            y_cnt = []
            month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            for item in dict_items:
                x_mon.append(month_names[item[0]])
                y_cnt.append(item[1])

            plt.bar(x_mon, y_cnt)
            plt.xlabel('Months')
            plt.ylabel('Days count')
            plt.title('Monthly Exercise Days count')
            plt.savefig('static/temp/exercise.png')
            plt.close()
            return "success"
        except Exception as ex:
            #            print(ex)
            return "error"
