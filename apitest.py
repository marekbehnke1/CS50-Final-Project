import requests

APIheaders = {
    'Content-Type':'application/json',
    'Authorization':'Token 877c60a71d24e500a3767c3875e6845c35df8564'
}

requestResponse = requests.get("https://api.tiingo.com/api/test/", headers=APIheaders)

print(requestResponse.json())