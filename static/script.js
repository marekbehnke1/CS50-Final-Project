
let remove_fav = document.getElementsByClassName("remove_favourite")
let add_fav = document.getElementsByClassName("add_favourite")
let stock_links = document.getElementsByClassName("ticker-code")
let sent_panel = document.getElementById("overall-sentiment-panel")


// attaches all event listeners for the page
async function update_page(){

    // these get redclared so the lists are updated
    let remove_fav = document.getElementsByClassName("remove_favourite")
    let add_fav = document.getElementsByClassName("add_favourite")
    let stock_links = document.getElementsByClassName("ticker-code")
    let chart_dates = document.getElementsByClassName("chartDates")
    let centre_add_button = document.getElementById("centre-fav-add")

    // attach link listeners
    for (item of stock_links){
        item.addEventListener("click", add_link)
    }

    // attach fav listeners
    for (item of add_fav){
        item.addEventListener("click", fav_add_listen)
    }

    // attach listener to centre button
    centre_add_button.addEventListener("click", centre_fav_add_listen)

    // attach remove fav listeners
    for (item of remove_fav){
        item.addEventListener("click", fav_rm_listen)
    }

    // attach listeners to chart dates
    for (item of chart_dates){
        item.addEventListener("input", date_listen)
    }

    let search_form = document.getElementById("search")
    // attach search box listener
    search_form.addEventListener("input", search_listen)

    // clear search box on focusout
    search_form.addEventListener("focusout", search_close)

    // update the add fav icon in centre
    center_fav_icon_update(await get_fav())

}

function fav_rm_listen(){
    code = this.parentElement.previousElementSibling.value
    remove_favourite(code)
}
function fav_add_listen(){
    code = this.parentElement.previousElementSibling.value
    add_favourite(code)
}
function centre_fav_add_listen(){
    code = this.previousElementSibling.value
    add_favourite(code)
}
function search_listen(){
    let search_form = document.getElementById("search")
    search(search_form.value)
}
function search_close(){
    setTimeout(function(){
        document.getElementById("search-results").innerHTML = "";
        document.getElementById("search").value ="";
    }, 100)
}
function date_listen(){
    code = document.getElementById("current-ticker").value
    dateFrom = document.getElementById("dateFrom").value    
    dateTo = document.getElementById("dateTo").value 

    if (code && dateFrom && dateTo){
        update_graph(code, dateTo, dateFrom)
    }
}

async function add_favourite(code) {
    await fetch('/favourite?q=ad&ticker=' + code)
    update_favourites()
}

async function remove_favourite(code) {
    await fetch('/favourite?q=rm&ticker=' + code)
    update_favourites()
}

// Graph/Table Functions
async function update_graph(code, dateTo, dateFrom) {

    let response = await fetch('/chart?q=' + code +'&to=' + dateTo + '&from=' + dateFrom)
    let chartData = await response.json()

    drawChart(chartData, code)
    update_table(code)
    update_page()
};

async function update_table(code){
    let response = await fetch('/stock?q=' + code);
    let table_info = await response.json()
    let table_fields = document.getElementsByClassName("table_field")
    
    for (item of table_fields){

        item.innerHTML = table_info[item.id]

    }
}

//Search
async function search(code){

    let response = await fetch("/search?q=" + code) 
    let searchItems = await response.json();

    let html = '';
    for (let item of searchItems){
        html += '<li class="search-link border-y border-slate-600 bg-slate-400 hover:bg-slate-600 cursor-pointer">' + item[1] + "</li>";
    } 
    document.getElementById("search-results").innerHTML = html;

    let search_links = document.getElementsByClassName("search-link")
    for(item of search_links){
        item.addEventListener("click", add_link)
    }
}

//Functions:
    // Update Favourites()
async function update_favourites(){

    favourites_list = await get_fav()
    
    let html = ''
    for(let item of favourites_list){
        if(item["change"] > 0){
            icon = '<svg width="20px" height="20px" viewBox="0 0 16.00 16.00" fill="none" xmlns="http://www.w3.org/2000/svg" transform="rotate(0)matrix(1, 0, 0, 1, 0, 0)" stroke="#0ea5e9"><g stroke-width="0"></g><g stroke-linecap="round" stroke-linejoin="round" stroke="#0ea5e9" stroke-width="0.032"></g><g> <path d="M6 8L2 8L2 6L8 5.24536e-07L14 6L14 8L10 8L10 16L6 16L6 8Z" fill="#0ea5e9"></path> </g></svg>'
        }
        else{
            icon = '<svg width="20px" height="20px" viewBox="0 0 16.00 16.00" fill="none" xmlns="http://www.w3.org/2000/svg" transform="rotate(0)matrix(1, 0, 0, -1, 0, 0)" stroke="#ec4899"><g stroke-width="0"></g><g stroke-linecap="round" stroke-linejoin="round" stroke="#ec4899" stroke-width="0.032"></g><g> <path d="M6 8L2 8L2 6L8 5.24536e-07L14 6L14 8L10 8L10 16L6 16L6 8Z" fill="#ec4899"></path> </g></svg>'
        };
        
        html += fav_element(icon, item)
    }
    document.getElementById("favourite-list").innerHTML = html
        
    let remove_icon = '<svg class="cursor-pointer remove_favourite stock-list-item" width="20px" height="20px" viewBox="0 0 24 24" fill="" xmlns="http://www.w3.org/2000/svg"><g> <path class="hover:stroke-slate-200" d="M6 12L18 12" stroke="#475569" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>'
    let add_icon = '<svg class="hover:fill-slate-200 cursor-pointer add_favourite stock-list-item" fill="#475569" height="20px" width="20px" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 455 455" xml:space="preserve"><g stroke-width="0"></g><g stroke-linecap="round" stroke-linejoin="round"></g><g> <polygon points="455,212.5 242.5,212.5 242.5,0 212.5,0 212.5,212.5 0,212.5 0,242.5 212.5,242.5 212.5,455 242.5,455 242.5,242.5 455,242.5 "></polygon> </g></svg>'

    let fav_buttons = document.getElementsByClassName("stock-list-item")
    for(button of fav_buttons){  

        code = button.parentElement.previousElementSibling.value
        count = 0

        // This is to account for removing the last fav item
        // in which case when it gets back here, the list length will be 0
        if (favourites_list.length == 0)
        {   //Set all signs to +
            button.parentElement.innerHTML = add_icon
        }
        else {
            for(item of favourites_list)
            {
                if(item["ticker"] == code){
                    button.parentElement.innerHTML = remove_icon
                    break
                }
    
                //THIS WORKS NOW
                else if(button.parentElement != null){
                    count += 1
                    // changes the button once it has checked the whole list and does not find a match.
                    if (count == favourites_list.length)
                    {
                        button.parentElement.innerHTML = add_icon
                    }
                }
            }
        }
    }

    update_page()
}

// adds standard link functionality to an item
function add_link(){
    code = this.textContent.trim()
    dateFrom = document.getElementById("dateFrom").value    
    dateTo = document.getElementById("dateTo").value
    
    document.getElementById("current-ticker").value = code
    update_graph(code, dateTo, dateFrom)
    get_news(code, dateFrom, dateTo)
}

// just an object that represebts the fav list item
function fav_element(icon, item){
    let fav_item = '<tr class="border-y h-10 border-solid border-collapse border-slate-400 bg-slate-600 hover:bg-slate-700 stock-item">' + 
                        '<td class="ticker-code cursor-pointer">' + item["ticker"] + '</td>' + 
                        '<td class="flex align-middle justify-evenly">' + '<p>' + item["change"] + ' %' + '</p>' + icon +'</td>' +
                        '<td>' + '<input type="hidden" name="q" value="' + item["ticker"] + '">' +
                            '<form class="fav-form" action="/favourite" method="get">' + 
                                '<svg class="cursor-pointer remove_favourite" width="20px" height="20px" viewBox="0 0 24 24" fill="" xmlns="http://www.w3.org/2000/svg"><g> <path class="hover:stroke-slate-200" d="M6 12L18 12" stroke="#475569" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>' + 
                            '</form>' + 
                        '</td>'+
                    '</tr>'
    return fav_item
}
// returns a promise of the favourites list
async function get_fav() {
    let response = await fetch('/retrieveFavourite')
    favourites_list = await response.json()
    return favourites_list
}

// updates the + icon in the centre based on fav stats of item
function center_fav_icon_update(favourites_list){
    current_stock = document.getElementById("current-ticker").value

    if (!current_stock){
        document.getElementById("centre-fav-add").style.visibility = "hidden"
    }
    
    // check if the item is in the favourites list
    else{
        for(item of favourites_list){
            
            if (item["ticker"] == current_stock){
                document.getElementById("centre-fav-add").style.visibility = "hidden"
                break
            }
            else{
                document.getElementById("centre-fav-add").style.visibility = "visible"
            }
        }
    }
}

async function get_news(code, dateFrom, dateTo)
{
    response = await fetch("/news?q=" + code + "&from=" + dateFrom + "&to=" + dateTo)
    result = await response.json()
    newsfeed = result.feed
    newspanel = document.getElementById("news_panel")
    sent_panel = document.getElementById("overall-sentiment-panel")
    
    newslist = ''
    // check newsfeed exists
    if (!newsfeed){
        newspanel.innerHTML = '<p> News feed not available </p>'
        sent_panel.style.visibility = "hidden"
        console.log("should be logging this")
    }
    else{
        // check if the returned object is an iterable object
        if (Symbol.iterator in Object(newsfeed)){
            // check the returned object items to display
            if(newsfeed.length <= 0){
                newspanel.innerHTML = '<p> News feed not available </p>'
                sent_panel.style.visibility = "hidden"
                console.log("should be logging this")
            }
            else{

                // Had to initialise this to 0
                let total_sentiment_score = 0 

                for(item of newsfeed){

                    // track sent score
                    total_sentiment_score += item.overall_sentiment_score

                    newslist += `<div class="h-100 news-card rounded-xl shadow-xl p-5 bg-linear-65 from-purple-700 to-pink-700">
                            <div class="w-full h-3/20 ">
                                <h1 class="font-bold text-slate-50"> `+ item.title +` </h1>
                            </div>
            
                            <div class="w-full h-14/20">
                                <div class=" w-full flex">
                                    <div class="mt-5 h-full w-2/3 text-left text-slate-100">
                                        <p class="px-5"> `+ item.summary +` </p>
                                    </div>
                                    <div class="mt-5 h-full w-1/3 text-left text-slate-100">
                                        <img src= `+ item.banner_image +` alt="News Icon" srcset="">
                                    </div>
                                </div>
            
                                <div class="w-full flex place-content-evenly mt-3 text-white">
                                    <p class="block">Sentiment: `+ item.overall_sentiment_label +`</p>   
                                    <p class="block">Sentiment: `+ item.overall_sentiment_score +`</p>
                                </div>
                            </div>
            
                            <div class=" w-full h-fit flex ">
                                <div class="w-1/3 text-slate-100">
                                    <p> `+ item.source +` </p>
                                </div>
                                <div class="w-2/3 text-slate-100 text-sm text-left truncate">
                                    <a class="text-slate-100 text-decoration-line: underline" href= "`+ item.url +`" > `+ item.url +` </a>
                                </div>
                            </div>
                        </div>`  
                }
                final_score = parseFloat(total_sentiment_score / newsfeed.length)
                let final_label;

                if (final_score < -0.35 ){
                    final_label = "Bearish"
                } 
                else if (final_score >= -0.35 && final_score < -0.15 ){
                    final_label = "Somewhat Bearish"
                }
                else if (final_score >= -0.15 && final_score < 0.15 ){
                    final_label = "Neutral"
                }
                else if (final_score >= 0.15 && final_score < 0.35 ){
                    final_label = "Somewhat Bullish"
                }
                else if (final_score >= 0.35 ){
                    final_label = "Bullish"
                }

                sent_panel.style.visibility = "visible"
                document.getElementById("sentiment-label").innerHTML = final_label
                document.getElementById("sentiment-score").innerHTML = final_score.toFixed(5)
            }
        }
        else{
            newspanel.innerHTML = '<p> News feed not available </p>'
            sent_panel.style.visibility = "hidden"
            console.log("should be logging this")
        }
    }

    newspanel.innerHTML = newslist
}