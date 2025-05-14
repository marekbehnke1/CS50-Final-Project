
# Personal Stock Tracker
#### Video Demo:  <URL HERE>
#### Description:

if i kil terminal
.venv\scripts\activate\ps1

# NEXT STEPS:
    [x] portfolio page - design card template
        [x] Configure some sort of basic tracking, so you can see a small graph for each stock in the portfolio card
        [x] When its added to holding, start tracking price once each day so you see how its doing
    [x] design data structure to populate it
    [] styling pass on portfolio page
    [] finish adding func. to buy/sell panels
        [] buy sell - let you choose either amount or no. of shared to purchase and it will calculate the other variable   

    [] styling pass on home page
        [x] re-do the items in side panels
        [x] include company name - bigger tiles
        [x] need to fettle with the way links are attached and retrieve the ticker code - so i can have the whole link icon be a link, not just the small code
        [x] finish alternate right side panel
            [x] the swap is working - but i need to now remove some of the old code for it and include a marker so you know which one you are on

        [] redo search panel to fit new style
        
        [x] find some good fonts - raleway
        [x] sort the colour change thing


    [] text overflow on news feed card titles
    [] do more testing with the real api data - some of the formatting goes mental with loads of text

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
                [x] need some error checking here for when a searched stock does not return a valid result
                [x] clear the search box once item has been clicked
            [x] add to favourite / remove from favourite
            [] up/down arrows not vertically aligning
            [x] info from tiingo on the bottom right panel
        [x] add favourite button for when stocks are searched
            [x] make button do button
        [x] favourite button turn to a - if stock is already in favs list

     [x] Portfolio Page
        [x] account stats
        [x] stock holding cards

     [x] Account Page
        [x] update password
        [x] update account details
        [] account page needs revisiting

     [x] Login page
        [x]finish register button
        [x]flash bar

     [x] Register Page
        [x]flash bar

    [] Leaderboards
        
     [] Styling
        [] finish styling
        [x] all page links on all pages
        [x] Their position needs to be consistent too

# [] Back End
    [] Database configuration
        raw python db api for now
        [x] users db
        [x] stocks table

    [] Page Code 
        [x] Login Functionality
            [x]find a better way of returning db results

        [x] Registration functionality
            [x] loop throgh a dict to check empty form fields and give appropriate error

        [x] Account page
            [x] password change
            [x] update account info

        [x] Favourites
            [x] add to favourites route
            [x] retrieve favourites on login
            [x] need to find a way to use the + to add to favourites using JS, so page doesnt have to reload

        [x] portfolio page
            [x] portfolio stats
            [x] data for stock holding cards
            [x] deposit money

        [] Leaderboards

    [x] API Connection 
        [x]Tiingo
            https://www.tiingo.com/documentation/general/connecting
        [x] API call on load and save data in memory to limit api calls
            [x]check for any additional api calls needed
        [x] Double check some of the variable naming conventions in the retrieve & sort  functions
# [] Bugs
    [x] makes 10 of the same api call when you click a stock link on the side panels
        - i think its linked to the updatePage function through the /chart route
        - doesnt happen if no search, no date, no graph 
        - happens if you have typed something into the search
    [x] if you use the main window add/remove fav thing then load a chart - it does a million network requests
        - the requests are going through stock and chart routes
        - i think this is to do with the js code added
    [x] Centre fav button not working now - as a result of my new fav button swap thing
    [x] we now have a weird duplacte flashed messages thing going on
    [] need to make account balance not go over int limit
        [] dont know why its doing this, as the check is in place?
    [x] the homepage colour thing is sort of fixed - still looks weird on big screens though
 


https://stackoverflow.com/questions/74808530/send-data-from-javascript-%E2%86%92-python-and-back-without-reloading-the-page

https://flask.palletsprojects.com/en/stable/patterns/javascript/

https://www.makeuseof.com/tag/python-javascript-communicate-json/

google visualisations api 
pip install gviz_api

This will host the site locally
flask run --host=0.0.0.0

alphavantage api key
LGMEY6AQKNGZO4TZ