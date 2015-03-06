
import java.util.List;

 
import edu.stanford.nlp.ling.IndexedWord;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.trees.international.pennchinese.ChineseTreebankLanguagePack;

import com.chaoticity.dependensee.*;
import jopencc.ZhtZhsConvertor;

/*
	The parser which contains zht<->zht converter, 
	stanford segmenter and stanford parser.
    This parser can be used to output constituent
    parsing and dependency parsing.
	Date: 2014/12/15
    Last Update: 2015/02/28
*/
public class FullPCFGParser extends PCFGParser{
	public static void main(String[] args){
		//initialize the converter
        System.err.println(" ===== Initializing Convertor =====");
        ZhtZhsConvertor convertor = new ZhtZhsConvertor("./jopencc");

        //initialize the segmenter
        System.err.println(" ===== Initializing Segmentor =====");
        Segmenter seg = new Segmenter("./stanford_segmenter", convertor);
        
        //intialize the parser
        System.err.println(" ===== Initializing PCFGParser =====");
        FullPCFGParser fpp = new FullPCFGParser(Lang.ZHS, seg, convertor);

        String untokenizedSent = "今天天氣很好，我早餐吃蛋餅";
        Tree parse = fpp.parseUntokenizedSent(untokenizedSent, Lang.ZHT, Lang.ZHT);
        System.out.println("Constituent parsing:");
        parse.pennPrint();
        System.out.println("Dependency parsing:");
        List<TypedDependency> tdl = fpp.toTypedDependency(parse);
        System.out.println(DepToString.TDsToString(tdl));

    }
	
	private Segmenter segmenter;
	private ZhtZhsConvertor convertor;
    public String[] tokenizedSentBuffer = null;

	public FullPCFGParser(int lang, Segmenter segmenter){
		super(lang);
		this.segmenter = segmenter;
	}

	public FullPCFGParser(int lang, Segmenter segmenter, ZhtZhsConvertor convertor){
		super(lang);
		this.segmenter = segmenter;
		this.convertor = convertor;
	}

	//sent: untokenized sentence
	public Tree parseUntokenizedSent(String untokenizedSent, int inLang, int outLang){
		if(inLang == Lang.ENG){
			System.err.println("Untokenized English sentences parsign is not supported now");
			return null;	
		}

		// tokenize the sentence & converting the language
		String[] sent = null;
		sent = segmenter.segmentStr(untokenizedSent, inLang, Lang.ZHS);

		// parse
		Tree result = parseTokenizedSent(sent);

		// convert the language if necessary
		if(outLang == Lang.ZHT){
			//TODO
			return result;
		}
		return result;
	}

    public List<TypedDependency> depParseUntokenizedSent(String untokenizedSent, 
            int inLang, int outLang, String imgPath){
        if(inLang == Lang.ENG){
			System.err.println("Untokenized English sentences parsign is not supported now");
			return null;	
		}

        // tokenize the sentence & converting the language
        tokenizedSentBuffer = segmenter.segmentStr(untokenizedSent, inLang, Lang.ZHS);

		// constituent parsing
		Tree parse = parseTokenizedSent(tokenizedSentBuffer);
    
        // convert to typed dependencies
        List<TypedDependency> tdl = toTypedDependency(parse);

		// convert the language if necessary
		if(outLang == Lang.ZHT){
		    tdl = wordToZht(tdl); 
            tokenizedSentBuffer = wordToZht(tokenizedSentBuffer);
            //TODO: the conversion from zhs to zht is inperfect
        }

        //drawing the dependency tree
        if(imgPath != null){
            drawDepTree(parse, tdl, imgPath, 3);
        }

		return tdl;
    }

    // convert to dependency parsing 
    public List<TypedDependency> toTypedDependency(Tree parse){
        GrammaticalStructure gs = gsf.newGrammaticalStructure(parse);
        List<TypedDependency> tdl = gs.typedDependenciesCCprocessed();
        return tdl;
    }

    public String getTokenizedSentBuffer(){
        return mergeStr(tokenizedSentBuffer);
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

    public void drawDepTree(Tree parse, List<TypedDependency> tdl, String filePrefix, int scale){
        //drawing image
        try {
            DepDrawer.writeImage(parse, tdl, filePrefix + ".png" , scale);
        }
        catch(Exception e){
            e.printStackTrace();
        }
    }

    public TypedDependency wordToZht(TypedDependency td){
        IndexedWord g = td.gov();
        IndexedWord d = td.dep();

        g.setWord(convertor.convertToZht(g.word()));
        d.setWord(convertor.convertToZht(d.word()));

        return td;
    }

    public List<TypedDependency> wordToZht(List<TypedDependency> tdl){
        for(int i = 0; i < tdl.size(); i++){
            tdl.set(i, wordToZht(tdl.get(i)));
        }
        return tdl;
    }

    public String[] wordToZht(String[] text){
        for(int i = 0; i < text.length; i++){
            text[i] = convertor.convertToZht(text[i]);
        }
        return text;
    }


}
