"""

"""

import logging

import statistics
import re
import csv
from pprint import pprint

from selfgraph.utils.csv import import_csv, export_csv
from selfgraph.core.categories import RELATIONS, ROLES, MESSAGES
from selfgraph.core.db import GraphDB

db = GraphDB()


def select_words(person_name):

    # find all words and total frequency
    min_freq = 5
    stdev_weight = 5

    query_str = 'match (w:Word)-[h:HEARD]-(p:Person) where p.address = \'{}\' ' \
                'OR h.name = \'{}\' return w.value, ' \
                'sum(h.frequency)'.format(person_name, person_name)

    words = db.query(query_str)

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

    logging.info('TO REMOVE, freq < {}, {} words: {}\n\n'.format(
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

    logging.info('TO REMOVE, freq > {}, {} words: {}\n\n'.format(
        max_freq, len(words_freq_too_high), [w[0] for w in words_freq_too_high]))

    words_to_remove = words_freq_too_high + words_freq_too_low

    word_vals = sorted([w[0] for w in words])
    words_to_remove_vals = sorted([w[0] for w in words_to_remove])

    words_to_keep_vals = sorted(set(word_vals).difference(set(words_to_remove_vals)))
    logging.info('TO KEEP, {} words: {}\n\n'.format(
        len(words_to_keep_vals), words_to_keep_vals))

    # Deactivate words in DB
    word_nodes = [n[0] for n in db.query('MATCH (w:Word) return w')]
    word_nodes_dict = {n.get_cached_properties()['value']: n for n in word_nodes}

    activated = 0
    for word, word_node in word_nodes_dict.items():

        if word not in word_vals:
            continue

        state = not word in words_to_remove_vals
        logging.debug('Word: {}, New: {}, Old: {}'.format(
            word, state, word_node.get_cached_properties()['active']
        ))

        # if word_node.active != state:
        db.batch.set_property(word_node, 'active', state)

        #word_node.set_properties = state
        #word_node.save()
        #else:
        #    logging.debug('States are the same!')

        if state:
            activated += 1
            logging.debug('Words active: {}'.format(activated))

    db.run()

    logging.info('Query string for select_words:\n{}'.format(query_str))

    return words


def train_people(person_name):

    options = dict(
        acquaintance=RELATIONS['acquaintance'],
        friend=RELATIONS['friend']
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


def build_training_matrix(words, freq, people, distinct_people, person_name):

    query_str = 'match (p:Person {{address: \'{}\'}})-[r:RELATION]-(p1:Person) ' \
                'return p1.address, r.category'.format(person_name)
    logging.info('Build training matrix query: {}'.format(query_str))
    data = db.query(query_str)

    person_relations = dict(data)
    relation = [person_relations[p] for p in distinct_people]

    return create_word_people_freq(words, freq, people, distinct_people), relation


def build_testing_matrix(words, freq, people, distinct_people):
    return create_word_people_freq(words, freq, people, distinct_people), [0]*len(distinct_people)


def build_unsupervised_matrix(words, freq, people, distinct_people):
    return create_word_people_freq(words, freq, people, distinct_people), [0]*len(distinct_people)


def build_training_and_testing_sets(person_name):

    percent_training = 0.7
    select_words(person_name)

    query_str = \
        'match (w:Word)-[h:HEARD]-(p:Person) where w.active = True and ' \
        '(p.address=\'{}\' or h.name=\'{}\') ' \
        'return w.value, h.frequency, h.name, p.address'.format(person_name, person_name)
    heard_words = db.query(query_str)
    logging.info('Heard words query:\n{}'.format(query_str))

    # Just show the person who is not known
    heard_words = [[w[0], w[1], (w[2] if w[3] == person_name else w[3])] for w in heard_words]

    logging.info('All heards: {}'.format(len(heard_words)))

    # Merge operation to combine words sent and received
    heard_words.sort()
    for i in range(len(heard_words)-1):
        h0, h1 = heard_words[i-1], heard_words[i]
        if h0[0] == h1[0] and h0[2] == h1[2]:

            logging.info('Merge: {}, {}'.format(heard_words[i], heard_words[i-1]))
            h1[1] += h0[1]
            h0[1] = h1[1]

    # Deduplicate list, frequencies already added
    heard_words = sorted(set(tuple(word) for word in heard_words))

    logging.info('Unique heards: {}'.format(len(heard_words)))

    logging.info('Unique words: {}'.format(len(list(set([w[0] for w in heard_words])))))

    words, freq, people = list(zip(*heard_words))
    distinct_people = list(set(people))

    # find test and training matrices
    training_inx = round(len(distinct_people)*percent_training)

    logging.info('Chose {} people for training, {} for testing.'.format(
        training_inx,
        len(distinct_people) - training_inx
    ))

    train_people_list = distinct_people[:training_inx]
    test_people_list = distinct_people[training_inx:]

    logging.debug('Training people: {}'.format(train_people_list))
    logging.debug('Testing people: {}'.format(test_people_list))

    training_dict, training_relation = build_training_matrix(
        words, freq, people,
        train_people_list, person_name
    )

    testing_dict, testing_relation = build_testing_matrix(
        words, freq, people,
        test_people_list
    )

    # output training matrix to file
    train_filename = '{}.TRAIN'.format(re.search('<?(.*)>?', person_name).group(1))
    export_csv(
        filename=train_filename,
        person=person_name,
        word_list=list(training_dict.keys()),
        people_list=train_people_list,
        X=list(zip(*training_dict.values())),
        Y=training_relation
    )
    # output testing matrix to file
    test_filename = '{}.TEST'.format(re.search('<?(.*)>?', person_name).group(1))
    export_csv(
        filename=test_filename,
        person=person_name,
        word_list=list(testing_dict.keys()),
        people_list=test_people_list,
        X=list(zip(*testing_dict.values())),
        Y=testing_relation
    )


def build_unsupervised_set(person_name):
    select_words(person_name)

    query_str = \
        'match (w:Word)-[h:HEARD]-(p:Person) where w.active = True and ' \
        '(p.address=\'{}\' or h.name=\'{}\') ' \
        'return w.value, h.frequency, h.name, p.address'.format(person_name, person_name)
    heard_words = db.query(query_str)
    logging.info('Heard words query:\n{}'.format(query_str))

    # Just show the person who is not known
    heard_words = [[w[0], w[1], (w[2] if w[3] == person_name else w[3])] for w in heard_words]

    logging.info('All heards: {}'.format(len(heard_words)))

    # Merge operation to combine words sent and received
    heard_words.sort()
    for i in range(len(heard_words)-1):
        h0, h1 = heard_words[i-1], heard_words[i]
        if h0[0] == h1[0] and h0[2] == h1[2]:

            logging.info('Merge: {}, {}'.format(heard_words[i], heard_words[i-1]))
            h1[1] += h0[1]
            h0[1] = h1[1]

    # Deduplicate list, frequencies already added
    heard_words = sorted(set(tuple(word) for word in heard_words))

    logging.info('Unique heards: {}'.format(len(heard_words)))

    logging.info('Unique words: {}'.format(len(list(set([w[0] for w in heard_words])))))

    words, freq, people = list(zip(*heard_words))
    distinct_people = list(set(people))

    word_dict, relation = build_unsupervised_matrix(words, freq, people, distinct_people)

    # output testing matrix to file
    test_filename = '{}.UNSUPERVISED'.format(re.search('<?(.*)>?', person_name).group(1))
    export_csv(
        filename=test_filename,
        person=person_name,
        word_list=list(word_dict.keys()),
        people_list=distinct_people,
        X=list(zip(*word_dict.values())),
        Y=relation
    )


if __name__ == '__main__':

    import sys

    prepare_types = ['sup', 'unsup']

    if len(sys.argv) != 4 or len(sys.argv) != 2:
        print("Error! Wrong number of input arguments. \n"
              "USAGE: prepare.py [NAME] --type [PREPARE TYPE: {}]".format(', '.join(prepare_types)))

    p_type = sys.argv[3]
    name = sys.argv[1]
    if p_type == 'sup':
        build_training_and_testing_sets(name)
    elif p_type == 'unsup':
        build_unsupervised_set(name)
