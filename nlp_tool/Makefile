PACKAGE=./stanford_segmenter/stanford-segmenter-3.5.0.jar:./stanford_parser/*:./stanford_postagger/*:./jopencc/
JAVA_PATH=~/package/jdk1.8.0_25/bin

#convertor (ZHT <-> ZHS)
convertor_compile:
	$(JAVA_PATH)/javac -cp "./jopencc/src" -d ./jopencc ./jopencc/src/jopencc/ZhtZhsConvertor.java 
	
convertor: convertor_compile
	$(JAVA_PATH)/java -cp "./jopencc" jopencc.ZhtZhsConvertor ./jopencc

#segmenter
segmenter_compile: convertor_compile
	$(JAVA_PATH)/javac -cp "$(PACKAGE):./bin:./src" -d ./bin ./src/Segmenter.java

segmenter: segmenter_compile
	$(JAVA_PATH)/java -cp "$(PACKAGE):./bin" Segmenter 

# POS tagger
tagger_compile: segmenter_compile
	$(JAVA_PATH)/javac -cp "$(PACKAGE):./bin:./scr" -d ./bin ./src/FullPOSTagger.java

tagger: tagger_compile
	$(JAVA_PATH)/java -cp "$(PACKAGE):./bin:./src" FullPOSTagger

# full dependency parser
dep_parser_compile: tagger_compile
	$(JAVA_PATH)/javac -cp "$(PACKAGE):./bin:./scr" -d ./bin ./src/FullDependencyParser.java

dep_parser: dep_parser_compile
	$(JAVA_PATH)/java -cp "$(PACKAGE):./bin:./src" FullDependencyParser

# full constituent parser 
parser_compile: segmenter_compile
	$(JAVA_PATH)/javac -cp "$(PACKAGE):./bin:./src" -d ./bin ./src/FullParser.java

parser: parser_compile
	$(JAVA_PATH)/java -cp "$(PACKAGE):./bin" FullParser

server_compile: segmenter_compile
	$(JAVA_PATH)/javac -cp "$(PACKAGE):./bin:./src" -d ./bin ./src/NLPToolServer.java

server: server_compile
	$(JAVA_PATH)/java -cp "$(PACKAGE):./bin" NLPToolServer

