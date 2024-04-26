"""
This model deals with accessing data from Settings table.
Settings tables stores the configuration parameters for each individual web module
"""
from pymongo import MongoClient


class SingletonClass:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance


class Settings(SingletonClass):
    def __init__(self):
        self.client = MongoClient()
        self.personalWebDb = self.client.PersonalWebDb
        self.settings = self.personalWebDb.Settings

    def get_settings(self, userid, module, attribute):
        settings_cursor = self.settings.find({"UserId": userid,
                                              "Module": module,
                                              "Attribute": attribute})
        return settings_cursor
