project-platypus
================
This study aims to predict a user's relationships with his or her contacts
based solely on the words used in electronic communications between them.
Software was created that reads in bulk exported email data and builds a
comprehensive graph database of people, the words communicated between them,
and their relationships to each other. Several stages of preprocessing and
feature selection were applied, and then various classifiers were shown to
effectively predict relationships using 10-fold cross validation. Logistic
regression showed 5.9% testing error on a sample set of 3000 emails and 309
contacts. The study shows promising results and suggests future work that
incorporates message meta-data, other mediums of communication like text messaging,
and larger data sets.

## Final results 12/11/2014
All results are calculated using a grid search and 10-fold cross validation.
The pipeline is a TfidfTransformer, a SelectKBest features, and a classifier.

 * Emails: 3000
 * Total words spoken: 225000
 * Samples: 309
 * Min. freq. cutoff: 5
 * Max. freq. cutoff stddev: 20

List of classifiers:

 * Logistic Regression
 * SGD - Logistic Regression
 * Linear SVC
 * SVC, Exponential Kernel
 * Ridge Classifier
 * Multinomial Naive Bayes
 
#### Logistic Regression

	Best score: 0.941
	Best parameters set:
		clf__C: 100000
		clf__class_weight: 'auto'
		clf__penalty: 'l1'
		kbest__k: 'all'
		kbest__score_func: <function chi2 at 0x7fe88dd01510>
		tfidf__use_idf: False

#### Stochastic Gradient Descent - Various Classifiers
Best loss function was 'log' (Logistic Regression)

    Best score: 0.934
    Best parameters set:
        clf__class_weight: 'auto'
        clf__loss: 'log'
        clf__n_iter: 10
        clf__penalty: 'l2'
        clf__shuffle: True
        kbest__k: 3000
        tfidf__use_idf: True

#### Linear SVC

    Best score: 0.931
    Best parameters set:
    	clf__C: 5.0
    	clf__class_weight: 'auto'
    	clf__loss: 'l2'
    	clf__penalty: 'l2'
    	kbest__k: 3000
    	kbest__score_func: <function f_classif at 0x7f14474ba400>
    	tfidf__use_idf: False

#### SVC, RBF kernel

	Best score: 0.925
	Best parameters set:
		clf__alpha: 0.04
		clf__normalize: True
		kbest__k: 'all'
		kbest__score_func: <function chi2 at 0x7f1a26e6d510>
		tfidf__use_idf: False

#### Ridge Classifier

    Best score: 0.925
    Best parameters set:
        clf__alpha: 0.04
        clf__normalize: True
        kbest__k: 'all'
        kbest__score_func: <function chi2 at 0x7f1a26e6d510>
        tfidf__use_idf: False

#### Multinomial Naive Bayes

    Best score: 0.915
    Best parameters set:
    	clf__alpha: 0.07
    	kbest__k: 1000
    	kbest__score_func: <function chi2 at 0x7f6cafc1e510>
    	tfidf__use_idf: True
