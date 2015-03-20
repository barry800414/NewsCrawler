
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
Sentence::Sentence(char *sent, char *wordSep){
    char *wBuf = strtok(sent, wordSep);
    while(wBuf != NULL){
        words.push_back(atoi(wBuf));  //unsafe
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


//Class Document
Document::Document(char *article, char *sentSep, char *wordSep){
    char *s = strtok(article, sentSep);
    while(s != NULL){
        Sentence sent = Sentence(s, wordSep);
        sents.push_back(sent);
        //build wordCnt mapping
        for(vector<int>::iterator wIt = sent.words.begin(); wIt != sent.words.end(); wIt++){
            map<int, unsigned int>::iterator pos = wordCnt.find(*wIt);
            if(pos == wordCnt.end()){
                wordCnt.insert(pair<int, int>(*wIt,1));
            }
            else{
                pos->second = pos->second + 1;
            }
        }
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

int Corpus::read(ifstream *fin, char *sentSep, char *wordSep){
    string line; 
    if(fin->is_open()){
        while(getline(*fin, line)){
            char *lineBuf = new char[line.length() + 1];
            strcpy(lineBuf, line.c_str());
            docs.push_back(Document(lineBuf, sentSep, wordSep));
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

int SentiDict::read(ifstream *fin, char* sep){
    string line;
    if(fin->is_open()){
        while(getline(*fin, line)){
            char *lineBuf = new char[line.length() + 1];
            strcpy(lineBuf, line.c_str());
            char *buf = strtok(lineBuf, sep);
            int cnt = 0, wId, senti;
            while(buf != NULL){
                if(cnt == 0){
                    wId = atoi(buf);
                }
                else if(cnt == 1){
                    senti = atoi(buf);
                    d.insert(pair<int, int>(wId, senti));
                }
                else{
                    cerr << "Sentiment dictionary file error" << endl;
                }
                cnt = cnt + 1;
                strtok(NULL, buf);
            }
        }
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







int main(int argc, char* argv[]) {
    return 0;
}
