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

    function addUser($user_id, $passwd, $token){
        if ($user_id != "" && $passwd !=""){
            if($token == $GLOBALS['token'] ) {

                $exist = userExist($user_id);
                if($exist){
                    return 'There is already the same user id';
                }

                /* prepare statements*/
                $mysqli = $GLOBALS['mysqli'];
                $success = True;
                if (!($stmt = $mysqli->prepare("INSERT INTO labeler(id, password) VALUES (?,?)"))) {
                    return "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
                    $success=FALSE;
                }

                if (!$stmt->bind_param("ss", $user_id, $passwd)) {
                    return "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
                    $success=FALSE;
                }

                if (!$stmt->execute()) {
                    echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
                    $success=FALSE;
                }
                $stmt->close();

                if($success){
                    return 'Add a user successfully';
                }
                else{
	                return "Error";
                }

            } 
            else {
                return 'Please enter correct tokens';
            }
        }else{
            return 'User id and password cannot be empty';
        }
    }

    function userExist($user_id){
        $mysqli = $GLOBALS['mysqli'];
        $success = True;
        if (!($stmt = $mysqli->prepare("SELECT COUNT(id) FROM labeler WHERE id=?"))) {
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

    function generatorPassword(){
        $password_len = 10;
        $password = '';

        // remove o,0,1,l
        $word = 'abcdefghijkmnpqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ23456789';
        $len = strlen($word);

        for ($i = 0; $i < $password_len; $i++) {
            $password .= $word[rand() % $len];
        }
        return $password;
    }	

    $result_message = '';
    if(isset($_POST['user_id']) && isset($_POST['passwd']) && isset($_POST['token'])){
        $result_message = addUser($_POST['user_id'], $_POST['passwd'], $_POST['token']);
    }

?>
<form action="addUser.php" method="post">
<table width="200" border="0">
  <tr>
    <td width="85" nowrap>Add Labeler</td>
    <td width="105" nowrap>&nbsp;</td>
  </tr>
  <tr>
    <td nowrap>ID </td>
    <td nowrap><input type="text" name="user_id" size="20"></td>
  </tr>
  <tr>
    <td nowrap>Password </td>
    <td nowrap><input type="text" name="passwd" size="10" value="<?php echo generatorPassword()?>"></td>
  </tr>
  <tr>
    <td nowrap>Token </td>
    <td nowrap><input type="text" name="token" size="10"></td>
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
