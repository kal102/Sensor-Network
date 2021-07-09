<?php

// Get authentication details
$id   = $_GET["id"];
$pass = $_GET["pass"];

// Get data
$date = $_POST["date"];
$stat = $_POST["stat"];
$temp = $_POST["temp"];
$humi = $_POST["humi"];
$pres = $_POST["pres"];
$lati = $_POST["lati"];
$long = $_POST["long"];
$fail = $_POST["fail"];

// Convert encoding
$lati = utf8_decode($lati);
$long = utf8_decode($long);

// Escape forbidden characters
$lati = str_replace('\'', '\'\'', $lati);
$long = str_replace('\'', '\'\'', $long);

// Get device IP
$ip = $_SERVER['REMOTE_ADDR'];

// Get server timestamp
$tmsp = date('Y-m-d H:i:s');

// Set default values
if (! $temp) {
    $temp = '0.0';
}
if (! $humi) {
    $humi = '0.0';
}
if (! $pres) {
    $pres = '0.0';
}
if (! $fail) {
    $fail = 0;
}

// Get configuration and devices list
$cfg = include('/home/eaiibgrp/lkalina/config/config.php');
$devices = include('/home/eaiibgrp/lkalina/config/devices.php');

// Authenticate device
if (array_key_exists($id, $devices)) {
    if ($pass == $devices[$id]) {
        echo "Device authenticated\n";
    } else {
        die("Authentication error");  
    }
} else {
    die("Authentication error");
}

// Create connection
$conn = new mysqli($cfg['host'], $cfg['username'], $cfg['password'], $cfg['db']);
// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

$sql = "INSERT INTO sensors (timestamp, date, id, status, ip, temperature, humidity, pressure, latitude, longitude, fails) 
            VALUES ('$tmsp', '$date', '$id', '$stat', '$ip', '$temp', '$humi', '$pres', '$lati', '$long', '$fail')";

if ($conn->query($sql) === TRUE) {
    echo "New record created successfully\n";
} else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}
  
$conn->close();
?> 
