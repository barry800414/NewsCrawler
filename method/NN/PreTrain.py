
import sys
import numpy as np
from scipy.sparse import csr_matrix, vstack
from sklearn.metrics import accuracy_score
from sklearn.cross_validation import StratifiedKFold
import climate
import theanets

from scipy.io import mmwrite, mmread

from misc import *


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'allX.mtx middleLayer modelName', file=sys.stderr)
        exit(-1)
 
    climate.enable_default_logging()
    allXFile = sys.argv[1]
    middleLayer = int(sys.argv[2])
    modelName = sys.argv[3]

    allX = mmread(allXFile).toarray()
    print('AllData:', allX.shape)
    exp = theanets.Experiment( 
        theanets.Classifier,
        layers=(allX.shape[1], middleLayer, 2),
    )
    
    exp.train(
        allX,
        optimize='pretrain',
        learning_rate=0.1,
        momentum=0.5,
        hidden_l1=2,
    )
    exp.network.save(modelName)

