The way to preprocess
============================
    insert_topics.py
    ./preprocess_table.py preprocess_table.json db_info.json
    ./merge.py table_info.json db_info.json
    ./filter.py topic_config.json db_info.json
    ./rm_duplicate.py topic_config.json db_info.json
    ./preprocess_news.py preprocess_news.json db_info.json


To add more news
============================


Clean news 
============================
cleaned_news_part1.json: all valid & small error news in statement_news before 2015/3/31
cleaned_news_part2.json: all news in topic_news after 2015/4/9 (topic3 has been added)
