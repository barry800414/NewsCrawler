
trainData=../../samples/C++/dataTrain.csv 
#trainLabel=../../samples/C++/labelsTrain.csv 
trainLabel=../../samples/C++/seqLabelsTrain.csv
testData=../../samples/C++/dataTest.csv
#testLabel=../../samples/C++/labelsTest.csv 
testLabel=../../samples/C++/seqLabelsTest.csv
model=model.txt
results=results.txt

./hcrfTest -t -TT -d $trainData -l $trainLabel -D $testData -L $testLabel -m $model -r $results -a hcrf -h 5 -i 100
