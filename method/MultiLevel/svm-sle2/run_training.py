import sys, os
import math
from FindBestParam import *

cRange = [math.pow(2, i) for i in range(-5, 3)]
iter = 30
sizeRange = [20, 40, 60]
foldNum = 10
vfoldNum = 10

def run(iter, c, size, train_file, init_file, model_file, test_file, scoreFile, remove=False):
    m = '3' # feature smoothing -- see Section 4.5 in paper
    norm = '2' # sqrt norm -- see Eq. (3) and Section 4.3 in paper
    subdir = model_file + '_temp'
    # creating directory for intermediate outputs
    os.system('mkdir ' + subdir)
    # training first iteration using initialization file 
    cmd = './svm_sle_learn -c %s -m %s -n %s -l %s %s %s %s/model_0 >/dev/null' %(c, m, norm, size, train_file, init_file, subdir)
    os.system(cmd)
    # classification performance of model from first iteration
    cmd = './svm_sle_classify ' + train_file + ' ' + subdir + '/model_0 ' + subdir + '/pred_0 |tee ' + subdir + '/pred_dump_0' + ' >/dev/null'
    os.system(cmd)
    cmd = './svm_sle_classify ' + test_file + ' ' + subdir + '/model_0 ' + subdir + '/test_pred_0 |tee '+ subdir + '/test_pred_dump_0' + ' >/dev/null' 
    os.system(cmd)

    # iteration for n iterations
    for nn in range(1,iter):
        # generating a new initilization file using model learned from previous iteration
        os.system('./svm_sle_classify -l ' + train_file + ' ' + subdir + '/model_' + str(nn-1) + ' ' + subdir + '/latent_' + str(nn) + ' >/dev/null')

        # training new iteration
        os.system('./svm_sle_learn -c ' + c + ' -m ' + m + ' -n ' + norm + ' -l ' + size + ' ' + train_file + ' ' + subdir + '/latent_' + str(nn)+ ' ' + subdir + '/model_' + str(nn) + ' >/dev/null')

        # classification performance of current iteration
        os.system('./svm_sle_classify ' + train_file + ' ' + subdir + '/model_' + str(nn) + ' ' + subdir + '/pred_' + str(nn) + ' |tee ' + subdir + '/pred_dump_' + str(nn)  + ' >/dev/null')
        os.system('./svm_sle_classify '+ test_file + ' ' + subdir + '/model_' + str(nn) + ' ' + subdir + '/test_pred_'+str(nn) + ' |tee ' + subdir + '/test_pred_dump_' + str(nn) + " >> %s" % scoreFile)

    if remove:
        os.system('rm -rf %s' % (subdir))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'T Fold Seed', file=sys.stderr)
        exit(-1)

    t = int(sys.argv[1])
    fold = int(sys.argv[2])
    seed = int(sys.argv[3])

    dataDir = '..'
    tmpFolder = '/utmp/weiming/svm-sle'
    seed = 1
    
    print('T:%d Fold:%d Seed:%d' % (t, fold, seed))
    print('Cross-validation to search best parameters ...')
    taskNum = len(cRange) * len(sizeRange) * vfoldNum
    cnt = 0
    for c in cRange:
        for size in sizeRange:
            for vfold in range(0, vfoldNum):
                prefix = 'T%dS%dF%d' % (t, seed, fold)
                prefix2 = 'T%dS%dF%dV%d' % (t, seed, fold, vfold)
                train_file='%s/%s/%s.train' % (dataDir, prefix, prefix2)
                init_file='%s/%s/%s.init' % (dataDir, prefix, prefix2)
                model_prefix='%s_C%f_iter%d_size%d' % (prefix2, c, iter, size)
                model_folder='%s/%s' % (tmpFolder, model_prefix)
                test_file='%s/%s/%s.test' % (dataDir, prefix, prefix2)

                resultFolder = './%s_result' % (prefix)
                scoreFile = '%s/%s' % (resultFolder, model_prefix)

                os.system('rm -rf %s_temp' % model_folder)
                os.system("mkdir -p %s" % (resultFolder))
                run(iter, str(c), str(size), train_file, init_file, model_folder, test_file, scoreFile, remove=True)
                cnt += 1
                if (cnt + 1) % 1 == 0:
                    print('%cProgress(%d/%d)' % (13, cnt+1, taskNum), end='')

    bestParam = getBestParam(t, seed, fold)
    print('Testing on testing data using best parameters ...')
    c = bestParam['c']
    size = bestParam['size']
    prefix = 'T%dS%dF%d' % (t, seed, fold)
    train_file='%s/%s/%s.train' % (dataDir, prefix, prefix)
    init_file='%s/%s/%s.init' % (dataDir, prefix, prefix)
    model_prefix='%s_C%f_iter%d_size%d' % (prefix, c, iter, size)
    model_folder='%s/%s' % (tmpFolder, model_prefix)
    test_file='%s/%s/%s.test' % (dataDir, prefix, prefix)

    resultFolder = './%s_result' % (prefix)
    scoreFile = '%s/%s' % (resultFolder, model_prefix)

    os.system('rm -rf %s_temp' % model_folder)
    os.system("mkdir -p %s" % (resultFolder))
    run(iter, str(c), str(size), train_file, init_file, model_folder, test_file, scoreFile)

