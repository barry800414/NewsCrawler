import sys, os

def run(iter, c, size, train_file, init_file, model_file, test_file, scoreFile):
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


if len(sys.argv) != 4:
    print('Usage:', sys.argv[0], 'T Fold Seed', file=sys.stderr)
    exit(-1)

t = int(sys.argv[1])
fold = int(sys.argv[2])
seed = int(sys.argv[3])

import math

dataDir = '..'
tmpFolder = '/utmp/weiming/svm-sle'
seed = 1

cRange = [math.pow(2, i) for i in range(-5, 3)]
iter = 30
sizeRange = [20, 40, 60]
print('T:%d Fold:%d Seed:%d' % (t, fold, seed))
taskNum = len(cRange) * len(sizeRange)
cnt = 0
try:
    for c in cRange:
        for size in sizeRange:
            train_file='%s/sle_T%d_Seed%d_Fold%d.train' % (dataDir, t, seed, fold)
            init_file='%s/sle_T%d_Seed%d_Fold%d.init' % (dataDir, t, seed, fold)
            model_prefix='T%dS%dF%d_C%f_iter%d_size%d' % (t, seed, fold, c, iter, size)
            model_folder='%s/%s' % (tmpFolder, model_prefix)
            test_file='%s/sle_T%d_Seed%d_Fold%d.test' % (dataDir, t, seed, fold)

            resultFolder = './T%dS%dF%d_result' % (t, seed, fold)
            scoreFile = '%s/%s' % (resultFolder, model_prefix)

            os.system('rm -rf %s_temp' % model_folder)
            os.system("mkdir -p %s" % (resultFolder))
            run(iter, str(c), str(size), train_file, init_file, model_folder, test_file, scoreFile)
            cnt += 1
            if (cnt + 1) % 1 == 0:
                print('%cProgress(%d/%d)' % (13, cnt+1, taskNum), end='')

    print('')
except KeyboardInterrupt: # Ctrl + C interrupt (i.e. want to exit)
    print('KerboardInterrupt')
    exit(-1)


