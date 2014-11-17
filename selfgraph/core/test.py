"""

"""

import logging
import csv
from .graph import Relation
import operator
import math
from .train import *


def matrix_read_test(file_name):
    matrix = []
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            matrix.append(row)

    people = matrix[0]
    word = matrix[1]
    frequency = []
    for i in range(2, len(matrix)):
        frequency.append(list(map(int, matrix[i])))

    return word, people, frequency


def test_naive_bayes(words, people, frequency, friend_phi, friend_prior, acquaint_phi, acquaint_prior):
    ttl_num_words = len(words)

    for i in range(len(frequency)):
        friend_prob = sum(list(map(operator.mul, frequency[i], friend_phi))) + friend_prior
        acquaint_prob = sum(list(map(operator.mul, frequency[i], acquaint_phi))) + acquaint_prior

        print(friend_prior)
        print(acquaint_prior)
        if(friend_prob > acquaint_prob):
            print("{} is a friend with {} to {}".format(people[i], friend_prob, acquaint_prob))
        elif(friend_prob < acquaint_prob):
            print("{} is a acquaintance with {} to {}".format(people[i], acquaint_prob, friend_prob))
        else:
            print("Can not decide relationship for {}".format(people[i]))


if __name__ == '__main__':
    import sys

    train_name = sys.argv[1]
    words, friend_words, acquaint_words, num_people = matrix_read_train(train_name)
    friend_phi, friend_prior, acquaint_phi, acquaint_prior = naive_bayes(words, friend_words,
                                                                         acquaint_words, num_people)

    test_name = sys.argv[2]
    word_list, people_list, frequency_matrix = matrix_read_test(test_name)
    test_naive_bayes(word_list, people_list, frequency_matrix, friend_phi, friend_prior, acquaint_phi, acquaint_prior)


