<?php 
ini_set('default_charset', 'utf8');
ini_set('log_errors', 1);
ini_set('error_log', '/home/r02922010/www/error.log');
error_reporting(E_ALL);
ini_set('display_errors', 1);
header('Content-Type: text/html; charset=utf-8');


$success=TRUE;

//connect to db
$mysqli = new mysqli("localhost", "r02922010", "r02922010", "r02922010", 3306);
if ($mysqli->connect_errno) {
    echo "Failed to connect to MySQL: (" . $mysqli->connect_errno . ") " . $mysqli->connect_error;
    $success=FALSE;
}
if(!$mysqli->set_charset("utf8")){
    echo "Error loading character set utf8".$mysqli->error;
    $success=FALSE;
}

/*statement*/
$query = "SELECT DISTINCT(statement) from corpus_tw";
if (!($stmt = $mysqli->prepare($query))) {
    echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    $success=FALSE;
}

if (!$stmt->execute()) {
    echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

$statement_array = array();
$statement = NULL;
if (!$stmt->bind_result($statement)) {
    echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
}
while ($stmt->fetch()) {
    array_push($statement_array, $statement);
}


/*author*/
$query = "SELECT DISTINCT(author) from corpus_tw";
if (!($stmt = $mysqli->prepare($query))) {
    echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    $success=FALSE;
}

if (!$stmt->execute()) {
    echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

$author_array = array();
$author = NULL;
if (!$stmt->bind_result($author)) {
    echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
}
while ($stmt->fetch()) {
    array_push($author_array, $author);
}


/* source */
$query = "SELECT DISTINCT(source) from corpus_tw";
if (!($stmt = $mysqli->prepare($query))) {
    echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    $success=FALSE;
}

if (!$stmt->execute()) {
    echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

$source_array = array();
$source = NULL;
if (!$stmt->bind_result($source)) {
    echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
}
while ($stmt->fetch()) {
    array_push($source_array, $source);
}


/* explicit close recommended */
$stmt->close();

if($success){
    $result = array();
    $result['success'] = TRUE;
    $result['statement'] = $statement_array; 
    $result['author'] = $author_array;
    $result['source'] = $source_array;
    echo json_encode($result);
}
else{
    $result = array();
    $result['success'] = FALSE;
    echo json_encode($result);
}




?>
