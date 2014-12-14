import java.util.ArrayList;
import java.util.List;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.trees.Tree;


public class Parser {
	public LexicalizedParser lp = null;
	
	public Parser(String lang){
		if(lang.equals("english")){
			lp = LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz");
		}
		else if(lang.equals("chinese")){
			lp = LexicalizedParser.loadModel("edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz");
		}
	}
	
	public Tree parseTokenizedSent(String[] sent){
	    List<CoreLabel> rawWords = Sentence.toCoreLabelList(sent);
	    Tree parse = lp.apply(rawWords);
	    return parse;
	}
	
	public Tree parseSpaceDeliminatedSent(String sent){
		String[] tokenizedSent = sent.split(" ");
		//TODO: need more preprocess
		return parseTokenizedSent(tokenizedSent);
	}
	
	//TODO
	public Tree parseSent(String sent){
		return null;
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
