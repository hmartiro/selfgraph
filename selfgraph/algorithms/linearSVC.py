import csv
from sklearn import svm


def import_CSV(file_name):
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


def train(X, Y):
    clf = svm.SVC()
    clf.fit(X, Y)

    return clf


def test(clf, X):
    predicted_Y = clf.predict(X)

    return predicted_Y


def output_results(people, test_results):
    for x in zip(people, test_results):
        if x[1] == '1':
            print("{} is a friend".format(x[0]))
        elif x[1] == '3':
            print("{} is an acquaintance".format(x[0]))