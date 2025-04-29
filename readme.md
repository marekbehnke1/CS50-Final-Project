
# Personal Stock Tracker
#### Video Demo:  <URL HERE>
#### Description:

if i kil terminal
.venv\scripts\activate\ps1

TODO
# [] Front End
     [] Landing Page
        [x] graphs
            [x] graph working
            [x] graph date selection working
            [x] finish default values and error check for graph date update
            [] default display for graph
            [x] search for stock info to generate graphs
            [x] Autocomplete search when searching for ticker codes
                [] need some error checking here for when a searched stock does not return a valid result
                [x] clear the search box once item has been clicked
            [x] add to favourite / remove from favourite
            [] up/down arrows not vertically aligning
            [x] info from tiingo on the bottom right panel
        [] add favourite button for when stocks are searched
        [] favourite button turn to a - if stock is already in favs list

     [] Portfolio Page
        [] stocks interested in?
        [] stocks to watch? 

     [x] Account Page
        [x] update password
        [x] update account details
        
     [x] Login page
        [x]finish register button
        [x]flash bar

     [x] Register Page
        [x]flash bar
        
     [] Styling
        [] finish styling

# [] Back End
    [] Database configuration
        raw python db api for now
        [x] users db
        [x] stocks table

    [] Page Code 
        [x] Login Functionality
            []find a better way of returning db results

        [x] Registration functionality
            [x] loop throgh a dict to check empty form fields and give appropriate error

        [x] Account page
            [x] password change
            [x] update account info

        [x] Favourites
            [x] add to favourites route
            [x] retrieve favourites on login
            [x] need to find a way to use the + to add to favourites using JS, so page doesnt have to reload

        [] portfolio page
            [x] retrieve favourites
            [] display more interesting data

    [] API Connection 
        [x]Tiingo
            https://www.tiingo.com/documentation/general/connecting
        [x] API call on load and save data in memory to limit api calls
            []check for any additional api calls needed
        [x] Double check some of the variable naming conventions in the retrieve & sort  functions
# [] Bugs
    [x] makes 10 of the same api call when you click a stock link on the side panels
        - i think its linked to the updatePage function through the /chart route
        - doesnt happen if no search, no date, no graph 
        - happens if you have typed something into the search


https://stackoverflow.com/questions/74808530/send-data-from-javascript-%E2%86%92-python-and-back-without-reloading-the-page

https://flask.palletsprojects.com/en/stable/patterns/javascript/

https://www.makeuseof.com/tag/python-javascript-communicate-json/

google visualisations api 
pip install gviz_api