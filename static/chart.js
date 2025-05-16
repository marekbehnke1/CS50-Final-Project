function drawChart(chartData, code, name){

    var options = {
        //width: 300,
        //height: 200,
        chartArea: {
            left: '10%',
            right:'10%',
            top: '10%',
            height: '75%'
        },
        legend: 'none',
        title: name+': '+code,
        titleTextStyle: {color: 'white'},
        bar: {groupWidth: '100%'},
        candlestick: {
            fallingColor: {stroke: 'white', strokeWidth: 0, fill: '#ec4899'},
            risingColor: {stroke: 'white', strokeWidth: 0, fill: '#0ea5e9'},
        },
        backgroundColor: {fill: 'transparent'}, 

        hAxis: {
                gridlines: {color: 'white'},
                minorGridlines: {color: 'white'},
                textStyle: {color: 'white'}
            },

        vAxis: {
                gridlines: {color: 'white'},
                textStyle: {color: 'white'}
            },
        titleTextStyle: {
                color: "white",
                fontName: "Raleway",
                bold: true,
                fontSize: 20
        }
    };
    
    var chart = new google.visualization.CandlestickChart(document.getElementById("main-chart"));
    var data = new google.visualization.DataTable(chartData, 0.6);
    chart.draw(data, options);
};