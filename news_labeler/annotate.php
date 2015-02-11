<html>
<head>
	<title>Corpus Annotation Page</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
	<link rel="stylesheet" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.11.1/themes/smoothness/jquery-ui.css" />
	<script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.11.1/jquery-ui.min.js"></script>

    <?php
        require_once('check_login.php');
    ?>
    <script>
    $(document).ready(function(){
        hide_elements();    
		load_a_statement_news();
        load_labeled_num();
		$("#submit").click(function(){
			if(checkInput()){
				upload();
			}
		});
		$("#reset").click(function(){
			reset();
        });
        $("#valid_format_button").click(function(){
            click_valid_format_button(); 
        });
        $("#relevance_button").click(function(){
            click_relevance_button();
        });
	});

    function hide_elements(){
        $("#topic_row").hide();
        $("#relevance_row").hide();
        $("#statement_row").hide();
        $("#mention_row").hide();
        $("#label_row").hide();
        $("#submit").hide();
    }

    function click_valid_format_button(){
        var valid_format=$(".valid_format:checked").val();
        if(typeof(valid_format) == 'undefined'){
            alert("請選 格式正確性 標記");
            return;
        }
        else{
            if(valid_format == 'valid' || valid_format == 'small_error'){
                //disable current row
                $(".valid_format").prop('disabled', true);
                $("#valid_format_button").prop('disabled', true);
                $("#valid_format_row").addClass("disabled_row");

                //show next row
                $("#topic_row").show();
                $("#relevance_row").show();
                var destination = $("#topic_row").offset().top;
                $("html:not(:animated),body:not(:animated)").animate({ scrollTop: destination-15}, 500 );
                
            }
            else if(valid_format == 'invalid'){
                alert("由於格式有誤，此篇文章將不需要標記！");
                upload(false);
            }
        }
    }

    function click_relevance_button(){
        var relevance=$(".relevance:checked").val();
        if(typeof(relevance) == 'undefined'){
            alert("請選 內文相關性 標記");
            return;
        }
        else{
            if(relevance == 'relevant'){
                //disable current row
                $(".relevance").prop('disabled', true);
                $("#relevance_button").prop('disabled', true);
                $("#relevance_row").addClass('disabled_row');

                //show next rows
                $("#statement_row").show();
                $("#mention_row").show();
                $("#label_row").show();
                $("#submit").show();
                var destination = $("#statement_row").offset().top;
                $("html:not(:animated),body:not(:animated)").animate({ scrollTop: destination-50}, 500 );
            }
            else if(relevance == 'irrelevant'){
                alert("由於與主題相關性不高，此篇文章將不需要後續的標記！");
                upload(false);
            }    
        }
    }


    //containing existing statement, author, source
    function load_a_statement_news(){
        var user_id = <?php echo '"'.$_SESSION['valid_user'].'";'; ?>
        $.ajax({
            type: "POST",
            url: "load_a_statement_news.php",
            data: {
                user_id: user_id
            },
            dataType: "json",
            success: function(response){
                //console.log(response);
                if(response['success']){
                    var data = response['data']; 
                    $("#statement_id").val(data["statement_id"]);
                    $("#news_id").val(data["news_id"]);
                    $("#statement").text(data["statement"]);
                    $(".statement").each(function(){
                        $(this).text(data["statement"]);
                    });
                    //$("#source").text(response["source"]);
                    $("#title").text(data["news_title"]);
                    $("#content").html(content_preprocess(data["news_content"]));
                    if(data["news_url"].length > 60){
                        var shorten_url = data["news_url"].substring(0,59)+"...";
                    }
                    else{
                        var shorten_url = data["news_url"];
                    }
                    $("#url").text(shorten_url);
                    $("#url").attr("href", data["news_url"]);
                    $("#topic").text(data["topic_name"]);
                    $(".topic").each(function(){
                        $(this).text(data["topic_name"]);
                    });
                }
                else{
                    alert("1.資料可能已全部標記完畢 \n2.您已經沒有可以標記的文章了 \n3.發生錯誤。 \n\n1.There is no articles to be labeled. \n2.There is no article for you to label. \n3. Errors occurred.");
                }
            }
        });
    }

    function load_labeled_num(){
        var user_id = <?php echo '"'.$_SESSION['valid_user'].'";'; ?>
        $.ajax({
            type: "POST",
            url: "load_labeled_num.php",
            dataType: "json",
            data: { user_id: user_id },
            success: function(response){
                //console.log(response);
                if(response['success']){
                    //console.log(response['labeled_num']);
                    $("#labeled_num").text(response['labeled_num']);
                    var length = response['total_labeled_length'];
                    if(length != null){
                        $("#total_labeled_length").text(length);
                    }
                    else{
                        $("#total_labeled_length").text("0");
                    }
                }
            }
        });
    }


    function content_preprocess(content){
        //console.log(content);
        return content.replace(/[\n]+/g, "<br><br>");
    }

    function checkInput(){
        var valid_format=$(".valid_format:checked").val();
        var relevance=$(".relevance:checked").val();
        var overall_polarity=$(".overall_polarity:checked").val();
        //console.log(valid_format);
        //console.log(relevance);
        //console.log(overall_polarity);

        var err_msg="";

        if(typeof(valid_format)=='undefined'){
            err_msg += "請選擇 格式正確性 標記\n";
        }
        if(typeof(relevance)=='undefined'){
            if(valid_format == 'valid'){
                err_msg += "請選擇 內文相關性 標記\n";
            }
        }
        if(typeof(overall_polarity)=='undefined'){
            if(valid_format == 'valid' && relevance == 'relevant'){
                err_msg += "請選擇 整體 標記\n";
            }
        }

        if(err_msg.length!=0){
            alert(err_msg);
            return false;
        }
        else{
            return true;
        }
    }

    function upload(alert_msg){
        if(typeof(alert_msg) == 'undefined'){
            alert_msg = true;
        }
        var valid_format=$(".valid_format:checked").val();
        var relevance=$(".relevance:checked").val();
        var overall_polarity=$(".overall_polarity:checked").val();
        var statement_id = $("#statement_id").val();
        var news_id = $("#news_id").val();
        var user_id = <?php echo '"'.$_SESSION['valid_user'].'";'; ?>

        var mention_agree = 'no';
        var mention_disagree = 'no';
        $(".user_mention_label:checked").each(function(){
            var value = $(this).val();
            if(value == 'positive'){
                mention_agree = 'yes';
            }
            else if(value == 'negative'){
                mention_disagree = 'yes';
            } 
        });
        
        if(typeof(relevance) == 'undefined'){
            relevance = '';
        }
        if(typeof(overall_polarity) == 'undefined'){
            overall_polarity = '';
        }
        
        //console.log(mention_agree);
        //console.log(mention_disagree);
        //console.log(user_id);
        $.ajax({
            type: "POST",
            url: "upload_annotation.php",
            data: { 
                valid_format: valid_format,
                relevance: relevance,
                mention_agree: mention_agree,
                mention_disagree: mention_disagree,
                overall_polarity: overall_polarity,
                statement_id: statement_id,
                news_id: news_id,
                user_id: user_id
            },
            dataType: "json",
            success: function(response){
                //console.log(response);
                if(response['success'] == true){
                    if(alert_msg){
                        alert("上傳成功，感謝大大無私奉獻^_^");
                    }
                    location.reload();
                }
                else{
                    alert("上傳失敗，請聯絡r02922010@ntu.edu.tw");
                }
            }
        });
    }

    function reset(){
        $(".overall_polarity").attr("checked", false);
    }

        </script>
        <link rel="stylesheet" href="./annotation_page.css" />
        <link rel="stylesheet" href="./bootstrap.min.css">
    </head>
    <body>
        <?php
            require_once('head.php');
        ?>
        <div id="main_interface" class="container"> 
            <h3 class="title"> 「文章」對「立場」支持/反對/中立預測 資料庫建立頁面 </h3>
            <br>
            
            <div id="step_intro">
                <br>         
                <h4> 標記步驟 Steps </h4>
                <p>你將會被給定一篇從網路上擷取的文章，以及一個敘述句(立場)。我們希望您能協助我們標記下面四個問題的答案:</p>
                <ol>
                    <li class="text-left"><strong>該文章是否有格式上的錯誤</strong>(包含: 存在非內文之廣告、編碼錯誤、編排錯誤、段落遺失等等)。</li>
                    <li class="text-left"><strong>該文章是否與主題高度相關</strong>。</li>
                    <li class="text-left"><strong>該文章是否有句子闡述支持或不支持該立場的原因。</strong></li>
                    <li class="text-left"><strong>該文章對該立場 整體而言 是 支持/反對/中立。</strong></li>
                </ol>
                <br>
            </div>
        <br>
        
        <h2>------------------開始標記--------------------</h2><br>
        <p class="text-right">您已經協助標記 <span id="labeled_num"></span> 篇文章了!  
            所有標記文章之內容字數總計 <span id="total_labeled_length"></span> 個字! </p>
        <p style="text-align:right"> 若欲取消或放棄標記此篇文章，請按重新整理即可</p>

    	<table class="main_table table table_bordered table-hover table-responsive">
    		<input type="hidden" id="statement_id">
    		<input type="hidden" id="news_id">
    		<tr id="topic_row_top" class="statement_row" >
                <td class="first_col">主題</td>
                <td class="second_col"><span id="topic" class="second_row topic"></span></td>
            </tr>

    		<tr class="news_row">
    			<td class="first_col">標題</td>
    			<td class="second_col"><span id="title"></span></td>
    		</tr>
    		<!--<tr class="small_row">
    			<td class="first_col">來源</td>
    			<td class="second_col"><span id="source"></span></td>
    		</tr>-->
    		<tr class="news_row">
    			<td class="first_col">來源網址</td>
    			<td class="second_col"><a target="_blank" id="url"></a></td>
    		</tr>
    		<tr class="news_row">
    			<td class="first_col">內文</td>
    			<td class="second_col"><span id="content" class="content"></span></td>
            </tr>
            <tr id="valid_format_row" class="label_row">
    			<td class="first_col">格式正確性</td>
    			<td class="second_col">
                <div>
                    <label class="radio-inline">
                        <input type="radio" name="valid_format" class="valid_format" value="small_error">內文有些許錯誤，但不致影響閱讀
                    </label>
                    <br>
                    <label class="radio-inline">
                        <input type="radio" name="valid_format" class="valid_format" value="invalid">內文有較大錯誤（例如段落遺失、大量廣告文字、亂碼等等）
                    </label>
                    <br>
                    <label class="radio-inline">
    				    <input type="radio" name="valid_format" class="valid_format" value="valid">內文無錯誤
                    </label>

                </div>
                <br><span id="overall_polarity_hint_text"> 請標記<span class="this_article">本篇文章</span>內，是否有段落遺失、廣告文字、亂碼或格式上的錯誤。<!--<ul><li>若文章內有少許錯誤，但不致影響閱讀，請標記「內文有些許錯誤」。</li><li>若內文有相當大的錯誤（例如段落遺失、大量廣告文字等等），請標記「內文不完整/格式有大錯誤/有很多非文章內文的雜訊」。</li><li>若沒有錯誤，請標記「內文無錯誤」。</li></ul>--!></span>
                    <button class="btn btn-primary pull-right" id="valid_format_button">確定</button>
                </td>
            </tr>
            <tr id="topic_row" class="statement_row" >
                <td class="first_col">主題</td>
                <td class="second_col"><span id="topic" class="second_row topic"></span></td>
            </tr>
            <tr id="relevance_row" class="label_row">
    			<td class="first_col">文章與主題相關性</td>
    			<td class="second_col">
                <div>
                    <label class="radio-inline">
                        <input type="radio" name="relevance" class="relevance" value="relevant"> 本篇文章 與「<span class="topic"></span>」高度相關 &nbsp;&nbsp;
                    </label>
                    <br>
                    </label>
                    <label class="radio-inline">
                        <input type="radio" name="relevance" class="relevance " value="irrelevant"> 本篇文章 </span>與「<span class="topic"></span>」無相關或不太相關&nbsp;&nbsp;
                    </label>
                </div>
    				
                <br><span id="overall_polarity_hint_text"> 請標記<span class="this_article">本篇文章</span>與「<span class="topic"></span> 」是否高度相關。若只是一篇剛好提及文章關鍵字的新聞，但內容並非以「<span class="topic"></span>」這個主題為主，請標記為無相關。</span>
                    <button class="btn btn-primary pull-right" id="relevance_button">確定</button>
                </td>
    		</tr>
            
            <tr id="statement_row" class="statement_row">
                <td class="first_col">立場</td>
                <td class="second_col"><span id="statement" class="second_col"></span></td>
            </tr>
           
            <tr id="mention_row" class="label_row">
    			<td class="first_col">文章提及正反意見</td>
    			<td class="second_col">
                <div>
                    <label class="checkbox-inline">
                        <input type="checkbox" name="user_mention_label" class="user_mention_label" value="positive"> 提及支持「<span class="statement"></span>」之論述
                    </label>
                    <br>
                    </label>
                    <label class="checkbox-inline">
                        <input type="checkbox" name="user_mention_label" class="user_mention_label " value="negative"> 提及反對「<span class="statement"></span>」之論述
                    </label>
                </div>
    				
                <br><span id="overall_polarity_hint_text"> 請標記<span class="this_article">本篇文章</span>是否提及支持或反對「<span class="statement"></span>」的論述 (可複選或都不選) </span>
    			</td>
    		</tr>
            
    		<tr id="label_row" class="label_row">
    			<td class="first_col">標記</td>
    			<td class="second_col">
                <div>
                    <label class="radio-inline">
    				    <input type="radio" name="overall_polarity" class="overall_polarity" value="agree">支持「<span class="statement"></span>」
                    </label>
                    <br>
                    <label class="radio-inline">
                        <input type="radio" name="overall_polarity" class="overall_polarity" value="neutral">中立
                    </label>
                    <br>
                    <label class="radio-inline">
                        <input type="radio" name="overall_polarity" class="overall_polarity" value="oppose">反對「<span class="statement"></span>」
                    </label>
                </div>
    				
                <br><span id="overall_polarity_hint_text"> 請標記<span class="this_article">本篇文章</span>針對「<span class="statement"></span>」這個立場 <span class="highlight_text">整體而言</span> 表達 (1)支持、同意 (2)持中立立場 或(3)反對、不同意 </span>
                <br><br>
                <span style="font-size:12pt"> 附註: 由於文章可能包含不同人對於該議題不同的立場。請不論表達立場的人是誰，整體而言，認定整篇文章的內容是比較支持、中立、或是比較反對。</span>
    			</td>
    		</tr>
        </table>
        <p style="text-align:right"> 若欲取消或放棄標記此篇文章，請按重新整理即可</p>
            <br><br>
            <button class="btn btn-primary" id="submit">上傳</button>
    	    <div style="height:100px"></div>
        </div>
            	<!--<button id="reset">清空</button>-->
    </body>
    </html>
