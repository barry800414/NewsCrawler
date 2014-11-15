<?php


require_once('connect.php');


$query = 
"";

$query =
"SELECT 
	A.diff, C.topic_id, D.name, C.id as statement_id,
	C.content as statement, B.id as news_id, 
    B.title as news_title, B.content as news_content, 
	B.url as news_url 
FROM (
	SELECT diff, statement_id, news_id 
	FROM `FINAL_TABLE` 
	WHERE diff = (SELECT MAX(diff) FROM `FINAL_TABLE`) 
	order by rand()) as A, merge as B, statement as C, topic as D
WHERE 
	B.id = A.news_id AND A.statement_id = C.id AND D.id = C.topic_id";

//echo $query;

$success=TRUE;
/*statement*/
if (!($stmt = $mysqli->prepare($query))) {
    echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    $success=FALSE;
}

if (!$stmt->execute()) {
    echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

$remain_num = NULL;
$topic_id = NULL;
$topic_name = NULL;
$statement_id = NULL;
$statement = NULL;
$news_id = NULL;
$news_title = NULL;
$news_content = NULL;
$news_url = NULL;

if (!$stmt->bind_result($remain_num, $topic_id, $topic_name, $statement_id, 
	$statement, $news_id, $news_title, $news_content, 
	$news_url)) {
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
    $return_value = array();
    $return_value['data'] = $data;
    $return_value['success'] = TRUE;
}
else{
    $return_value = array();
    $return_value['success'] = FALSE;
}
echo json_encode($return_value);


?>


