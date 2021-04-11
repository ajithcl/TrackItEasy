import datetime

import pymongo, bcrypt
from pymongo import MongoClient


class Login:

    def __init__(self):
        self.client = MongoClient()
        self.personalwebdb = self.client.PersonalWebDb
        self.UserData = self.personalwebdb.UserData

    def createUser(self, data):
        hashedpwd = bcrypt.hashpw(data.Password.encode('utf8'), bcrypt.gensalt())
        data.Password = hashedpwd
        try:
            self.UserData.insert_one({"UserId": data.UserId,
                                      "Password": data.Password,
                                      "LastLoggedInTime": datetime.datetime.now()})
            return "success"
        except:
            return "error"

    def checkUser(self, data):
        user = self.UserData.find_one({"UserId": data.UserId})
        if user:
            if bcrypt.checkpw(data.password.encode('utf8'), user["Password"]):
                return user
            else:
                return False

    def updateUser(self, data):
        user = self.UserData.find_one({"UserId": data["UserId"]})
        if user:
            self.UserData.update_one(
                {"UserId": data["UserId"]},
                {"$set": data}
            )
