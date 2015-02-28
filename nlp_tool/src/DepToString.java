 
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.ling.IndexedWord;
import java.util.List;

public class DepToString{
    //format: reln gov_index gov_word gov_tag dep_index dep_word dep_tag
    public static String TDToString(TypedDependency td){
        if(td == null){
            return null;
        }
        IndexedWord g = td.gov();
        IndexedWord d = td.dep();
        String str = String.format("%s %d %s %s %d %s %s", 
                td.reln(), g.index(), g.word(), g.tag(),
                d.index(), d.word(), d.tag());
        return str;
    }

    public static String TDsToString(List<TypedDependency> tdList){
        if(tdList == null){
            return null;
        }
        String str = "";
        for(TypedDependency td: tdList){
            str = str + DepToString.TDToString(td) + "\n";
        }
        return str;

    }
}

