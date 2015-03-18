
#include<vector>
#include<map>

using namespace std;

// a sentence
class Sentence{
    public:
        Sentence(char *sent, char *wordSep);
        ostream& operator<<(ostream &strm, const Sentence &s);
        string toString();
        vector<int> words;
};

//a document 
class Document{
    public:
        Document(char *article, char *sentSep, char *wordSep);
        string toString();
        ostream& operator<<(ostream &strm, const Document &d);

        //vector<int>::iterator wordIt();
        bool hasWord(int word);
        unsigned int wordCount(int word);
        vector<Sentence> sents;
        map<int, unsigned int> wordCnt;
};

//whole corpus, which consists of documents
class Corpus{
    public:
        Corpus(char *filename, char *sentSep, char *wordSep);
        string toString();
        ostream& operator<<(ostream &strm, const Corpus &c);

        vector<Document> docs;
        
};

//sentiment dictionary
class SentiDict{
    public:
        SentiDict(char *filename, char *sep);
        string toString();
        ostream& operator<<(ostream &strm, const SentiDict &s);

        int getSenti(int word);
        map<int, int> d;
};


