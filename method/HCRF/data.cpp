
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

string Sentence::toString(){
    string str = "Sentence:"; 
    for(vector<int> wIt = a.words.begin(); wIt != a.end(); ++wIt){
        str += wIt + " ";
    }
    return str;
}

ostream& Sentence::operator<<(ostream &strm, const Sentence &s){
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

string Document::toString(){
    string str = "Document:\n";
    for(vector<Sentence> sIt = sents.begin(); sIt != sents.end(); ++sIt){
        str += sIt->toString() + "\n";    
    }
    return str;
}

ostream& Document::operator<<(ostream &strm, const Document &d){
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
Corpus::Corpus(char *filename, char *sentSep, char *wordSep){
    ifstream fin(filename);
    string line; 
    if(fin.is_open()){
        while(getline(fin, line)){
            char *lineBuf = new char[line.length() + 1];
            strcpy(lineBuf, line.c_str());
            docs.push_back(Document(lineBuf, sentSep, wordSep));
        }
        fin.close();
    }
    else{
        cerr << "Cannot open " << filename << endl;
    }
}

string Corpus::toString(){
    string str = "Corpus:\n";
    for(vector<Document>::iterator dIt = docs.begin(); dIt != docs.end(); ++dIt){
        str += dIt->toString() + "\n";
    }
    return str;
}

ostream& Corpus::operator<<(ostream &strm, const Corpus &c){
    return strm << c.toString();
}


//Class SentiDict
SentiDict::SentiDict(char *filename, char* sep){
    ifstream fin(filename);
    string line;
    if(fin.is_open()){
        while(getline(fin, line)){
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
        fin.close();
    }
    else{
        cerr << "Cannot open " << filename << endl;
    }
}

string SentiDict::toString(){
    string str = "Seniment Dictionary: \n";
    for(map<int, int>::iterator wsIt = d.begin(); wsIt != d.end(); ++wsIt){
        str += wsIt->first + " " + wsIt->second + "\n";
    }
    return str;
}

ostream& SentiDict::operator<<(ostream &strm, const SentiDict &s){
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
