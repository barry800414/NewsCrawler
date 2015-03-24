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

import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.ling.Sentence;

public class EngNLPToolServer {

    public static FullPOSTagger tagger;
    public static FullNNDepParser fdp;
    public static PCFGParser fpp;

    private static final String imgFolder = "/utmp/weiming/eng_deptree_img/";
    
    public static void main(String[] args) {

        //initialize the pos-tagger 
        System.out.println(">>>>>> Initializing POS-tagger ...");
        tagger = new FullPOSTagger("./stanford_postagger", Lang.ENG);

        //Initialize the English PCFG parser
        System.out.println(">>>>> Initializing PCFG Parser ...");
        fpp = new PCFGParser(Lang.ENG);

        //Initialize the server
        try{
            HttpServer server = HttpServer.create(new InetSocketAddress(8000), 0);
            server.createContext("/info", new InfoHandler());
            server.createContext("/pos", new POSHandler());
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
            String response = "/pos?seg_s=sentence\n/pcfg_dep?seg_s=sentence";
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
            String input = parms.get("seg_s");

            List<TaggedWord> tagged = tagger.tagTokenizedSent(input, Lang.ENG, Lang.ENG);
            String output = Sentence.listToString(tagged, false);
            response.append(output);
            
            //System.out.println("Reqeust:" + input.substring(0, input.length() > 10 ? 10: input.length()) + "...");
            //System.out.println("Response:" + output.substring(0, output.length() > 10 ? 10: output.length()) + "...");
            System.out.println("Reqeust:" + input);
            System.out.println("Response:" + output);
            
            NLPToolServer.writeResponse(httpExchange, response.toString());
        }
    }


    // Stanford PCFG Dependency Parser handler (output: stanford dependencies)
    //http://localhost:port/pcfg_dep?s=sentence?f_name=ooo?f_folder=xxx
    static class PCFGDepParserHandler implements HttpHandler {
        public void handle(HttpExchange httpExchange) throws IOException {
            String imgPath = null;

            //retrieve sentence
            StringBuilder response = new StringBuilder();
            Map <String,String>parms = NLPToolServer.queryToMap(httpExchange.getRequestURI().getQuery());
            String text = parms.get("seg_s");

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
                    imgPath = EngNLPToolServer.imgFolder + fileFolder + "/" + fileName;
                }
            }

            //dependency parsing by pcfg parser
            List<TypedDependency> tdList = fpp.depParseTokenizedSent(text, " ", imgPath);
            String depStr = DepToString.TDsToString(tdList); //get typed dependencies
            response.append(depStr);

            //System.out.println("Reqeust:" + input.substring(0, input.length() > 10 ? 10: input.length()) + "...");
            //System.out.println("Response:" + output.substring(0, output.length() > 10 ? 10: output.length()) + "...");
            System.out.println("Reqeust:" + text);
            System.out.println("Response:" + depStr);
 
            
           
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
