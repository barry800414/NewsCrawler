import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.nio.charset.Charset;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.Headers;

import jopencc.ZhtZhsConvertor;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.ling.Sentence;

public class NLPToolServer {

    public static ZhtZhsConvertor convertor;
    public static Segmenter seg;
    public static FullPOSTagger tagger;
    public static FullNNDepParser fdp;
    public static FullPCFGParser fpp;

    private static final String imgFolder = "/utmp/weiming/deptree_img/";
    
    public static void main(String[] args) {

        //Initialize the converter
        System.out.println(">>>>>> Initializing Converter ... ");
        convertor = new ZhtZhsConvertor("./jopencc");

        //Initialize the segmenter
        System.out.println(">>>>>> Initializing Segmenter ... ");
        seg = new Segmenter("./stanford_segmenter", convertor);

        //initialize the pos-tagger 
        System.out.println(">>>>>> Initializing POS-tagger ...");
        tagger = new FullPOSTagger("./stanford_postagger", Lang.ZHS, 
            seg, convertor);

        //Initialize the dependency parser
        /*
        System.out.println(">>>>> Initailizing NN Dependency Parser ...");
        fdp = new FullNNDepParser(Lang.ZHS, tagger, 
            seg, convertor);
        */

        //Initialize the PCFG parser
        System.out.println(">>>>> Initializing PCFG Parser ...");
        fpp = new FullPCFGParser(Lang.ZHS, seg, convertor);

        //Initialize the server
        try{
            HttpServer server = HttpServer.create(new InetSocketAddress(8000), 0);
            server.createContext("/info", new InfoHandler());
            server.createContext("/segmenter", new SegHandler());
            server.createContext("/pos", new POSHandler());
            //server.createContext("/nn_dep", new NNDepParserHandler());
            server.createContext("/pcfg_dep", new PCFGDepParserHandler());

            server.setExecutor(null); // creates a default executor
            server.start();
            System.out.println("The server is running");
        }
        catch(Exception e){
            e.printStackTrace();
        }
    }

    // http://localhost:8000/info
    static class InfoHandler implements HttpHandler {
        public void handle(HttpExchange httpExchange) throws IOException {
            String response = "/segmenter?s=sentence\n/pos?s=sentence\n/nndep?s=sentence";
            NLPToolServer.writeResponse(httpExchange, response.toString());
        }
    }

    // Stanford Segmenter handler
    // http://localhost:port/segmenter?s=sentence
    static class SegHandler implements HttpHandler {
        public void handle(HttpExchange httpExchange) throws IOException {
            StringBuilder response = new StringBuilder();
            Map <String,String>parms = NLPToolServer.queryToMap(httpExchange.getRequestURI().getQuery());
            String text = parms.get("s");
            
            //segement the string
            String output = seg.mergeStr(seg.segmentStrZht(text), " ");
            response.append(output);

            //System.out.println("Reqeust:" + text.substring(0, text.length() > 10 ? 10: text.length()) + "...");
            //System.out.println("Response:" + output.substring(0, output.length() > 10 ? 10: output.length()) + "...");
            System.out.println("Reqeust:" + text);
            System.out.println("Response:" + output);
            
            NLPToolServer.writeResponse(httpExchange, response.toString());
        }
    }

    // http://localhost:port/pos?s=sentence
    // http://localhost:port/pos?seg_s=sentence
    static class POSHandler implements HttpHandler {
        public void handle(HttpExchange httpExchange) throws IOException {
            StringBuilder response = new StringBuilder();
            Map <String,String>parms = NLPToolServer.queryToMap(httpExchange.getRequestURI().getQuery());
            
            // default: segemented sentence (word delimiter is space)
            boolean seg = false;
            String text = parms.get("seg_s");
            if(text == null || text.length() == 0){
                text = parms.get("s");
                if(text == null || text.length() == 0){
                    return ;
                }
            }
            else{
                seg = true;
            }
            
            List<TaggedWord> tagged;
            if(seg){
                tagged = tagger.tagTokenizedSent(text, Lang.ZHT, Lang.ZHT);
            }
            else{
                tagged = tagger.tagUntokenizedSent(text, Lang.ZHT, Lang.ZHT);
            }

            String output = Sentence.listToString(tagged, false);
            response.append(output);
            
            //System.out.println("Reqeust:" + text.substring(0, text.length() > 10 ? 10: text.length()) + "...");
            //System.out.println("Response:" + output.substring(0, output.length() > 10 ? 10: output.length()) + "...");
            System.out.println("Reqeust:" + text);
            System.out.println("Response:" + output);
            
            NLPToolServer.writeResponse(httpExchange, response.toString());
        }
    }
    
    
    // Stanford NN Dependency Parser Handler (output: Collx Format)
    //http://localhost:port/nn_dep?s=sentence
    /*
    static class NNDepParserHandler implements HttpHandler {
        public void handle(HttpExchange httpExchange) throws IOException {
            //retrieve sentence
            StringBuilder response = new StringBuilder();
            Map <String,String>parms = NLPToolServer.queryToMap(httpExchange.getRequestURI().getQuery());
            String text = parms.get("s");

            //dependency parsing
            List<TypedDependency> tdList = fdp.parseUntokenizedSent(text, Lang.ZHT, Lang.ZHT);
            String tokenizedSent = fdp.getTokenizedSentBuffer();
            response.append(tokenizedSent + "\n");
            String output = DepToString.TDsToString(tdList);
            response.append(output);

            //System.out.println("Reqeust:" + text.substring(0, text.length() > 10 ? 10: text.length()) + "...");
            //System.out.println("Response:" + output.substring(0, output.length() > 10 ? 10: output.length()) + "...");
            System.out.println("Reqeust:" + text);
            System.out.println("Response:" + tokenizedSent + "\n" + output);
            
            NLPToolServer.writeResponse(httpExchange, response.toString());
        }
    }*/

    // Stanford PCFG Dependency Parser handler (output: stanford dependencies)
    //http://localhost:port/pcfg_dep?s=sentence?f_name=ooo?f_folder=xxx
    static class PCFGDepParserHandler implements HttpHandler {
        public void handle(HttpExchange httpExchange) throws IOException {
            String imgPath = null;

            //retrieve sentence
            StringBuilder response = new StringBuilder();
            Map <String,String>parms = NLPToolServer.queryToMap(httpExchange.getRequestURI().getQuery());
            
            boolean seg = false;
            String text = parms.get("seg_s");
            if(text == null || text.length() == 0){
                text = parms.get("s");
                if(text == null || text.length() == 0){
                    return ;
                }
            }
            else{
                seg = true;
            }


            //Check drawing dependency tree or not
            String drawFlag = parms.get("draw");
            if(drawFlag != null){
                if(drawFlag.toLowerCase().compareTo("true") == 0){
                    String fileFolder = parms.get("f_folder");
                    String fileName = parms.get("f_name");
                    if(fileFolder == null || fileName == null || 
                       fileFolder.length() == 0 || fileName.length()==0){
                        fileFolder = ".";
                        fileName = text;
                    }
                    imgPath = NLPToolServer.imgFolder + fileFolder + "/" + fileName;
                }
            }

            //dependency parsing by pcfg parser
            List<TypedDependency> tdList;
            if(seg){
                tdList = fpp.depParseTokenizedSent(text, " ", Lang.ZHT, Lang.ZHT, imgPath);
            }
            else{
                tdList = fpp.depParseUntokenizedSent(text, Lang.ZHT, Lang.ZHT, imgPath);
            }
            String tokenizedSent = fpp.getTokenizedSentBuffer(); //get tokenized text
            response.append(tokenizedSent + "\n");
            String depStr = DepToString.TDsToString(tdList); //get typed dependencies
            response.append(depStr);

            //System.out.println("Reqeust:" + text.substring(0, text.length() > 10 ? 10: text.length()) + "...");
            //System.out.println("Response:" + output.substring(0, output.length() > 10 ? 10: output.length()) + "...");
            System.out.println("Reqeust:" + text);
            System.out.println("Response:" + tokenizedSent + "\n" + depStr);
 
            
           
            NLPToolServer.writeResponse(httpExchange, response.toString());
        }
    }


    public static void writeResponse(HttpExchange httpExchange, String response) throws IOException {
        Headers header = httpExchange.getResponseHeaders();
        header.add("Content-Type", "text/plain; charset=utf-8");
        httpExchange.sendResponseHeaders(200, response.getBytes().length);
        OutputStream os = httpExchange.getResponseBody();
        os.write(response.getBytes());
        os.close();
    }


    /**
     * returns the url parameters in a map
     * @param query
     * @return map
     */
    public static Map<String, String> queryToMap(String query){
        Map<String, String> result = new HashMap<String, String>();
        for (String param : query.split("&")) {
            String pair[] = param.split("=");
            if (pair.length>1) {
                result.put(pair[0], pair[1].replace("+", " "));
            }else{
                result.put(pair[0], "");
            }
        }
        return result;
    }

}
