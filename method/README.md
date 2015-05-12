
How to merge label, news and statement?
===================
     ./dataPreprocess.py label.json parsedNews.json/taggerNews.json/segNews.json preStat.json mergeConfig.json tfidf_labelNews.json

Please first edit mergeConfig.json to select the field you want. The use the command to merge them.



Word Model
==================
    python3 ./baseline/WordModel.py WM_labelNews.json
    python3 ./baseline/WordModelImproved.py taggedLabelNews.json [volcFile]

OneLayerDepModel
==================
    python3 ./DepBased/OneLayerDepModel.py OLPDM_labelNews.json

OneLayerPhraseDepModel 
==================
    python3 ./DepBased/ExtractPhrases.py ./zhtNewsData/constParsedNews.json ./DepBased/phrase.json
    python3 ./DepBased/OneLayerPhraseDepModel.py OLPDM_labelNews.json ./DepBased/phrase.json ./res/NTUSD_core.csv





LDA
==================
    python3 LDA_Model.py ../zhtNewsData/taggedNews.json topWords TW_Matrix volc.txt


tmp
==================
python3 ./DepBased/ExtractPhrases.py ./zhtNewsData/constParsedNews20150419_new.json ./DepBased/phrase.json
python3 ./DepBased/OneLayerPhraseDepModel.py ./zhtNewsData/OLPDM_labelNews_20150504.json ./res/NTUSD_core.csv -p ./DepBased/phrase.json
