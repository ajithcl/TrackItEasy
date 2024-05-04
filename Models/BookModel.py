import pymongo
import datetime
from bson import ObjectId
from pymongo import MongoClient
import matplotlib.pyplot as plt


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

    def getBooksReadPerYearGraph(self, userid):
        return_value = "error"
        aggregation_pipeline = [{"$match": {"UserId": userid}},
                                {"$project": {"year": {"$year": "$EndDate"}}},       # Extract year from EndDate
                                {"$group": {"_id": "$year", "Count": {"$sum": 1}}},  # Group by year and count
                                {"$sort": {"_id": 1}}                                # Optionally sort by year
                                ]

        books_cursor = self.books.aggregate(aggregation_pipeline)
        year_list = []
        count_list = []
        if books_cursor:
            for document in books_cursor:
                if document['_id'] != 9999:
                    year_list.append(document['_id'])
                    count_list.append(document['Count'])

            # Plot the line graph

            plt.plot(year_list, count_list)
            #plt.tight_layout(pad=0)
            plt.title("Books read per Year")
            plt.savefig("static/temp/books_per_year_graph.png")
            plt.close()
            return_value = "success"
        else:
            return_value = "error"

        return return_value

    def getCompletedBooksCount(self, userid):
        result = self.books.count_documents({"UserId": userid,
                                  "EndDate": {"$lt": datetime.datetime.strptime("9999-12-31", "%Y-%m-%d")}})
        # return result.count_documents()
        return  result
