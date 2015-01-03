<?php

function fail(){
    $return_value = array();
	$return_value['success'] = FALSE;
	echo json_encode($return_value);
	exit();
}

if(!isset($_POST['user_id'])){
    fail();
}
else{
    $user_id = $_POST['user_id'];
}

require_once('connect.php');

/**get the labeled number**/
$query = "SELECT COUNT(id) FROM `statement_news` WHERE labeler=?";
$success=TRUE;
if (!($stmt = $mysqli->prepare($query))) {
    echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    $success=FALSE;
}

if (!$stmt->bind_param("s", $user_id)) {
    echo "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

if (!$stmt->execute()) {
    echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}
$labeled_num=0;
if (!$stmt->bind_result($labeled_num)) {
    echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

$stmt->fetch();
$stmt->close();

if(!$success){
    fail();
}


/*load total length of contents*/
$query = "SELECT SUM(C.length) 
          FROM (SELECT CHAR_LENGTH(B.content) as length 
                    FROM `statement_news` as A, `merge_necessary` as B 
                    WHERE A.news_id = B.id AND labeler=?) as C";

$success=TRUE;
if (!($stmt = $mysqli->prepare($query))) {
    echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    $success=FALSE;
}

if (!$stmt->bind_param("s", $user_id)) {
    echo "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

if (!$stmt->execute()) {
    echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}
$total_labeled_length=0;
if (!$stmt->bind_result($total_labeled_length)) {
    echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

$stmt->fetch();
$stmt->close();

if($success){
    $return_value = array();
    $return_value['labeled_num'] = $labeled_num;
    $return_value['total_labeled_length'] = $total_labeled_length;
    $return_value['success'] = TRUE;    
}
else{
    fail();
}
echo json_encode($return_value);

?>
