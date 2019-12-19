//Get data from page
var dataSpan = document.getElementById("dataSpan").innerHTML;
dataSpan = JSON.parse(dataSpan);
var title = document.getElementById("titleSpan").innerHTML;
var type = document.getElementById("typeSpan").innerHTML;

var myChart;
var ctx = document.getElementById("chart");

var config = {
    type: 'bar',
    data: {
        labels: Object.keys(dataSpan).slice(0,20),
        datasets: [{
            data: Object.values(dataSpan).slice(0,20),
            backgroundColor: [
            ],
            borderColor: [
            ],
            borderWidth: 1
        }]
    },
    options: {
        title: {
            display: true,
            text: title
        },
        scales: {
            yAxes: [{
                display: true,
                ticks: {
                    beginAtZero: true   // minimum value will be 0.
                }
            }]
        }
    }
}

//Create default chart
var myChart = new Chart(ctx, config);
myChart.responsive = true;

function changeChart(newType) {
    // Remove the old chart and all its event handles
    if (myChart) {
        myChart.destroy();
    }
    // Chart.js modifies the object you pass in. Pass a copy of the object so we can use the original object later
    var temp = jQuery.extend(true, {}, config);
    temp.type = newType;
    if(newType == "pie"){
        temp.options = {
            title: {
                display: true,
                text: title
            }
        }
    }
    myChart = new Chart(ctx, temp);
    myChart.responsive = true;
}

function setEventListeners(){
    var bar = document.getElementById("bar");
    bar.addEventListener('click', () => {changeChart('bar')});

    var bar = document.getElementById("pie");
    bar.addEventListener('click', () => {changeChart('pie')});
}


setEventListeners();

