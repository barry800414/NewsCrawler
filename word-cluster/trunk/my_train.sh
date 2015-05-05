#./word2vec -train ./my_folder/Preprocess.txt -output all_content_vector.bin cbow 1 -size 300 -window 8 -negative 0 -hs 1 -sample 1e-3 -thread 12 -binary 1 -class
#./word2vec -train ./my_folder/Preprocess.txt -output classes_new_400.txt -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -iter 15 -classes 400
sort classes_new_400.txt -k 2 -n > classes_new.sorted_400
echo The word classes were saved to file classes_new.sorted_1.txt
