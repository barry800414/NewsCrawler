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
require_once('connect.php');
require_once('check_login.php');

function check_labeled($statement_id, $news_id, $user_id){
    global $mysqli;
    $query =
    "SELECT COUNT(*) FROM `statement_news` WHERE statement_id=? AND news_id=? AND labeler=?";
    if (!($stmt = $mysqli->prepare($query))) {
        echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    }
    

    if (!$stmt->bind_param("sss", $statement_id, $news_id, $user_id)) {
        echo "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
    }

    if (!$stmt->execute()) {
        echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    }
    $num = NULL;
    if (!$stmt->bind_result($num)) {
        echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
    }

    $stmt->fetch();
    if($num == 0){
        return TRUE;
    }
    else{
        return FALSE;
    }
}

function load_a_statement_news(){
    global $mysqli;
    $query =
	"SELECT diff, statement_id, news_id 
	FROM `FINAL_TABLE` 
	WHERE diff = (SELECT MAX(diff) FROM `FINAL_TABLE`) 
    order by rand() LIMIT 0, 1";
    if (!($stmt = $mysqli->prepare($query))) {
        echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    }
    if (!$stmt->execute()) {
        echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    }

    $diff = NULL;
    $news_id = NULL;
    $statement_id = NULL;
    if (!$stmt->bind_result($diff, $statement_id, $news_id)){
        echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
    }

    $stmt->fetch();
    if($news_id != NULL && $statement_id != NULL){
        $r = array();
        $r['diff'] = $diff;
        $r['statement_id'] = $statement_id;
        $r['news_id'] = $news_id;
        return $r;
    }
    else{
        return NULL;
    }
}

/*Get a piece of news-statement*/
function get_content($statement_id, $news_id, $remain_num){
    global $mysqli;
    $query =
    "SELECT 
        C.topic_id, D.name, C.content as statement,
        B.title as news_title, B.content as news_content, 
        B.url as news_url 
    FROM merge as B, statement as C, topic as D
    WHERE 
        B.id = ? AND C.id = ? AND D.id = C.topic_id";
    $success=TRUE;
    if (!($stmt = $mysqli->prepare($query))) {
        echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
        $success=FALSE;
    }
    if (!$stmt->bind_param("ss", $news_id, $statement_id)) {
        echo "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
        $success=FALSE;
    }
    if (!$stmt->execute()) {
        echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
        $success=FALSE;
    }

    $topic_id = NULL;
    $topic_name = NULL;
    $statement = NULL;
    $news_title = NULL;
    $news_content = NULL;
    $news_url = NULL;
    if (!$stmt->bind_result($topic_id, $topic_name, $statement, 
        $news_title, $news_content, $news_url)) {
        echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
        $success=FALSE;
    }

    $stmt->fetch();

    if($success){
        $data = array();
        $data['remain_num'] = $remain_num;
        $data['topic_id'] = $topic_id;
        $data['topic_name'] = $topic_name;
        $data['statement_id'] = $statement_id;
        $data['statement'] = $statement;
        $data['news_id'] = $news_id;
        $data['news_title'] = $news_title;
        $data['news_content'] = $news_content;
        $data['news_url'] = $news_url;
        return $data;
    }
    else{
        return NULL;
    }
}

/*Get a piece of news-statement that not label before*/
$diff = NULL;
$statement_id = NULL;
$news_id = NULL;
$remain_trial = 100;
$data = NULL;


while($statement_id == NULL || $news_id == NULL){
    $r = load_a_statement_news();

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


