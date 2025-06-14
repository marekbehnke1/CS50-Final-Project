from functools import wraps
from flask import request, redirect, session
import requests
import re

# login required function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# pulls all iex data
def retrieve_iex():
    # set api headers
    APIheaders = {
        'Content-Type':'application/json',

        ### API KEY NEEDED ###
        'Authorization':'TIINGO API KEY HERE'
        #######################
        
    }
    # retrieve data from api and convert to json format
    Response = requests.get("https://api.tiingo.com/iex", headers=APIheaders).json()
    return Response

# sorts & trims iex data
# default direction is set to descending order of sort
def sort_data(option, records, data, direction=True):

    """ Direction is a bool parameter, set to True by default.
        True = sort descending,
        False = sort ascending """
    
    # sorts dict into a list of sorted data    
    sorted_full_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=direction))
    
    # creates a list, of the items from the dict, then slices it to 50 entries
    sorted_trimmed_data = dict(list(sorted_full_data.items())[:records])

    # This then loops through the sorted, trimmed dict & returns a list of dicts.
    newList = []
    for k, v in sorted_trimmed_data.items():
        newList.append(
            {
                "ticker" : k,
                option : round(v,2)
            }
        )
    return newList

def retrieve_history(ticker, dateFrom, dateTo ):
    """ Dates are in the form YYYY-MM-DD """
    headers = {
    'Content-Type': 'application/json'
    }
    requestResponse = requests.get("https://api.tiingo.com/tiingo/daily/" + ticker + "/prices?startDate=" + dateFrom + "&endDate=" + dateTo + "&token=877c60a71d24e500a3767c3875e6845c35df8564", headers=headers)
    return requestResponse.json()

def retrieve_metadata(ticker):
    headers = {
    'Content-Type': 'application/json'
    }
    requestResponse = requests.get("https://api.tiingo.com/tiingo/daily/" + ticker + "?token=877c60a71d24e500a3767c3875e6845c35df8564", headers=headers)
    return requestResponse.json()

def retrieve_news(ticker, dateFrom, dateTo):

    time_from = re.sub('-','',dateFrom)+ "T0000"
    time_to = re.sub('-','',dateTo) + "T0000"

    ### API KEY NEEDED ###
    key = "ALPHAVANTAGE API KEY HERE"
    ########################

    url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&time_from='+ time_from +'&time_to='+ time_to +'&tickers='+ ticker +'&apikey=' + key
    r = requests.get(url)
    data = r.json()

    return data

def retrieve_stock_data(code):
    
    headers = {
    'Content-Type': 'application/json'
    }
    requestResponse = requests.get("https://api.tiingo.com/iex/?tickers=" + code + "&token=877c60a71d24e500a3767c3875e6845c35df8564", headers=headers)
    return requestResponse.json()

#converts db results into dictionaries
def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}