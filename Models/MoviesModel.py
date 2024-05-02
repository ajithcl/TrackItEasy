import pymongo
from pymongo import MongoClient
import datetime
from Models import Common
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd


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

    def get_movies_count_for_user(self, userid):
        movies_count = self.movies.count_documents({"UserId": userid})
        return movies_count

    def get_wordcloud_for_movie_types(self, userid):
        movies_type_list = []
        field_selection = {"MovieType": 1, "_id": 0}
        movies_cursor = self.movies.find({"UserId": userid,
                                          "Watched": True},
                                         field_selection)

        for document in movies_cursor:
            movies_type_list.append(document["MovieType"])

        movies_cursor.close()

        wc = WordCloud(background_color='white', collocations=False).generate(
            " ".join(movies_type_list))

        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig("static/temp/movies_types_wordcloud.png")
        plt.close()

        return "success"
        # TODO : Add error handling with success and failure

    def get_bar_for_movie_types(self, userid):
        bargraph_created = "error"
        aggregation_pipeline = [
            {
                "$match": {
                    "UserId": userid
                }
            },
            {
                "$group": {
                    "_id": "$MovieType",
                    "MovieCount": {"$sum": 1}}}]

        movies_cursor = self.movies.aggregate(aggregation_pipeline)
        movie_type_list = []
        movie_count_list = []
        for document in movies_cursor:
            movie_type_list.append(document['_id'])
            movie_count_list.append(document['MovieCount'])

        if len(movie_type_list) > 0:
            df_movie_types = pd.DataFrame({
                "Type": movie_type_list,
                "Count": movie_count_list})

            df_movie_types.sort_values(["Count"], inplace=True, ascending=False)

            # Plot the graph
            plt.bar(df_movie_types["Type"], df_movie_types["Count"])
            plt.tight_layout(pad=0)
            plt.savefig("static/temp/movies_types_bar.png")
            plt.close()

            bargraph_created = "success"
        else:
            bargraph_created = "error"

        return bargraph_created

