<?php

if(!isset($_POST['label']) || !isset($_POST['statement_id']) || 
	!isset($_POST['news_id']) || !isset($_POST['user_id'])){
	$return_value = array();
	$return_value['success'] = FALSE;
	echo json_encode($return_value);
	exit();
}

$label = $_POST['label'];
$statement_id = $_POST['statement_id'];
$news_id = $_POST['news_id'];
$user_id = $_POST['user_id'];

require_once('connect.php');

$query = 
"INSERT INTO `statement_news`(statement_id, news_id, label, labeler) VALUES(?,?,?,?)";

/* prepare statements*/
if (!($stmt = $mysqli->prepare($query))) {
    echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    $success=FALSE;
}

$success=TRUE;
if (!$stmt->bind_param("ssss", $statement_id, $news_id, $label, $user_id)) {
    echo "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

if (!$stmt->execute()) {
    echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

/* explicit close recommended */
$stmt->close();

$return_value= array();
$return_value['success']= $success;
echo json_encode($return_value);

?>