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

    # sorts dict into a list of sorted data    
    sorted_full_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    
    # creates a list, of the items from the dict, then slices it to 50 entries
    # it is then converted straight into a dict
    sorted_trimmed_data = dict(list(sorted_full_data.items())[:records])

    # This then loops through the sorted, trimmed dict & returns a list of dicts.
    newList = []
    for k, v in sorted_trimmed_data.items():
        newList.append(
            {
                "ticker" : k,
                option : v
            }
        )
    return newList

print(sort_iex(option, records, IEXdata))




########
#returning a list of dicts, rather than a massive dict
def dict_iex(option, IEXdata):
    
    data = []
    for item in IEXdata:
        data.append(
                {
                    "ticker" : item["ticker"],
                    option:item[option]
                }
            )
        
    return data 

#print(dict_iex(option, IEXdata))