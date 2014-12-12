"""

"""
import numpy as np
from py2neo import neo4j
from sklearn import cross_validation
from sklearn import svm

from selfgraph.algorithms import linearSVC, naive_bayes
from selfgraph.utils.csv import import_csv
from selfgraph.core.categories import RELATIONS
from selfgraph.core.db import GraphDB

db = GraphDB()


def test_naive_bayes(train_name, test_name):

    person, words, word_freq_friends, word_freq_acquaints, Y = naive_bayes.import_train_CSV(train_name)

    print('len words: {}, len friends: {}, len acquaint: {}'.format(
        len(words),
        len(word_freq_friends),
        len(word_freq_acquaints)
    ))

    print('Friend words: {}'.format(word_freq_friends))
    print('Acquaintance words: {}'.format(word_freq_acquaints))

    phi_k_friend, phi_friend, phi_k_acquaint, phi_acquaint = naive_bayes.train(
        words, word_freq_friends, word_freq_acquaints, Y
    )

    print('friend_prior: {}'.format(phi_friend))
    print('acquaint_prior: {}'.format(phi_acquaint))

    word_list, people_list, X = naive_bayes.import_test_CSV(test_name)

    friend_prob, acquaint_prob = naive_bayes.test(
        X, phi_k_friend, phi_friend, phi_k_acquaint, phi_acquaint
    )

    Y_test = naive_bayes.output_results(friend_prob, acquaint_prob, people_list)

    confusion = confusion_matrix(person, people_list, Y_test)

    return person, people_list, confusion


def test_SVM(train_name, test_name):

    person, words, train_people, X, Y = import_csv(train_name)
    person, words, test_people, X_test, Y_test = import_csv(test_name)

    lin_clf, pca = linearSVC.train(X, Y)

    Y_test = linearSVC.test(lin_clf, pca, X_test)
    linearSVC.output_results(test_people, Y_test)

    confusion = confusion_matrix(person, test_people, Y_test)

    return person, test_people, confusion


def confusion_matrix(person, people, Y):

    print('Confusion matrix for classifying {} people in relation to [{}]:'.format(
        len(people), person
    ))

    query_str = 'match (p:Person {{address: \'{}\'}})-[r:RELATION]-(p1:Person) ' \
                'return p1.address, r.category'.format(person)
    print(query_str)

    data = db.query(query_str)
    data.sort()

    relation_map = {}
    for p, r in data:
        relation_map[p] = r

    confusion = {
        RELATIONS['friend']: [0, 0],
        RELATIONS['acquaintance']: [0, 0]
    }

    for p, y in zip(people, Y):
        if y == relation_map[p]:
            confusion[y][0] += 1
        else:
            print('Incorrect classification: {}, given {} not {}'.format(
                p, y, relation_map[p]
            ))
            confusion[y][1] += 1

    return confusion


def print_results(person, people, confusion):

    total_correct = sum(v[0] for v in confusion.values())
    total_incorrect = sum(v[1] for v in confusion.values())
    assert(total_correct + total_incorrect == len(people))
    error = total_incorrect / len(people)

    print('')
    print('Results')
    print('-----------------------------------')
    print('Person: {}'.format(person))

    print('')
    print('Confusion Matrix:\n')
    for relation, v in confusion.items():
        print('  Relation {}:'.format(relation))
        print('      Correct: {}'.format(v[0]))
        print('    Incorrect: {}'.format(v[1]))

    print('')
    print('# total classifications:     {}'.format(len(people)))
    print('# correct classifications:   {}'.format(total_correct))
    print('# incorrect classifications: {}'.format(total_incorrect))
    print('')
    print('Error rate: {}'.format(error))




if __name__ == '__main__':

    import sys

    algo_names = ['nb', 'linSVC']

    if len(sys.argv) != 4:
        print("Error! Wrong number of input arguments. \n"
              "USAGE: test.py [TRAIN TYPE: {}] [TRAIN FILENAME] [TEST FILENAME]".format(', '.join(algo_names)))

    algorithm = sys.argv[1]
    train_name = sys.argv[2]
    test_name = sys.argv[3]

    test_cross_validation(train_name)

    # validation_count = 5
    # categories = 2
    #
    # results = []
    # for i in range(validation_count):
    #
    #     if algorithm == 'nb':
    #         person, people_list, confusion = test_naive_bayes(
    #             '{}.{}'.format(train_name, i), '{}.{}'.format(test_name, i)
    #         )
    #     elif algorithm == 'linSVC':
    #         person, people_list, confusion = test_SVM(
    #             '{}.{}'.format(train_name, i), '{}.{}'.format(test_name, i)
    #         )
    #     else:
    #         raise Exception("{} is not a valid algorithm name. Valid names are: {}".format(', '.join(algo_names)))
    #
    #     results.append((person, people_list, confusion))
    #
    # person = results[0][0]
    # people_list_total = []
    # confusion_total = None
    #
    # for person, people_list, confusion in results:
    #
    #     people_list_total.extend(people_list)
    #
    #     if not confusion_total:
    #         confusion_total = confusion
    #     else:
    #         for key, value in confusion.items():
    #             for i, entry in enumerate(value):
    #                 confusion_total[key][i] += entry
    #
    # print_results(person, people_list_total, confusion_total)
