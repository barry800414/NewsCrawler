<?php 
ini_set('log_errors', 'On');
ini_set('error_log', '/home/r02922010/www/error.log');

$statement=$_POST['statement'];
$label=$_POST['label'];
$title=$_POST['title'];
$author=$_POST['author'];
$source=$_POST['source'];
$url=$_POST['url'];
$content=$_POST['content'];
$comment=$_POST['comment'];

$success=TRUE;

//connect to db
$mysqli = new mysqli("localhost", "r02922010", "r02922010", "r02922010", 3306);
if ($mysqli->connect_errno) {
    echo "Failed to connect to MySQL: (" . $mysqli->connect_errno . ") " . $mysqli->connect_error;
    $success=FALSE;
}

if(!$mysqli->set_charset("utf8")){
    echo "Error loading character set utf8".$mysqli->error;
    $success=FALSE;
}

/* prepare statements*/
if (!($stmt = $mysqli->prepare(
	"INSERT INTO corpus_tw(statement, label, title, author, source, url, content, comment) 
	VALUES (?,?,?,?,?,?,?,?)"))) {
    echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
    $success=FALSE;
}

if (!$stmt->bind_param("sissssss", $statement, $label, $title, $author, $source, $url, $content, $comment)) {
    echo "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

if (!$stmt->execute()) {
    echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
    $success=FALSE;
}

/* explicit close recommended */
$stmt->close();

if($success){
	echo "success";
}
else{
	echo "failed";
}


?>
