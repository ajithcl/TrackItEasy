import pymongo
from pymongo import MongoClient
import datetime


class Feelings:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.PersonalWebDb
        self.feelings = self.db.Feelings

    def updateFeeling(self, identifier, data):
        return self.feelings.update_one(identifier, data, upsert=True)

    def getLastUpdatedDate(self, userid):
        result = self.feelings.find({"UserId": userid}).sort("FeltDate", -1).limit(1)
        lastUpdateDate = None
        for rec in result:
            lastUpdateDate = datetime.datetime.date(rec["FeltDate"])
        return lastUpdateDate
