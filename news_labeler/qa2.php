<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<head>
    <style type="text/css">
        #main_interface{
            max-width: 600px;
            margin:auto;
            font-family: "微軟正黑體";
        }
        .q_title{
            font-weight: bold;
            color:rgb(0, 109, 255);
        }
    </style>
</head>
<body style="padding-top:70px">

<div class="container">

<?php
	require("head.php");
?>

    <div id="main_interface" class="text-left">
        <h3> 標記 Q&A </h3><br>
        <ol>
            <li class="q_title"><h4>文章作者以中立的角度撰寫，但內容是持支持或反對的立場，我應該如何標記呢?</h4></li>
            <p>請以文章內容為主，標記支持或反對，而非因記者中立書寫而標記中立。</p><br>

            <li class="q_title"><h4>有些文章的內容包含不同人對於該議題的不同立場，我應該如何標記呢?</h4></li>
            <p>這確實是很常見的狀況。請先不要理會是誰的立場，如此會有若干支持或反對的論述。接著請憑您對文章內容的理解，判斷整體而言，整篇文章是偏向支持/反對，或者中立。</p></br>   

            <li class="q_title"><h4>文章內容僅反對爭議主體的部分而非全部(例如: 反對服貿協議的某些條款，但不反對整個服務貿易協議)，我應該如何標記呢?</h4></li>
            <p>請標記為反對兩岸服務貿易協議</p><br>

            <li class="q_title"><h4>文章內容並非直接提及支持或反對該議題，而是建議以其他方法解決(例如: 認為服務貿易協議應退回重審)，我應該如何標記呢?</h4></li>
            <p>請根據您的推測，決定其立場為支持、中立或反對</p><br>

        </ol>
        <br>
        <h4>若您還有任何疑問或建議，請回饋給我們，非常感謝您。</h4>
        
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
    </div>
</div>

</body>
</html>
