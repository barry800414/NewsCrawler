<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<head>
    <title>新聞標記系統-介紹</title>
    <style type="text/css">
        #main_interface{
            max-width: 700px;
            margin:auto;
            font-family: "微軟正黑體";
        }
        p {
            font-size:14pt;
        }
    </style>
</head>
<body style="padding-top:70px">

<div class="container">

<?php
	require("head.php");
?>

    <div id="main_interface" class="text-center">
    <h2> 專案介紹 Introduction </h2>
        <p> 在現今的社會中，網路新聞媒體蓬勃發展，新聞隨手可得。然而，您是否覺得，<span style="color:red">部分媒體經常僅以特定立場報導新聞、立場有所偏頗呢?</span> 若我們能夠為每一個社會議題，呈現不同立場之新聞給閱聽者，是否能夠讓閱聽者擁有更完整的資訊，進而做出更好的決定呢!? </p>
        <p>
            在此研究中，<span style="color:blue">我們希望建立一個電腦程式，輸入一個<span style="font-weight:bold">立場</span>(例如: 支持廢除死刑)，以及一篇<span style="font-weight:bold">文章</span>(例如: 一篇支持廢除死刑的文章)，就能夠<span style="font-weight:bold">智慧地判定本篇文章是支持這個廢除核四這個立場的</span>。</span> 而我們預計使用機器學習技術建立此一程式，因此我們需要您的幫忙，建立訓練語料庫，意即許多 [立場, 文章, 支持/反對/中立] 這樣的資料。</p>
    <br><br>
    <h2> 研究動機 Motivation </h2>
        <p>
            即使現在已經有大量的網路新聞、評論，現今許多媒體經常傳遞立場不中立的文章給閱聽者。因此，我們希望能夠建立一智慧程式，能自動判定文章之立場，如此一來，便能運用此程式將支持不同立場的文章呈現給使用者，以紓解此問題。         </p>
    <br><br>
    <h2> 標記步驟 Steps </h2>
    <p>若您尚未擁有帳號，請先至 <a class="btn btn-primary" href="./register.php">註冊頁面</a> 註冊帳號。 <a style="font-size:10pt" title="由於每一篇文章僅能被同一個人標記過一次，因此我們需要您註冊帳號，以分辨您的身分。">為什麼要有帳號?</a> <p>
    <p class="text-left">你將會被給定一篇從網路上擷取的文章，以及一個敘述句(立場)。我們希望您能協助我們標記下面四個問題的答案:</p>
    <ol>
        <li class="text-left" style="font-size:14pt">該文章是否有格式上的錯誤(包含: 存在非內文之廣告、編碼錯誤、編排錯誤、段落遺失等等)。</li>
        <li class="text-left" style="font-size:14pt">該文章是否與主題高度相關。</li>
        <li class="text-left" style="font-size:14pt">該文章是否有句子闡述支持或不支持該立場的原因。</li>
        <li class="text-left" style="font-size:14pt">該文章對該立場 整體而言 是 支持/反對/中立。</li>
    </ol>
    </p>
    
    <br><br>
    <h2> ----標記Q&A---- </h2>
    <p> 在開始標記前，請先參考標記時可能會遇到的疑問與回答: <a href="qa2.php">標記Q&A</a></p>
    
    <br><br><br><br>

    <a class="btn btn-primary" href="./annotate.php" style="font-size:18pt">前往標記頁面</a><br><br>
    <p>如果有任何疑問，歡迎隨時<a href="./contact.php" >聯絡我們</a></p>
    <p>If you have any question, please <a href="./contact.php">contact us</a></p>
    <div style="height:100px"></div>
    </div>

</div>

</body>
</html>
