import pymongo
from pymongo import MongoClient
import datetime
from Models import Common


class Movies:
    def __init__(self):
        self.client = MongoClient()
        self.personalwebdb = self.client.PersonalWebDb
        self.movies = self.personalwebdb.Movies

    def insert_one_movie(self, movie_data):
        try:
            self.movies.insert_one(movie_data)
            return "success"
        except:
            return "error"

    def get_movies(self, userid):
        return self.movies.find({'UserId': userid}).sort("WatchDate", pymongo.DESCENDING)

    def get_movies_to_watch(self, userid):
        return self.movies.find({'UserId': userid, 'Watched': False}).sort("WatchDate", pymongo.DESCENDING)

    def get_movies_count_current_year(self, userid):
        current_year = datetime.datetime.now().year
        start_date = datetime.datetime(current_year, 1, 1)
        today = datetime.datetime.now().today()
        movies_count = self.get_movies_count(userid,
                                             start_date,
                                             today)
        return movies_count

    def get_movies_current_month(self, userid):
        current_month_dates = Common.getCurrentMonthStartEndDates()
        start_date = current_month_dates["MonthStartDate"]
        end_date = current_month_dates["MonthEndDate"]
        start_date = datetime.datetime.combine(start_date, datetime.time())
        end_date = datetime.datetime.combine(end_date, datetime.time())

        movies_count = self.get_movies_count(userid,
                                             start_date,
                                             end_date)
        return movies_count

    def get_movies_count(self, userid, start_date, end_date):
        movies_count = self.movies.count_documents({"UserId": userid,
                                                    "Watched": True,
                                                    "WatchDate": {"$gte": start_date,
                                                                  "$lte": end_date}})
        return movies_count
