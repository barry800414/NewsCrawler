#!/bin/bash 
for i in 2 3 4 5 6 10 13 16 
do 
    #python3 colorWordList.py  ./tf/Stat${i}_VA_wordFrequency.txt ntu_sentiment_dict.csv ./color_tf/Stat${i}_VA_colored.txt
    #python3 colorWordList.py  ./tf/Stat${i}_VV_wordFrequency.txt ntu_sentiment_dict.csv ./color_tf/Stat${i}_VV_colored.txt
    #python3 colorWordList.py  ./tf/Stat${i}_NN_wordFrequency.txt ntu_sentiment_dict.csv ./color_tf/Stat${i}_NN_colored.txt
    #python3 colorWordList.py  ./tf/Stat${i}_NR_wordFrequency.txt ntu_sentiment_dict.csv ./color_tf/Stat${i}_NR_colored.txt
    #python3 colorWordList.py  ./tf/Stat${i}_JJ_wordFrequency.txt ntu_sentiment_dict.csv ./color_tf/Stat${i}_JJ_colored.txt
    python3 colorWordList.py  ./tf/Stat${i}_AD_wordFrequency.txt ntu_sentiment_dict.csv ./color_tf/Stat${i}_AD_colored.txt

done

