
trainData=../../samples/C++/dataTrain.csv 
trainLabel=../../samples/C++/labelsTrain.csv 
testData=../../samples/C++/dataTest.csv
testLabel=../../samples/C++/labelsTest.csv 
model=model.txt
results=results.txt

./hcrfTest -t -TT -d $trainData -l $trainLabel -D $testData -L $testLabel -m $model -r $results
