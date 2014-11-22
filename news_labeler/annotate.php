<html>
<head>
	<title>Corpus Input Page</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
	<link rel="stylesheet" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.11.1/themes/smoothness/jquery-ui.css" />
	<script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.11.1/jquery-ui.min.js"></script>

    <?php
        require_once('check_login.php');
    ?>
    <script>
	$(document).ready(function(){
		load_a_statement_news();

		$("#submit").click(function(){
			if(checkInput()){
				upload();
			}
		});
		$("#reset").click(function(){
			reset();
		});
	});

        //containing existing statement, author, source
        function load_a_statement_news(){
        	var user_id='user';
        	$.ajax({
        		type: "POST",
        		url: "load_a_statement_news.php",
        		dataType: "json",
        		data: { user_id: user_id },
        		success: function(response){
        			console.log(response);

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
                        $("#url").text(data["news_url"]);
                        $("#url").attr("href", data["news_url"]);
                        $("#topic").text(data["topic_name"]);
						$(".topic").each(function(){
							$(this).text(data["topic_name"]);
						});
                    }
                }
            });
        }

        function content_preprocess(content){
            return content.replace("\n", "<br><br>");
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
				if(valid_format == 'yes'){
					err_msg += "請選擇 內文相關性 標記\n";
				}
            }
        	if(typeof(overall_polarity)=='undefined'){
        		if(valid_format == 'yes' && relevance == 'yes'){
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

        function upload(){
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
        			console.log(response);
        			if(response['success'] == true){
        				alert("上傳成功，感謝大大無私奉獻^_^");
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
            <h3 class="title"> 「文章」對「敘述句」支持/反對/中立預測 資料庫建立頁面 </h3>
            <br><br>
    	<table class="main_table table table_bordered table-hover table-responsive">
    		<input type="hidden" id="statement_id">
    		<input type="hidden" id="news_id">
    		
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
    			<td class="second_col"><a  id="url"></a></td>
    		</tr>
    		<tr class="news_row">
    			<td class="first_col">內文</td>
    			<td class="second_col"><span id="content" class="content"></span></td>
            </tr>
            <tr class="statement_row">
                <td class="first_col">主題</td>
                <td class="second_col"><span id="topic" class="second_col"></span></td>
            </tr>
            <tr class="statement_row">
                <td class="first_col">敘述句<br>(論點)</td>
                <td class="second_col"><span id="statement" class="second_col"></span></td>
            </tr>
            <tr class="overall_polarity_row">
    			<td class="first_col">格式正確性</td>
    			<td class="second_col">
                <div>
                    <label class="radio-inline">
    				    <input type="radio" name="valid_format" class="valid_format" value="valid">內文格式大致無錯誤&nbsp;&nbsp;
                    </label>
                    <label class="radio-inline">
    				    <input type="radio" name="valid_format" class="valid_format" value="invalid">內文不完整/格式錯誤/有非文章內文的雜訊&nbsp;&nbsp;
                    </label>
                </div>
                <br><span id="overall_polarity_hint_text"> 請標記本篇文章內，是否有缺漏、非內文的文字在內(例如廣告)、或格式上的錯誤。<br>若格式有誤，可直接跳到最後，按上傳。</span>
    			</td>
    		</tr>
            <tr class="overall_polarity_row">
    			<td class="first_col">文章與主題相關性</td>
    			<td class="second_col">
                <div>
                    <label class="radio-inline">
                        <input type="radio" name="relevance" class="relevance" value="relevant"> 與<span class="topic"><span>高度相關 &nbsp;&nbsp;
                    </label>
                    </label>
                    <label class="radio-inline">
                        <input type="radio" name="relevance" class="relevance " value="irrelevant"> 與 <span class="topic"></span>無相關&nbsp;&nbsp;
                    </label>
                </div>
    				
                <br><span id="overall_polarity_hint_text"> 請標記<strong>本篇文章</strong>與「<span class="topic"></span> 」是否相關。若只是一篇剛好提及文章關鍵字的新聞，請標記為無相關。<br>若本文與主題無相關，可直接跳到最後上傳。</span>
    			</td>
    		</tr>
            
            <tr class="overall_polarity_row">
    			<td class="first_col">文章提及正反意見</td>
    			<td class="second_col">
                <div>
                    <label class="checkbox-inline">
                        <input type="checkbox" name="user_mention_label" class="user_mention_label" value="positive"> 提及支持「<span class="statement"></span>」之論述 &nbsp;&nbsp;
                    </label>
                    </label>
                    <label class="checkbox-inline">
                        <input type="checkbox" name="user_mention_label" class="user_mention_label " value="negative"> 提及反對「<span class="statement"></span>」之論述 &nbsp;&nbsp;
                    </label>
                </div>
    				
                <br><span id="overall_polarity_hint_text"> 請標記<strong>本篇文章</strong>是否提及支持或反對「<span class="statement"></span>」的論述 (可複選) </span>
    			</td>
    		</tr>
            
    		<tr class="overall_polarity_row">
    			<td class="first_col">標記</td>
    			<td class="second_col">
                <div>
                    <label class="radio-inline">
    				    <input type="radio" name="overall_polarity" class="overall_polarity" value="agree">支持&nbsp;&nbsp;
                    </label>
                    <label class="radio-inline">
                        <input type="radio" name="overall_polarity" class="overall_polarity" value="neutral">中立 &nbsp;&nbsp;
                    </label>
                    <label class="radio-inline">
                        <input type="radio" name="overall_polarity" class="overall_polarity" value="oppose">反對&nbsp;&nbsp;
                    </label>
                </div>
    				
                <br><span id="overall_polarity_hint_text"> 請標記<span class="highlight_text">本篇文章</span>針對<span class="statement"></span> <span class="highlight_text2">整體而言</span> 表達 (1)支持、同意 (2)反對、不同意 (3)持中立立場。</span>
    			</td>
    		</tr>
    	</table>
             <button id="submit">上傳</button>
    	
             </div>

    	<!--<button id="reset">清空</button>-->
    </body>
    </html>
