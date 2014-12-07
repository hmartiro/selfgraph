import logging
import csv
import operator
import math
from selfgraph.core.categories import RELATIONS
from selfgraph.utils.csv import import_csv


def import_train_CSV(file_name):

    person, word_list, people_list, X, Y = import_csv(file_name)

    options = dict(
        acquaintance=RELATIONS['acquaintance'],
        friend=RELATIONS['friend']
    )

    word_freq_friends = [0]*len(X[0])
    word_freq_acquaints = [0]*len(X[0])

    for x, y in zip(X, Y):
        if y == options['friend']:
            word_freq_friends = list(map(operator.add, word_freq_friends, x))
        if y == options['acquaintance']:
            word_freq_acquaints = list(map(operator.add, word_freq_acquaints, x))

    return person, word_list, word_freq_friends, word_freq_acquaints, Y


def import_test_CSV(file_name):

    person, word_list, people_list, X, Y = import_csv(file_name)

    # matrix = []
    # with open(file_name, 'r') as csvfile:
    #     reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    #     for row in reader:
    #         matrix.append(row)
    #
    # people = matrix[0]
    # word = matrix[1]
    # frequency = []
    # for i in range(2, len(matrix)):
    #     frequency.append(list(map(int, matrix[i])))

    return word_list, people_list, X


def train(words, word_freq_friends, word_freq_acquaints, Y):

    # Size of vocabulary
    ttl_num_words = len(words)

    # Total words said between friends vs acquaintances
    ttl_num_friend_words = sum(word_freq_friends)
    ttl_num_acquaint_words = sum(word_freq_acquaints)

    print(Y)
    num_people = len(Y)
    num_friends = sum(y == RELATIONS['friend'] for y in Y)
    num_acquaints = sum(y == RELATIONS['acquaintance'] for y in Y)
    print('Num people: {}, friends: {}, acquaintances: {}'.format(
        num_people, num_friends, num_acquaints
    ))

    phi_friend = num_friends / num_people
    phi_acquaint = num_acquaints / num_people

    phi_k_friend = []
    phi_k_acquaint = []
    for i in range(len(words)):

        phi_k_friend.append(
            math.log(
                (word_freq_friends[i] + 1) / (ttl_num_friend_words + ttl_num_words)
            )
        )
        phi_k_acquaint.append(
            math.log(
                (word_freq_acquaints[i] + 1) / (ttl_num_acquaint_words + ttl_num_words)
            )
        )

        print('Word: {}, friend phi: {}, acquaintence phi: {}'.format(words[i], phi_k_friend[i], phi_k_acquaint[i]))

    # Get the margin between the friend and acquintance for each word
    phi_k_diff = [phi_k_friend[i] - phi_k_acquaint[i] for i in range(len(phi_k_friend))]

    # Print top friend and acquaintance words
    top_friend_words = sorted(list(zip(phi_k_diff, words)))
    for i in range(10):
        print('#{} friend word: {}'.format(i+1, top_friend_words[-1-i]))
    for i in range(10):
        print('#{} acquaintance word: {}'.format(i+1, top_friend_words[i]))

    return phi_k_friend, phi_friend, phi_k_acquaint, phi_acquaint


def test(X, phi_k_friend, phi_friend, phi_k_acquaint, phi_acquaint):

    friend_prob = []
    acquaint_prob = []

    for i in range(len(X)):
        friend_prob.append(sum(list(map(operator.mul, X[i], phi_k_friend))) + phi_friend)
        acquaint_prob.append(sum(list(map(operator.mul, X[i], phi_k_acquaint))) + phi_acquaint)

    return friend_prob, acquaint_prob


def output_results(friend_prob, acquaint_prob, people):

    Y = []
    for x in zip(friend_prob, acquaint_prob, people):
        if x[0] > x[1]:
            print("{} is a friend with {} to {}".format(x[2], x[0], x[1]))
            Y.append(RELATIONS['friend'])
        elif x[0] < x[1]:
            print("{} is a acquaintance with {} to {}".format(x[2], x[0], x[1]))
            Y.append(RELATIONS['acquaintance'])
        else:
            print("Can not decide relationship for {}".format(x[2], x[0], x[1]))
            Y.append(RELATIONS['unknown'])
    return Y
