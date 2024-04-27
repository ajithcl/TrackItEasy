############################
# Author : Ajith kumar CL  #
# Date   : 07 Nov 2019     #
############################

import datetime
import humanize
import json
import web
from bson import ObjectId

from Models import UserAccountModel, BookModel, FeelingsModel, LearningsModel, ExpenseModel, ReminderModel, JournalModel
from Models import HealthModel, Common, MoviesModel, SettingsModel
from datetime import date

web.config.debug = False

urls = (
    '/', 'Home',
    '/summary', 'Summary',
    '/login', 'Login',
    '/logout', 'Logout',
    '/checklogin', 'CheckLogin',
    '/register', 'Register',
    '/postregistration', 'PostRegistration',
    '/books', 'Books',
    '/learnings', 'Learnings',
    '/savelearning', 'SaveLearning',
    '/places', 'Places',
    '/reminders', 'Reminders',
    '/getallreminders', 'GetAllReminders',
    '/savereminder', 'SaveReminder',
    '/delete_reminder_one', 'DeleteReminderOne',
    '/getbookone', 'GetBookOne',
    '/savebook', 'SaveBook',
    '/deletebook', 'DeleteBook',
    '/health', 'Health',
    '/updateExerciseStatus', 'UpdateExerciseStatus',
    '/journal', 'Journal',
    '/createjournal', 'createJournal',
    '/updatejournal', 'updateJournal',
    '/getjournalone', 'GetJournalOne',
    '/delete_journal_one', 'DeleteJournalOne',
    '/photos', 'Photos',
    '/feelings', 'Feelings',
    '/savefeeling', 'SaveFeeling',
    '/expenses', 'Expenses',
    '/save_expense', 'Save_Expense',
    '/getcurrentmonthexpensedetails', 'GetCurrentMonthExpenseDetails',
    '/getAllExpenseTrend', 'AllExpenseTrend',
    '/movies', 'Movies',
    '/save_movie', 'SaveMovie',
    '/viewallmovies', 'ViewAllMovies',
    '/viewmoviestowatch', 'ViewMoviesToWatch'
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore("sessions"), initializer={'user': None})
session_data = session._initializer
render = web.template.render("Views/Templates", base="MainLayout",
                             globals={'session': session_data, 'current_user': session_data["user"]})


class Home:
    def GET(self):
        return render.Home()


class Login:
    def GET(self):
        return render.Login()


class CheckLogin:
    def POST(self):
        formData = web.input()
        login = UserAccountModel.Login()
        user = login.checkUser(formData)
        if user:
            session_data["user"] = user
            data = {"UserId": session_data["user"]["UserId"],
                    "LastLoggedInTime": datetime.datetime.now()}
            login.updateUser(data)
            return "success"
        return "error"


class Register:
    def GET(self):
        return render.Register()


class PostRegistration:
    def POST(self):
        formData = web.input()
        login = UserAccountModel.Login()
        result = login.createUser(formData)
        return result


class Logout:
    def GET(self):
        session["user"] = None
        session_data["user"] = None
        session.kill()
        return "success"


class Summary:
    def GET(self):
        lastTimeVisit = None
        category_amounts_dict = {}
        book_read_list = None
        completed_books = 0
        feelings_update_info = ""
        current_month_expense_amount = 0
        last_month_expense_amount = 0
        current_year_expense_graph_loaded = "error"
        reminder_list = []
        pending_reminder_list = []
        learning_list = []
        today_expense = 0
        monthly_avg_expense = 0
        monthly_exp_warning = False
        health_graph_loaded = "error"
        weekly_budget = 0

        if session_data["user"] is not None:
            # Last time visit
            lastTimeVisit = humanize.naturaltime(datetime.datetime.now() - session_data["user"]["LastLoggedInTime"])

            # Expense summary
            expense = ExpenseModel.Expense()
            category_amounts_dict = expense.getMonthlyExpenseCategorySplit(session_data["user"]["UserId"])
            if len(category_amounts_dict.items()) > 0:
                key_of_maxvalue = max(category_amounts_dict, key=category_amounts_dict.get)
                category_amounts_dict[key_of_maxvalue + '__max'] = category_amounts_dict[key_of_maxvalue]
                del category_amounts_dict[key_of_maxvalue]
            # Current month expense
            current_month_expense_amount = expense.getCurrentMonthAmount(session_data["user"]["UserId"])
            # Last month expense
            current_year = datetime.date.today().year
            if datetime.date.today().month == 1:
                prev_month = 12
                prev_year = current_year - 1
            else:
                prev_month = datetime.date.today().month - 1
                prev_year = current_year
            last_month_expense_amount = expense.get_nth_month_amount(userid=session_data["user"]["UserId"],
                                                                     month_n=prev_month,
                                                                     year_n=prev_year)
            current_year_expense_graph_loaded = expense.current_year_total_graph(userid=session_data["user"]["UserId"])

            # Todays expense
            today_expense = expense.getTodaysExpense(session_data["user"]["UserId"])

            # Monthly average expense
            monthly_avg_expense = expense.getAverageMonthlyExpense(session_data["user"]["UserId"])

            # Current month expense warning
            if current_month_expense_amount > 0.00:
                if (current_month_expense_amount >= (monthly_avg_expense - 5000) or
                        current_month_expense_amount >= (last_month_expense_amount - 5000)):
                    monthly_exp_warning = True
                else:
                    monthly_exp_warning = False

            # Weekly budget
            remaining_weeks = Common.get_remaining_weeknumbers_in_month()
            weekly_budget = (monthly_avg_expense - current_month_expense_amount) / remaining_weeks

            # Books details
            books = BookModel.Book()
            book_read_list = books.getReadInProgressBookList(session_data["user"]["UserId"])
            completed_books = books.getCompletedBooksCount(session_data["user"]["UserId"])
            # Feelings details
            feelings = FeelingsModel.Feelings()
            lastUpdateDate = feelings.getLastUpdatedDate(session_data["user"]["UserId"])
            if lastUpdateDate is not None:
                feelings_update_info = "Feelings information updated on " + str(lastUpdateDate)
            else:
                feelings_update_info = "Update your feelings information"

            # Reminders
            reminder_model = ReminderModel.Reminder()
            start_date = datetime.datetime.now()
            reminder_result = reminder_model.get_n_reminders(userid=session_data["user"]["UserId"],
                                                             start_date=start_date,
                                                             record_numbers=10)

            for record in reminder_result:
                reminder_dict = {
                    "ReminderId": record["ReminderId"],
                    "EventName": record["EventName"],
                    "NextDate": datetime.datetime.strftime(record["ReminderDate"], "%Y-%m-%d")
                }
                reminder_list.append(reminder_dict)

            reminder_result = reminder_model.get_n_pending_reminders(userid=session_data["user"]["UserId"],
                                                                     record_count=10)
            for record in reminder_result:
                reminder_dict = {
                    "ReminderId": record["ReminderId"],
                    "EventName": record["EventName"],
                    "NextDate": datetime.datetime.strftime(record["ReminderDate"], "%Y-%m-%d")
                }
                pending_reminder_list.append(reminder_dict)

            # Learnings for the year
            learning_model = LearningsModel.Learning()
            results = learning_model.getLearningsForCurrentYear(userid=session_data["user"]["UserId"])
            month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                          "October", "November", "December"]
            for mnth in month_list:
                learning_list.append({'month': mnth, 'subject': []})
            for rec in results:
                learning_list[rec["LearnedDate"].month - 1]['subject'].append(rec["Subject"])

            # Health details
            health_class = HealthModel.Health()
            health_graph_loaded = health_class.get_current_year_graphics(userid=session_data["user"]["UserId"])

        data = {"LastTimeVisit": lastTimeVisit,
                "ExpenseCategoryAmounts": category_amounts_dict,
                "ExpenseCurrentMonthAmount": current_month_expense_amount,
                "ExpenseLastMonthAmount": last_month_expense_amount,
                "ExpenseWarning": monthly_exp_warning,
                "ExpenseYearGraph": current_year_expense_graph_loaded,
                "TodaysExpense": today_expense,
                "MonthlyAverageExpense": monthly_avg_expense,
                "ReadInProgressBooks": book_read_list,
                "CompletedBooksCount": completed_books,
                "LastFeelingUpdate": feelings_update_info,
                "ReminderList": reminder_list,
                "PendingReminderList": pending_reminder_list,
                "LearningList": learning_list,
                "ExerciseGraph": health_graph_loaded,
                "WeeklyBudget": weekly_budget
                }
        return render.Summary(data)


class Learnings:
    def GET(self):
        currentmonth = datetime.datetime.now().strftime('%B')
        learning = LearningsModel.Learning()
        if session_data["user"] is not None:
            userid = session_data["user"]["UserId"]
        else:
            userid = ""
        currMonthdata = learning.getLearningsForCurrentMonth(userid)
        currentMonthDetails = []
        for data in currMonthdata:
            currentMonthDetails.append(data["Subject"])
        pagedata = {"CurrentMonth": currentmonth,
                    "CurrentMonthDetails": currentMonthDetails}
        return render.Learning(pagedata)


class SaveLearning:
    def POST(self):
        data = web.input()
        strCurrentDate = str(date.today())
        currentDate = datetime.datetime.strptime(strCurrentDate, "%Y-%m-%d")
        learningData = {"UserId": session_data["user"]["UserId"],
                        "LearnedDate": currentDate,
                        "Subject": data["Subject"]}
        learning = LearningsModel.Learning()
        return learning.createLearning(learningData)


class Places:
    def GET(self):
        return render.Places()


class Movies:
    def GET(self):
        settings = SettingsModel.Settings()
        if session_data["user"] is not None:
            userid = session_data["user"]["UserId"]
        else:
            userid = ""
        # Load movie types for the html drop down
        movie_cursor = settings.get_settings(userid,
                                             'Movies',
                                             'Type')
        movie_types = []
        if movie_cursor is None:
            movie_types = []
        else:
            for document in movie_cursor:
                movie_types.append(document['Content'])
            movie_cursor.close()

        # Load Movie languages for html drop down
        movie_languages = []
        movie_cursor = settings.get_settings(userid,
                                             'Movies',
                                             'Language')

        if movie_cursor is None:
            movie_languages = []
        else:
            for document in movie_cursor:
                movie_languages.append(document['Content'])
            movie_cursor.close()

        movie_data = {'movie_types': movie_types,
                      'movie_languages': movie_languages}

        return render.Movies(movie_data)

class Reminders:
    def GET(self):
        return render.Reminders()


class SaveReminder:
    def POST(self):
        data = web.input()
        reminder_obj = ReminderModel.Reminder()
        result = reminder_obj.saveReminder(session_data["user"]["UserId"], data=data)
        return result


class GetAllReminders:
    def GET(self):
        reminder_obj = ReminderModel.Reminder()
        result_set = reminder_obj.get_all_reminders(userid=session_data["user"]["UserId"])
        json_string = ""
        for record in result_set:
            record["_id"] = str(record["_id"])
            reminder_dict = {'StartDate': datetime.datetime.strftime(record["StartDate"], "%Y-%m-%d"),
                             'IntervalPeriod': record['IntervalPeriod'],
                             'IntervalType': record['IntervalType'],
                             'ReminderDate': datetime.datetime.strftime(record["ReminderDate"], "%Y-%m-%d"),
                             'Comments': record['Comments'],
                             'ReminderId': record['ReminderId'],
                             'EventName': record['EventName'],
                             '_id': record['_id']
                             }
            json_string = json_string + json.dumps(reminder_dict) + "`^`"
        return json_string


class DeleteReminderOne:
    def POST(self):
        web_input = web.input()
        reminder_class = ReminderModel.Reminder()
        result = reminder_class.delete_reminder_by_id(web_input)
        return "success"


class Books:
    def GET(self):
        book = BookModel.Book()
        result = []
        if session_data["user"] is not None:
            result = book.getBooks(session_data["user"]["UserId"])
        bookList = []
        for bookone in result:
            bookone["StartDate"] = str(bookone["StartDate"])[:10]
            if str(bookone["EndDate"])[:10] == "9999-12-31":
                bookone["EndDate"] = ""
            else:
                bookone["EndDate"] = str(bookone["EndDate"])[:10]
            bookList.append(bookone)

        return render.Books(bookList)


class SaveBook:
    def POST(self):
        data = web.input()
        book = BookModel.Book()
        listKeys = data.keys()
        if data.StartDate == "":
            data.StartDate = str(datetime.datetime.now())
            data.StartDate = data.StartDate[:10]  # get the first 10 digits

        if data.EndDate == "":
            data.EndDate = str(datetime.datetime.strptime("9999-12-31", "%Y-%m-%d"))
            data.EndDate = data.EndDate[:10]

        dtStartDate = datetime.datetime.strptime(data.StartDate, "%Y-%m-%d")
        bookData = {"UserId": session_data["user"]["UserId"], "BookName": data.BookName, "StartDate": dtStartDate,
                    "EndDate": datetime.datetime.strptime(data.EndDate, "%Y-%m-%d"), "RelatedTo": data.RelatedTo,
                    "Author": data.Author,
                    "Comments": data.Comments, "PrivateInfo": listKeys.__contains__("PrivateInfo")}
        # if hiddenbookid is blank, means new record which we need to create
        # else we need to update the existing record
        if data.hiddenbookid == "":
            result = book.createBook1(bookData)
        else:
            result = book.updateOneBook(
                {"_id": ObjectId(data.hiddenbookid)},
                {"$set": bookData}
            )
        return result


class GetBookOne:
    def GET(self):
        data = web.input()
        book = BookModel.Book()
        result = book.getBookOne({"_id": ObjectId(data["_id"])})
        if str(result["EndDate"])[:4] == "9999":
            strEndDate = ""
        else:
            strEndDate = str(result["EndDate"])[:10]

        if result["PrivateInfo"]:
            strPrivateInfo = "True"
        else:
            strPrivateInfo = ""

        dictobj = {"UserId": result["UserId"],
                   "BookName": result["BookName"],
                   "StartDate": str(result["StartDate"])[:10],
                   "EndDate": strEndDate,
                   "RelatedTo": result["RelatedTo"],
                   "Author": result["Author"],
                   "Comments": result["Comments"],
                   "PrivateInfo": strPrivateInfo
                   }
        jsonString = json.dumps(dictobj)
        return jsonString


class DeleteBook:
    def POST(self):
        data = web.input()
        book = BookModel.Book()
        result = book.deleteBook(data)
        return result


class Health:
    def GET(self):
        return render.Health()


class UpdateExerciseStatus:
    def POST(self):
        health_class = HealthModel.Health()
        data = web.input()
        if session_data["user"] is not None:
            userid = session_data["user"]["UserId"]
        else:
            userid = ""

        exercise_date = data["ExerciseDate"]
        record_date = datetime.datetime.strptime(exercise_date, "%Y-%m-%d")

        try:
            exercise_update_result = health_class.update_exercise_status(userid, True, record_date)
            print(exercise_update_result.modified_count)

            if exercise_update_result.acknowledged:
                return "success"
            else:
                return "error"
        except Exception as ex:
            return "error"


class Journal:
    def GET(self):
        journal_class = JournalModel.Journal()
        if session_data["user"] is not None:
            userid = session_data["user"]["UserId"]
        else:
            userid = ""
        journal_notes = journal_class.getAllJournalsForUser(userid)
        journal_list = []
        for data in journal_notes:
            journal_list.append({"subject": data["Subject"],
                                 "notes": data["Notes"][0:50] + "..",
                                 "ObjectId": data["_id"]}
                                )
        pagedata = {"journal_records": journal_list}
        return render.Journal(pagedata)


class createJournal:
    def POST(self):
        data = web.input()
        encode_text = True
        try:
            data["encode_data"]
        except Exception as ex:
            encode_text = False
        journal_class = JournalModel.Journal()
        str_current_date = str(date.today())
        current_date = datetime.datetime.strptime(str_current_date, "%Y-%m-%d")
        journal_data = {"UserId": session_data["user"]["UserId"],
                        "CreatedDate": current_date,
                        "UpdatedDate": current_date,
                        "Subject": data["subject"],
                        "Notes": data["notes"],
                        "EncodedInformation": encode_text,
                        "PriorityLevel": data["radio_priority"]
                        }
        result = journal_class.createNewJournal(journal_data)
        return result


class updateJournal:
    def POST(self):
        data = web.input()
        journal_class = JournalModel.Journal()
        str_current_date = str(date.today())
        current_date = datetime.datetime.strptime(str_current_date, "%Y-%m-%d")
        result = journal_class.updateJournal(data)
        return result


class GetJournalOne:
    def POST(self):
        data = web.input()
        journal_class = JournalModel.Journal()
        result = journal_class.getJournalRecord_one(data)
        dict_obj = {"ObjectId": str(result["_id"]),
                    "Subject": result["Subject"],
                    "Notes": result["Notes"],
                    "EncodedInformation": False,
                    "PriorityLevel": "Normal"
                    }
        json_string = json.dumps(dict_obj)
        return json_string


class DeleteJournalOne:
    def POST(self):
        data = web.input();
        journal_class = JournalModel.Journal()
        result = journal_class.delete_journal_one(data["objectid"])
        return result


class Photos:
    def GET(self):
        return render.Photos()


class Feelings:
    def GET(self):
        return render.Feelings()


class SaveFeeling:
    def POST(self):
        data = web.input()
        feeling = FeelingsModel.Feelings()
        strCurrentDate = str(date.today())
        currentDate = datetime.datetime.strptime(strCurrentDate, "%Y-%m-%d")
        result = feeling.updateFeeling({"UserId": session_data["user"]["UserId"], "FeltDate": currentDate},
                                       {"$set": {"Feelings": data["Feeling"]}})
        if result:
            return "success"
        else:
            return "error"


class Expenses:
    def GET(self):
        expense = ExpenseModel.Expense()
        settings = SettingsModel.Settings()

        if session_data["user"] is None:
            userid = None
        else:
            userid = session_data["user"]["UserId"]
        currMonthAmt = expense.getCurrentMonthAmount(userid)

        #Load expense categories  for html drop down
        expense_categories = []
        settings_cursor = settings.get_settings(userid,
                                                "Expenses",
                                                "Category")
        if settings_cursor is None:
            expense_categories = []
        else:
            for document in settings_cursor:
                expense_categories.append(document["Content"])
        settings_cursor.close()

        pageinput = {"CurrentMonthAmount": currMonthAmt,
                     "Categories": expense_categories}

        return render.Expenses(pageinput)


class Save_Expense:
    def POST(self):
        data = web.input()
        strDate = str(data["ExpenseDate"])
        if strDate == "" or strDate is None:
            currentDate = datetime.date.today()
            strDate = str(currentDate)
        sendData = {"UserId": session_data["user"]["UserId"],
                    "ExpenseDate": datetime.datetime.strptime(strDate, "%Y-%m-%d"),
                    "Amount": int(data["Amount"]),
                    "Category": data["Category"],
                    "Description": data["Description"]
                    }
        expense = ExpenseModel.Expense()
        result = expense.createExpense(sendData)
        if result:
            return "success"
        else:
            return "error"


class GetCurrentMonthExpenseDetails:
    def GET(self):
        expense = ExpenseModel.Expense()
        if session_data["user"] is None:
            userid = None
        else:
            userid = session_data["user"]["UserId"]
        result = expense.getCurrentMonthExpenseDetails(userid)
        if result == "error":
            return "error"
        else:
            jsonString = ""
            for data in result:
                data["_id"] = str(data["_id"])
                data["ExpenseDate"] = str(data["ExpenseDate"])[:10]
                obj = {"_id": data["_id"],
                       "ExpenseDate": data["ExpenseDate"],
                       "Amount": data["Amount"],
                       "Category": data["Category"],
                       "Description": data["Description"]
                       }
                jsonString = jsonString + json.dumps(obj) + "`^`"

            return jsonString


class AllExpenseTrend:
    def GET(self):
        expense = ExpenseModel.Expense()
        if session_data["user"] is None:
            userid = None
        else:
            userid = session_data["user"]["UserId"]
        result = expense.get_all_expense_trend(userid)
        return result


class SaveMovie:
    def POST(self):
        movie = MoviesModel.Movies()
        data = web.input()

        watch_date = str(data["WatchDate"])
        if watch_date == "" or watch_date is None:
            watch_date = str(datetime.date.today())

        already_watched = True
        try:
            data['watched']
            already_watched = True
        except KeyError:
            already_watched = False

        insert_data = {"UserId": session_data["user"]["UserId"],
                       "MovieName": data["MovieName"],
                       "MovieType": data["Type"],
                       "Language": data["Language"],
                       "WatchDate": datetime.datetime.strptime(watch_date, "%Y-%m-%d"),
                       "Comments": data["Comments"],
                       "Watched": already_watched
                       }
        # print(insert_data)
        result = movie.insert_one_movie(insert_data)
        return result


class ViewAllMovies:
    def GET(self):
        movie = MoviesModel.Movies()
        if session_data["user"] is None:
            return
        movies_data = movie.get_movies(userid=session_data["user"]["UserId"])

        movie_record_list = []

        if movies_data:
            for item in movies_data:
                movie_dict = item
                movie_dict.pop('_id')  # TODO - Removing the record object id
                movie_dict['WatchDate'] = movie_dict['WatchDate'].strftime("%Y-%m-%d")
                movie_dict.pop('UserId')
                movie_record_list.append(movie_dict)
            json_string = json.dumps(movie_record_list)
            return json_string
        else:
            return "error"


class ViewMoviesToWatch:
    def GET(self):
        movie = MoviesModel.Movies()
        if session_data["user"] is None:
            return
        movies_data = movie.get_movies_to_watch(userid=session_data["user"]["UserId"])

        movie_record_list = []

        if movies_data:
            for item in movies_data:
                movie_dict = item
                movie_dict.pop('_id')  # TODO - Removing the record object id
                movie_dict['WatchDate'] = movie_dict['WatchDate'].strftime("%Y-%m-%d")
                movie_dict.pop('UserId')
                movie_record_list.append(movie_dict)
            json_string = json.dumps(movie_record_list)
            return json_string
        else:
            return "error"


if __name__ == "__main__":
    app.run()
