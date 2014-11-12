<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
    
    <title>AddStatement</title>    
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
	<link rel="stylesheet" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.11.1/themes/smoothness/jquery-ui.css" />
	<script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.11.1/jquery-ui.min.js"></script>

    <script>
        $(document).ready(function(){
			loadTopics();
		});


        function loadTopics(){
            $.ajax({
				type: "POST",
				url: "load_topics.php",
				dataType: "json",
				success: function(response){
					console.log(response);
                    
                    if(response['success']){
						$("#topic").autocomplete({
                            source: response['topic'],
                            minLength:0, 
                        }).on("focus", function(){
                            $(this).autocomplete("search", "");   
                        }).on("autocompleteselect", function(event, ui){
                            $("#topic_id").val(ui['item']['topic_id']);
                        })
					}
				}
			});
        }
    </script>

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

    function addUser($topic_id, $statement){
        if ($topic_id != "" && $statement !=""){
            $exist = statementExist($topic_id);
            if($exist){
                return 'There is already the same statement';
            }

            /* prepare statements*/
            $mysqli = $GLOBALS['mysqli'];
            $success = True;
            if (!($stmt = $mysqli->prepare("INSERT INTO statement(content, topic_id) VALUES (?,?)"))) {
                return "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
            }

            if (!$stmt->bind_param("ss", $statement, $topic_id)) {
                return "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
            }

            if (!$stmt->execute()) {
                return "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
            }
            $stmt->close();

            if($success){
                return 'Add a statement successfully';
            }
            else{
	            return "Error";
            }

        }else{
            return 'topic id and statement cannot be empty';
        }
    }

    function statementExist($statement){
        $mysqli = $GLOBALS['mysqli'];
        $success = True;
        if (!($stmt = $mysqli->prepare("SELECT COUNT(id) FROM statement WHERE content=?"))) {
            echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
            $success=FALSE;
        }

        if (!$stmt->bind_param("s", $statement)) {
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
    if(isset($_POST['topic_id']) && isset($_POST['statement'])){
        $result_message = addUser($_POST['topic_id'], $_POST['statement']);
    }

?>
<form action="addStatement.php" method="post">
<table width="200" border="0">
  <tr>
    <td width="100" nowrap>Add Statement</td>
    <td width="105" nowrap>&nbsp;</td>
  </tr>
  <tr>
    <td nowrap>Topic </td>
    <td nowrap><input id="topic" type="text" name="topic" size="20"></td>
  </tr>
    <input id="topic_id" type="hidden" name="topic_id" size="100">
  <tr>
  </tr>
  <tr>
    <td nowrap>Statement </td>
    <td nowrap><textarea name="statement"></textarea></td>
  </tr>
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
