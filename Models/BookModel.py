import pymongo
import datetime
from bson import ObjectId
from pymongo import MongoClient


class Book:
    def __init__(self):
        self.client = MongoClient()
        self.personalwebdb = self.client.PersonalWebDb
        self.books = self.personalwebdb.Books

    def createBook1(self, bookdata):
        try:
            self.books.insert_one(bookdata)
            return "success"
        except:
            return "error"

    def getBooks(self, userid):
        return self.books.find({"UserId": userid})

    def getBookOne(self, rowid):
        return self.books.find_one(rowid)

    def deleteBook(self, inputrowid):
        result = self.books.delete_one({"_id": ObjectId(inputrowid["_id"])})
        if result.deleted_count > 0:
            return "success"
        else:
            return "error"

    def updateOneBook(self, identifier, data):
        result = self.books.update_one(identifier,
                                       data)
        if result:
            return "success"
        else:
            return "error"

    def getReadInProgressBookList(self, userid):
        result = self.books.find({"UserId": userid,
                                  "EndDate": datetime.datetime.strptime("9999-12-31", "%Y-%m-%d")})
        book_list = []
        for rec in result:
            item = {"Name": rec["BookName"]}
            book_list.append(item)
        if book_list.__len__() == 0:
            return None
        else:
            return book_list

    def getCompletedBooksCount(self, userid):
        result = self.books.find({"UserId": userid,
                                  "EndDate": {"$lt": datetime.datetime.strptime("9999-12-31", "%Y-%m-%d")}})
        return result.count()
