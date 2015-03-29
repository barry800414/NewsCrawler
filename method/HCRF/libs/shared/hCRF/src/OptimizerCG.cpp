#include "optimizer.h"
#include "cg_descent.h"
#include <iostream>

static Model* currentModel=NULL;
static DataSet* currentDataset=NULL;
static Evaluator* currentEvaluator=NULL;
static Gradient* currentGradient=NULL;


OptimizerCG::OptimizerCG() : Optimizer()
{
}

OptimizerCG::~OptimizerCG()
{
}


void OptimizerCG::optimize(Model* m, DataSet* X,Evaluator* eval, Gradient* grad)
{
	currentModel = m;
	currentDataset = X;
	currentEvaluator = eval;
	currentGradient= grad;
	double* weights;
	//weights = currentModel->getWeights()->get();

	int status = -1;
	cg_stats Stats;
	double* work;
    
    //std::cerr << "t1" << std::endl;
	work = (double *) malloc(4*currentModel->getWeights()->getLength()*sizeof(double));
	//std::cerr << "t2" << std::endl;
    weights = (double *) malloc (currentModel->getWeights()->getLength()*sizeof(double)) ;
	double step = 0.001;
	//std::cerr << "t3" << std::endl;
    memcpy(weights,currentModel->getWeights()->get(),currentModel->getWeights()->getLength()*sizeof(double));

	// Call
	//std::cerr << "t4" << std::endl;
    status = cg_descent(1.e-8, weights, currentModel->getWeights()->getLength(), callbackComputeError, 
						callbackComputeGradient,work, step, &Stats, maxit);
    //std::cerr << "t5" << std::endl;
	dVector vecGradient(currentModel->getWeights()->getLength());
	//std::cerr << "t6" << std::endl;
    memcpy(vecGradient.get(),weights,currentModel->getWeights()->getLength()*sizeof(double));
	//std::cerr << "t7" << std::endl;
    currentModel->setWeights(vecGradient);

    //std::cerr << "t8" << std::endl;
	dVector tmpWeights = *(currentModel->getWeights());
	//std::cerr << "t9" << std::endl;
    tmpWeights.transpose();
	//std::cerr << "t10" << std::endl;
    tmpWeights.multiply(*currentModel->getWeights());
    lastNormGradient = tmpWeights[0];

	lastNbIterations = Stats.iter;
	lastFunctionError = Stats.f;
	

	if(currentModel->getDebugLevel() >= 1)
	{
		std::cout << "F = " << lastFunctionError << "  |w| = " << lastNormGradient << std::endl;
		std::cout<<"  Iteration # = "<<lastNbIterations<<"   Nb error eval = "<<Stats.nfunc;
		std::cout<< "   Nb gradient eval =  " << Stats.ngrad <<std::endl << std::endl;
		if(currentModel->getDebugLevel() >= 3){
			std::cout<<"X = "<<currentModel->getWeights();
		}
	}
	free(work);
	//TODO:: Check if we want to also free weights hsalamin 2010.02.05
}

double OptimizerCG::callbackComputeError(double* weights)
{
    //std::cerr << "start callback compute error " << std::endl;
    dVector vecGradient(currentModel->getWeights()->getLength());
    //std::cerr << "ttt1"  << std::endl;
	memcpy(vecGradient.get(),weights,currentModel->getWeights()->getLength()*sizeof(double));
    //std::cerr << "ttt2"  << std::endl;

	currentModel->setWeights(vecGradient);
    //std::cerr << "ttt3"  << std::endl;

//	currentModel->getWeights()->set(weights);
	if(currentModel->getDebugLevel() >= 2){
		std::cout << "Compute error... "  << std::endl;
	}
	double errorVal = currentEvaluator->computeError(currentDataset, currentModel);

    //std::cerr << "leave callback computer error" << std::endl;
	return errorVal;
	
}

void OptimizerCG::callbackComputeGradient(double* gradient, double* weights)
{
    //std::cerr << "start callback compute gradient" << std::endl;
	dVector dgrad(currentModel->getWeights()->getLength());
	memcpy(dgrad.get(),weights,currentModel->getWeights()->getLength()*sizeof(double));
	currentModel->setWeights(dgrad);
	dgrad.set(0);
	if(currentModel->getDebugLevel() >= 2){
		std::cout<<"Compute gradient... "<<std::endl;
	}
	currentGradient->computeGradient(dgrad, currentModel,currentDataset);
	memcpy(gradient,dgrad.get(),dgrad.getLength()*sizeof(double));
    //std::cerr << "leave callback compute gradient" << std::endl;
}


