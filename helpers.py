from functools import wraps
from flask import request, redirect, session
import requests

# login required function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#maybe include database connection func here?

#function to return top 50 results of given field from iex exchange

# pulls all iex data
def retrieve_iex():
    # set api headers
    APIheaders = {
        'Content-Type':'application/json',
        'Authorization':'Token 877c60a71d24e500a3767c3875e6845c35df8564'
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
    # it is then converted straight into a dict
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
