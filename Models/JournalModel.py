import pymongo
import datetime
from bson import ObjectId
from pymongo import MongoClient


class Journal:

    def __init__(self):
        self.client = MongoClient()
        self.PersonalWebDb = self.client.PersonalWebDb
        self.journal_table = self.PersonalWebDb.Journal

    def createNewJournal(self, journal_data):
        try:
            self.journal_table.insert_one(journal_data)
            return "success"
        except:
            return "error"

    def updateJournal(self, data):
        print(data)
        update_data = {"Subject": data["subject"],
                       "Notes": data["notes"],
                       "PriorityLevel": data["radio_priority"]
                       }
        try:
            self.journal_table.update_one({"_id": ObjectId(data["objectid_input"])},
                                          {"$set": update_data})
            return "success"
        except:
            return "error"

    def getAllJournalsForUser(self, userid):
        results = self.journal_table.find({"UserId": userid})
        return results

    def getCountjournalsForUser(self, userid):
        documents_count = self.journal_table.count_documents({"UserId": userid})
        return documents_count

    def getJournalRecord_one(self, input_id):
        object_id = input_id["ObjectId"]
        try:
            return self.journal_table.find_one({"_id": ObjectId(object_id)})
        except:
            return "error"

    def delete_journal_one(self, input_id):
        result = self.journal_table.delete_one({"_id": ObjectId(input_id)})
        if result.deleted_count > 0:
            return "success"
        else:
            return "error"
