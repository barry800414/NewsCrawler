# coding=utf-8
import urlparse

url = "HTTP://www.Python.org/docs/?ada=dasd#dsa"

print urlparse.urldefrag(url)


from scrapy.selector import Selector
from scrapy.http import HtmlResponse

body = '<td class="story_title"><div style="float:left">wait 13 year</div><div id=bq  style="float:right">sdadsadsa<IFRAME height=25 src="/2010/AD/CAMPUS_BQ.html" frameBorder=0 width=150 scrolling=no></IFRAME></div></td>'

body2 = '''<td class="story_author">

            <a href="author_arts.jsp?f_AUTHOR=%BC%C6%A6%EC%B8%EA%B0%54" class="story_author">Digital Info</a> 2014/10/23
            
                      </td>'''

print Selector(text=body2).xpath("//td[@class='story_author']/text()").extract()


body3 = '''<div id="newstext" class="text ">
    <span>2014-11-05</span>
    <p>〔記者吳亮儀／台北報導〕總統馬英九、台北市長郝龍斌上週五陪同國民黨台北市長候選人連勝文到東區龍門廣場拜票，再度引發部分民眾不滿；北市副議長周柏雅指出，連營未向廣場所有權人台北捷運公司申請付費、捷運公司也沒有做處置，嚴重違反行政中立。</p><H4>捷運公司：僅短暫集結</H4><p>對此，台北捷運公司昨發布聲明，當天有派員到現場查看，認為只是掃街前短暫集結，也有人員提醒該廣場不得從事競選活動。</p><p>周柏雅說，馬英九與郝龍斌為連勝文到東區掃街拜票，還占據人行空間發表演說拉票好幾分鐘，明顯與一般民眾只是去廣場集合不同；且根據捷運公司出借規定，競選活動、政黨黨務活動、政治性議題活動都不能借，「不管怎樣都是不合規定」。</p><p>周柏雅痛批，馬英九、郝龍斌與特定市長候選人不尊重民主機制在先，北市府與台北捷運公司又公然屢次大開方便門給予特定候選人超級市民待遇，嚴重違反行政中立。</p><p>捷運公司重申，對上週的掃街活動和以往其他活動都採派員注意現場，確認只是暫時集結，並未持續使用。捷運公司強調，捷運各相關場所一律禁止競選活動，若有發現，先予勸阻並通報捷運警察處理。</p>
    <div id="newspic" class="pic ">
    <div id="newsad" class="ad">廣告</div>
    <ul id="newsphoto" class="photo300 liadd">
        <li><a href="/photo/local/paper/509626"><img onError="imgErr(this)" onLoad="imgLoad(this)" src="http://img.ltn.com.tw/2014/new/nov/5/images/bigPic/400_400/190.jpg" alt="上週五連勝文等人到東區龍門廣場拜票，引發部分民眾不（記者簡榮豐攝）" title="上週五連勝文等人到東區龍門廣場拜票，引發部分民眾不（記者簡榮豐攝）" /></a>
        <p>上週五連勝文等人到東區龍門廣場拜票，引發部分民眾不（記者簡榮豐攝）</p></li>
          <script>
          
          $("#newsad").hide();
          function NewsPicAd(){
            return false;
        }
        
        </script>
        </ul>
        <div id="newspicpg" class="pg"></div>
        </div>
        <script>
        
        newspicnum = $("#newsphoto a").length;
        //newspicchange(1);
        $("#newspicpg").hide();
        if(newspicnum==0)
            $("#newspic").hide();
            $('#newstext > p:lt(2)').each(function(i){ if ($(this).html().length>70 || i>0){ $(this).after($("#newspic")); //NewsPicAd();
             return false; }});
         
         </script></div>'''

a = Selector(text=body3).xpath("//div[@id='newstext']/p/text()").extract()

print a
