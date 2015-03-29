#include "MyFeatures.h"

/*
 * seqLabel: looks like docuement level label
 * state: outcome of that hidden state(not the index of hidden variable)
 */

/***********************************************************************
 *  Feature function 1: w in TOKENS(si) and y^s_i = a  (ZERO_ONE or COUNT)
 *  Dimension: volcSize * #HiddenState * #SentenceLabelOutcome
 * *********************************************************************
 * */
WordCntFeatures::WordCntFeatures(int type):FeatureType()
{
	strFeatureTypeName = "Word occurence feature 0/1 or count";
	featureTypeId = WORD_CNT_FEATURE; 
    this->type = type;
}

//get features of certain state with certain label
void WordCntFeatures::getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel)
{
	// If raw/precomputed features are available and the getFeatures() call is for state features
	if(X->getPrecomputedFeatures() != NULL && prevNodeIndex == -1)
	{
        //std::cerr << "In get Features, in getprecomputedfeatures != NULL" << std::endl;
        //This precomputed feature matrix is 1 x #HiddenState, the value is the document ID.
        //TODO: check matrix size
        dMatrix* preFeatures = X->getPrecomputedFeatures(); 
        feature* pFeature;
		int nbState = m->getNumberOfStates();

		// For every possible outcome of this hidden variable(y_i)
		for(int s = 0; s < nbState; s++)
		{
			//for each word in volcabulary
            for(unsigned int f = 0; f < nbFeaturesPerState; f++)
			{
				pFeature = listFeatures.addElement();
				pFeature->id = getIdOffset(seqLabel) + f + s*nbFeaturesPerState;
				pFeature->globalId = getIdOffset() + f + s*nbFeaturesPerState;
				pFeature->nodeIndex = nodeIndex;
				pFeature->nodeState = s;
				pFeature->prevNodeIndex = -1;
				pFeature->prevNodeState = -1;
				pFeature->sequenceLabel = seqLabel;
				pFeature->value = 0.0; //default

                int docIndex = (unsigned int) preFeatures->getValue(0, nodeIndex);
                int sentIndex = (unsigned int) nodeIndex;

                Sentence *sent = pDataSet->getSent(docIndex, sentIndex);
                if(sent != NULL){
                    int wordId = f;
                    if(this->type == WordCntFeatures::ZERO_ONE){
                        if(sent->hasWord(wordId)){
                            pFeature->value = 1.0;
                        }
                    }
                    else if(this->type == WordCntFeatures::COUNT){
                        pFeature->value = sent->wordCount(wordId);
                    }
                }
            }
		}
	}
    //std::cerr << "in getFeatures, outside" << std::endl;
}

void WordCntFeatures::getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures)
{
    std::cerr << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!In getAllFeature" << std::endl;
}


// Determine the number of features(dimension)
void WordCntFeatures::init(DataSet& dataset, const Model& m)
{
	FeatureType::init(dataset,m);
    
    //pointer to dataset
    pDataSet = &dataset;
    
	if(dataset.size() > 0)
	{
		int nbStates = m.getNumberOfStates();
		int nbSeqLabels = m.getNumberOfSequenceLabels();
        nbFeaturesPerState = pDataSet->corpus->volcSize; //depends on volcabulary size

		nbFeatures = nbStates * nbFeaturesPerState;

		for(int i = 0; i < nbSeqLabels; i++){
			nbFeaturesPerLabel[i] = nbFeatures;
        }
	}

}

bool WordCntFeatures::isEdgeFeatureType()
{
	return false;
}



/***********************************************************************
 * feature function 2: w in POS_TOKENS(si) and y^s_i = a  (POSITIVE or NEGATIVE)
 * Dimension: PosVolcSize * #hiddenStateOutcome (*#hiddenState)
 * *********************************************************************
 * */

PosNegWordOccurFeatures::PosNegWordOccurFeatures(int type):FeatureType()
{
	strFeatureTypeName = "Positive or negative word occurence feature 0/1 ";
	featureTypeId = POS_NEG_WORD_FEATURE;
    this->type = type;
}

//get features of certain state with certain label
void PosNegWordOccurFeatures::getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel)
{
	// If raw/precomputed features are available and the getFeatures() call is for state features
	if(X->getPrecomputedFeatures() != NULL && prevNodeIndex == -1)
	{
        //std::cerr << "In get Features, in getprecomputedfeatures != NULL" << std::endl;
        //This precomputed feature matrix is 1 x #HiddenState, the value is the document ID.
        //TODO: check matrix size
        dMatrix * preFeatures = X->getPrecomputedFeatures(); 
        feature* pFeature;
		int nbState = m->getNumberOfStates();

		// For every possible outcome of this hidden variable(y_i)
		for(int s = 0; s < nbState; s++)
		{
			//for each word in volc
            for(unsigned int f = 0; f < nbFeaturesPerState; f++)
			{
				pFeature = listFeatures.addElement();
				pFeature->id = getIdOffset(seqLabel) + f + s*nbFeaturesPerState;
				pFeature->globalId = getIdOffset() + f + s*nbFeaturesPerState;
				pFeature->nodeIndex = nodeIndex;
				pFeature->nodeState = s;
				pFeature->prevNodeIndex = -1;
				pFeature->prevNodeState = -1;
				pFeature->sequenceLabel = seqLabel;
				pFeature->value = 0.0; //default

                unsigned int docIndex = (unsigned int) preFeatures->getValue(0, nodeIndex);
                unsigned int sentIndex = (unsigned int) nodeIndex;
                Sentence *sent = pDataSet->getSent(docIndex, sentIndex);
                SentiDict *sentiDict = pDataSet->sentiDict;

                //f is the word id in postive dictionary, here we convert it into corpus word id
                int wordId = f;
                if(sent != NULL && sentiDict != NULL){
                    if(sent->hasWord(wordId)){
                        if(this->type == PosNegWordOccurFeatures::POSITIVE && sentiDict->getSenti(wordId) > 0){
                            pFeature->value = 1.0;
                        }
                        else if(this->type == PosNegWordOccurFeatures::NEGATIVE && sentiDict->getSenti(wordId) < 0){
                            pFeature->value = 1.0;
                        }
                    }
                }
			}
		}
	}
    //std::cerr << "in getFeatures, outside" << std::endl;
}

void PosNegWordOccurFeatures::getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures)
{
    std::cerr << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!In getAllFeature" << std::endl;
}


// Determine the number of features(dimension)
void PosNegWordOccurFeatures::init(DataSet& dataset, const Model& m)
{
	FeatureType::init(dataset,m);
    
    //pointer to dataset
    pDataSet = &dataset;
    

	if(dataset.size() > 0)
	{
		int nbStates = m.getNumberOfStates(); //cardinality(#outcome) of hidden variable)
		int nbSeqLabels = m.getNumberOfSequenceLabels(); //cardinality of document-level label

        nbFeaturesPerState = pDataSet->corpus->volcSize; //depends on positive volcabulary size
        nbFeatures = nbStates * nbFeaturesPerState;
		for(int i = 0; i < nbSeqLabels; i++){
			nbFeaturesPerLabel[i] = nbFeatures;
        }
	}
}

bool PosNegWordOccurFeatures::isEdgeFeatureType()
{
	return false;
}

/***********************************************************************
 * feature function 3: POS_TOKEN(si) >/=/< NEG_TOKENS(si) and y^s_i = a
 * Dimension: #hiddenStateOutcome (*#hiddenState)
 * *********************************************************************
 * */
PosNegSumFeatures::PosNegSumFeatures(int type, int posWeight, int negWeight):FeatureType()
{
	strFeatureTypeName = "#POS_TOKEN(si) >/=/< #NEG_TOKEN(si) feature";
	featureTypeId = POS_NEG_SUM_FEATURE;
    this->type = type;
    this->posWeight = posWeight;
    this->negWeight = negWeight;
}

void PosNegSumFeatures::getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel)
{
	// If raw/precomputed features are available and the getFeatures() call is for state features
	if(X->getPrecomputedFeatures() != NULL && prevNodeIndex == -1)
	{
        //std::cerr << "In get Features, in getprecomputedfeatures != NULL" << std::endl;
        //This precomputed feature matrix is 1 x #HiddenState, the value is the document ID.
        //TODO: check matrix size
        dMatrix * preFeatures = X->getPrecomputedFeatures(); 
        feature* pFeature;
		int nbState = m->getNumberOfStates();

		// For every possible outcome of this hidden variable(y_i)
		for(int s = 0; s < nbState; s++)
		{
			pFeature = listFeatures.addElement();
			pFeature->id = getIdOffset(seqLabel) + s;
			pFeature->globalId = getIdOffset() + s;
			pFeature->nodeIndex = nodeIndex;
			pFeature->nodeState = s;
			pFeature->prevNodeIndex = -1;
			pFeature->prevNodeState = -1;
			pFeature->sequenceLabel = seqLabel;
		    pFeature->value = 0.0; //default

            unsigned int docIndex = (unsigned int) preFeatures->getValue(0, nodeIndex);
            unsigned int sentIndex = (unsigned int) nodeIndex;
            Sentence *sent = pDataSet->getSent(docIndex, sentIndex);
            SentiDict *sentiDict = pDataSet->sentiDict;
            
            //calculate the number of the set of POS WORDS and the set of NEG WORDS
            int polarity = 0;
            for(map<int, unsigned int>::iterator wIt=sent->wordCnt.begin(); wIt != sent->wordCnt.end(); ++wIt){
                int senti = sentiDict->getSenti(wIt->first);
                if(senti > 0){
                    polarity += this->posWeight;
                }
                else if(senti < 0){
                    polarity -= this->negWeight;
                }
            }    
            if(this->type == PosNegSumFeatures::LARGER && polarity > 0){
                pFeature->value = 1.0;
            }		
            else if(this->type == PosNegSumFeatures::SMALLER && polarity < 0){
                pFeature->value = 1.0;
            }
            else if(this->type == PosNegSumFeatures::EQUAL && polarity == 0){
                pFeature->value = 1.0;
            }		
		}
	}
   // std::cerr << "in getFeatures, outside" << std::endl;
}

void PosNegSumFeatures::getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures)
{
    std::cerr << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!In getAllFeature" << std::endl;
}

// Determine the number of features(dimension)
void PosNegSumFeatures::init(DataSet& dataset, const Model& m)
{
	FeatureType::init(dataset,m);
    
    //pointer to dataset
    pDataSet = &dataset;

	if(dataset.size() > 0)
	{
		int nbStates = m.getNumberOfStates(); //cardinality(#outcome) of hidden variable)
		int nbSeqLabels = m.getNumberOfSequenceLabels(); //cardinality of document-level label

        nbFeaturesPerState = 1; //depends on positive volcabulary size
		nbFeatures = nbStates * nbFeaturesPerState;
		for(int i = 0; i < nbSeqLabels; i++){
			nbFeaturesPerLabel[i] = nbFeatures;
        }
	}
}

bool PosNegSumFeatures::isEdgeFeatureType()
{
	return false;
}



/***********************************************************************
 * feature function 4: Document label feature (node potential)
 * Dimension: #DocumentLabelOutcome
 * *********************************************************************
 * */
DocLabelFeatures::DocLabelFeatures():FeatureType()
{
	strFeatureTypeName = "#POS_TOKEN(si) >/=/< #NEG_TOKEN(si) feature";
	featureTypeId = DOC_LABEL_FEATURE;
}

void DocLabelFeatures::getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel)
{
	// If raw/precomputed features are available and the getFeatures() call is for state features
	if(prevNodeIndex == -1)
	{
        feature* pFeature;

		pFeature = listFeatures.addElement();
		pFeature->id = getIdOffset(seqLabel);
		pFeature->globalId = getIdOffset();
        pFeature->nodeIndex = -1; //??
        pFeature->nodeState = -1; //??
        pFeature->prevNodeIndex = -1;
        pFeature->prevNodeState = -1;
        pFeature->sequenceLabel = seqLabel;
        pFeature->value = 1.0; //default

	}
}

void DocLabelFeatures::getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures)
{
    std::cerr << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!In getAllFeature" << std::endl;
}

// Determine the number of features(dimension)
void DocLabelFeatures::init(DataSet& dataset, const Model& m)
{
	FeatureType::init(dataset,m);
	if(dataset.size() > 0)
	{
		int nbSeqLabels = m.getNumberOfSequenceLabels(); //cardinality of document-level label
		nbFeatures = 1;
		for(int i = 0; i < nbSeqLabels; i++){
			nbFeaturesPerLabel[i] = nbFeatures;
        }
	}
}

bool DocLabelFeatures::isEdgeFeatureType()
{
	return false;
}



/***********************************************************************
 * feature function 5: sentence-label feature (node potential for hidden variable)
 * Dimension: #hiddenStateOutcome
 * *********************************************************************
 * */
SentLabelFeatures::SentLabelFeatures():FeatureType()
{
	strFeatureTypeName = "Hidden variable outcome feature";
	featureTypeId = SENT_LABEL_FEATURE;
}

void SentLabelFeatures::getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel)
{
	if(prevNodeIndex == -1)
	{
        feature* pFeature;
		int nbState = m->getNumberOfStates();

		// For every possible outcome of this hidden variable(y_i)
		for(int s = 0; s < nbState; s++)
		{
			pFeature = listFeatures.addElement();
			pFeature->id = getIdOffset(seqLabel) + s;
			pFeature->globalId = getIdOffset() + s;
			pFeature->nodeIndex = nodeIndex;
			pFeature->nodeState = s;
			pFeature->prevNodeIndex = -1;
			pFeature->prevNodeState = -1;
			pFeature->sequenceLabel = seqLabel;
		    pFeature->value = 1.0; //default
		}
	}
}

void SentLabelFeatures::getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures)
{
    std::cerr << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!In getAllFeature" << std::endl;
}

// Determine the number of features(dimension)
void SentLabelFeatures::init(DataSet& dataset, const Model& m)
{
	FeatureType::init(dataset,m);
    
	if(dataset.size() > 0)
	{
		int nbStates = m.getNumberOfStates(); //cardinality(#outcome) of hidden variable)
		int nbSeqLabels = m.getNumberOfSequenceLabels(); //cardinality of document-level label

        nbFeaturesPerState = 1; 
		nbFeatures = nbStates * nbFeaturesPerState;
		for(int i = 0; i < nbSeqLabels; i++){
			nbFeaturesPerLabel[i] = nbFeatures;
        }
	}
}

bool SentLabelFeatures::isEdgeFeatureType()
{
	return false;
}




/***********************************************************************
 * feature function 6: Document-label and Sentence-label features
 * Dimension: #hiddenVariableOutcome (*#docLabelOutcome)
 * *********************************************************************
 * */
DocSentLabelFeatures::DocSentLabelFeatures():FeatureType()
{
	strFeatureTypeName = "Document-label and Sentence-label features";
	featureTypeId = DOC_SENT_LABEL_FEATURE;
}

void DocSentLabelFeatures::getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel)
{
	if(prevNodeIndex == -1)
	{
        feature* pFeature;
		int nbState = m->getNumberOfStates();

		// For every possible outcome of this hidden variable(y_i)
		for(int s = 0; s < nbState; s++)
		{
			pFeature = listFeatures.addElement();
			pFeature->id = getIdOffset(seqLabel) + s;
			pFeature->globalId = getIdOffset() + s;
			pFeature->nodeIndex = nodeIndex;
			pFeature->nodeState = s;
			pFeature->prevNodeIndex = -1;
			pFeature->prevNodeState = -1;
			pFeature->sequenceLabel = seqLabel;
            pFeature->value = 0.0; //default
            
            if(seqLabel == s){
                pFeature->value = 1.0;
            }
		}
	}
}

void DocSentLabelFeatures::getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures)
{
    std::cerr << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!In getAllFeature" << std::endl;
}

// Determine the number of features(dimension)
void DocSentLabelFeatures::init(DataSet& dataset, const Model& m)
{
	FeatureType::init(dataset,m);
    
	if(dataset.size() > 0)
	{
		int nbStates = m.getNumberOfStates(); //cardinality(#outcome) of hidden variable)
		int nbSeqLabels = m.getNumberOfSequenceLabels(); //cardinality of document-level label

        nbFeaturesPerState = 1; 
		nbFeatures = nbStates * nbFeaturesPerState;
		for(int i = 0; i < nbSeqLabels; i++){
			nbFeaturesPerLabel[i] = nbFeatures;
        }
	}
}

bool DocSentLabelFeatures::isEdgeFeatureType()
{
	return false;
}




/***********************************************************************
 * feature function 7: Document-label and Sentence-label, Sentence-label  features
 * Dimension: #hiddenVariableOutcome^2 (*#docLabelOutcome)
 * *********************************************************************
 * */
DocSentSentLabelFeatures::DocSentSentLabelFeatures():FeatureType()
{
	strFeatureTypeName = "Document-label and Sentence-label, Sentence-label features";
	featureTypeId = DOC_SENT_SENT_LABEL_FEATURE;
}

void DocSentSentLabelFeatures::getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel)
{
	int nbNodes = -1;
	
	if(X->getPrecomputedFeatures())
		nbNodes = X->getPrecomputedFeatures()->getWidth();
	else
		nbNodes = (int)X->getPrecomputedFeaturesSparse()->getWidth();
	
	if( ((prevNodeIndex == nodeIndex-1) || prevNodeIndex == nodeIndex-1 + nbNodes) && (prevNodeIndex != -1)){
        feature* pFeature;
        int nbState = m->getNumberOfStates();

        // For every possible outcome of this hidden variable(y_i)
        for(int s1 = 0; s1 < nbState; s1++)
        {
            for(int s2 = 0; s2 < nbState; s2++){
                pFeature = listFeatures.addElement();
                pFeature->id = getIdOffset(seqLabel) + s2 + s1*nbFeaturesPerState;
                //pfeature->globalid = getidoffset() + s2 + s1*nbfeaturesperstate + seqLabel*nbState*nbState ;
                pFeature->globalId = getIdOffset() + s2 + s1*nbFeaturesPerState;
                pFeature->nodeIndex = nodeIndex;
                pFeature->nodeState = s2;
                pFeature->prevNodeIndex = prevNodeIndex;
                pFeature->prevNodeState = s1;
                pFeature->sequenceLabel = seqLabel;
                pFeature->value = 1.0;
            }
        }
    }
}

void DocSentSentLabelFeatures::getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures)
{
    std::cerr << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!In getAllFeature" << std::endl;
}

// Determine the number of features(dimension)
void DocSentSentLabelFeatures::init(DataSet& dataset, const Model& m)
{
	FeatureType::init(dataset,m);
    
	if(dataset.size() > 0)
	{
		int nbStates = m.getNumberOfStates(); //cardinality(#outcome) of hidden variable
		int nbSeqLabels = m.getNumberOfSequenceLabels(); //cardinality of document-level label

        if(nbSeqLabels == 0){
            nbFeatures = nbStates * nbStates;
        }
        else{
            nbFeaturesPerState = nbStates; //depends on cardinality of hidden variable
		    nbFeatures = nbStates * nbStates;
		    for(int i = 0; i < nbSeqLabels; i++){
			    nbFeaturesPerLabel[i] = nbFeatures;
            }
        }
	}
}

//this is edge feature
bool DocSentSentLabelFeatures::isEdgeFeatureType()
{
	return true;
}





