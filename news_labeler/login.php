<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>
  <title>Login</title>  
  <link rel="stylesheet" href="./bootstrap.min.css" />

</head>
<body style="padding-top:70px">
<?php
	require_once("head.php");
    #session_start();
    require_once("connect.php");
    
    if (isset($_POST['user_id']) && $_POST['user_id']!="" && $_POST['user_pwd']!="" && $_GET['err']==0){
        $user_id = $_POST['user_id'];
        $user_pwd = $_POST['user_pwd'];
        $query = "select COUNT(*) from labeler where id =? AND password=?";
        $success=TRUE;
        /*statement*/
        if (!($stmt = $mysqli->prepare($query))) {
            echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
            $success=FALSE;
        }

        if (!$stmt->bind_param("ss", $user_id, $user_pwd)) {
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
            $success=FALSE;
        }
        $stmt->fetch();
        if($success && $num == 1){
            //login success
            $_SESSION['valid_user'] = $_POST['user_id'];
            header("location: annotate.php");
        }
        else{
            header("location: login.php?err=1");  
        }
    }
?>

<p>

<div style="max-width:400px;margin:auto"> 
<form role="form" action="login.php" method="post">
  <div class="form-group">
    <label>User ID</label>
    <input type="text" class="form-control" name="user_id" placeholder="Enter ID">
  </div>
  <div class="form-group">
    <label>Password</label>
    <input type="password" class="form-control" name="user_pwd" placeholder="Password">
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
  <button type="reset" class="btn btn-default">Reset</button>
</form>
<?php
    if(isset($_GET['err'])){
	    if ($_GET['err']==1){
            echo "<font color='red'>密碼錯誤! Wrong password!!</font><p>";
        }
	    if ($_GET['err']==2){
            echo "<font color='red'>請先登入! Please log in first!</font><p>";
        }
    }
?>

<div align="center">
   <h3 style="font-family:'微軟正黑體'">登入後將進入標記頁面</h3>
    <p> 若您尚未擁有帳號，請先點 <a class="btn btn-primary" href="./register.php">註冊頁面</a> 註冊帳號。
<div>

</div>

<p align="center">
</p>


</body>
</html>
