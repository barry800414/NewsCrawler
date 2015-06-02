#!/bin/zsh
gsed "s/<95>//g" \
|gsed "s/》//g" \
|gsed "s/《//g" \
|gsed "s/〔.*〕//g" \
|gsed "s/加入粉絲團列印本頁 轉寄//g" \
|gsed "s/\.//g" \
|gsed "s/（整理.*）//g" \
|gsed "s/(整理.*)//g" \
|gsed "s/(台北市.*）//g" \
|gsed "s/★//g" \
|gsed "s/按我報名===>請點選此處//g" \
|gsed "s/==//g" \
|gsed "s/…//g" \
|gsed "s/-//g" \
|gsed "s/\[.*\]//g" \
|gsed "s/拍賣頁面：//g"  \
|gsed "s/^記者.*\n//g" \
|gsed "s/～//g" \
|gsed "s/\~//g" \
|gsed "s/特派記者.....報導//g" \
|gsed "s/記者.....報導//g" \
|gsed "s/鳳凰衛視報導//g" \
|gsed "s/（連絡人：.*）//g" \
|gsed "s/＊//g" \
|gsed "s/综合報導//g" \
|gsed "s/\/ 綜合報導//g" \
|gsed "s/公視新聞//g" \
|gsed "s/◎//g" \
|gsed "s/新聞稿//g" \
|gsed "s/(作者.*)//g" \
|gsed "s/(見圖.*)//g" \
|gsed "s/新聞稿//g" \
|gsed "s/（tinyurlcomk6uyg3g）//g"\
|gsed "s/\\t/ /g"\
|gsed "s/上一篇：//g" \
|gsed "s/相關新聞：//g" \
|gsed "s/各界看法//g" \
|gsed "s/詳見下圖//g" \
|gsed "s/()//g" \
|gsed "s/記者.*SNG小組//g" \
|gsed "s/高雄報導//g" \
|gsed "s/記者林建成//g" \
|gsed "s/蘋果日報//g" \
|gsed "s/( )//g" \
|gsed "s/▼//g" \
|gsed "s/點標籤觀看更多本週NGO新聞影音//g" \
|gsed "s/更多本週NGO新聞影音//g" \
|gsed "s/環球時報//g" \
|gsed "s/記者提問//g" \
|gsed "s/環球網//g" \
|gsed "s/點標籤看//g" \
|gsed "s/台北[0-9]日電//g" \
|gsed "s/文字翻譯//g" \
|gsed "s/語音口譯//g" \
|gsed "s/資料來源//g" \
|gsed "s/台北[0-9]日電//g" \
|gsed "s/A2版財經要聞//g" \
|gsed "s/記者...\/...報導//g" \
|gsed "s/記者..\/...報導//g" \
|gsed "s/記者...\/..報導//g" \
|gsed "s/記者..\/..報導//g" \
|gsed "s/記者.........高雄//g" \
|gsed "s/記者楊文琪//g" \
|gsed "s/整理 \/ 鐘聖雄、張岱屏、胡慕情；攝影 \/ 張光宗//g" \
|gsed "s/\+//g" \
|gsed "s/#//g" \
|gsed "s/\?{2,}//g" \
|gsed "s/\///g" \
|gsed "s/、//g" \
|gsed "s/立報//g" \
|gsed "s/\bb.*@\w*//g" \
|gsed "s/記者黃驛淵//g" \
|gsed "s/曼谷.日專電//g" \
|gsed "s///g"

#|gsed "s/^[ \t]*//;s/[ \t]*$//g"
#|gsed "s/一、      時間：.*//g" \
#|gsed "s/報名：.*//g" \
#|gsed "s/^[ \t]*//g" \
#|gsed "s/[\t ]*$//g"
#|gsed "s/台北[0-9]日電//g"

#|gsed "s/\.{2,}//g" \

#|gsed "s/\d\d\d\d-\d\d\d-\d\d\d//g"
#|gsed "s/\d\d\d\d\/\d\d\/\d\d//g" \
#|gsed "s/\d\d\d\d\/\d\d//g" \



#|gsed "s/()//g"  


#gsed "s/^M//g" \
#| gsed "s/(\([^()]*\))/\n\1\n/g" \
#| tr '\n' ' ' \

#| gsed "s/(\([^()]*\))/\n\1\n/g" \
#| gsed "s/\"\([^\"]*\)\"/\n\1\n/g" \
#| gsed "s/\'\([^\']*\)\'/\n\1\n/g" \
#| gsed "s/\[[^][]*\]//g" \
#| gsed "s/[,:\/\' ]/ /g" \
#| gsed "s/[\?\!\.;]/\n/g" \
#| gsed "s/[^a-zA-Z0-9 ]/ /g" \
#| gsed "s/./\L&/g" \
#| gsed "s/ [ ]*/ /g" \
#| gsed "/^$/d" \
#| gsed "/^[^ ]*$/d" \
#| gsed "s/[^[:print:]]//g" \
#| gsed "s/^/<s> /" \
#| gsed "s/$/ <\/s>/"
