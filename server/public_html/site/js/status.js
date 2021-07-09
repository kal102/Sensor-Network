/**
 * status.js: script updating active devices table
 * uses query.php script to get records from database
 */

//get script attributes
var script = document.currentScript;
var fillForm = script.getAttribute('fillForm');
if (typeof fillForm !== "undefined" ) {
    console.log("Attribute fillForm set.");
}

//run this code on load event
window.addEventListener("load",function(e){
    var deviceList = [];
    var deviceValues = [];

    // update form
    function UpdateConnectForm(){
        var device = document.getElementById("device").value;
        var idx = deviceList.indexOf(device);
        if (typeof deviceValues[idx] != "undefined" ) {
            if (deviceList[idx].includes("rb")) {
                document.getElementById("protocol").value = "https";
                document.getElementById("port").value = 8080;
            }
            else {
                document.getElementById("protocol").value = "http";
                document.getElementById("port").value = 8081;
            }
            document.getElementById("ip").value = deviceValues[idx][2];
            console.log("Updated connect form fields.");
        }
    }

    // main function executed on load
    async function main(){
        var deviceData = new Map();

        // parse data record from DB 
        function parseDataRecord(record){
            var date = record['date'];
            var id = record['id'];
            var status = record['status'];
            var ip = record['ip'];

            // check if any data already exists
            var singleDeviceData = deviceData.get(id);
            if (typeof singleDeviceData === 'undefined') {

                // check if data is correct
                if (status.includes("ok")) {

                    // save coordinates
                    deviceData.set(id, [date, status, ip]);
                }
            }
        }

        // get and parse JSON from database
        await $.getJSON('query.php?value=status', function(data) {
            $.each(data, function( index ) {
                let record = data[index];
                parseDataRecord(record);
            });
            console.log('Fetched data records from database.');
        });

        deviceList = Array.from(deviceData.keys());
        deviceValues = Array.from(deviceData.values());

        // fill connect form
        function FillConnectForm(){

            document.getElementById("device").options.length = 0;

            for(i = 0; i < deviceList.length; i++){
                let option = document.createElement("option");
                option.text = deviceList[i];
                option.value = deviceList[i];

                let select = document.getElementById("device");
                select.appendChild(option);
            }

            if (deviceList[0].includes("rb")) {
                document.getElementById("protocol").value = "https";
                document.getElementById("port").value = 8080;
            }
            else {
                document.getElementById("protocol").value = "http";
                document.getElementById("port").value = 8081;
            }
            document.getElementById("device").value = deviceList[0];
            document.getElementById("ip").value = deviceValues[0][2];
        }

        if (fillForm) {
            form = document.getElementById("connect");
            FillConnectForm();
            console.log('Filled connect form fields.');    
        }    

        // table generator
        function CreateTable(table, deviceList, deviceValues){

            for(i = 0; i < deviceList.length; i++){
                var row = table.insertRow();
                row.className += "table-row";
                row.insertCell();
                row.insertCell();
                row.insertCell();
                row.insertCell();
            }
            
            tds = document.querySelectorAll("td");
            for (let j = 0; j < tds.length; j++) {
                if (j % 4 == 0) {
                    tds[j].className += "devices";
                }
                else if (j % 4 == 1) {
                    tds[j].className += "statuses";
                }
                else if (j % 4 == 2) {
                    tds[j].className += "ips";
                }
                else {
                    tds[j].className += "dates";
                }
            }
            devices = document.querySelectorAll(".devices");
            statuses = document.querySelectorAll(".statuses");
            ips = document.querySelectorAll(".ips");
            dates = document.querySelectorAll(".dates");

            for(k = 0; k < deviceList.length; k++){
                devices[k].textContent = deviceList[k];
                statuses[k].textContent = deviceValues[k][1];
                ips[k].textContent = deviceValues[k][2];
                dates[k].textContent = deviceValues[k][0];
            }
        }

        table = document.getElementById("table");
        CreateTable(table, deviceList, deviceValues);
        console.log('Generated table with data records.');
    }
    
    if (fillForm) {
        document.getElementById("device").addEventListener("change", function (evt) {
            UpdateConnectForm();
        }, false)
    }

    main();
});
