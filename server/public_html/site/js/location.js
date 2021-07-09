/**
 * location.js: script setting device markers on Google map
 * uses query.php script to get records from database
 */

// set global variables
var markers = {};

// initialize and add the map
async function initMap() {
    var deviceData = {};

    // generate map
    const cracow = { lat: 50.061921094894345, lng: 19.93675658488488 };
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: cracow,
    });
    console.log('Map initialized.')

    // convert coordinates to decimal format
    function convertDMToDD(degrees, minutes, direction) {
        var dd = Number(degrees) + Number(minutes)/60;
    
        if (direction == "S" || direction == "W") {
            dd = dd * -1;
        }
        return dd;
    }

    // parse data record from DB 
    function parseDataRecord(record){
        var id = record['id'];
        var status = record['status'];
        var latitude = record['latitude'];
        var longitude = record['longitude'];

        // parse coordinates
        var parts = latitude.split(/[^\d\w]+/);
        var lati = convertDMToDD(parts[0], parts[1] + '.' + parts[2], parts[3]);

        var parts = longitude.split(/[^\d\w]+/);
        var long = convertDMToDD(parts[0], parts[1] + '.' + parts[2], parts[3]);

        // check if any data already exists
        var singleDeviceData = deviceData[id];
        if (typeof singleDeviceData == 'undefined') {

            // check if data is correct
            if (!status.includes("gps error") && !Number.isNaN(lati) && !Number.isNaN(long)) {

                // save coordinates
                deviceData[id] = [lati, long];
            }
        }
    }

    // get and parse JSON from database
    await $.getJSON('query.php?value=location', function(data) {
        $.each(data, function( index ) {
            let record = data[index];
            parseDataRecord(record);
        });
        console.log('Fetched data records from database.');
    });

    // set device markers on map
    for (var id in deviceData) {
        let pos = { lat: deviceData[id][0], lng: deviceData[id][1] };
        markers[id] = new google.maps.Marker({
            position: pos,
            label: id,
            map: map,
        });       
    }
}