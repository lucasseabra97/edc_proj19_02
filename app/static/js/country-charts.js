function createChart(chart, ctx, type, labels, data, title, yAxe){
    var config = {type: type,
    data: {
        labels: labels,
        datasets: [{
            data: data,
            backgroundColor: [
            ],
            borderColor: [
                'rgba(0,0,0,1)'
            ],
            borderWidth: 1,
            fill: false
        }]
    },
    options: {
        legend: {
            display: false,
        },
        title: {
            display: true,
            text: title
        },
        scales: {
            yAxes: [{
                display: true,
                ticks: {
                    beginAtZero: true   // minimum value will be 0.
                },
                scaleLabel: {
                    display: true,
                    labelString: yAxe
                  }
            }],
            xAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'year'
                  }
            }]
        }
    }}
    var chart = new Chart(ctx, config);
    chart.responsive = true;
}

var dataSpan_infla = document.getElementById("dataSpan_infla").innerHTML;
dataSpan_infla = JSON.parse(dataSpan_infla);
var title_infla = document.getElementById("titleSpan_infla").innerHTML;
var type_infla = document.getElementById("typeSpan_infla").innerHTML;
var yAxe_infla = document.getElementById("yAxeSpan_infla").innerHTML;

var myChart_infla;
var ctx_infla = document.getElementById("chart_infla");
ctx_infla.height = 100

createChart(myChart_infla, ctx_infla, type_infla, Object.keys(dataSpan_infla), Object.values(dataSpan_infla), title_infla, yAxe_infla)

var dataSpan_pop = document.getElementById("dataSpan_pop").innerHTML;
dataSpan_pop = JSON.parse(dataSpan_pop);
var title_pop = document.getElementById("titleSpan_pop").innerHTML;
var type_pop = document.getElementById("typeSpan_pop").innerHTML;
var yAxe_pop = document.getElementById("yAxeSpan_pop").innerHTML;

var myChart_pop;
var ctx_pop = document.getElementById("chart_pop");
ctx_pop.height = 100

createChart(myChart_pop, ctx_pop, type_pop, Object.keys(dataSpan_pop), Object.values(dataSpan_pop), title_pop, yAxe_pop)
