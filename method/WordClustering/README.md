
Run LDA Model
---------------------------
Run LDA model on text data
    python3 LDA_Model.py TaggedNewsJsonFile TopTopicWordFile WordTopicMatrixPrefix Volcabulary
    e.g. python3 LDA_Model.py ~/codes/AgreementPrediction/method/zhtNewsData/taggedNews_all.json topTopicWords.txt WTMatrix volc.txt

Run Word2Vec
---------------------------
Run word2vec(RNN) model on text data, output word vector file

Convert word vector file to numpy(npy) file
---------------------------
    python3 convertWordVector.py InWordVectorFile(text) OutWordVectorFile(npy) volcFile -wt
    e.g. python3 convertWordVector.py news7852.vector news7852.npy news7852_volc.txt
    e.g. python3 ./ConvertWordVector.py news7852Final.vector ../DepBased/entity_tag_topic4.npy ../DepBased/entity_tag_topic4_volc.txt -wc ../DepBased/entity_tag_topic4.txt 0 -es ../DepBased/entity_tag_topic4_excluded.txt

Run WordTag 
---------------------------
Get tag of words 
    python3 WordTag.py TaggedNewsJsonFile WordTagFile
    e.g. python3 WordTag.py ~/codes/AgreementPrediction/method/zhtNewsData/taggedNews_all.json wordTag7852.txt



Run Word Clustering
---------------------------
    python3 WordClustering.py WordVector volcFile nCluster outWordCluster [WordTagFile]
    e.g. python3 WordClustering.py news7852.npy news7852_volc.txt 100 cluster7852_tag100.txt wordTag_news7852.txt


