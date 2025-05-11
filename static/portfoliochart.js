async function portfolioGraph() {
    
    let graph_list = document.getElementsByClassName("portfolio_graph")
    
    for (item of graph_list){
        let response = await fetch("/portfoliograph?code=" + item.id)
        let graphData = await response.json()
        
        draw_port_graph(graphData, item.id)
    }

}

function draw_port_graph(graphData, code){

    var options = {
        curveType: 'function',
        legend: 'none',
        hAxis: {
            gridlines: {color: 'white'},
            minorGridlines: {color: 'white'},
            textStyle: {color: 'white'}
        },

        vAxis: {
            gridlines: {color: 'white'},
            textStyle: {color: 'white'}
        },
        backgroundColor: {fill: 'transparent'},
        crosshair: {
            trigger: 'focus',
            color: 'green'
        },
        hAxis: {
            textStyle: {color: 'none'},
        },
        vAxis: {
                gridlines: {color: 'none'},
                textStyle: {color: 'none'},

            },
        series: {
            0: {color: '#be185d'}
        }
    };

    var chart = new google.visualization.LineChart(document.getElementById(code));
    var data = new google.visualization.DataTable(graphData, 0.6);
    chart.draw(data, options)
}