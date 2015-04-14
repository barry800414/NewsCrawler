<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<head>
    <link rel="stylesheet" href="./bootstrap.min.css" />
    <style type="text/css">
        #main_interface{
            max-width: 800px;
            margin:auto;
            font-family: "微軟正黑體";
        }
    </style>
</head>
<body style="padding-top:70px">

<div id="main_interface" class="container" >

<?php
	require("head.php");
?>

   <p align="center">
    <h3> Members:</h3> <h4> Wei-Ming Chen, Ran-Yu, Ming-Lun Cai </h4>
    <h3> Advisor:</h3> <h4> <a href="http://www.csie.ntu.edu.tw/~sdlin/">Prof. Shou-de Lin</a><h4>
    <h3> Laboratory: </h3> <h4><a href="http://mslab.csie.ntu.edu.tw/">Machine Discovery and Social Network Mining Laboratory</a>, the Department of Computer Science and Information Engineering, National Taiwan University. </h4>
    <h3> E-mail: </h3> <h4> r02922010@ntu.edu.tw</h4>
   <p>
    <br><br><br>
    <div style="max-width:600px;margin:auto;text-align:center"> 
        <h4>若您有任何疑問或建議，請回饋給我們，非常感謝您。</h4>
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


</div>

</body>
</html>
