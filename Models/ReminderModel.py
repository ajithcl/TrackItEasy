import pymongo
from bson import ObjectId
from pymongo import MongoClient
import datetime
import random

# import sys, traceback

next_reminder_date = datetime.date.today()


class Reminder:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.PersonalWebDb
        self.reminders_collection = self.db.Reminders

    def saveReminder(self, userid, data):
        start_date = datetime.datetime.strptime(data["StartDate"], "%Y-%m-%d")
        start_date = start_date.date()
        reminder_date = self.getReminderDate(start_date=start_date,
                                             interval_type=data["IntervalType"],
                                             interval=int(data["Interval"]))
        str_date = datetime.datetime.strftime(start_date, "%Y-%m-%d")
        str_reminder_date = datetime.datetime.strftime(reminder_date, "%Y-%m-%d")
        data_collection = {
            "UserId": userid,
            "EventName": data["EventName"],
            "StartDate": datetime.datetime.strptime(str_date, "%Y-%m-%d"),
            "IntervalPeriod": data["Interval"],
            "IntervalType": data["IntervalType"],
            "ReminderDate": datetime.datetime.strptime(str_reminder_date, "%Y-%m-%d"),
            "Comments": data["Comments"],
            "ReminderId": random.randint(1, 100)
        }
        try:
            self.reminders_collection.insert_one(data_collection)
            result = "success"
        except:
            result = "error"
            # traceback.print_exc()
        finally:
            return result

    def getReminderDate(self, start_date, interval_type="Days", interval=1):
        global next_reminder_date
        if interval_type == 'Days':
            interval_days = datetime.timedelta(days=interval)
            next_reminder_date = start_date + interval_days
        elif interval_type == 'Months':
            interval_days = datetime.timedelta(days=(interval * 30))
            next_reminder_date = start_date + interval_days
        else:
            interval_days = datetime.timedelta(days=(interval * 365))
            next_reminder_date = start_date + interval_days
        return next_reminder_date

    def get_n_reminders(self, userid, start_date, record_numbers):
        result = self.reminders_collection.find({"UserId": userid,
                                                 "ReminderDate": {"$gte": start_date}}) \
            .sort('ReminderDate', pymongo.ASCENDING) \
            .limit(record_numbers)
        return result

    def reset_reminder_ids(self):
        result_set = self.reminders_collection.find().sort('ReminderDate', pymongo.ASCENDING)
        count = 0
        for record in result_set:
            print(record)
            count = count + 1
            self.reminders_collection.update_one({"_id": record["_id"]},
                                                 {"$set": {"ReminderId": count}})

    def get_n_pending_reminders(self, userid, record_count=1):
        start_date = datetime.datetime.today()
        result_set = self.reminders_collection.find({"UserId": userid,
                                                     "ReminderDate": {'$lte': start_date}}) \
            .sort('ReminderDate', pymongo.ASCENDING) \
            .limit(record_count)
        return result_set

    def get_all_reminders(self, userid):
        result_set = self.reminders_collection.find({"UserId": userid}).sort('ReminderDate', pymongo.ASCENDING)
        return result_set

    def delete_reminder_by_id(self, record_id):
        result = self.reminders_collection.delete_one({"_id": ObjectId(record_id["_id"])})
        if result.deleted_count > 0:
            return "success"
        else:
            return "error"
