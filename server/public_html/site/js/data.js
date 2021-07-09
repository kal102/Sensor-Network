/**
 * data.js: script filling chart and table with data
 * uses query.php script to get records from database
 */

//get script attributes
var script = document.currentScript;
var dataType = script.getAttribute('dataType');
if (typeof dataType === "undefined" ) {
    throw new Error("No attribute dataType for script data.js!");
}
else {
    console.log("Data type attribute set to " + dataType)
}

//set variables
var deviceData;
if (dataType == 'humidity') {
    var chartTitle = "Wilgotność";
    var dataUnit = "%";
    var deviceListPath = "config/devices/humidity.txt";
}
else if (dataType == 'pressure') {
    var chartTitle = "Ciśnienie";
    var dataUnit = "hPa";
    var deviceListPath = "config/devices/pressure.txt";
}
else {
    var chartTitle = "Temperatura";
    var dataUnit = "°C";
    var deviceListPath = "config/devices/temperature.txt";
}

//get document elements
var minDate = document.getElementById("min_date");
var minTime = document.getElementById("min_time");
var maxDate = document.getElementById("max_date");
var maxTime = document.getElementById("max_time");
var errLabel = document.getElementById("date_error_label");

//run this code on load event
window.addEventListener("load",function(e){

    // create chart
    const timeFormat = "DD-MM-YYYY HH:mm";
    const chart = new CanvasJS.Chart("chartContainer", {
        animationEnabled: true,
        backgroundColor: "transparent",
        title:{
            text: chartTitle,
            fontSize: 20
        },
        axisX: {
            valueFormatString: timeFormat,
            labelFontSize: 14,
            interval: 1
        },
        axisY: {
            titleFontSize: 16,
            labelFontSize: 14,
            suffix: dataUnit
        },
        legend:{fontSize: 14},
        toolTip:{shared: false},
        data: []
    });
    chart.render();
    
    // set specific plot to chart
    function setPlot(idx,x,y){
        data = [];
        for(let i = 0;i < Math.min(x.length,y.length);i++){
            data.push({x:new Date(x[i]),y:y[i]})
        }
        chart.data[idx].set("dataPoints",data,false);
    }

    // filter data between dates
    function selectData(data,mind,maxd){
        let x = data[0];
        let y = data[1];
        let dx = [];
        let dy = [];
        for(let i = 0; i < x.length; i++){
            if(x[i] >= mind && x[i] <= maxd) {
                dx.push(x[i]);
                dy.push(y[i]);
            }
        }
        return [dx,dy];
    }

    // run when date was updated
    function updateDate(){
        let dmin = Date.parse(minDate.value + " " + minTime.value);
        let dmax = Date.parse(maxDate.value + " " + maxTime.value);

        if(Number.isNaN(dmin) || Number.isNaN(dmax)) {
            errLabel.style = "color:red;";
            errLabel.innerText = "Wybierz własciwy format daty.";
            dmin = dmax = NaN;
        } else if(dmin > dmax) {
            errLabel.style = "color:red;";
            errLabel.innerText = "Data \"Od\" nie może być większa od daty \"Do\".";
            dmin = dmax = NaN;
        } else {
            errLabel.style = "display:none;"
            errLabel.innerText = "";
        }

        if(!Number.isNaN(dmin)) {
            data = new Map();
            for(let[key,val] of deviceData) {
                data.set(key,selectData(val,dmin,dmax));
            }
        } else {
            data = deviceData;
        }

        for(let[key,val] of data) {
            let datasets = chart.data;
            let i = 0;
            for(; i < datasets.length; i++) {
                if(datasets[i].name === key) break;
            }
            setPlot(i, val[0], val[1]);
        }
        chart.render();
        console.log('Updated date range on chart.');
    }

    // main function executed on load
    async function main(){

        // asynchronious download of data files
        function loadFile(filePath){
            return new Promise((resolve, reject) => {
                let req = new XMLHttpRequest();
                req.open("GET", filePath, true);
                req.onload = function(e){
                    if(req.readyState == 4){
                        if(req.status == 200) resolve(req.responseText);
                        else reject(req.statusText);
                    }
                };
                req.onerror = function(e){ reject(req.statusText); };
                req.send(null);
            });
        }

        // parse device list
        var devices = [];
        for(let device of (await loadFile(deviceListPath)).split(/\r?\n/)) {
            if(device.trim().length != 0) {
                devices.push(device);
            }
        }
        console.log('Fetched list of devices.');

        // parse data record from DB 
        function parseDataRecord(record){
            let date = record['date'];
            let id = record['id'];
            var status = record['status'];
            let value = record[dataType];

            // check if record origins from device on list
            if (devices.includes(id)) {
                let singleDeviceData = deviceData.get(id);

                // check if any data already exists
                if (typeof singleDeviceData == 'undefined') {
                    var time = [];
                    var data = [];
                } else {
                    var time = singleDeviceData[0];
                    var data = singleDeviceData[1];
                }

                let d = Date.parse(date);
                let t = Number(value);

                if(status.includes("ok") && !Number.isNaN(d) && !Number.isNaN(t)) {
                    time.push(d);
                    data.push(t);
                    deviceData.set(id, [time, data]);									
                }
            }
        }

        // get and parse JSON from database
        deviceData = new Map();
        await $.getJSON('query.php?value=' + dataType, function(data) {
            $.each(data, function( index ) {
                let record = data[index];
                parseDataRecord(record);
            });
            console.log('Fetched data records from database.');
        });
        
        // set data and render chart
        dataArray = [];
        for(let [key,value] of deviceData){
            dataArray.push({
                name: key,
                xValueFormatString: timeFormat,
                yValueFormatString: "0.00",
                type: "line",
                showInLegend: true,
                legendText: "Urządzenie " + key,
                dataPoints: []
            })
        }
        chart.set("data",dataArray,false);
        chart.render();
        console.log('Chart generated.');

        // set initial data range
        var timezoneOffset = (new Date()).getTimezoneOffset() * 60000;
        var currentDateTime = new Date(Date.now() - timezoneOffset);
        maxDate.value = currentDateTime.toISOString().substr(0, 10);
        maxTime.value = currentDateTime.toISOString().substr(11, 5);

        var previousDateTime = new Date(currentDateTime.getTime() - 24 * 60 * 60000);
        minDate.value = previousDateTime.toISOString().substr(0, 10);
        minTime.value = previousDateTime.toISOString().substr(11, 5);

        updateDate();
        
        // table update
        deviceList = Array.from(deviceData.keys());
        deviceValues = Array.from(deviceData.values());

        // table generator
        function CreateTable(table, deviceList, deviceValues){
            for(i=0; i<deviceList.length; i++){
                var row = table.insertRow();
                row.className += "table-row";
                row.insertCell();
                row.insertCell();
                row.insertCell();
            }
            tds = document.querySelectorAll("td");
            for (let j = 1; j < tds.length; j++) {
                if (j % 3 == 1) {
                    tds[j].className += "devices";
                }
                else if (j % 3 == 2) {
                    tds[j].className += "values";
                }
                else {
                    tds[j].className += "dates";
                }
            }
            devices = document.querySelectorAll(".devices");
            values = document.querySelectorAll(".values");
            dates = document.querySelectorAll(".dates");
            for(k = 0; k < deviceList.length; k++){
                devices[k].textContent = deviceList[k];
                values[k].textContent = deviceValues[k][1][deviceValues[k][1].length-1].toString();
                var date = new Date(deviceValues[k][0][deviceValues[k][0].length-1]);
                dates[k].textContent = date.toLocaleString();
            }
        }

        table = document.getElementById("table");
        CreateTable(table, deviceList, deviceValues);
        console.log('Generated table with data records.');
    }
    
    //setup events
    minDate.onchange = updateDate;
    minTime.onchange = updateDate;
    maxDate.onchange = updateDate;
    maxTime.onchange = updateDate;

    //run main
    main();
});
