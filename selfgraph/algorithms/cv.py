"""

"""
from pprint import pprint
from time import time
from copy import deepcopy
from selfgraph.utils.csv import import_csv
from sklearn import cross_validation

from sklearn.svm import LinearSVC, SVC, NuSVC
from sklearn.decomposition import PCA, KernelPCA, TruncatedSVD
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.linear_model import SGDClassifier, LogisticRegression, Perceptron, RidgeClassifier
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import chi2, SelectKBest, f_classif
from sklearn.pipeline import Pipeline


def get_best_features(features, N, X, y):

    tfidf = TfidfTransformer()
    print(tfidf)
    X = tfidf.fit_transform(X)

    selector = SelectKBest(score_func=chi2, k=N)
    X = selector.fit_transform(X, y)
    return features[selector.get_support()]


def pipeline_cross_validation(X, y):

    pipeline = Pipeline([
        ('tfidf', TfidfTransformer(use_idf=False)),
        ('kbest', SelectKBest(k=100, score_func=chi2)),
        ('clf', LogisticRegression(C=100, class_weight='auto', penalty='l2')),
    ])

    pipeline_copy = deepcopy(pipeline)
    pipeline_copy.fit(X, y)
    y_true, y_pred = y, pipeline_copy.predict(X)
    train_only_score = pipeline_copy.score(X, y_true)

    scores = cross_validation.cross_val_score(pipeline, X, y, cv=10, scoring='accuracy')

    print('{} on {}:'.format(sys.argv[2], sys.argv[1]))
    print('    Train only score: {:2.2f}%'.format(train_only_score * 100))
    #print('    All scores: {}'.format(scores))
    print('    CV score: %0.2f (+/- %0.2f)%%' % (scores.mean()*100, scores.std() * 2 * 100))


def grid_search(pipeline, parameters, X, y):

    gs = GridSearchCV(
        pipeline,
        parameters,
        n_jobs=-1,
        verbose=1,
        scoring='accuracy',
        cv=10
    )

    print("Performing grid search...")
    print("pipeline:", [name for name, _ in pipeline.steps])
    print("parameters:")
    pprint(parameters)
    t0 = time()
    gs.fit(X, y)
    print("done in %0.3fs" % (time() - t0))
    print()

    print("Best score: %0.3f" % gs.best_score_)
    print("Best parameters set:")
    best_parameters = gs.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print("\t%s: %r" % (param_name, best_parameters[param_name]))


def grid_search_svc_rbf(X, y):

    pipeline_svc_rbf = Pipeline([
        ('tfidf', TfidfTransformer()),
        ('kbest', SelectKBest()),
        ('clf', SVC())
    ])

    parameters_svc_rbf = {
        'tfidf__use_idf': (True, False),
        'kbest__k': (2000, 3000,),
        'kbest__score_func': (chi2,),
        'clf__kernel': ('rbf',),
        'clf__C': (.1, 1, 10, 100, 1000, 10000),
        'clf__gamma': (.001, .005, .01, .02, .1),
        'clf__class_weight': ('auto', None),
    }

    grid_search(pipeline_svc_rbf, parameters_svc_rbf, X, y)

    # Best score: 0.925
    # Best parameters set:
    #     clf__C: 100
    #     clf__class_weight: None
    #     clf__gamma: 0.01
    #     clf__kernel: 'rbf'
    #     kbest__k: 2000
    #     kbest__score_func: <function chi2 at 0x7f1362c64510>
    #     tfidf__use_idf: False


def grid_search_lr(X, y):

    pipeline_lr = Pipeline([
        ('tfidf', TfidfTransformer()),
        ('kbest', SelectKBest()),
        ('clf', LogisticRegression())
    ])

    parameters_lr = {
        'tfidf__use_idf': (True, False),
        'kbest__k': (500, 1000, 3000, 'all'),
        'kbest__score_func': (chi2,),
        'clf__C': (100, 1000, 10000, 50000, 100000, 200000, 1000000),
        'clf__penalty': ('l1', 'l2'),
        'clf__class_weight': ('auto', None),
    }

    grid_search(pipeline_lr, parameters_lr, X, y)

    # Best score: 0.941
    # Best parameters set:
    #     clf__C: 100000
    #     clf__class_weight: 'auto'
    #     clf__penalty: 'l1'
    #     kbest__k: 'all'
    #     kbest__score_func: <function chi2 at 0x7fe88dd01510>
    #     tfidf__use_idf: False


def grid_search_lin_svc(X, y):

    pipeline_lin_svc = Pipeline([
        ('tfidf', TfidfTransformer()),
        ('kbest', SelectKBest()),
        ('clf', LinearSVC())
    ])

    parameters_lin_svc = {
        'tfidf__use_idf': (True, False),
        'kbest__k': (1000, 3000, 'all'),
        'kbest__score_func': (chi2, f_classif),
        'clf__C': (.1, .5, 1.0, 2.0, 5.0, 10.0, 100, 1000),
        'clf__class_weight': ('auto',),  # None was never better
        'clf__penalty': ('l2',),  # l1 was never better
        'clf__loss': ('l2',),  # l1 never was better
    }

    grid_search(pipeline_lin_svc, parameters_lin_svc, X, y)

    # Best score: 0.931
    # Best parameters set:
    # 	clf__C: 5.0
    # 	clf__class_weight: 'auto'
    # 	clf__loss: 'l2'
    # 	clf__penalty: 'l2'
    # 	kbest__k: 3000
    # 	kbest__score_func: <function f_classif at 0x7f14474ba400>
    # 	tfidf__use_idf: False


def grid_search_sgdc(X, y):

    pipeline_sgdc = Pipeline([
        ('tfidf', TfidfTransformer()),
        ('kbest', SelectKBest()),
        ('clf', SGDClassifier())
    ])

    parameters_sgdc = {
        'tfidf__use_idf': (True, False),
        'kbest__k': (3000, 'all'),
        'clf__class_weight': ('auto', None),
        'clf__loss': ('log', 'hinge', 'modified_huber', 'squared_hinge', 'perceptron'),
        'clf__penalty': ('l1', 'l2', 'elasticnet'),
        'clf__n_iter': (10,),
        'clf__shuffle': (True, False),

    }

    grid_search(pipeline_sgdc, parameters_sgdc, X, y)

    # Best score: 0.934
    # Best parameters set:
    #     clf__class_weight: 'auto'
    #     clf__loss: 'log'
    #     clf__n_iter: 10
    #     clf__penalty: 'l2'
    #     clf__shuffle: True
    #     kbest__k: 3000
    #     tfidf__use_idf: True


def grid_search_nb(X, y):

    pipeline_nb = Pipeline([
        ('tfidf', TfidfTransformer()),
        ('kbest', SelectKBest()),
        ('clf', MultinomialNB())
    ])

    parameters_nb = {
        'tfidf__use_idf': (True,),  # Much better than False for nb
        'kbest__k': (500, 1000, 3000, 'all'),
        'kbest__score_func': (chi2,),
        'clf__alpha': (.01, .02, .05, .06, .07, .08, .09, .10),
    }

    grid_search(pipeline_nb, parameters_nb, X, y)

    # Best score: 0.915
    # Best parameters set:
    # 	clf__alpha: 0.07
    # 	kbest__k: 1000
    # 	kbest__score_func: <function chi2 at 0x7f6cafc1e510>
    # 	tfidf__use_idf: True


def grid_search_ridge(X, y):

    pipeline_ridge = Pipeline([
        ('tfidf', TfidfTransformer()),
        ('kbest', SelectKBest()),
        ('clf', RidgeClassifier())
    ])

    parameters_ridge = {
        'tfidf__use_idf': (True, False),
        'kbest__k': (500, 1000, 3000, 'all'),
        'kbest__score_func': (chi2,),
        'clf__alpha': (.01, .04, .05, .06, .07, .08),
        'clf__normalize': (True, False),
    }

    grid_search(pipeline_ridge, parameters_ridge, X, y)

    # Best score: 0.925
    # Best parameters set:
    #     clf__alpha: 0.04
    #     clf__normalize: True
    #     kbest__k: 'all'
    #     kbest__score_func: <function chi2 at 0x7f1a26e6d510>
    #     tfidf__use_idf: False


def grid_search_perceptron(X, y):

    pipeline_perceptron = Pipeline([
        ('tfidf', TfidfTransformer()),
        ('kbest', SelectKBest()),
        ('clf', Perceptron())
    ])

    parameters_perceptron = {
        'tfidf__use_idf': (True, False),
        'kbest__k': (1000, 'all'),
        'kbest__score_func': (chi2,),
        'clf__alpha': (.01, .1, .5, 1.0, 5, 10),
        'clf__penalty': (None, 'l2', 'l1', 'elasticnet'),
        'clf__class_weight': ('auto', None),
        'clf__warm_start': (True, False),
        'clf__eta0': (0.1, 1, 10)
    }

    grid_search(pipeline_perceptron, parameters_perceptron, X, y)


def grid_search_by_name(name, X, y):

    name_to_func = {
        'lin_svc': grid_search_lin_svc,
        'svc_rbf': grid_search_svc_rbf,
        'lr': grid_search_lr,
        'sgdc': grid_search_sgdc,
        'nb': grid_search_nb,
        'ridge': grid_search_ridge,
        'perceptron': grid_search_perceptron
    }

    name_to_func[name](X, y)


if __name__ == '__main__':

    import sys

    algorithms = {
        'LinearSVC': LinearSVC(C=100),
        'GaussianNB': GaussianNB(),
        'PolySVC': SVC(kernel='poly', degree=3, C=5000),
        'ExpSVC': SVC(kernel='rbf', C=5000),
        'SGDC': SGDClassifier(loss="log"),
        'LogisticRegression': LogisticRegression(C=10000),
        'Perceptron': Perceptron(),
        'Ridge': RidgeClassifier(alpha=.02)
    }

    classifiers = ['lin_svc', 'svc_rbf', 'lr', 'nb', 'sgdc', 'ridge', 'perceptron']
    classifiers.sort()

    if len(sys.argv) != 3:
        print("Wrong number of input arguments. \n"
              "Usage: {} [DATA FILENAME] [ALGORITHM: {}]".format(sys.argv[0], classifiers))

    data_file = sys.argv[1]
    person, words, people, X, y = import_csv(data_file)

    name = sys.argv[2]

    #grid_search_by_name(name, X, y)

    pipeline_cross_validation(X, y)

    top_word = get_best_features(words, 1, X, y)
    top_20_words = get_best_features(words, 20, X, y)

    print('Best word for classification: {}'.format(top_word))
    print('Best 20 words for classification: {}'.format(top_20_words))
