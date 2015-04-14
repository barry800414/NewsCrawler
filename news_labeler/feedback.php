<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>
  <title>Login</title>  
  <link rel="stylesheet" href="./bootstrap.min.css" />
  <style type="text/css">
        #main_interface{
            max-width: 600px;
            margin:auto;
            font-family: "微軟正黑體";
        }
    </style>
</head>
<body style="padding-top:70px">
<?php
	require_once("head.php");
    #session_start();
    require_once("connect.php");
    
    if (isset($_POST['user_name']) && isset($_POST['user_email']) && isset($_POST['user_feedback']) && $_GET['err']==0){
        $user_name = $_POST['user_name'];
        $user_email = $_POST['user_email'];
        $user_feedback = $_POST['user_feedback'];
        $query = "INSERT INTO feedback (name, email, feedback) VALUES(?,?,?)";
        $success=TRUE;
        /*statement*/
        if (!($stmt = $mysqli->prepare($query))) {
            echo "Prepare failed: (" . $mysqli->errno . ") " . $mysqli->error;
            $success=FALSE;
        }

        if (!$stmt->bind_param("sss", $user_name, $user_email, $user_feedback)) {
            echo "Binding parameters failed: (" . $stmt->errno . ") " . $stmt->error;
            $success=FALSE;
        }
        
        if (!$stmt->execute()) {
            echo "Execute failed: (" . $stmt->errno . ") " . $stmt->error;
            $success=FALSE;
        }
        
        if($success){
            //login success
            header("location: feedback.php?msg=1");
        }
        else{
            //header("location: feedback.php?err=1");  
        }
    }
?>

<div id="main_interface">
    <h4>若您有任何疑問或建議，請回饋給我們，非常感謝您。</h4>
    <div style="max-width:600px;margin:auto;text-align:center"> 
        <form role="form" action="feedback.php" method="post">
            <div class="form-group">
                <input type="text" class="form-control" name="user_name" placeholder="您的名字 Your name">
            </div>
            <div class="form-group">
                <input type="text" class="form-control" name="user_email" placeholder="您的電子郵件 Your e-mail">
            </div>
            <div class="form-group">
                <textarea class="form-control" style="min-height:200px" name="user_feedback" placeholder="您的疑問或建議 Your questions or suggestions "></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
            <button type="reset" class="btn btn-default">Reset</button>
        </form>
    </div>


    <?php
        if(isset($_GET['err'])){
            if ($_GET['err']==1){
                echo "<font color='red'>訊息傳送錯誤! 請再試一次!</font><p>";
            }
        }
        else if(isset($_GET['msg'])){
            if ($_GET['msg']==1){
                echo "<font color='red'>您已成功將問題或訊息回饋給我們了! 我們會盡速回覆您!</font><p>";
            }
        }

    ?>

</div>

</body>
</html>
