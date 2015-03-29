
#include<vector>
#include<map>

using namespace std;

// a sentence
class Sentence{
    public:
        Sentence(char *sent, const char *wordSep);
        friend ostream& operator<<(ostream &strm, const Sentence& s);
        string toString() const;
        void addWord(int word);
        
        int getWord(unsigned int index);
        bool hasWord(int word);
        unsigned int wordCount(int word);
        
        vector<int> words;
        map<int, unsigned int> wordCnt;
};


//a document 
class Document{
    public:
        Document(char *article,const char *sentSep,const char *wordSep);
        string toString() const;
        friend ostream& operator<<(ostream &strm, const Document& d);

        //vector<int>::iterator wordIt();
        void addSent(char *sent, const char *wordSep);

        Sentence * getSent(unsigned int index);
        bool hasWord(int word);
        unsigned int wordCount(int word);
        
        vector<Sentence> sents;
        map<int, unsigned int> wordCnt;
};

//whole corpus, which consists of documents
class Corpus{
    public:
        Corpus();
        //Corpus(char *filename, char *sentSep, char *wordSep);
        //Corpus(ifstream *fin, char *sentSep, char *wordSep);
        int read(ifstream *fin, const char *sentSep,const char *wordSep);
        string toString() const;
        friend ostream& operator<<(ostream &strm, const Corpus& c);

        Document * getDoc(unsigned int index);
        Sentence * getSent(unsigned int docIndex, unsigned sentIndex);
        
        vector<Document> docs;
        unsigned int volcSize;
        
};

//sentiment dictionary
class SentiDict{
    public:
        SentiDict();
        //SentiDict(char *filename, char *sep);
        int read(ifstream *fin,const char *sep);
        string toString() const;
        friend ostream& operator<<(ostream &strm, const SentiDict& s);

        int getSenti(int word);
        //int getWordIdInCorpus(int oriWordId, int posOrNeg);
        map<int, int> d;
        //map<int, int> posWordIdMapping; //word id in positive lexicon -> word id in corpus
        //map<int, int> negWordIdMapping; //word id in negative lexicon -> word id in corpus
        //unsigned int posVolcSize;
        //unsigned int negVolcSize;
        //static const int POS_WORD = 1;
        //static const int NEG_WORD = -1;
};

