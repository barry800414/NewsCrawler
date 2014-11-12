#!/bin/bash
# $1 is the short name of news source
if [ "$#" -ne 1 ]; then
    echo "./clear.sh source_short_name"
else
    rm -f *~   
    rm -rf ./spider_data/$1
fi

