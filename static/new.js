
let remove_fav = document.getElementsByClassName("remove_favourite")
let add_fav = document.getElementsByClassName("add_favourite")
let stock_links = document.getElementsByClassName("ticker-code")


//TODO: Update page (event) - run on page load with no event

// attaches all event listeners for the page
function update_page(){

    // these get redclared so the lists are updated
    let remove_fav = document.getElementsByClassName("remove_favourite")
    let add_fav = document.getElementsByClassName("add_favourite")
    let stock_links = document.getElementsByClassName("ticker-code")
    let chart_dates = document.getElementsByClassName("chartDates")
    

    // attach link listeners
    for (item of stock_links){
        item.addEventListener("click", add_link)
    }

    // attach fav listeners
    for (item of add_fav){
        item.addEventListener("click", fav_add_listen)
    }

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
}

function fav_rm_listen(){
    code = this.previousElementSibling.value
    remove_favourite(code)
}
function fav_add_listen(){
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
    let chartDates = document.getElementsByClassName("chartDates")

    drawChart(chartData, code)
    update_table(code)
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
        // TODO: update the add/remove icons on all links
        // TODO: update the item in the centre if necesary


async function update_favourites(){

    let response = await fetch('/retrieveFavourite')
    console.log("retrieving fav list")
    let result = await response.json()

    let html = ''
    for(let item of result){
        if(item["change"] > 0){
            icon = '<svg width="20px" height="20px" viewBox="0 0 16.00 16.00" fill="none" xmlns="http://www.w3.org/2000/svg" transform="rotate(0)matrix(1, 0, 0, 1, 0, 0)" stroke="#0ea5e9"><g stroke-width="0"></g><g stroke-linecap="round" stroke-linejoin="round" stroke="#0ea5e9" stroke-width="0.032"></g><g> <path d="M6 8L2 8L2 6L8 5.24536e-07L14 6L14 8L10 8L10 16L6 16L6 8Z" fill="#0ea5e9"></path> </g></svg>'
        }
        else{
            icon = '<svg width="20px" height="20px" viewBox="0 0 16.00 16.00" fill="none" xmlns="http://www.w3.org/2000/svg" transform="rotate(0)matrix(1, 0, 0, -1, 0, 0)" stroke="#ec4899"><g stroke-width="0"></g><g stroke-linecap="round" stroke-linejoin="round" stroke="#ec4899" stroke-width="0.032"></g><g> <path d="M6 8L2 8L2 6L8 5.24536e-07L14 6L14 8L10 8L10 16L6 16L6 8Z" fill="#ec4899"></path> </g></svg>'
        };

        html += fav_element(icon, item)
    }
    document.getElementById("favourite-list").innerHTML = html

    update_page()

}

// adds standard link functionality to an item
function add_link(){
    code = this.textContent.trim()
    dateFrom = document.getElementById("dateFrom").value    
    dateTo = document.getElementById("dateTo").value
    
    document.getElementById("current-ticker").value = code
    update_graph(code, dateTo, dateFrom)
}

// just an object that creates the fav list item
function fav_element(icon, item){
    let fav_item = '<tr class="border-y h-10 border-solid border-collapse border-slate-400 bg-slate-600 hover:bg-slate-700 stock-item">' + 
                        '<td class="ticker-code cursor-pointer">' + item["ticker"] + '</td>' + 
                        '<td>' + item["change"] + ' %' + icon +'</td>' +
                        '<td>' + 
                            '<form action="/favourite" method="get">' + 
                                '<input type="hidden" name="q" value="' + item["ticker"] + '">' + 
                                '<svg class="cursor-pointer remove_favourite" width="20px" height="20px" viewBox="0 0 24 24" fill="" xmlns="http://www.w3.org/2000/svg"><g> <path class="hover:stroke-slate-200" d="M6 12L18 12" stroke="#475569" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>' + 
                            '</form>' + 
                        '</td>'+
                    '</tr>'
    return fav_item
}