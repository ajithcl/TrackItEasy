import datetime
from datetime import date
import pymongo
from pymongo import MongoClient


# This is the static function
def getCurrentMonthStartEndDates():
    currentYear = datetime.datetime.now().year
    currentMonth = datetime.datetime.now().month
    nxtdt = datetime.date.today()
    continueloop = True
    # Find the last date of the current month
    while continueloop:
        prevdt = nxtdt
        nxtdt = nxtdt + datetime.timedelta(days=1)
        if nxtdt.month == currentMonth:
            continueloop = True
        else:
            continueloop = False

    startDate = date(currentYear, currentMonth, 1)
    endDate = prevdt
    result = {"MonthStartDate": startDate,
              "MonthEndDate": endDate}
    return result


def get_months_start_end_dates(month_n, year_n):
    date_string = str(year_n) + "-" + str(month_n) + "-1"
    start_date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    continue_loop = True
    nxt_date = start_date
    while continue_loop:
        prevdt = nxt_date
        nxt_date = nxt_date + datetime.timedelta(days=1)
        if nxt_date.month == month_n:
            continue_loop = True
        else:
            continue_loop = False

    return {
        "StartDate": start_date,
        "EndDate": prevdt
    }


def get_remaining_weeknumbers_in_month():
    curr_date = datetime.date.today()
    curr_year = curr_date.year
    next_month = curr_date.month
    if next_month == 12:
        next_month = 1
    else:
        next_month = next_month + 1
    last_date = datetime.date(year=curr_year, month=next_month, day=1)
    last_date = last_date - datetime.timedelta(days=1)
    return last_date.isocalendar()[1] - curr_date.isocalendar()[1] + 1


def get_start_end_dates(userid,
                        collection_name):
    client = MongoClient()
    db = client.PersonalWebDb
    collection = db[collection_name]

    minDate = None
    maxDate = None

    # Aggregate pipeline to find minimum and maximum dates
    pipeline = []
    if collection_name == "Movies":
        pipeline = [{"$match": {"UserId": userid,
                                "Watched": True}},
                    {"$group": {
                        "_id": None,
                        "minDate": {"$min": "$WatchDate"},
                        "maxDate": {"$max": "$WatchDate"}
                    }}
                    ]

    collection_cursor = list(collection.aggregate(pipeline))

    if collection_cursor:
        minDate = collection_cursor[0]["minDate"]
        maxDate = collection_cursor[0]["maxDate"]

    return {"minDate": minDate,
            "maxDate": maxDate}
