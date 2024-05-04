import pymongo
import datetime
from bson import ObjectId
from pymongo import MongoClient
import matplotlib.pyplot as plt
from Models import Common


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
                                {"$project": {"year": {"$year": "$EndDate"}}},  # Extract year from EndDate
                                {"$group": {"_id": "$year", "Count": {"$sum": 1}}},  # Group by year and count
                                {"$sort": {"_id": 1}}  # Optionally sort by year
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
            # plt.tight_layout(pad=0)
            plt.title("Books read per Year")
            plt.savefig("static/temp/books_per_year_graph.png")
            plt.close()
            return_value = "success"
        else:
            return_value = "error"

        return return_value

    def getBooksReadPerMonthCurrentYear(self, userid):
        return_value = "error"

        current_year = datetime.date.today().year
        start_date = str(current_year) + "-01-01"
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

        end_date = Common.getCurrentMonthStartEndDates()["MonthEndDate"]
        end_date = datetime.datetime.strftime(end_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        aggregation_pipeline = [{"$match": {"UserId": userid,
                                            "EndDate": {"$gte": start_date,
                                                        "$lte": end_date}}},
                                {"$project": {"month": {"$month": "$EndDate"}}},
                                {"$group": {"_id": "$month", "Count": {"$sum": 1}}}
                                ]
        expense_cursor = self.books.aggregate(aggregation_pipeline)

        month_list = []
        count_list = []
        graph_input = {}
        if expense_cursor:
            for count_value in expense_cursor:
                month_list.append(count_value['_id'])
                count_list.append(count_value['Count'])

            for mon, cnt in zip(month_list, count_list):
                graph_input[mon] = cnt

            x_mon = []
            y_cnt = []
            dict_items = sorted(graph_input.items())
            month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            for item in dict_items:
                x_mon.append(month_names[item[0]])
                y_cnt.append(item[1])

            # Plot the graph
            plt.plot(x_mon, y_cnt)
            for mon, cnt in zip(x_mon, y_cnt):
                plt.annotate(cnt, xy=(mon, cnt))
            plt.savefig("static/temp/books_per_month_current_year.png")
            plt.close()

            return_value = "success"
        else:
            return_value = "error"

        return return_value

    def getCompletedBooksCount(self, userid):
        result = self.books.count_documents({"UserId": userid,
                                             "EndDate": {"$lt": datetime.datetime.strptime("9999-12-31", "%Y-%m-%d")}})
        # return result.count_documents()
        return result
