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
        movies_count = self.movies.count_documents({"UserId": userid,
                                                    "Watched": True})
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
            plt.title("Movie types")
            plt.tight_layout(pad=0)
            plt.savefig("static/temp/movies_types_bar.png")
            plt.close()

            bargraph_created = "success"
        else:
            bargraph_created = "error"

        return bargraph_created

    def get_bar_count_per_month(self, userid):
        current_year = datetime.date.today().year
        start_date = str(current_year) + "-01-01"
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = str(current_year) + "-12-31"
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        aggregation_pipeline = [{"$match": {"UserId": userid,
                                            "Watched": True,
                                            "WatchDate": {"$gte": start_date,
                                                          "$lt": end_date}}},
                                {"$group": {
                                    "_id": {"month": {"$month": "$WatchDate"}},
                                    "MovieCount": {"$sum": 1}
                                }}
                                ]
        movies_cursor = self.movies.aggregate(aggregation_pipeline)
        months = []
        count = []
        graph_input = {}
        for doc in movies_cursor:
            months.append(doc["_id"]["month"])
            count.append(doc["MovieCount"])

        movies_cursor.close()

        for mon, cnt in zip(months, count):
            graph_input[mon] = cnt

        dict_items = sorted(graph_input.items())
        x_mon = []
        y_cnt = []
        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        for item in dict_items:
            x_mon.append(month_names[item[0]])
            y_cnt.append(item[1])

        # Plot the graph
        plt.plot(x_mon, y_cnt)
        plt.title("Number of Movies per month in " + str(current_year))
        plt.tight_layout(pad=1)
        plt.savefig("static/temp/movies_months_bar.png")
        plt.close()

        return "success"

    def get_graph_count_per_year(self, userid):
        aggregation_pipeline = [{"$match": {"UserId": userid,
                                            "Watched": True}},
                                {"$group": {
                                    "_id": {"$year": "$WatchDate"},
                                    "MovieCount": {"$sum": 1}
                                }}
                                ]
        movies_cursor = self.movies.aggregate(aggregation_pipeline)

        year_list = []
        count_list = []
        for doc in movies_cursor:
            year_list.append(str(doc['_id']))
            count_list.append(doc['MovieCount'])

        movies_cursor.close()

        # Plot the graph
        plt.plot(year_list, count_list)
        plt.title("Movies watched per year")
        plt.tight_layout(pad=1)
        plt.savefig("static/temp/movies_year_line.png")
        plt.close()

        return "success"
