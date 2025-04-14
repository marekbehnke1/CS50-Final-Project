function drawChart(chartData, code){

    var options = {
        legend: 'none',
        title: code,
        titleTextStyle: {color: 'white'},
        bar: {groupWidth: '100%'},
        candlestick: {
            fallingColor: {stroke: 'white', strokeWidth: 0, fill: '#ec4899'},
            risingColor: {stroke: 'white', strokeWidth: 0, fill: '#0ea5e9'},
        },
        backgroundColor: {fill: '#334155'}, 

        hAxis: {
                gridlines: {color: 'white'},
                minorGridlines: {color: 'white'},
                textStyle: {color: 'white'}
            },

        vAxis: {
                gridlines: {color: 'white'},
                textStyle: {color: 'white'}
            }
    };
    
    var chart = new google.visualization.CandlestickChart(document.getElementById("main-chart"));
    var data = new google.visualization.DataTable(chartData, 0.6);
    chart.draw(data, options);
};

async function updateChart(code, dateTo, dateFrom) {
    let response = await fetch('/chart?q=' + code +'&to=' + dateTo + '&from=' + dateFrom)

    let chartData = await response.json()
    drawChart(chartData, code)
}