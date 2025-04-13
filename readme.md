
# Personal Stock Tracker
#### Video Demo:  <URL HERE>
#### Description:

if i kil terminal
.venv\scripts\activate\ps1

TODO
# [] Front End
     [] Landing Page
        [] graphs
        [] search for stock info to generate graphs
            [] Autocomplete search when searching for ticker codes

     [] Portfolio Page
        [] stocks interested in?
        [] stocks to watch? 

     [] Account Page
        [] update password
        [] update account details
        
     [] Login page
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

        [] Account page
            [] password change
            [] update account info

    [] API Connection 
        [x]Tiingo
            https://www.tiingo.com/documentation/general/connecting
        [x] API call on load and save data in memory to limit api calls
            []check for any additional api calls needed
        [x] Double check some of the variable naming conventions in the retrieve & sort  functions


https://stackoverflow.com/questions/74808530/send-data-from-javascript-%E2%86%92-python-and-back-without-reloading-the-page

https://flask.palletsprojects.com/en/stable/patterns/javascript/

https://www.makeuseof.com/tag/python-javascript-communicate-json/

pip install gviz_api