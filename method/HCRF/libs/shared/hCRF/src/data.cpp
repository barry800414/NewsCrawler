
#include<vector>
#include<map>
#include<fstream>
#include<string>
#include<iostream>
#include<string.h>
#include<stdlib.h>

#include "data.h"

using namespace std;

//Class Sentence
Sentence::Sentence(char *sent, const char *wordSep){
    char *wBuf = strtok(sent, wordSep);
    while(wBuf != NULL){
        addWord(atoi(wBuf)); //unsafe
        wBuf = strtok(NULL, wordSep);
    }
}

string Sentence::toString() const{
    string str = "Sentence:"; 
    for(vector<int>::const_iterator wIt = words.begin(); wIt != words.end(); ++wIt){
        str += *wIt + " ";
    }
    return str;
}

ostream& operator<<(ostream &strm, const Sentence& s){
    return strm << s.toString() << endl;
}

int Sentence::getWord(unsigned int index){
    if(index >= words.size()){
        return -1;
    }
    else{
        return words.at(index);
    }
}

void Sentence::addWord(int word){
    words.push_back(word);
    map<int, unsigned int>::iterator it = wordCnt.find(word);
    if(it == wordCnt.end()){
        wordCnt.insert(pair<int, unsigned int> (word, 1));
    }
    else{
        it->second += 1;
    }
}
        
bool Sentence::hasWord(int word){
    return (wordCnt.find(word) != wordCnt.end()) ;
}

unsigned int Sentence::wordCount(int word){
    map<int, unsigned int>::iterator it = wordCnt.find(word);
    if(it == wordCnt.end()){
        return 0;
    }
    else{
        return it->second;
    }
}



//Class Document
Document::Document(char *article, const char *sentSep, const char *wordSep){
    char *s = strtok(article, sentSep);
    while(s != NULL){
        addSent(s, wordSep);
        s = strtok(NULL, sentSep);
    }
}

string Document::toString() const{
    string str = "Document:\n";
    for(vector<Sentence>::const_iterator sIt = sents.begin(); sIt != sents.end(); ++sIt){
        str += sIt->toString() + "\n";    
    }
    return str;
}

ostream& operator<<(ostream &strm, const Document &d){
    return strm << d.toString() << endl;
}

void Document::addSent(char *sent, const char *wordSep){
    Sentence *s = new Sentence(sent, wordSep);
    sents.push_back(*s);
    
    //build wordCnt mapping
    for(vector<int>::iterator wIt = s->words.begin(); wIt != s->words.end(); wIt++){
        map<int, unsigned int>::iterator pos = wordCnt.find(*wIt);
        if(pos == wordCnt.end()){
            wordCnt.insert(pair<int, int>(*wIt,1));
        }
        else{
            pos->second = pos->second + 1;
        }
    }
}

Sentence * Document::getSent(unsigned int index){
    if(index >= sents.size()){
        return NULL;  
    }
    else{
        return &sents.at(index); 
    }
}

bool Document::hasWord(int word){
    return (wordCnt.find(word) != wordCnt.end()) ;
}

unsigned int Document::wordCount(int word){
    map<int, unsigned int>::iterator pos = wordCnt.find(word);
    if(pos == wordCnt.end()){
        return 0;
    }
    else{
        return pos->second;
    }
}


//Class Corpus
/*
Corpus::Corpus(char *filename, char *sentSep, char *wordSep){
    ifstream *fin = new ifstream(filename);
    if(fin == NULL){
        cerr << "Open file failure:" << filename << endl;
    }
    else{
        Corpus(fin, sentSep, wordSep);
        delete fin;
    }
}*/
Corpus::Corpus(){
}

int Corpus::read(ifstream *fin,const char *sentSep,const char *wordSep){
    string line; 
    unsigned int docNum;
    if(fin->is_open()){
        //second line: #doc volcabulary_size
        if(getline(*fin, line)){
            sscanf(line.c_str(), "%u%u", &docNum, &volcSize);
        }
        else{
            cerr << "Corpus file error: second line error" << endl;
        }
        unsigned int i; 
        for(i = 0; i < docNum; i++){
            if(!getline(*fin, line)){
                cerr << "Data number inconsistent" << endl;
                return 1;
            }
            char *lineBuf = new char[line.length() + 1];
            strcpy(lineBuf, line.c_str());
            Document *doc = new Document(lineBuf, sentSep, wordSep);
            docs.push_back(*doc);
        }
        return 0; //success
    }
    else{
        cerr << "input filestream invalid" << endl;
        return 1; //fail
    }
}

string Corpus::toString() const{
    string str = "Corpus:\n";
    for(vector<Document>::const_iterator dIt = docs.begin(); dIt != docs.end(); ++dIt){
        str += dIt->toString() + "\n";
    }
    return str;
}

ostream& operator<<(ostream &strm, const Corpus &c){
    return strm << c.toString();
}

Document * Corpus::getDoc(unsigned int index){
    if(index >= docs.size()){
        return NULL;
    }
    else{
        return &docs.at(index);
    }
}

Sentence * Corpus::getSent(unsigned int docIndex, unsigned int sentIndex){
    Document * doc = getDoc(docIndex);
    if(doc != NULL){
        return doc->getSent(sentIndex);
    }
    else{
        return NULL;
    }
}

//Class SentiDict
/*
SentiDict::SentiDict(char *filename, char* sep){
    ifstream *fin = new ifstream(filename);
    if(fin == NULL){
        cerr << "Open file failure:" << filename << endl;
    }
    else{
        SentiDict(fin, sep);
        delete fin;
    }
}*/

//Class SentiDict
SentiDict::SentiDict(){
}

int SentiDict::read(ifstream *fin,const char* sep){
    string line;
    if(fin->is_open()){ 
        /*
        //ignore first line, if NULL, return error
        if(!getline(*fin, line)){
            cerr << "Sentiment dictionary file error: no content in file" << endl;
        }
        //second line: #POS_WORD #NEG_WORD
        if(getline(*fin, line)){
            sscanf(line.c_str(), "%u%u", &posVolcSize, &negVolcSize);
        }
        else{
            cerr << "Corpus file error: second line error" << endl;
        }*/
        while(getline(*fin, line)){
            char *lineBuf = new char[line.length() + 1];
            strcpy(lineBuf, line.c_str());
            char *buf = strtok(lineBuf, sep);
            int cnt = 0, wId, newWId, senti;
            while(buf != NULL){
                if(cnt == 0){
                    wId = atoi(buf); //word id in corpus
                }
                /*
                else if(cnt == 1){
                    newWId = atoi(buf); //word id in pos/neg dict
                }*/
                else if(cnt == 1){
                    senti = atoi(buf);
                    d.insert(pair<int, int>(wId, senti));
                    /*
                    if(senti > 0 && posWordIdMapping.find(newWId) == posWordIdMapping.end()){
                        posWordIdMapping.insert(pair<int, int>(newWId, wId));
                    }
                    else if(senti < 0 && negWordIdMapping.find(newWId) == negWordIdMapping.end()){
                        negWordIdMapping.insert(pair<int, int>(newWId, wId));
                    }*/ 
                }
                else{
                    cerr << "Sentiment dictionary file error" << endl;
                }
                cnt = cnt + 1;
                buf = strtok(NULL, sep);
            }
        }
        /*
        if(posWordIdMapping.size() != posVolcSize){
            cerr << "Positive word number inconsistent" << endl;
            return 1;
        }
        if(negWordIdMapping.size() != negVolcSize){
            cerr << "Negative word number inconsistent" << endl;
            return 1;
        }*/
        return 0; //success
    }
    else{
        cerr << "Input stream error" << endl;
        return 1; //fail
    }
}


string SentiDict::toString() const{
    string str = "Seniment Dictionary: \n";
    for(map<int, int>::const_iterator wsIt = d.begin(); wsIt != d.end(); ++wsIt){
        str += wsIt->first + ' ' + wsIt->second + '\n';
    }
    return str;
}

ostream& operator<<(ostream &strm, const SentiDict &s){
    return strm << s.toString() << endl;
}


int SentiDict::getSenti(int word){
    map<int, int>::iterator pos = d.find(word);
    if(pos == d.end()){
        return 0;
    }
    else{
        return pos->second;
    }
}
/*
int SentiDict::getWordIdInCorpus(int oriWordId, int posOrNeg){
    if(posOrNeg == SentiDict::POS_WORD){
        return posWordIdMapping.find(oriWordId)->second;
    }
    else if(posOrNeg == SentiDict::NEG_WORD){
        return negWordIdMapping.find(oriWordId)->second;
    }
    else{
        return -1;
    }
}*/

/*
int main(int argc, char* argv[]) {
    return 0;
}*/
