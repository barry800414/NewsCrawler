<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<head>
    <title>新聞標記系統-介紹</title>
    <style type="text/css">
        #main_interface{
            max-width: 600px;
            margin:auto;
            font-family: "微軟正黑體";
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
        <p>
            此網頁是用於建立「電腦自動判定文章對給定立場支持與否」研究之資料庫。研究目的是建立一個電腦程式，輸入一個立場(例如: 支持廢除死刑)，以及一篇文章(例如: 一篇支持廢除死刑的論述文)，能智慧地判定本篇文章是支持這個立場的。 
        </p>
        <p>在此研究中，我們預計使用機器學習技術建立此一程式。因此我們需要您的幫忙，建立訓練語料庫，意即許多 [立場, 文章, 支持/反對/中立] 這樣的資料。</p>

        <p> This is the annotation web page for annotating the articles in our "Agreement Prediction" research. The goal of our research is to build a program which can intelligently judge whether one given article agrees, disagrees, or is neutral to one given statement(i.e. the standpoint). For example, if you give us a statement said "I support the abolishment of death penalty", and an article which elaborate the reasons why the author also supports the abolishment of death penalty, then our program should intelligently say "the article agrees the statement". </p>

    <p>This research may utilize machine learning techniques, so we have to build an training corpus for computers to learn how to judge.</p>
    <h2> 研究動機 Motivation </h2>
        <p>
            即使現在已經有大量的網路新聞、評論，現今許多媒體經常傳遞立場不中立的文章給閱聽者。因此，我們希望能夠建立一智慧程式，能自動判定文章之立場，如此一來，便能運用此程式將支持不同立場的文章呈現給使用者，以紓解此問題。         </p>
        <p> There has been huge amounts of online newspapers, comments and articles on the Internet in recent decades. However, some of media often deliver biased articles to the audience. As a result, it is crucial to build up an intelligent agent who can help us judge the standpoints of articles. With the assistance of intelligent agent, we can easily find articles with certain standpoints.</p>
    <h2> 標記步驟 Steps </h2>
    <p>你將會被給定一篇從網路上擷取的文章，以及一個敘述句(立場)。我們希望您能協助我們標記下面四個問題的答案:</p>
    <ol>
        <li class="text-left">該文章是否有格式上的錯誤(包含: 存在非內文之廣告、編碼錯誤、編排錯誤、段落遺失等等)。</li>
        <li class="text-left">該文章是否與主題高度相關。</li>
        <li class="text-left">該文章是否有句子闡述支持或不支持該立場的原因。</li>
        <li class="text-left">該文章對該立場 整體而言 是 支持/反對/中立。</li>
    </ol>
    <p>On this annotation website, you will be give one article crawled from online websites and one statement(i.e. the standpoint). We hope you can help us find that 
        <ol>
            <li class="text-left">whether the article has noisy content(including advertisements, encoding errors, format errors, missing paragraphs...)</li>
            <li class="text-left">whether the article is highly related to the statement </li>
            <li class="text-left">whether there is any sentences, paragraphs elaborate the standpoints of author or the reasons why the author agree or disagree the statement </li>
            <li class="text-left">the overall polarity(agree/disagree/neutral) of the whole article to the given statement.</li>
        </ol>
    </p>
    

    <h2> 標記Q&A </h2>
    <p> 在開始標記前，請先參考標記時可能會遇到的疑問與回答: <a href="qa2.php">標記Q&A</a></p>
    
    <br><br>

    <a class="btn btn-primary" href="./annotate.php">前往標記頁面</a><br><br>
    <p>如果有任何疑問，歡迎隨時<a href="./contact.php" >聯絡我們</a></p>
    <p>If you have any question, please <a href="./contact.php">contact us</a></p>
    <div style="height:100px"></div>
    </div>

</div>

</body>
</html>
