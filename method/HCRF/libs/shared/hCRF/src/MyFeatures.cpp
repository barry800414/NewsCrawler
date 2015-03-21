#include "MyFeatures.h"

MyFeatures::MyFeatures():FeatureType()
{
	strFeatureTypeName = "My Feature Type";
	featureTypeId = MY_FEATURE_ID;
}

void MyFeatures::getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel)
{
	// If raw/precomputed features are available and the getFeatures() call is for state features
	if(X->getPrecomputedFeatures() != NULL && prevNodeIndex == -1)
	{
		dMatrix * preFeatures = X->getPrecomputedFeatures();
		int nbFeatures = preFeatures->getHeight();
		feature* pFeature;
		int nbStateLabels = m->getNumberOfStates();

		// For every possible state
		for(int s = 0; s < nbStateLabels; s++)
		{
			// For every features in the precomputed feature matrix
			for(int f = 0; f < nbFeatures; f++)
			{
				pFeature = listFeatures.addElement();
				pFeature->id = getIdOffset(seqLabel) + f + s*nbFeatures;
				pFeature->globalId = getIdOffset() + f + s*nbFeatures;
				pFeature->nodeIndex = nodeIndex;
				pFeature->nodeState = s;
				pFeature->prevNodeIndex = -1;
				pFeature->prevNodeState = -1;
				pFeature->sequenceLabel = seqLabel;
				// Returns the square of the precomputed value
				pFeature->value = preFeatures->getValue(f,nodeIndex) * preFeatures->getValue(f,nodeIndex); // TODO: optimize
			}
		}
	}
}

void MyFeatures::getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures)
{
	int nbStateLabels = m->getNumberOfStates();
	feature* pFeature;

	// For every possible state
	for(int s = 0; s < nbStateLabels; s++)
	{
		// For every features in the precomputed feature matrix
		for(int f = 0; f < NbRawFeatures; f++)
		{
			pFeature = listFeatures.addElement();
			pFeature->id = getIdOffset() + f + s*NbRawFeatures;
			pFeature->globalId = getIdOffset() + f + s*NbRawFeatures;
			pFeature->nodeIndex = featureTypeId;
			pFeature->nodeState = s;
			pFeature->prevNodeIndex = -1;
			pFeature->prevNodeState = -1;
			pFeature->sequenceLabel = -1;
			pFeature->value = f; 
		}
	}
}


// Determine the number of features
void MyFeatures::init(const DataSet& dataset, const Model& m)
{
	FeatureType::init(dataset,m);
	if(dataset.size() > 0)
	{
		int nbStates = m.getNumberOfStates();
		int nbSeqLabels = m.getNumberOfSequenceLabels();
		int nbFeaturesPerStates = dataset.at(0)->getPrecomputedFeatures()->getHeight();

		nbFeatures = nbStates * nbFeaturesPerStates;
		for(int i = 0; i < nbSeqLabels; i++)
			nbFeaturesPerLabel[i] = nbFeatures;
	}
}

bool MyFeatures::isEdgeFeatureType()
{
	return false;
}


/***********************************************************************
 *
 *  Feature function 1: w in TOKENS(si) and y^s_i = a
 *  Dimension: volcSize * #HiddenState * #SentenceLabelOutcome
 *
 * *********************************************************************
 * */

WordOccurFeatures::WordOccurFeatures():FeatureType()
{
	strFeatureTypeName = "Word occurence feature (0/1)";
	featureTypeId = 100; //TODO
}

//get features of certain state with certain label
void WordOccurFeatures::getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel)
{
	// If raw/precomputed features are available and the getFeatures() call is for state features
	if(X->getPrecomputedFeatures() != NULL && prevNodeIndex == -1)
	{
        //This precomputed feature matrix is 1 x #HiddenState, the value is the document ID.
        //TODO: check matrix size
        dMatrix * preFeatures = X->getPrecomputedFeatures(); 
        feature* pFeature;
		int nbState = m->getNumberOfStates();

		// For every possible state
		for(int s = 0; s < nbState; s++)
		{
			//for each word in volcabulary
            for(int f = 0; f < nbFeatures; f++)
			{
				pFeature = listFeatures.addElement();
				pFeature->id = getIdOffset(seqLabel) + f + s*nbFeatures;
				pFeature->globalId = getIdOffset() + f + s*nbFeatures;
				pFeature->nodeIndex = nodeIndex;
				pFeature->nodeState = s;
				pFeature->prevNodeIndex = -1;
				pFeature->prevNodeState = -1;
				pFeature->sequenceLabel = seqLabel;
				
                int docId = (int) preFeatures->getValue(0, nodeIndex);
                Document doc = pDataSet->corpus->docs.at(docId);
                if(doc.hasWord(f)){
                    pFeature->value = 1.0;
                }
                else{
                    pFeature->value = 0.0;
                }
			}
		}
	}
}

//TODO
void WordOccurFeatures::getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures)
{
	int nbStateLabels = m->getNumberOfStates();
	feature* pFeature;

	// For every possible state
	for(int s = 0; s < nbStateLabels; s++)
	{
		// For every features in the precomputed feature matrix
		for(int f = 0; f < NbRawFeatures; f++)
		{
			pFeature = listFeatures.addElement();
			pFeature->id = getIdOffset() + f + s*NbRawFeatures;
			pFeature->globalId = getIdOffset() + f + s*NbRawFeatures;
			pFeature->nodeIndex = featureTypeId;
			pFeature->nodeState = s;
			pFeature->prevNodeIndex = -1;
			pFeature->prevNodeState = -1;
			pFeature->sequenceLabel = -1;
			pFeature->value = f; 
		}
	}
}


// Determine the number of features(dimension)
void WordOccurFeatures::init(const DataSet& dataset, const Model& m)
{
	FeatureType::init(dataset,m);
    
    //pointer to dataset
    pDataSet = &dataset;

	if(dataset.size() > 0)
	{
		int nbStates = m.getNumberOfStates();
		int nbSeqLabels = m.getNumberOfSequenceLabels();
        const int nbFeaturesPerStates = pDataSet->corpus->volcSize; //depends on volcabulary size

		nbFeatures = nbStates * nbFeaturesPerStates;
		for(int i = 0; i < nbSeqLabels; i++){
			nbFeaturesPerLabel[i] = nbFeatures;
        }
	}
}

bool WordOccurFeatures::isEdgeFeatureType()
{
	return false;
}
