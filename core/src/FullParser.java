
import Segmenter;
import Parser; 

/*
	The parser which contains zht<->zht converter, 
	stanford segmenter and stanford parser
	Date: 2014/12/15
*/
public class FullParser extends Parser{
	public static void main(String[] args){

	}
	
	private Segmenter segmenter;
	public FullParser(int lang, String segPath){
		super(lang);
		segmenter = new Segmenter(segPath);
	}

	public FullParser(int lang, String segPath, String jopenccPath){
		super(lang);
		segmenter = new Segmenter(segPath, jopenccPath);
	}

	public Tree parseZhtSent(String sent){
		String[] tokenizedSent = s.segmentStrZht(sent)
	}

	//sent: untokenized sentence
	public Tree parseUntokenizedSent(String untokenizedSent, int inLang, int outLang){
		if(inLang == Parser.ENG){
			System.err.println("Untokenized English sentences parsign is not supported now");
			return null;	
		}

		// tokenize the sentence & converting the language
		String[] sent = null;
		if(inLang == Parser.ZHT){
			//convert to zhs -> segment(tokenize)
			sent = segmenter.segmentStr(untokenizedSent, ZhtZhsConvertor.ZHT, ZhtZhsConvertor.ZHS);
		}
		else if(inLang == Parser.ZHS){
			//segment(tokenize)
			sent = segmenter.segmentStr(untokenizedSent, ZhtZhsConvertor.ZHS, ZhtZhsConvertor.ZHS);
		}

		// parse
		Tree result = parseTokenizedSent(sent);

		// convert the langauga if necessary
		if(outLang == Parser.ZHT){
			
		}

	}

}