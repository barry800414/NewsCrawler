<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>
  <title>AddUser</title>
  
  <STYLE TYPE="text/css"> 
  <!-- 
    @import url(style.css); 
  --> 
  </STYLE> 
</head>

<body>
<div class="wrap">



<?php
    require_once("config.php");
    require_once("head.php");
	require_once("connect.php");

    function addTopic($topic){
        if ($topic != ""){
            $exist = topicExist($topic);
            if($exist){
                return 'There is already the same topic';
            }

            /* prepare statements*/
            $mysqli = $GLOBALS['mysqli'];
            if (!($stmt = $mysqli->prepare("INSERT INTO topic(name) VALUES (?)"))) {
                return "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
            }

            if (!$stmt->bind_param("s", $topic)) {
                return "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
            }

            if (!$stmt->execute()) {
                return "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
            }
            $stmt->close();

            return 'Add a user successfully';

        } 
        else{
            return 'User id and password cannot be empty';
        }
    }

    function topicExist($topic){
        $mysqli = $GLOBALS['mysqli'];
        $success = True;
        if (!($stmt = $mysqli->prepare("SELECT COUNT(id) FROM topic WHERE name=?"))) {
            echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
            $success=FALSE;
        }

        if (!$stmt->bind_param("s", $topic)) {
            echo "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
            $success=FALSE;
        }

        if (!$stmt->execute()) {
            echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
            $success=FALSE;
        }
        
        $num = NULL;
        if (!$stmt->bind_result($num)) {
            echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
        }
        $stmt->fetch();
        $stmt->close();

        if(!$success){
            return NULL;
        }
        if($success && $num != 0){
            return True;
        }
        else{
	        return False;
        }
    }


    $result_message = '';
    if(isset($_POST['topic'])){
        $result_message = addTopic($_POST['topic']);
    }

?>
<form action="addTopic.php" method="post">
<table width="200" border="0">
  <tr>
    <td width="85" nowrap>Add Topic</td>
    <td width="105" nowrap>&nbsp;</td>
  </tr>
  <tr>
    <td nowrap>ID </td>
    <td nowrap><input type="text" name="topic" size="100"></td>
  </tr>
  <tr>
  <tr>
    <td nowrap>&nbsp;</td>
    <td nowrap><input type="submit" value="Add"/></td>
  </tr>
</table>
</form>

<?php
    if(isset($result_message)){
        echo "<h3 style='color:red'>$result_message</h3>";
    }
?>

<?php
   require("tail.php");
?>
</div>
</body>
</html>
