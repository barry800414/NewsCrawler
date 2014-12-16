import java.util.ArrayList;
import java.util.List;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.trees.Tree;

/*
	The lexicalized parser for parsing Simplfied Chinese sentences only.
*/
public class Parser{
	// Demo 
    public static void main(String[] args){
        //initialize the parser
    	Parser p = new Parser("chinese");

    	//Example 1: Parse tokenized sentences
    	String[] tokenizedSent = ["今天", "天气", "很", "好"];
    	Tree result = parseTokenizedSent(tokenizedSent);

    	//Example 2: Parse tokenized sentences 
    	//(original sentence which is separated by sep)
    	String sepSent = "今天 天气 很 好";
    	Tree result = parseSepSent(sepSent, ' ');
    }

    public static final int ZHT = 0;
	public static final int ZHS = 1;
	public static final int ENG = 2;
	public LexicalizedParser lp = null;
	private int lang = -1;
	public Parser(int lang){
		this.lang = lang;
		if(lang == Parser.ENG){
			lp = LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz");
		}
		else if(lang == Parser.ZHS){
			lp = LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz");
		}
	}
	
	public Tree parseTokenizedSent(String[] sent){
	    List<CoreLabel> rawWords = Sentence.toCoreLabelList(sent);
	    Tree parse = lp.apply(rawWords);
	    return parse;
	}
	
	public Tree parseSepSent(String sent, String sep){
		String[] tokenizedSent = sent.split(sep);
		return parseTokenizedSent(tokenizedSent);
	}
	
	public static Label[] getPOSTags(Tree parse){
		ArrayList<Label> posTags = new ArrayList<Label>();
		treeTraversalGetPOSTags(parse, posTags);
		Label[] tags = new Label[posTags.size()];
		posTags.toArray(tags);
		return tags;
	}
	
	private static boolean treeTraversalGetPOSTags(Tree t, ArrayList<Label> posTags){
		if(t.numChildren() == 0){
			return true;
		}
		else{
			boolean childIsLeave;
			for(Tree c: t.children()){
				childIsLeave = treeTraversalGetPOSTags(c, posTags);
				if(childIsLeave){
					//t.pennPrint();
					posTags.add(t.label());
					return false;
				}
			}
			return false;
		}
	}
}
