#!/bin/bash

## declare an array variable
declare -a arr=("tag100" "100" "tag300" "300" "tag500" "500")
#declare -a arr=("tag100" "100" "300")

#declare -a arr=("H" "T" "OT" "HO" "HOT" "HT" "H_T_HT" "all")
#declare -a arr=("HT" "H_T_HT" "all")

#file=WM_7852_testing.csv
file=OLDM_corpus_testing.csv
#file=OM_testing.csv

## now loop through the above array
for i in "${arr[@]}"
do  
    echo "$i"
    #echo "WM $i" >> ${file}
    #python3 CollectResult.py MacroF1 ./WM_cluster7852_${i}_results.csv 01.json 0 7 >> ${file}
    
    echo "OLDM $i" >> ${file}
    python3 CollectResult.py MacroF1 ./OLDM_cluster_corpus_${i}_results.csv 01.json 0 7 >> ${file}

    #echo "OM $i" >> ${file}
    #python3 CollectResult.py MacroF1 ./OM_${i}_results.csv 01.json 7 >> ${file}

done
