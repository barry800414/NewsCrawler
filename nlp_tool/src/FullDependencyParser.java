
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.parser.nndep.DependencyParser;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import edu.stanford.nlp.trees.GrammaticalStructure;

import java.io.StringReader;
import java.util.List;

import jopencc.ZhtZhsConvertor;


/**
 * Demonstrates how to first use the tagger, then use the NN dependency
 * parser. Note that the parser will not work on untagged text.
 *
 * @author Jon Gauthier
 */
public class FullDependencyParser {
    public static void main(String[] args) {
        //initialize the converter
        System.err.println(" ===== Initializing Convertor =====");
        ZhtZhsConvertor convertor = new ZhtZhsConvertor("./jopencc");

        //initialize the segmenter
        System.err.println(" ===== Initializing Segmentor =====");
        Segmenter seg = new Segmenter("./stanford_segmenter", convertor);

        //initialize the pos-tagger 
        System.err.println(" ===== Initializing pos-tagger =====");
        FullPOSTagger tagger = new FullPOSTagger("./stanford_postagger", Lang.ZHS, 
            seg, convertor);

        //Initialize the dependency parser
        FullDependencyParser fdp = new FullDependencyParser(Lang.ZHS, tagger, 
            seg, convertor);

        //String text = "I can almost always tell when movies use fake dinosaurs.";
        String untokenizedSent = "這是一個測試用的句子";
        fdp.parseUntokenizedSent(untokenizedSent, Lang.ZHT, Lang.ZHT);

    }

    public DependencyParser parser = null; 
    public FullPOSTagger tagger = null;
    public Segmenter segmenter = null;
    public ZhtZhsConvertor convertor = null;
    public int lang = 0;

    private String modelPath = DependencyParser.DEFAULT_MODEL;

    public FullDependencyParser(int lang){
        this.lang = lang;
        if(lang == Lang.ENG){
            modelPath = "edu/stanford/nlp/models/parser/nndep/PTB_CoNLL_params.txt.gz";
        }
        else if(lang == Lang.ZHS){
            modelPath = "edu/stanford/nlp/models/parser/nndep/CTB_CoNLL_params.txt.gz"; 
        }
        parser = DependencyParser.loadFromModelFile(modelPath);
    }

    public FullDependencyParser(int lang, Segmenter segmenter){
        this(lang);
        this.segmenter = segmenter;
    }

    public FullDependencyParser(int lang, Segmenter segmenter, 
        ZhtZhsConvertor convertor){
        this(lang);
        this.segmenter = segmenter;
        this.convertor = convertor;
    }

    public FullDependencyParser(int lang, FullPOSTagger tagger, 
        Segmenter segmenter, ZhtZhsConvertor convertor){
        this(lang);
        this.tagger = tagger;
        this.segmenter = segmenter;
        this.convertor = convertor;
    }

    //get the dependency parsed results from "tokenized" and "ZHS" sentence
    public void parseTokenizedSent(String sent){
        List<TaggedWord> tagged = tagger.tagTokenizedSent(sent);
        GrammaticalStructure gs = parser.predict(tagged);
        // Print typed dependencies
        System.err.println(gs);
        //TODO
    }

    public void parseUntokenizedSent(String untokenizedSent, int inLang, int outLang){
        if(inLang == Lang.ENG){
            System.err.println("Untokenized English sentences parsing is not supported now");
            return ;    
        }

        // tokenize the sentence & converting the language
        String[] sent = null;
        sent = segmenter.segmentStr(untokenizedSent, inLang, Lang.ZHS);

        // dependency parsing
        parseTokenizedSent(mergeStr(sent));

        // convert the language if necessary
        /*
        if(outLang == Lang.ZHT){
            //TODO
            return result;
        }
        return result;*/
    }

    private String mergeStr(String[] str){
        String del = " ";
        if(str.length > 0){
            String result = "";
            for(int i = 0; i < str.length -1 ; i++){
                result = result + str[i] + del;
            }
            result = result + str[str.length - 1];
            return result;
        }
        else{
            return null;
        }
    }
}
