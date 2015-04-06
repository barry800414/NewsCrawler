import java.util.ArrayList;
import edu.stanford.nlp.trees.*;

public class TreePrinter{
    public static int getNodesEdges(Tree tree, int startIndex, ArrayList<Node> nodes, ArrayList<Edge> edges){
        if(tree.numChildren() == 0){ //leave node (word node)
            Node leaf = new Node(startIndex, Node.WORD_NODE, tree.label().toString());
            nodes.add(leaf);
            return startIndex;
        }
        else{ //not leave node: 1.child is leaf  2. child is not leave
            int childIndex = startIndex+1, nowIndex=startIndex; 

            //for each child
            for(Tree c: tree.children()){
                //add edge first
                edges.add(new Edge(startIndex, childIndex));

                nowIndex = getNodesEdges(c, childIndex, nodes, edges);
                if(nowIndex == childIndex){ //child is leaf
                    // if child is leaf, there should be only one child
                    if(tree.numChildren() != 1){
                        System.err.println("if child is leaf, there should be only one child");
                        break;
                    }
                    // if child is leaf, then this node is POS_NODE
                    Node posNode = new Node(startIndex, Node.POS_NODE, tree.label().toString());
                    nodes.add(posNode);
                    return nowIndex;
                }
                else{ //child is not leaf 
                    childIndex = nowIndex + 1;
                }
            }
            Node phraseNode = new Node(startIndex, Node.PHRASE_NODE, tree.label().toString());
            nodes.add(phraseNode);
            return nowIndex;
        }
    }

    public static String treeToString(Tree tree){
        ArrayList<Node> nodes = new ArrayList<Node>();
        ArrayList<Edge> edges = new ArrayList<Edge>();
        getNodesEdges(tree, 0, nodes, edges);
        for(Node n: nodes){
            System.out.println(n);
        }
        for(Edge e: edges){
            System.out.println(e);
        }
        return "";
    }
}


class Node{
    public static final int PHRASE_NODE=0, POS_NODE=1, WORD_NODE=2;
    public static final String[] TYPE_STR = new String[] { "phrase", "POS", "word" };
    int id, type;
    String word;

    public Node(int id, int type){
        this(id, type, (String) null);
    }
    public Node(int id, int type, String word){
        this.id = id;
        this.type = type;
        this.word = word;
    }

    public String toString(){
        return id + " " + Node.TYPE_STR[type] + " " + word;
    }
}

class Edge{
    int fromId, toId;
    public Edge(int fromId, int toId){
        this.fromId = fromId;
        this.toId = toId;
    }
    public String toString(){
        return fromId + " " + toId; 
    }
}

