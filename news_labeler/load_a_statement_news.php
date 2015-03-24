<?php

function fail(){
    $return_value = array();
	$return_value['success'] = FALSE;
	echo json_encode($return_value);
	exit();
}

# check the input
if(!isset($_POST['user_id'])){
    fail();
}
if(strlen($_POST['user_id'])==0){
    fail();
}

require_once('load_functions.php');

/*Get a piece of news-statement that not label before*/
$diff = NULL;
$statement_id = NULL;
$news_id = NULL;
$data = NULL;
$labeled_num = get_labeled_num($_POST['user_id']);
//if user only label few data
if($labeled_num < 200){
    $remain_trial = 100;
    while($statement_id == NULL || $news_id == NULL){
        $r = load_a_statement_news_fewer();

        if($r != NULL){

            if(check_labeled($r['statement_id'], $r['news_id'], $_POST['user_id'])){
                $data = get_content($r['statement_id'], $r['news_id'], $r['diff']);
                break;
            }    
        }
        else{
            fail();
        }
        $remain_trial = $remain_trial - 1;
        if($remain_trial <= 0){
            fail();
        }
    }
}
//otherwise
else{
    $stat_news = load_a_statement_news_more($_POST['user_id']);
    if($stat_news == NULL){
        fail();
    }
    else{
        $data = get_content($stat_news['statement_id'], $stat_news['news_id'], 0);
    }
}


if($data != NULL){
    $return_value = array();
    $return_value['data'] = $data;
    $return_value['success'] = TRUE;
    echo json_encode($return_value);
}
else{
    fail();
}
 

?>


