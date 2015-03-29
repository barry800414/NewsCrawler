//-------------------------------------------------------------
// Hidden Conditional Random Field Library - Implementation of
// MyFeatures: Sample class on how to create your own features
//   Similar for Raw features but returns the square value of the
//   raw features instead of the raw feature value.
//
//	June 18, 2007

#ifndef MY_FEATURES_H
#define MY_FEATURES_H

#include "featuregenerator.h"

// We dont want our feature ID to conflict with futur version.
#define WORD_CNT_FEATURE LAST_FEATURE_ID+1
#define POS_NEG_WORD_FEATURE LAST_FEATURE_ID+2
#define POS_NEG_SUM_FEATURE LAST_FEATURE_ID+3
#define DOC_LABEL_FEATURE LAST_FEATURE_ID+4
#define SENT_LABEL_FEATURE LAST_FEATURE_ID+5
#define DOC_SENT_LABEL_FEATURE LAST_FEATURE_ID+6
#define DOC_SENT_SENT_LABEL_FEATURE LAST_FEATURE_ID+7

//feature function 1: w in TOKENS(si) and y^s_i = a
//Dimension: volcSize * #hiddenStateOutcome (*#hiddenState)
class WordCntFeatures : public FeatureType
{
public:
	WordCntFeatures(int type);

	// Called once to initialize this type of features
	virtual void init(DataSet& dataset, const Model& m);
	// Called for every sample of a data sequence. Returns the features (square of the raw feature) for every states for that sample.
	virtual void getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel = -1);
	virtual bool isEdgeFeatureType();

	// Utility function: returns all possible features that this class can produce
	void getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures);

    DataSet* pDataSet;
    unsigned int nbFeaturesPerState;
    int type;
    static const int ZERO_ONE = 0;
    static const int COUNT = 1;
};

//feature function 2: w in POS_TOKENS(si) and y^s_i = a
//Dimension: PosVolcSize * #hiddenStateOutcome (*#hiddenState)
class PosNegWordOccurFeatures : public FeatureType
{
public:
	PosNegWordOccurFeatures(int type);

	// Called once to initialize this type of features
	virtual void init(DataSet& dataset, const Model& m);
	// Called for every sample of a data sequence. Returns the features (square of the raw feature) for every states for that sample.
	virtual void getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel = -1);
	virtual bool isEdgeFeatureType();

	// Utility function: returns all possible features that this class can produce
	void getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures);

    DataSet* pDataSet;
    unsigned int nbFeaturesPerState;
    int type;
    
    static const int POSITIVE = 0;
    static const int NEGATIVE = 1;

};



//feature function 4: POS_TOKENS(si) > NEG_TOKENS(si) and y^s_i = a
//Dimension: #hiddenStateOutcome (*#hiddenState)
class PosNegSumFeatures : public FeatureType
{
public:
	PosNegSumFeatures(int type, int posWeight, int negWeight);

	// Called once to initialize this type of features
	virtual void init(DataSet& dataset, const Model& m);
	// Called for every sample of a data sequence. Returns the features (square of the raw feature) for every states for that sample.
	virtual void getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel = -1);
	virtual bool isEdgeFeatureType();

	// Utility function: returns all possible features that this class can produce
	void getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures);

    DataSet* pDataSet;
    int nbFeaturesPerState;
    int type, posWeight, negWeight;

    static const int LARGER = 0;
    static const int SMALLER = 1;
    static const int EQUAL = 2;
};




class DocLabelFeatures : public FeatureType
{
public:
	DocLabelFeatures();

	// Called once to initialize this type of features
	virtual void init(DataSet& dataset, const Model& m);
	// Called for every sample of a data sequence. Returns the features (square of the raw feature) for every states for that sample.
	virtual void getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel = -1);
	virtual bool isEdgeFeatureType();

	// Utility function: returns all possible features that this class can produce
	void getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures);
    int nbFeaturesPerState;

};

class SentLabelFeatures : public FeatureType
{
public:
	SentLabelFeatures();

	// Called once to initialize this type of features
	virtual void init(DataSet& dataset, const Model& m);
	// Called for every sample of a data sequence. Returns the features (square of the raw feature) for every states for that sample.
	virtual void getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel = -1);
	virtual bool isEdgeFeatureType();

	// Utility function: returns all possible features that this class can produce
	void getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures);
    int nbFeaturesPerState;
};


class DocSentLabelFeatures : public FeatureType
{
public:
	DocSentLabelFeatures();

	// Called once to initialize this type of features
	virtual void init(DataSet& dataset, const Model& m);
	// Called for every sample of a data sequence. Returns the features (square of the raw feature) for every states for that sample.
	virtual void getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel = -1);
	virtual bool isEdgeFeatureType();

	// Utility function: returns all possible features that this class can produce
	void getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures);
    int nbFeaturesPerState;
};


class DocSentSentLabelFeatures : public FeatureType
{
public:
	DocSentSentLabelFeatures();

	// Called once to initialize this type of features
	virtual void init(DataSet& dataset, const Model& m);
	// Called for every sample of a data sequence. Returns the features (square of the raw feature) for every states for that sample.
	virtual void getFeatures(featureVector& listFeatures, DataSequence* X, Model* m, int nodeIndex, int prevNodeIndex, int seqLabel = -1);
	virtual bool isEdgeFeatureType();

	// Utility function: returns all possible features that this class can produce
	void getAllFeatures(featureVector& listFeatures, Model* m, int NbRawFeatures);
    int nbFeaturesPerState;
};



#endif 




