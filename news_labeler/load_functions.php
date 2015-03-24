<?php

require_once('connect.php');
require_once('check_login.php');

/* older version: load a statement news by randomly sample available 
 * statement news, then check whether the user has labeled it or not
 * It is better to use it when the user label fewer data */
function load_a_statement_news_fewer(){
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

//check whether the user has labeled the statement news or not
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



/*new version: direct use set operation to find the 
 * available statement news. It's better to use it
 * when user has labeled lots of data
 * */
function load_a_statement_news_more($user_id){
    global $sep;
    $labeled = load_labeled_statement_news($user_id);
    $toLabel = load_toLabel_statement_news();

    $candidate = array_diff($toLabel, $labeled);
    if(count($candidate) == 0){
        return NULL;
    }
    else{
        //randomly select on statement news
        $r = array_rand($candidate);
        $tmp = explode($sep, $candidate[$r]);
        return array('statement_id' => $tmp[0], 'news_id' => $tmp[1]);
    }
}

$sep = '#$#$#$#';
//load all statement news that the user labeled
function load_labeled_statement_news($user_id){
    global $mysqli, $sep;
    $query = 
        "SELECT statement_id, news_id FROM `statement_news` WHERE labeler=? GROUP BY statement_id, news_id";
    if (!($stmt = $mysqli->prepare($query))) {
        echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    }
    if (!$stmt->bind_param("s", $user_id)) {
        echo "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
    }
    if (!$stmt->execute()) {
        echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    }
    $statement_id = NULL;
    $news_id = NULL;
    if (!$stmt->bind_result($statement_id, $news_id)) {
        echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
    }

    $stat_news_list = array();
    while($stmt->fetch()){
        array_push($stat_news_list, $statement_id.$sep.$news_id); //concate it into string
    }
    return $stat_news_list;   
}

//load all statement news that now should be labeled
function load_toLabel_statement_news(){
    global $mysqli, $sep;
    $query =
	"SELECT diff, statement_id, news_id 
	 FROM `FINAL_TABLE` 
	 WHERE diff = (SELECT MAX(diff) FROM `FINAL_TABLE`)";

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

    $stat_news_list = array();
    while($stmt->fetch()){
        array_push($stat_news_list, $statement_id.$sep.$news_id);
    }   
    return $stat_news_list;
    
}



/*Get a piece of news-statement*/
function get_content($statement_id, $news_id, $remain_num){
    global $mysqli;
    $query =
    "SELECT 
        C.topic_id, D.name, C.content as statement,
        B.title as news_title, B.content as news_content, 
        B.url as news_url 
    FROM merge_necessary as B, statement as C, topic as D
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


function get_labeled_num($user_id){
    global $mysqli;

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

    if($success){
        return $labeled_num;
    }
    else{
        return NULL;
    }
}


function get_label_content_length($user_id){
    global $mysqli;
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
        return $total_labeled_length;
    }
    else{
        return NULL;
    }

}


?>
