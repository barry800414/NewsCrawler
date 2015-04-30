'''
# list of parsedLabelNews: label & news 
# allowedWTList: allowed words for each kind of tag in each layer
#    allowedWTList[0]['NN']: the words allowed of NN in 0 layer (seed)
# allowedRelList: allowed dependency relations in each layer
def generateXYOneLayer(parsedLabelNews, allowedSeedWord, 
        allowedFirstLayerWord, allowedRel):
    
    Y = list()
    XFeature = list()
    volc = dict()
    
    # convert to X 
    # TODO:word/word-tag/word-relation ?
    seedVolc = dict()
    newVolc = dict()
    for contentEdgeList in corpusEdgeList:
        for depGraphEdgeList in contentEdgeList:
            for edge in depGraphEdgeList:
                
   

# list of parsedLabelNews: label & news 
# allowedWTList: allowed words for each kind of tag in each layer
#    allowedWTList[0]['NN']: the words allowed of NN in 0 layer (seed)
# allowedRelList: allowed dependency relations in each layer
def generateXY(parsedLabelNews, allowedWTList, allowedRelList):
    # check input
    #if len(allowedWTList) != (len(allowedRelList)+1) :
        #return None

    maxLayer = len(allowedWTList) - 1
    Y = list()
    XFeature = list()
    volc = dict()
    for labelNews in parsedLabelNews:
        contentDep = resetDep(labelNews['news']['content_dep'])
        allEdgeList = list() #
        for depList in contentDep:
            dg = DepGraph(depList, maxLayer)
            edgeListLayer = list() #edgeListLayer[layer][edgeIndex]
            edgeList = None
            for layer in range(0, maxLayer):
                dg.setAllowedDepWord(allowedWTList[layer+1], type='[t][w]')
                dg.setAllowedGovWord(allowedWTList[layer+1], type='[t][w]')
                dg.setAllowedRel(allowedRelList[layer])
                if layer == 0:
                    dg.setNowWord(allowedWTList[0])
                else:
                    if edgeList != None:
                        nowWords = [eP for rel,sP,sW,sT,eP,eW,wT in edgeList]
                        dg.setNowWord(nowWords, type='pos')
                edgeList = dg.searchOneStep()
                edgeListLayer.append(edgeList)
            allEdgeList.append(edgeListLayer)
'''

