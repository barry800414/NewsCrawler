<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<head>
    <title>Register</title>
    <link rel="stylesheet" href="./bootstrap.min.css" />
</head>

<body style="padding-top:70px">
<?php
    require_once('head.php');
    
    if(isset($_POST['user_id']) || isset($_POST['user_pwd']) || isset($_POST['user_pwd_2'])){
        if($_POST['user_id'] != '' && $_POST['user_pwd'] != '' && $_POST['user_pwd_2'] != ''){
            $user_id = $_POST['user_id'];
            $user_pwd = $_POST['user_pwd'];
            $user_pwd_2 = $_POST['user_pwd_2'];
            
            if(strcmp($user_pwd, $user_pwd_2) != 0){
                header("location: register.php?msg=2");
                exit();
            }
            
            if(!is_valid_account($user_id, $user_pwd)){
                header("location: register.php?msg=3");
                exit();
            }

            require_once('connect.php');
            if(!is_id_duplicated($user_id)){
                header("location: register.php?msg=4");
                exit();
            }
            $success = create_account($user_id, $user_pwd);
            if(!$success){
                header("location: register.php?msg=5");
                exit();
            }
            else{
                session_start();
                $_SESSION['valid_user'] = $_POST['user_id'];
                header("location: register.php?msg=6");
                exit();
            }
            
        }
        else{
            header("location: register.php?msg=1");
            exit();
        }
    }

    function is_valid_account($user_id, $user_pwd){
        return TRUE;
    }

    function is_id_duplicated($user_id){
        global $mysqli;
        $query = "SELECT COUNT(*) FROM labeler WHERE id=?";
        $success = TRUE;
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
		
		$num = 1;
		if (!$stmt->bind_result($num)) {
			echo "Bind failed: (" . $stmt->errno . ") " . $stmt->error;
			$success=FALSE;
		}
		$stmt->fetch();
        if($num >= 1 || $success == FALSE){
            return FALSE;
        }
        else{
            return TRUE;
        }
    
    }

    function create_account($user_id, $user_pwd){
        global $mysqli;
        $query = "INSERT INTO labeler(id, password) VALUES(?,?)";
        $success = TRUE;
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
        return $success;
    }


?>
<div style="max-width:400px;margin:auto"> 
<form role="form" action="register.php" method="post">
  <div class="form-group">
    <label>帳號 User ID</label>
    <input type="text" class="form-control" name="user_id" placeholder="Enter ID">
  </div>
  <div class="form-group">
    <label>密碼 Password</label>
    <input type="password" class="form-control" name="user_pwd" placeholder="Password">
    </div>
  <div class="form-group">
    <label>密碼確認 Password Confirmation</label>
    <input type="password" class="form-control" name="user_pwd_2" placeholder="Repeat Password Again">
    <font color='red'>由於本網站未使用https加密，請不要使用您常用的密碼。</font>
    <font color='red'>The website is not under https protocol, please do not use the password you often use.</font>
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
  <button type="reset" class="btn btn-default">Reset</button>
</form>
<?php
    if(isset($_GET['msg'])){
        if($_GET['msg']==1){
            echo "<font color='red'>請完整填寫表單</font><p>";
            echo "<font color='red'>Please fill the whole form.</font><p>";
        }
        else if($_GET['msg']==2){
            echo "<font color='red'>密碼確認與密碼不同</font><p>";
            echo "<font color='red'>Password confirmation should be identical to password.</font><p>";
        }
        else if($_GET['msg']==3){
            echo "<font color='red'>帳號或密碼有不合法字元</font><p>";
            echo "<font color='red'>ID or password contains invalid characters.</font><p>";
        }
        else if($_GET['msg']==4){
            echo "<font color='red'>您的帳號已經有人註冊過</font><p>";
            echo "<font color='red'>There has been a same ID in our website.</font><p>";
        }
        else if($_GET['msg']==5){
            echo "<font color='red'>帳號註冊錯誤，請聯絡 r02922010@ntu.edu.tw</font><p>";
            echo "<font color='red'>Creating account failed, please contact r02922010@ntu.edu.tw</font><p>";
        }
        else if($_GET['msg']==6){
            echo "<font color='red'>您成功註冊帳號了! 將於3秒內跳轉至介紹頁面! </font><p>";
            echo "<font color='red'>You created an account successfully! Redirect to Introduciton page in 3 seconds</font><p>";
            header("Refresh: 3; url=intro.php");
        }
    }
?>

</div>

</body>
</html>
