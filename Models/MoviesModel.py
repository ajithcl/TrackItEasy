from pymongo import MongoClient

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
        return self.movies.find({'UserId':userid})