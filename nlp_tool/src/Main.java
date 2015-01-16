import java.util.ArrayList;
import java.util.HashMap;

import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.trees.Tree;


public class Main {
	public static void main(String[] args){
		if(args.length != 1){
			System.err.println("java -cp ... ReviewFile");
			return;
		}
		String reviewFile = args[0];

        boolean segmented = true;
        boolean zht = false;
		
		//read reviews 
		ArrayList<Review> reviews = FileIO.readTrainingReview(reviewFile, segmented, zht);
		
		//Initialize opinion and aspect words extractor
		Extractor e = new Extractor(reviews.size(), "tags.txt");
		
		//Get POS tags
		Parser p = new Parser("chinese");
		HashMap<Label, Integer> tagMapping = new HashMap<Label, Integer>();
		for(int k = 0; k < reviews.size(); k++){
			Review r = reviews.get(k);
			//System.out.println(r.content);
			for(int i = 0; i< r.tokens.length; i++){
				r.trees[i] = p.parseTokenizedSent(r.tokens[i]);
				//parse.pennPrint();
				Label[] tags = Parser.getPOSTags(r.trees[i]);
				e.extract(k, r.tokens[i], tags);
				/*
				for(int j = 0; j< tags.length; j++){
					//System.out.print("(" + r.tokens[i][j] + " " + tags[j] + ")");
					if(r.tagCount.containsKey(tags[i])){
						
						r.tagCount.put(tags[i], r.tagCount.get(tags[i]) + 1);
					}
					else{
						r.tagCount.put(tags[i], 1);
					}
					if(tagMapping.containsKey(tags[j])){
						tagMapping.put(tags[j], tagMapping.size());
					}
				}
				for(Label l : r.tagCount.keySet()){
					System.out.println(l + ":" + r.tagCount.get(l));
				}
				*/
				//System.out.println("");	
			}
			/*
			for(Label l :tagMapping.keySet()){
				System.out.println(l + ":" + tagMapping.get(l));
			}*/
			if(k % 10 == 0){
				System.err.print(".");
				System.err.flush();
				if(k % 100 == 0){
					System.err.println("Progress(" + k + "/" + reviews.size() + ")");
				}
			}
		}
		FileIO.writeReviewAndTree("parsedReviews.txt", reviews);
		
		WordScore[] aspectOrder = e.rankAspectWords(Extractor.USE_TFIDF);
		WordScore[] opinionOrder = e.rankOpinionWords(Extractor.USE_TFIDF);
		FileIO.writeWordScore("aspect.rank", aspectOrder);
		FileIO.writeWordScore("opinion.rank", opinionOrder);
		
	}
}
