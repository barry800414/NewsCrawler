<?php 
ini_set('default_charset', 'utf8');
header('Content-Type: text/html; charset=utf-8');

$success=TRUE;

//connect to db
require_once('connect.php');

/*topic*/
$query = "SELECT id, name FROM topic";
if (!($stmt = $mysqli->prepare($query))) {
    echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    $success=FALSE;
}

if (!$stmt->execute()) {
    echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

$topic_array = array();
$topic_id = NULL;
$topic = NULL;
if (!$stmt->bind_result($topic_id, $topic)) {
    echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
}
while ($stmt->fetch()) {
    array_push($topic_array, array('topic_id' => $topic_id, 'value' => $topic) );
}


/* explicit close recommended */
$stmt->close();

if($success){
    $result = array();
    $result['topic'] = $topic_array;
    $result['success'] = TRUE; 
    echo json_encode($result);
}
else{
    $result = array();
    $result['success'] = FALSE;
    echo json_encode($result);
}




?>
