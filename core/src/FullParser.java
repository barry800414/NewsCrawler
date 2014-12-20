
import edu.stanford.nlp.trees.Tree;

import jopencc.ZhtZhsConvertor;

/*
	The parser which contains zht<->zht converter, 
	stanford segmenter and stanford parser
	Date: 2014/12/15
*/
public class FullParser extends Parser{
	public static void main(String[] args){
		//initialize the converter
        System.err.println(" ===== Initializing Convertor =====");
        ZhtZhsConvertor convertor = new ZhtZhsConvertor("./jopencc");

        //initialize the segmenter
        System.err.println(" ===== Initializing Segmentor =====");
        Segmenter seg = new Segmenter("./stanford_segmenter", convertor);
        
        //intialize the parser
        System.err.println(" ===== Initializing Parser =====");
        FullParser parser = new FullParser(Lang.ZHS, seg, convertor);

        String untokenizedSent = "今天天氣很好，我早餐吃蛋餅";
        Tree result = parser.parseUntokenizedSent(untokenizedSent, Lang.ZHT, Lang.ZHT);
        result.pennPrint();
        System.out.println();
        
	}
	
	private Segmenter segmenter;
	private ZhtZhsConvertor convertor;
	public FullParser(int lang, Segmenter segmenter){
		super(lang);
		this.segmenter = segmenter;
	}

	public FullParser(int lang, Segmenter segmenter, ZhtZhsConvertor convertor){
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

}
