import requests


option = "volume"
records = 100

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

IEXdata = retrieve_iex()


# sorts & trims iex data
def sort_iex(option, records, IEXdata):

    data = {}
    for item in IEXdata:
        data[item["ticker"]] = item[option]
        
    sorted_full_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    
    # creates a list, of the items from the dict, then slices it to 50 entries
    # it is then converted straight into a dict
    sorted_trimmed_data = dict(list(sorted_full_data.items())[:records])
    return sorted_trimmed_data


print(sort_iex(option, records, IEXdata))

