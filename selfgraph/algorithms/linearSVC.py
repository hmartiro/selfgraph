import csv
from sklearn import svm
import numpy as np
from sklearn.preprocessing import scale, normalize

def train(X, Y):

    X_array = np.array(X)
    #X_array = normalize(X_array, axis=0, norm='l2')

    lin_clf = svm.LinearSVC()
    lin_clf.fit(X_array, Y)

    return lin_clf


def test(lin_clf, X):
    predicted_Y = lin_clf.predict(X)

    return predicted_Y


def output_results(people, test_results):
    for person, label in zip(people, test_results):
        if label == 1:
            print("{} is a friend".format(person))
        elif label == 3:
            print("{} is an acquaintance".format(person))
        else:
            print('Uh oh, unknown label {} for person {}'.format(label, person))
