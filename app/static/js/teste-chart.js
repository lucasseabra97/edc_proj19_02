//Get data from page
var dataSpan = document.getElementById("dataSpan").innerHTML;
dataSpan = JSON.parse(dataSpan);

var title = document.getElementById("titleSpan").innerHTML;

var myChart;
var ctx = document.getElementById("chart");
//Default chart config
var config = {
    type: 'pie',
    data: {
        labels: Object.keys(dataSpan).slice(0,20),
        datasets: [{
            data: Object.values(dataSpan).slice(0,20),
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255,99,132,1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        title: {
            display: true,
            text: title
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
    if(newType == "bar"){
        temp.options.scales = {
            yAxes: [{
                display: true,
                ticks: {
                    beginAtZero: true   // minimum value will be 0.
                }
            }]
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

