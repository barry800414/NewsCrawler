<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<head>
  <STYLE TYPE="text/css"> 
  <!-- 
    @import url(style.css); 
  --> 
  </STYLE> 
  
</head>
<body style="padding-top:70px">

<div class="container">

<?php
	session_start();
    session_destroy();
?>

<?php
	require("head.php");
?>

   <p align="center">
   <h3 color='red'>You have logout.</h3>
   <p>

<?
    require("tail.php");
?>

</div>

</body>
</html>
