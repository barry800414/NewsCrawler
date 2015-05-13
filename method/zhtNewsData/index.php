<?php

$path = '.';
$files = scandir($path);

sort($files); 
foreach ($files as $entry){
    if(strpos($entry, '.json') != False){
        echo "<a href='./$entry'> $entry</a>  ";
        echo "   Time: ".date("Y/m/d H:i:s.", filemtime($entry));
        echo "   File Size: ".sprintf("%.2f", filesize($entry)/1024)."KB";
        echo "<br>";
    }
}
/*
if ($handle = opendir('.')) {

    while (false !== ($entry = readdir($handle))) {
        if ($entry != "." && $entry != "..") {
            if(strpos($entry, '.stderr') != False){
                echo "<a href='./$entry'> $entry</a><br>\n";
            }
        }
    }
        closedir($handle);
}*/
?>
