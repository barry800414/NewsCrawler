<?php

function fail(){
    $r = array();
	$r['success'] = FALSE;
	echo json_encode($r);
	exit();
}

if(!isset($_POST['user_id'])){
    fail();
}
else{
    $user_id = $_POST['user_id'];
}

require_once('load_functions.php');

$labeled_num = get_labeled_num($_POST['user_id']);
$total_labeled_length = get_label_content_length($_POST['user_id']);
if($labeled_num != NULL && $total_labeled_length != NULL){
    $r = array();
    $r['labeled_num'] = $labeled_num;
    $r['total_labeled_length'] = $total_labeled_length;
    $r['success'] = TRUE;  
    echo json_encode($r);
}
else{
    fail();
}

?>
