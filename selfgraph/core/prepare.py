"""

"""

import logging

import statistics
import re
import csv
from pprint import pprint

from neomodel import db
from .graph import Word, Heard, Person
from .graph import *


def select_words(person_name):

    # find all words and total frequency
    min_freq = 5
    stdev_weight = 6

    query_str = 'match (w:Word)-[h:HEARD]-(p:Person) where p.address = \'{}\' ' \
                'OR h.name = \'{}\' return w.value, ' \
                'sum(h.frequency)'.format(person_name, person_name)
    words, query_items = db.cypher_query(query_str)

    logging.info('Unique words: {}'.format(len(words)))
    logging.info('Total uses: {}'.format(sum(w[1] for w in words)))

    words_freq_too_low = []
    # remove words with freq too low
    appended_freq_list = []
    for word in list(words):
        word_freq = word[1]
        if word_freq < min_freq:
            words_freq_too_low.append(word)
            logging.debug('Removing word, freq < {}: {}'.format(
                min_freq,
                word[0]
            ))
        else:
            appended_freq_list.append(word_freq)

    print('TO REMOVE, freq < {}, {} words: {}\n\n'.format(
        min_freq, len(words_freq_too_low), [w[0] for w in words_freq_too_low]))

    # find mean of words
    stdev = statistics.stdev(w[1] for w in words)
    mean = statistics.mean(appended_freq_list)

    logging.info('stdev:{} and mean:{}'.format(stdev, mean))

    # remove words with freq too high
    max_freq = mean + stdev_weight*stdev
    words_freq_too_high = []
    for word in list(words):
        word_freq = word[1]
        if word_freq > max_freq:
            words_freq_too_high.append(word)
            logging.debug('Removing word, freq > {}: {}'.format(
                max_freq,
                word[0]
            ))

    print('TO REMOVE, freq > {}, {} words: {}\n\n'.format(
        max_freq, len(words_freq_too_high), [w[0] for w in words_freq_too_high]))

    words_to_remove = words_freq_too_high + words_freq_too_low

    word_vals = sorted([w[0] for w in words])
    words_to_remove_vals = sorted([w[0] for w in words_to_remove])

    words_to_keep_vals = sorted(set(word_vals).difference(set(words_to_remove_vals)))
    print('TO KEEP, {} words: {}\n\n'.format(
        len(words_to_keep_vals), words_to_keep_vals))

    # Deactivate words in DB
    word_nodes_dict = {n.value: n for n in Word.nodes.all()}
    activated = 0
    for word, word_node in word_nodes_dict.items():

        if word not in word_vals:
            continue

        state = not word in words_to_remove_vals
        logging.debug('Word: {}, New: {}, Old: {}'.format(
            word, state, word_node.active
        ))

        if word_node.active != state:
            word_node.active = state
            word_node.save()
        else:
            logging.debug('States are the same!')

        if state:
            activated += 1
            logging.debug('Words active: {}'.format(activated))

    logging.info('Query string for select_words:\n{}'.format(query_str))

    return words


def train_people(person_name):

    options = dict(
        acquaintance=Relation.CATEGORIES['acquaintance'],
        friend=Relation.CATEGORIES['friend']
    )

    while True:
        relation = input('Enter {} for acquaintance or {} for friend -> {}: '
                         .format(options['acquaintance'], options['friend'], person_name))

        try:
            relation = int(relation)
        except ValueError:
            logging.error('Enter a number!')
            continue

        if relation not in options.values():
            logging.error('{} is not a valid relation type!'.format(relation))
            continue

        return relation


def create_word_people_freq(words, freq, people, distinct_people):

    word_dict = {}
    for distinct_word in set(words):
        row_list = [0]*len(distinct_people)
        for i in range(len(words)):
            if distinct_word == words[i] and people[i] in distinct_people:
                row_list[distinct_people.index(people[i])] = freq[i]
        word_dict[distinct_word] = row_list

    return word_dict


def build_training_matrix(words, freq, people, distinct_people):

    # Get correct labels by prompting user
    relation = [train_people(p) for p in distinct_people]

    return create_word_people_freq(words, freq, people, distinct_people), relation


def build_testing_matrix(words, freq, people, distinct_people):
        return create_word_people_freq(words, freq, people, distinct_people), [0]*len(distinct_people)


def build_training_and_testing_sets(person_name):

    percent_training = 0.7
    select_words(person_name)

    query_str = \
        'match (w:Word)-[h:HEARD]-(p:Person) where w.active = True and ' \
        '(p.address=\'{}\' or h.name=\'{}\') ' \
        'return w.value, h.frequency, h.name, p.address'.format(person_name, person_name)
    heard_words, query_items = db.cypher_query(query_str)

    heard_words = [[w[0], w[1], (w[2] if w[3] == person_name else w[3])] for w in heard_words]
    logging.info('build training query:\n{}'.format(query_str))

    logging.info('All heards: {}'.format(len(heard_words)))

    # Merge operation
    heard_words.sort()

    for i in range(len(heard_words)-1):
        if heard_words[i] == heard_words[i-1]:
            logging.debug('Merge: {}, {}'.format(heard_words[i], heard_words[i-1]))
            heard_words[i][1] += heard_words[i-1][1]
            heard_words[i-1][1] = heard_words[i][1]

    # Deduplicate list, frequencies already added
    heard_words = list(set(tuple(word) for word in heard_words))

    logging.info('Unique heards: {}'.format(len(heard_words)))

    logging.info('Unique words: {}'.format(len(list(set([w[0] for w in heard_words])))))

    words, freq, people = list(zip(*heard_words))
    distinct_people = list(set(people))
    logging.debug('Distict people: {}'.format(distinct_people))

    # find test and training matrices
    training_inx = round(len(distinct_people)*percent_training)

    logging.info('Chose {} people for training, {} for testing.'.format(
        training_inx,
        len(distinct_people) - training_inx
    ))
    logging.debug('Training people: {}'.format(distinct_people[:training_inx]))
    logging.debug('Testing people: {}'.format(distinct_people[training_inx:]))

    training_dict, training_relation = build_training_matrix(
        words, freq, people,
        distinct_people[:training_inx]
    )

    testing_dict, testing_relation = build_testing_matrix(
        words, freq, people,
        distinct_people[training_inx:]
    )

    # output training matrix to file
    train_filename = '{}.TRAIN'.format(re.search('%s(.*)%s' % ('<', '>'), person_name).group(1))
    with open(train_filename, 'w') as train_file:
        writer = csv.writer(train_file, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["%s " % person for person in distinct_people[:training_inx]])
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
        writer.writerow(["%s " % person for person in distinct_people[training_inx:]])
        writer.writerow(["%s " % entry for entry in testing_dict])
        for i in range(len(testing_relation)):
            row = [training_dict[entry][i] for entry in testing_dict]
            row.insert(0, testing_relation[i])
            writer.writerow(row)

if __name__ == '__main__':

    import sys

    name = sys.argv[1]
    build_training_and_testing_sets(name)
