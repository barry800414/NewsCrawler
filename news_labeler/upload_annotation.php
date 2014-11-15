<?php

if( !isset($_POST['user_valid_format_label']) ||
    !isset($_POST['user_relevance_label']) ||
    !isset($_POST['user_mention_pos_label']) ||
    !isset($_POST['user_mention_neg_label']) ||
    !isset($_POST['user_label']) || !isset($_POST['statement_id']) || 
	!isset($_POST['news_id']) || !isset($_POST['user_id'])){
	$return_value = array();
	$return_value['success'] = FALSE;
	echo json_encode($return_value);
	exit();
}

$valid_format = $_POST['user_valid_format_label'];
$relevance = $_POST['user_relevance_label'];
$mention_agree = $_POST['user_mention_pos_label'];
$mention_disagree = $_POST['user_mention_neg_label'];
$label = $_POST['user_label'];
$statement_id = $_POST['statement_id'];
$news_id = $_POST['news_id'];
$user_id = $_POST['user_id'];

require_once('connect.php');

$query = 
"INSERT INTO `statement_news`(statement_id, news_id, valid_format, relevance, mention_agree, mention_disagree, label, labeler) VALUES(?,?,?,?,?,?,?,?)";

/* prepare statements*/
if (!($stmt = $mysqli->prepare($query))) {
    echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    $success=FALSE;
}

$success=TRUE;
if (!$stmt->bind_param("ssssssss", $statement_id, $news_id, $valid_format, $relevance, $mention_agree, $mention_disagree, $label, $user_id)) {
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
