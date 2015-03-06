import java.util.ArrayList;
import java.util.List;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.trees.*;

import com.chaoticity.dependensee.*;
/*
	The lexicalized parser for parsing Simplfied Chinese sentences only.
	Besides, it does not support untokenized sentence
*/
public class PCFGParser{
	// Demo 
    public static void main(String[] args){
        //initialize the parser
    	PCFGParser p = new PCFGParser(Lang.ZHS);

    	//Example 1: Parse tokenized sentences
    	String[] tokenizedSent = {"今天", "天气", "很", "好"};
    	Tree result = p.parseTokenizedSent(tokenizedSent);

    	//Example 2: Parse tokenized sentences 
    	//(original sentence which is separated by sep)
    	String sepSent = "今天 天气 很 好";
    	result = p.parseSepSent(sepSent, " ");
    }

	public LexicalizedParser lp = null;
	private int lang = -1;
    public TreebankLanguagePack tlp = null;    
    public GrammaticalStructureFactory gsf = null;

	public PCFGParser(int lang){
		this.lang = lang;
		if(lang == Lang.ENG){
			lp = LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz");
		}
		else if(lang == Lang.ZHS){
			lp = LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz");
		}
        tlp = lp.treebankLanguagePack(); // TreebankLanguagePack for Chinese
        gsf = tlp.grammaticalStructureFactory();
        DepDrawer.setTreebankLanguagePack(tlp); // for drawing dependency trees
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
