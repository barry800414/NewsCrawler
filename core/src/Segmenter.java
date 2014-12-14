
import java.util.Properties;
import java.util.List;

import edu.stanford.nlp.ie.crf.CRFClassifier;
import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ling.CoreLabel;

import jopencc.Convertor;

/**
 * General chinese segmenter interface
 *
 */
public class Segmenter {
    
    // Demo 
    public static void main(String[] args){
        //initialize the segmenter
        Segmenter seg = new Segmenter("./stanford_segmenter", "./jopencc");

        String str = "今天天氣很好,我中餐吃麵" ;
        String[] buf = seg.segmentStrZht(str);
        for(String word: buf){
            System.out.println(word);
        }
    }

    private Properties props;
    private CRFClassifier<CoreLabel> segmenter;
    private Convertor converter;

    /**
     *  segPath: the path of the needed in stanford segmenter
     *  jopenccPath: the path of jopencc package
     *  The segmenter will be able to deal with traditional chinese words
     * */
    public Segmenter(String segPath, String jopenccPath) {
        this(segPath);
        converter = new Convertor(jopenccPath);
    }

    /**
     *  segPath: the path of the needed in stanford segmenter
     *  The segmenter will not be able to deal with traditional chinese words
     * */
    public Segmenter(String segPath) {
        props = new Properties();
        props.setProperty("sighanCorporaDict", segPath + "/data");
        props.setProperty("serDictionary", segPath + "/data/dict-chris6.ser.gz");
        props.setProperty("inputEncoding", "UTF-8");
        props.setProperty("sighanPostProcessing", "true");
        segmenter = new CRFClassifier<CoreLabel>(props);
        try{
            segmenter.loadClassifier(segPath + "/data/ctb.gz", props);
        }
        catch(Exception e){
            System.err.println("Load dataset Error");
            e.printStackTrace();
        }
        this.converter = null;
    }


    //segment the string (simplified chinese)
    public String[] segmentStrZhs(String str){
        List<String> words = segmenter.segmentString(str);
        return (String[]) words.toArray();
    }

    //segment the string (traditional chinese)
    public String[] segmentStrZht(String str){
        if(this.converter == null){
            System.err.println("jopencc converter not found. View it as simplified Chinese");
            return segmentStrZhs(str);
        }
        String zhsStr = converter.convertToZhs(str);
        List<String> words = segmenter.segmentString(zhsStr);
        String[] output = new String[words.size()];
        for(int i = 0; i < words.size(); i++){
            output[i] = converter.convertToZht(words.get(i));
        }
        return output;
    }

    

}



