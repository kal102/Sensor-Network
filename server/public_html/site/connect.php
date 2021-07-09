<?php

// Get parameters
$protocol = $_POST["protocol"];
$ip = $_POST["ip"];
$port = $_POST["port"];

$url = $protocol."://".$ip.":".$port;

header("Location: ".$url);
exit();
?>