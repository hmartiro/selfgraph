import csv
from sklearn import svm

def SVM_matrix_read(file_name):
    Y = []
    X = []
    matrix = []
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            matrix.append(row)

    people_list = matrix[0]
    word_list = matrix[1]

    for row in matrix[2:]:
        Y.append(row[0])
        X.append(row[1:])

    return people_list, word_list, X, Y


def SVM(X, Y):
    clf = svm.SVC()
    clf.fit(X, Y)

    return clf

def test_SVM(clf, X):
    predicted_Y = clf.predict(X)

def print_SVM_results(people, test_results):
    for p, t in people, test_results:
        print("{} is a {}".format(p, t))