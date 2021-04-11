import pymongo
from pymongo import MongoClient
import datetime
from datetime import date


class Learning:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.PersonalWebDb
        self.learning = self.db.Learnings

    def createLearning(self, data):
        result = self.learning.insert_one(data)
        if result:
            return "success"
        else:
            return "error"

    def save_learning(self, identifier, data):
        pass

    def delete_learning(self):
        pass

    def getLearningsForCurrentMonth(self, userid):
        currentYear = datetime.datetime.now().year
        currentMonth = datetime.datetime.now().month
        nxtdt = datetime.date.today()
        continueloop = True
        # Find the last date of the current month
        while continueloop:
            prevdt = nxtdt
            nxtdt = nxtdt + datetime.timedelta(days=1)
            if nxtdt.month == currentMonth:
                continueloop = True
            else:
                continueloop = False

        startDate = date(currentYear, currentMonth, 1)
        endDate = prevdt
        strStartDate = str(startDate)
        strEndDate = str(endDate)
        results = self.learning.find({"UserId": userid,
                                      "LearnedDate": {"$gte": datetime.datetime.strptime(strStartDate, "%Y-%m-%d"),
                                                      "$lte": datetime.datetime.strptime(strEndDate, "%Y-%m-%d")}})
        return results

    def getLearningsForCurrentYear(self, userid):
        currentyear = datetime.datetime.now().year

        startdate = datetime.datetime.strptime(str(currentyear) + "-01-01", "%Y-%m-%d")
        currentdate = datetime.datetime.today()
        results = self.learning.find({"UserId": userid,
                                      "LearnedDate": {"$gte": startdate,
                                                      "$lte": currentdate
                                                      }})
        return results
