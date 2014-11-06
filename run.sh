#!/bin/bash
# $1 is the short name of news source
if [ "$#" -le 1 ]; then
    echo "./run.sh source_short_name debug (single_url)"
else   
    mkdir -p ./spider_data/$1
    scrapy crawl news_crawler -a config_file=$1.json -a debug=$2 -a single_url=$3 --loglevel='INFO' -s JOBDIR=./spider_data/$1 >> ./spider_data/$1/dropped_urls
fi
