# CS50 Stocks Game
## Introduction
The intention of this project was to create an online game where you could practise buying and selling stocks, using live stock market data without the worry of losing real money.  
This was then gamified with the inclusion of a leaderboard, which tracks everyones total account balance, and the fact that every user starts with a set balance with no opportunity to deposit more.
This incentivises people to actually trade stocks in order to win. 

### Future Additions
If i were to commit more time to this project in the future, one of the main additions i would make would be the inclusion of leagues.  
These would allow you to invite other users to a private league where you could play against each other for a set period of time.

#### Video Demo: <https://www.youtube.com/watch?v=XiWfWq87frU>
## Technologies
The project was made as a fullstack webapp, using Flask, Sqlite3, Javascript, HTML & Tailwind CSS
## Project Contents
### 1. HTML FIles  
As the project uses Flask, and also Jjina the main layout for all of the main pages are contained within layout.html.  
login.html & register.html do not use the layout template as their structure is significantly different from the other pages.  
</br>
Each html file corresponds to the relevant page on the site.

### 2. Javascript Files
There are 2 main js files within the project:

##### 2.1 Chart.js & Portfoliochart.js
These files contains the logic which displays the graphs on both the main index page and the smaller graphs on the portfolio page.  
They use the Google Data visualisations API to display data as both a candlestick chart on the index page and as line graphs on the portfolio.  
The data for the graphs is provided by the flask app, which itself pulls the data from a combination of information stored in the database (in the case of the portfolio) and information pulled from the tiingo web API (in the case of the index page).

#### 2.2 script.js
This is the main javascript file which is used to control many aspects of how the index page is displayed.  
It has 2 main functions which it performs.  
The first of which is to enable various elements on the page to be updated without reloading the page.  
It does this through a variety of async functions which access both data from the tiingo and alphavantage web API's and from the database.  
This includes things like dynamically creating new html elements for the page, a prime example of this is the news feed at the bottom of the page. This displays a series of cards, representing relevant news articles to the currently selected stock. 
This data is pulled from the alphavantage API, processed and then displayed to the user.  
The second main function it serves is to change the visual appearance of certain aspects of the page based on a condition.  
For instance in the watchlist panel, a different icon is displayed based on whether a stock is trending positively or negatively in value.  
Additionally the icon displayed next to the various stock items on the page changes based on whether you currently have that stock in your watchlist.

### 3. Python Files
There are 2 main python files which process all of the data for the website.  
The helpers file contains, as the name suggests, a variety of utility functions which are then used throughout the main app. API connection functions, data processing functions and the function which checks if a user is logged in.

#### 3.1 app.py
This is the main part of the project which provides routes through will all other functions in the project access and process data.  

##### 3.1.1 List of Routes
###### 1. "/"  
    This is the default route accessed once logged into the app.  
    This sets the initial data that is displayed to the user in both the "biggest winner/loser" panel on the right and the data shown in the watchlist panel on the left.  
    This data is then stored in the database, so that further refreshes of this page do not use more API calls.  
    As this site was made entirely using free API's which give you a limited amount of data and API calls to use, i have had to put various things in place in order to limit these.  
    If i did not have these restrictions, i would have data that is updated on a timer and would refresh continuously while the user is on the page.<br>

###### 2. "/differencepanel  
    Control of the winners/losers panel is taken over by javascript once the user has interacted with it.  
    This route provides a way for the js file to retrieve the information it needs without having to interact with the other main page elements that are intially set through the "/" route. 

###### 3. "/stock"  
    This route fills out the table & metadata panel which displays under the main graph when an individual stock item is selected.  
    As different stocks are accessed, it checks to see if they have saved metadata in the database, and if they do not it updates it.  
    This was done in order to limit API calls, as the stock metadate does not change.  
    It adds the metadata to the main stock price data dictionary, so that it is all served to the page in one dictionary.

###### 4. "/search"  
    As the name suggests this route controls the search panel at the top of the page.  
    It simply retrieves a list of stock items matching the search query as they are entered by the user.  
    It is limited to 20 results so as not to overwhelm the page.  
    The dynamic display element of this is controlled in script.js

###### 5. "/chart"  
    This route processes the data into the format required by the gviz_api.  
    It retrieves historical data from the tiingo api, as specificed by the dates entered by the user, falling back on a defualt if not dates are entered.  
    This data is processed via gviz_api datatable function and then served to the page as Json.

###### 6. "/retrieveFavourite"  
    This route simply retrieves the list of the users favourite stocks, which are displayed in the watchlist panel, and returns them as json to the page.  

###### 7. "/favourite"  
    This route is responsible for updating the users list of favourites saved in the database.  
    This route is triggered when a user clicks either the + or - buttons next to a stock item on the homepage.  
    It checks to see what type of request has been submitted and then performs the appropriate database action.

###### 8. "/login"  
    As the name implies.  
    Login information you submit is checked against users stored in the database.  
    A session cookie is then created which allows the user to access all of the pages on the site.
    
###### 9. "/register"  
    Submits information to the databse in order to register you as a new user.  
    Checks for usernames which already exists and fully checks your submitted information for errors.

###### 10. "/account"  
    Controls the data which is displayed to you when you access the account page and renders the correct template

###### 11. "/password"  
    allows you to update your password  

###### 12. "/emailupdate"  
    allows you to update your email address

###### 13. "/portfolio"  
    This route controls all of the data which is displayed to you on the portfolio page.  
    It connects to the tiingo API in order to retrieve updated price information from the previous day for all stock you currently hold.  
    In order to limit API calls it only does this once per day, once the stock market has opened and therefore, there is new information to be retrieved.  
    This date is then saved to the database, so a historical record can be built up.  
    This data is also shared across users who hold that stock, so that if the data is updated by someone, it does not need to be updated again for another user. This further limits the API calls which are needed.  
    It then uses this data, and data from the main API call done when you login, to display more detailed information about the performance of your stock holdings.

###### 14. "/portfoliograph"  
    This controls the processing of the data for each of the users stock holdings in order to display the graphs for each item.  
    The graphs will begin tracking data from the date of the users first purchase of that stock item.  
    Data is processed with the gviz_api

###### 15. "/buy"  
    This route controls the process of purchasing a stock.  
    It checks a users balance and updates their stock holdings appropriately.  
    It also allows a user to purchase either by quantity of shares, or by value of shares, and performs all the conversions appropriately depending on their selection.  
    It will not allow you to purchase partial shares.  
    It ensures that unnesecary database entries are not created and only 1 entry per stock item exists for each user.

###### 16. "/sell"  
    This performs the same functions as the /buy route, just in reverse.
    It contains a variety of error checks which ensure that a user cannot sell more than they have, and removes entries fromt the databse if their total number of stocks held goes to 0.

###### 17. "/preview"  
    This route provides the user with a dynamically updated price preview when buying or selling stocks.  
    This route is only accessed by a javascript async request once a user enters the quantity or value of stocks they would like to purchase.

###### 18. "/news"  
    This route provides the data for the newsfeed which is dynamically created when a user has selected the stock item they wish to view.  
    It uses the alphavantage api to get data in Json format, which is then processed and returned to the page to be displayed as cards for each news article.  
    It also calculates an overall "sentiment score" which is displayed above the newsfeed in order to give the user a quick overview on the general feeling towards a certain stock.

###### 19. "/leaderboard"  
    This route simply pulls the required data from the database and displays the top 20 users along with their score, username and position.

###### 20. "/logout"  
    As the name suggests.  
    Logs you out and removes your current session cookie.



##### 3.2 helpers.py
This file contains a variety of helper functions which are then used throughout app.py.  
The functions in this file are the ones used to pull data from various API's, as this functionality is required in multiple places throughout app.py

This file also includes the functions which are used to sort or otherwise process the data provided by these API's.
### 4. Database
Fields are described where the name does not give an obvious function.  
The database schema is as follows:
###### 1. Users  
    1.1. userid  
    1.2. fname  
    1.3. lname  
    1.4. email  
    1.5. hash  
        Contains the password hash for the user
    1.6. balance  
    1.7. lastupdate  
        This holds the timestamp for the last time that users favourites change values were updated.  
        This gets updated once per day

###### 2. Stocks
    2.1. id  
    2.2. ticker  
        Ticker code of the stock item
    2.3. exchange  
        Stock exchange on which the item is listed
    2.4. type  
        Category the item falls into, asset, security, bond etc.
    2.5. currency  
    2.6. info  
        Contains the metadata for the stock item
    2.7. name  
        Company name associated with the stock item

###### 3. Favourites  
    3.1. id  
    3.2. userid  
    3.3. ticker  
    3.4. change  
        Holds the % value for the amount by which the stock has gained or lost value over the preceeding 7 days

###### 4. Transactions  
    4.1. id  
    4.2. userid  
    4.3. value  
        Total value of the transaction
    4.4. transtype  
        Buy or Sell
    4.5. timelog  
        Transaction timestamp

###### 5. Holdings  
    5.1. id  
    5.2. userid  
    5.3. stock  
    5.4. quantity  
    5.5. datelog  

###### 6. Pricelog  
    6.1. id  
    6.2. code  
        Ticker code 
    6.3. datelog  
        date of recorded price
    6.4. price
        price recorded for the item
