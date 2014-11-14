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
                        //$("#source").text(response["source"]);
                        $("#title").text(data["news_title"]);
                        $("#content").html(content_preprocess(data["news_content"]));
                        $("#url").text(data["news_url"]);
                        $("#url").attr("href", data["news_url"]);
                    }
                }
            });
        }

        function content_preprocess(content){
            return content.replace("\n", "<br><br>");
        }

        function checkInput(){
        	var user_label=$(".user_label:checked").val();
        	console.log(user_label);

        	var err_msg="";

        	if(typeof(user_label)=='undefined'){
        		err_msg += "請選擇標記\n";
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
        	var user_label=$(".user_label:checked").val();
        	var statement_id = $("#statement_id").val();
        	var news_id = $("#news_id").val();
        	var user_id = 'user123';
        	$.ajax({
        		type: "POST",
        		url: "upload_annotation.php",
        		data: { 
        			label: user_label,
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
        				alert("上傳失敗QQQQQ，請聯絡barry800414@gmail.com");
        			}
        		}
        	});
        }

        function reset(){
        	$(".user_label").attr("checked", false);
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
            <h2 class="title"> 「文章」對「敘述句」支持/反對/中立預測 資料庫建立頁面 </h2>
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
                                        <td class="first_col">敘述句<br>(論點)</td>
                                        <td class="second_col"><span id="statement" class="second_col"></span></td>
                            </tr>
    		<tr class="user_label_row">
    			<td class="first_col">標記</td>
    			<td class="second_col">
                                        <div>
                                            <label class="radio-inline">
    				<input type="radio" name="user_label" class="user_label" value="agree">支持&nbsp;&nbsp;
                                            </label>
                                            <label class="radio-inline">
                                            <input type="radio" name="user_label" class="user_label" value="neutral">中立 &nbsp;&nbsp;
                                            </label>
                                            <label class="radio-inline">
                                            <input type="radio" name="user_label" class="user_label" value="oppose">反對&nbsp;&nbsp;
                                            </label>
                                            <label class="radio-inline">
                                                <input type="radio" name="user_label" class="user_label" value="both_agree_oppose">同時支持與反對&nbsp;&nbsp;
                                            </label>
                                        <label class="radio-inline">
                                            <input type="radio" name="user_label" class="user_label " value="irrelevant"> 無相關&nbsp;&nbsp;
                                        </label>
                                        </div>
    				
    				
                                        <br><span id="user_label_hint_text"> 請標記<strong>本篇文章</strong>對於這個<strong>論點</strong>表達 (1)支持、同意 (2)反對、不同意 (3)持中立立場  (4)同時支持與不支持  (5)文章與敘述句主題無關。</span>
    			</td>
    		</tr>
    	</table>
             <button id="submit">上傳</button>
    	
             </div>

    	<!--<button id="reset">清空</button>-->
    </body>
    </html>
