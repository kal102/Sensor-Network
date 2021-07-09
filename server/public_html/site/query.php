<?php

// Get parameters
$value = $_GET["value"];
$from = $_GET["from"];
$to = $_GET["to"];

// Get configuration
$cfg = include('/home/eaiibgrp/lkalina/config/config.php');

// Create connection
$conn = new mysqli($cfg['host'], $cfg['username'], $cfg['password'], $cfg['db']);
$conn->set_charset("utf8");

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

// Create query
if ($value == "status") {
  $sql = "SELECT date, id, status, ip, fails FROM sensors ORDER BY date DESC LIMIT 100";
}
else if ($value == "location") {
  $sql = "SELECT date, id, status, latitude, longitude FROM sensors ORDER BY date DESC LIMIT 100";
}
else {
  if ($from && $to) {
    $sql = "SELECT date, id, status, $value FROM sensors WHERE date > ".$from." AND date < ".$to." ORDER BY date ASC";
  }
  else {
    $sql = "SELECT date, id, status, $value FROM sensors ORDER BY date ASC";
  }
}

// Run query
$result = $conn->query($sql);

// Put data in array
$to_encode = array();
if ($result->num_rows > 0) {
  // output data of each row
  while($row = $result->fetch_assoc()) {
    $to_encode[] = $row;
  }
}

// Return JSON from array
$conn->close();
echo(json_encode($to_encode));
?> 
