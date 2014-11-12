<?php

//todo 


//connect to db
$mysqli = new mysqli("localhost", "news_crawler", "news_crawler", "news_crawler", 3306);
if ($mysqli->connect_errno) {
    echo "Failed to connect to MySQL: (" . $mysqli->connect_errno . ") " . $mysqli->connect_error;
    $success=FALSE;
}

if(!$mysqli->set_charset("utf8")){
    echo "Error loading character set utf8".$mysqli->error;
    $success=FALSE;
}


?>
