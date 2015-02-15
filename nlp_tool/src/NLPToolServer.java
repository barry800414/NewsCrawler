import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.Collection;
import java.nio.charset.Charset;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.Headers;

import jopencc.ZhtZhsConvertor;
import edu.stanford.nlp.trees.TypedDependency;

public class NLPToolServer {

    public static ZhtZhsConvertor convertor;
    public static Segmenter seg;
    public static FullPOSTagger tagger;
    public static FullDependencyParser fdp;
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
        System.out.println(">>>>> Initailizing Dependency Parser ...");
        fdp = new FullDependencyParser(Lang.ZHS, tagger, 
            seg, convertor);

        //Initialize the server
        try{
            HttpServer server = HttpServer.create(new InetSocketAddress(8000), 0);
            server.createContext("/info", new InfoHandler());
            server.createContext("/segmenter", new SegHandler());
            server.createContext("/pos", new POSHandler());
            server.createContext("/dep_parser", new DepParserHandler());

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
            String response = "/segmenter?s=sentence\n/pos?s=sentence\n/dep_parser?s=sentence";
            NLPToolServer.writeResponse(httpExchange, response.toString());
        }
    }

    // http://localhost:port/segmenter?s=sentence
    static class SegHandler implements HttpHandler {
        public void handle(HttpExchange httpExchange) throws IOException {
            StringBuilder response = new StringBuilder();
            Map <String,String>parms = NLPToolServer.queryToMap(httpExchange.getRequestURI().getQuery());
            String input = parms.get("s");
            
            //segement the string
            String output = seg.mergeStr(seg.segmentStrZht(input), " ");
            response.append(output);

            //System.out.println("Reqeust:" + input.substring(0, input.length() > 10 ? 10: input.length()) + "...");
            //System.out.println("Response:" + output.substring(0, output.length() > 10 ? 10: output.length()) + "...");
            System.out.println("Reqeust:" + input);
            System.out.println("Response:" + output);
            
            NLPToolServer.writeResponse(httpExchange, response.toString());
        }
    }

    // TODO
    // http://localhost:port/segmenter?s=sentence
    static class POSHandler implements HttpHandler {
        public void handle(HttpExchange httpExchange) throws IOException {
            StringBuilder response = new StringBuilder();
            Map <String,String>parms = NLPToolServer.queryToMap(httpExchange.getRequestURI().getQuery());
            String input = parms.get("s");
            
            //segement the string
            String output = seg.mergeStr(seg.segmentStrZht(input), " ");
            response.append(output);

            //System.out.println("Reqeust:" + input.substring(0, input.length() > 10 ? 10: input.length()) + "...");
            //System.out.println("Response:" + output.substring(0, output.length() > 10 ? 10: output.length()) + "...");
            System.out.println("Reqeust:" + input);
            System.out.println("Response:" + output);
            
            NLPToolServer.writeResponse(httpExchange, response.toString());
        }
    }


    static class DepParserHandler implements HttpHandler {
        public void handle(HttpExchange httpExchange) throws IOException {
            //retrieve sentence
            StringBuilder response = new StringBuilder();
            Map <String,String>parms = NLPToolServer.queryToMap(httpExchange.getRequestURI().getQuery());
            String input = parms.get("s");

            //dependency parsing
            Collection<TypedDependency> tdList = fdp.parseUntokenizedSent(input, Lang.ZHT, Lang.ZHT);
            String tokenizedSent = fdp.getTokenizedSentBuffer();
            response.append(tokenizedSent + "\n");
            String output = FullDependencyParser.typedDependenciesToString(tdList);
            response.append(output);

            //System.out.println("Reqeust:" + input.substring(0, input.length() > 10 ? 10: input.length()) + "...");
            //System.out.println("Response:" + output.substring(0, output.length() > 10 ? 10: output.length()) + "...");
            System.out.println("Reqeust:" + input);
            System.out.println("Response:" + tokenizedSent + "\n" + output);
            
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