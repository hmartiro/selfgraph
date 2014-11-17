"""

"""

import logging

import statistics
import re
import csv
from neomodel import db
from .graph import Word, Heard, Person
from .graph import *


def select_words():
    # find all words and total frequency
    min_freq = 5
    stdev_weight = 3
    words, query_items = db.cypher_query('match (w:Word)-[h:HEARD]-(p:Person) return w.value, count(h.frequency)')

    # remove words with freq too low
    appended_freq_list = []
    ttl_freq_list = []
    for word in list(words):
        word_freq = word[1]
        ttl_freq_list.append(word_freq)
        if word_freq < min_freq:
            words.remove(word)
        else:
            appended_freq_list.append(word_freq)

    # find mean of words
    stdev = statistics.stdev(ttl_freq_list)
    mean = statistics.mean(appended_freq_list)

    logging.debug('stdev:{} and mean:{}'.format(stdev, mean))

    # remove words with freq too high
    for word in list(words):
        word_freq = word[1]
        if word_freq > mean+stdev_weight*stdev:
            word.remove(word_freq)
            word_node = Word.get(word[0])
            word_node.active = False
            word_node.save()

    logging.debug('Important Words:', words)

    return words


def train_people(person_name):
    options = {}
    options.update({'acquaintance': Relation.CATEGORIES['acquaintance']})
    options.update({'friend': Relation.CATEGORIES['friend']})

    valid_relation = 0
    while valid_relation == 0:
        relation = input('Enter {} for acquaintance or {} for friend -> {}: '
                         .format(options['acquaintance'], options['friend'], person_name))
        for option in options:
            if options[option] == int(relation):
                valid_relation = 1
        if valid_relation == 0:
            print('ERROR! {} is a invalid relation type!'.format(relation*5))

    return relation

def create_word_people_freq(words, freq, people, distinct_people):
    word_dict = {}

    for distinct_word in set(words):
        row_list = [0]*len(distinct_people)
        for i in range(len(words)):
            if distinct_word == words[i]:
                said_person = people[i]
                if said_person in distinct_people:
                    row_list.insert(distinct_people.index(said_person), freq[i])
        word_dict.update({distinct_word: row_list})

    return word_dict

def build_training_matrix(words, freq, people, distinct_people):
    # train a portion of the people relations
    relation = []

    for person in distinct_people:
        relation.append(train_people(person))

    return create_word_people_freq(words, freq, people, distinct_people), relation


def build_testing_matrix(words, freq, people, distinct_people):
        return create_word_people_freq(words, freq, people, distinct_people), [0]*len(distinct_people)


def build_training_and_testing_sets(person_name):
    percent_training = 0.7
    select_words()
    heard_words, query_items = db.cypher_query('match (w:Word)-[h:HEARD]-(p:Person) where w.active = true AND '
                                               'p.address={} return w.value, '
                                               'h.frequency, h.name'.format(person_name))

    words, freq, people = list(zip(*heard_words))
    distinct_people = list(set(people))

    # find test and training matrices
    training_range = range(round(len(distinct_people)*percent_training))
    testing_range = range(training_range[-1]+1, len(distinct_people))
    distinct_people = list(set(people))
    training_dict, training_relation = build_training_matrix(words, freq, people,
                                                             distinct_people[training_range[0]:training_range[-1]])
    testing_dict, testing_relation = build_testing_matrix(words, freq, people,
                                                          distinct_people[testing_range[0]:testing_range[-1]])

    # output training matrix to file
    train_filename = '{}.TRAIN'.format(re.search('%s(.*)%s' % ('<', '>'), person_name).group(1))
    with open(train_filename, 'w') as train_file:
        writer = csv.writer(train_file, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["%s " % person for person in distinct_people[training_range[0]:training_range[-1]]])
        writer.writerow(["%s " % entry for entry in training_dict])
        for i in range(len(training_relation)):
            row = [training_dict[entry][i] for entry in training_dict]
            row.insert(0, training_relation[i])
            writer.writerow(row)

    # output testing matrix to file
    test_filename = '{}.TEST'.format(re.search('%s(.*)%s' % ('<', '>'), person_name).group(1))
    with open(test_filename, 'w') as test_file:
        writer = csv.writer(test_file, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["%s " % person for person in distinct_people[testing_range[0]:testing_range[-1]]])
        writer.writerow(["%s " % entry for entry in testing_dict])
        for i in range(len(testing_relation)):
            row = [training_dict[entry][i] for entry in testing_dict]
            row.insert(0, testing_relation[i])
            writer.writerow(row)

if __name__ == '__main__':

    import sys

    name = sys.argv[1]
    build_training_and_testing_sets(name)
