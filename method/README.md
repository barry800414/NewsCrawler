
How to merge label, news and statement?
------------------=
     ./dataPreprocess.py label.json parsedNews.json/taggerNews.json/segNews.json preStat.json mergeConfig.json tfidf_labelNews.json

Please first edit mergeConfig.json to select the field you want. The use the command to merge them.



Word Model
------------------
    python3 ./baseline/WordModel.py WM_labelNews.json
    python3 ./baseline/WordModelImproved.py taggedLabelNews.json [volcFile]

OneLayerDepModel
------------------
    python3 ./DepBased/OneLayerDepModel.py OLPDM_labelNews.json

OneLayerPhraseDepModel 
------------------
    python3 ./DepBased/ExtractPhrases.py ./zhtNewsData/constParsedNews.json ./DepBased/phrase.json
    python3 ./DepBased/OneLayerPhraseDepModel.py OLPDM_labelNews.json ./DepBased/phrase.json ./res/NTUSD_core.csv


OpinionModel
------------------
    python3 OpinionModel.py DepParsedLabelNews ModelConfigFile TreePatternFile NegPatternFile SentiDictFile [-p PhraseFile] [-v VolcFile]
    python3 ./DepBased/OpinionModel.py ./zhtNewsData/OLPDM_labelNews_20150504.json ./DepBased/config/OM_all_config.json ./DepBased/my_pattern.json ./DepBased/negPattern.json ./res/NTUSD_core.csv -v ./WordClustering/cluster7852_300.volc


LDA
------------------
    python3 LDA_Model.py ../zhtNewsData/taggedNews.json topWords TW_Matrix volc.txt


tmp
------------------
python3 ./DepBased/ExtractPhrases.py ./zhtNewsData/constParsedNews20150419_new.json ./DepBased/phrase.json

python3 ./baseline/WordModelImproved.py ./zhtNewsData/taggedLabelNews20150504.json ./WordClustering/cluster7852_tag100.volc
 python3 ./DepBased/OneLayerPhraseDepModel.py ./zhtNewsData/OLPDM_labelNews_20150504.json ./res/NTUSD_core.csv -p ./DepBased/phrase.json -v ./WordClustering/cluster7852_tag100.volc

python3 ./DepBased/OpinionModel.py ./zhtNewsData/OLPDM_labelNews_20150504.json ./DepBased/config/OM_H_config.json ./DepBased/my_pattern.json ./DepBased/negPattern.json ./res/NTUSD_core.csv

python3 ./DepBased/WM_OLPDM.py ./zhtNewsData/taggedAndDepParsedLabelNews20150504.json ./DepBased/phrase.json ./res/NTUSD_core.csv WM_20150504_params.json OLPDM_20150504_params.json


Merged Model
------------------
WM+OLDM
python3 ./DepBased/MergedModel.py ./zhtNewsData/taggedAndDepParsedLabelNews20150504.json ./DepBased/config/OM_H_config.json ./res/NTUSD_core.csv -WM ./WM_cluster7852_300_params.json -OLDM ./OLDM_cluster7852_300_params.json -v ./WordClustering/cluster7852_300.volc > WM_OLDM_cluster7852_300_results.csv

WM+OM
python3 ./DepBased/MergedModel.py ./zhtNewsData/taggedAndDepParsedLabelNews20150504.json ./DepBased/config/OM_H_config.json ./res/NTUSD_core.csv -WM ./WM_cluster7852_300_params.json -OM ./OM_all_cluster7852_300_params.json -v ./WordClustering/cluster7852_300.volc -tp ./DepBased/my_pattern.json -ng ./DepBased/negPattern.json  > WM_OM_cluster7852_300_results.csv

WM+OLDM+OM

Collect Results
------------------
python3 CollectResult.py MacroF1 WM20150504_results.csv WM_20150504_params.json 1 7
