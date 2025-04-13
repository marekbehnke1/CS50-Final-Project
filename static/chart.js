function drawChart(chartData, code){

    var options = {
        legend: 'none',
        title: code,
        bar: {groupWidth: '100%'},
        candlestick: {
            fallingColor: {strokeWidth: 0, fill: '#a52714'},
            risingColor: {strokWidth: 0, fill: '#0f9d58'},
        },
        backgroundColor: {fill: '#334155'} 
    };
    
    var chart = new google.visualization.CandlestickChart(document.getElementById("main-chart"));
    var data = new google.visualization.DataTable(chartData, 0.6);
    chart.draw(data, options);
};