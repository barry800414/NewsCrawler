PACKAGE=./stanford_segmenter/stanford-segmenter-3.5.0.jar:./stanford_parser/*:./jopencc/
JAVA_PATH=~/package/jdk1.8.0_25/bin

SRC=./src
BIN=./bin
FILE=./hotel_training_s_seg.txt
ASPECT_FILE=./aspect.csv
OPINION_FILE=./opinion.csv
PREDICT_FILE=./hotel_training_t_seg

PART1_FILE=./hotel_training_t_seg.txt
PART1_OUT_PRE=./hotel_training_t_seg
PART2_FILE=./hotel_testing_t_seg.txt
PART2_OUT_PRE=./hotel_testing_t_seg

METHOD=2
W_SIZE=3
N_SIZE=2

all: compile part1 part2

convertor_compile:
	$(JAVA_PATH)/javac -cp "./jopencc/src" -d ./jopencc ./jopencc/src/jopencc/ZhtZhsConvertor.java 
	
#convertor demo
convertor: convertor_compile
	$(JAVA_PATH)/java -cp "./jopencc" jopencc.ZhtZhsConvertor ./jopencc

segmenter_compile: convertor_compile
	$(JAVA_PATH)/javac -cp "$(PACKAGE):./bin:./src" -d ./bin ./src/Segmenter.java

#segmentor demo
segmenter: segmenter_compile
	$(JAVA_PATH)/java -cp "$(PACKAGE):./bin" Segmenter 

parser_compile: segmenter_compile
	$(JAVA_PATH)/javac -cp "$(PACKAGE):./bin:./src" -d ./bin ./src/FullParser.java

# full parser demo
parser: parser_compile
	$(JAVA_PATH)/java -cp "$(PACKAGE):./bin" FullParser

server_compile: segmenter_compile
	$(JAVA_PATH)/javac -cp "$(PACKAGE):./bin:./src" -d ./bin ./src/NLPToolServer.java

server: server_compile
	$(JAVA_PATH)/java -cp "$(PACKAGE):./bin" NLPToolServer



part1: compile
	$(JAVA_PATH)/javac -cp "$(PACKAGE):$(SRC)" $(SRC)/Main.java -d $(BIN)
	#java -mx5000m -cp "$(PACKAGE):$(BIN)" Main $(FILE)

part2: compile
	javac -cp "$(PACKAGE):$(SRC)" $(SRC)/Main_Part2.java -d $(BIN)
	java -mx5000m -cp "$(PACKAGE):$(BIN)" Main_Part2 $(METHOD) $(W_SIZE) $(N_SIZE) $(PART1_FILE) $(PART2_FILE) $(ASPECT_FILE) $(OPINION_FILE) $(PART1_OUT_PRE)_W$(W_SIZE)_N$(N_SIZE).predict $(PART2_OUT_PRE)_W$(W_SIZE)_N$(N_SIZE).predict

clean:
	rm -f ./bin/*
