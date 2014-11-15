<?php


require_once('connect.php');


$query = 
"";

$query =
"SELECT 
	C.diff, E.topic_id, E.id as statement_id,
	E.content as statement, D.id as news_id, 
        D.title as news_title, D.content as news_content, 
	D.url as news_url 
FROM (
	SELECT diff, statement_id, news_id 
	FROM `DIFFERENCE` 
	WHERE diff = (SELECT MAX(diff) FROM `DIFFERENCE`) 
	order by rand()) as C, merge as D, statement as E 
WHERE 
	D.id = C.news_id AND C.statement_id = E.id";

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
$statement_id = NULL;
$statement = NULL;
$news_id = NULL;
$news_title = NULL;
$news_content = NULL;
$news_url = NULL;

if (!$stmt->bind_result($remain_num, $topic_id, $statement_id, 
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


