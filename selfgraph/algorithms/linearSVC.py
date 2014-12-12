import csv
from sklearn import svm
import numpy as np
from sklearn.preprocessing import scale, normalize
from sklearn.decomposition import PCA, KernelPCA, TruncatedSVD
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import SGDClassifier, LogisticRegression, Perceptron

def train(X, Y):

    X_array = np.array(X)

    pca = PCA(n_components=250, whiten=True)

    X_pca = pca.fit_transform(X_array, y=Y)

    #lin_clf = svm.SVC(class_weight={1: 0.8, 3: 0.3})
    lin_clf = svm.LinearSVC(C=0.1, verbose=1)
    #lin_clf = LogisticRegression(C=1.0)
    #lin_clf = SGDClassifier()
    #lin_clf = Perceptron()
    lin_clf.fit(X_array, Y)

    print('Training score: {}'.format(lin_clf.score(X_array, Y)))

    return lin_clf, pca


def test(lin_clf, pca, X):

    X_array = np.array(X)
    X_pca = pca.transform(X_array)

    predicted_Y = lin_clf.predict(X_array)

    return predicted_Y


def output_results(people, test_results):
    for person, label in zip(people, test_results):
        if label == 1:
            print("{} is a friend".format(person))
        elif label == 3:
            print("{} is an acquaintance".format(person))
        else:
            print('Uh oh, unknown label {} for person {}'.format(label, person))
