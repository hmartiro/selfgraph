"""

"""

import yaml
import hashlib
import logging
import random
from collections import Counter
from py2neo import neo4j, node, rel
from py2neo.neo4j import Node, Record
from nltk.stem.snowball import SnowballStemmer

from .categories import ROLES, RELATIONS, MESSAGES

graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

BATCH_SIZE = 500
MAX_WORDS_PER_MESSAGE = 1000


def md5sum(data):
    return hashlib.md5(data.encode()).digest()


def merge_nodes(nodes):
    """
    :param nodes: List of (label, properties) tuples.
    """

    batch = neo4j.WriteBatch(graph_db)
    merges = [
        "MERGE (n%d:%s {%s})" % (
            i,
            node[0],
            ', '.join(['{}: \'{}\''.format(k, v) for k, v in node[1].items()])
        ) for i, node in enumerate(nodes)]

    query = ' \n'.join(merges)
    query += ' \nRETURN {};'.format(', '.join(
        ['n{}'.format(i) for i in range(len(nodes))]
    ))

    batch.append_cypher(query)
    return batch.submit()


def merge_nodes_in_batches(nodes_data):
    ret_nodes = []
    for i in range(len(nodes_data))[::BATCH_SIZE]:
        batch_args = nodes_data[i:i+BATCH_SIZE]
        ret = merge_nodes(batch_args)
        if type(ret[0]) == Record:
            ret_nodes.extend(ret[0].values)
        else:
            ret_nodes.append(ret[0])
    return ret_nodes


def get_or_create_relationships_in_batches(rels_data):
    ret_rels = []
    for i in range(len(rels_data))[::BATCH_SIZE]:
        batch_args = rels_data[i:i+BATCH_SIZE]
        ret = get_or_create_relationships(batch_args)
        if type(ret) == list:
            ret_rels.extend(ret)
        else:
            ret_rels.append(ret)
    return ret_rels


def get_or_create_relationships(relationships):
    """
    :param edges: List of (start_node, type, end_node, properties).
    """

    batch = neo4j.WriteBatch(graph_db)
    for r_data in relationships:
        batch.create(rel(r_data))
    return batch.submit()


def load_data(data, range_inx=None):
    """
    Creates Messages, People, and Roles for the given file.

    """
    logging.info('Total messages in file: {}'.format(len(data)))
    if range_inx:
        data = data[range_inx[0]:range_inx[1]]
    logging.info('Messages to be loaded: {}'.format(len(data)))

    # graph_db.clear()

    messages_to_merge = set()
    words_to_merge = set()
    people_to_merge = set()
    roles_to_merge = set()
    relations_to_merge = set()
    heards_to_merge = set()

    for m in data:
        print(m)
        # Queue all Message data
        msg_data = (
            MESSAGES['email'],
            m['date'],
            m['text'],
            #md5sum(m['text'] + m['date'])
        )
        messages_to_merge.add(msg_data)
        logging.info('Processing message of length {}'.format(len(m['text'])))

        # Queue all Word data
        # Take a max fixed number of random words
        stemmer = SnowballStemmer("english")
        random_plural_words = m['text'].split()
        random_words = []
        for word in random_plural_words:
            random_words.append(stemmer.stem(word))
        random.shuffle(random_words)
        word_freqs = Counter(random_words[:MAX_WORDS_PER_MESSAGE])
        words = set(word_freqs.keys())
        words_to_merge.update(words)
        #logging.info('Words in message: {}'.format(words))

        # Queue all People data
        people = set(m['to'] + m['from'] + m['cc'] + m['bcc'])
        people_to_merge.update(people)
        logging.info('People in message: {}'.format(people))

        # Queue all CONTAINS relationships
        # TODO do we even need these?

        # Queue all ROLE relationships
        roles = [(
            person,
            ROLES[field],
            msg_data
        ) for field in ['to', 'from', 'cc', 'bcc'] for person in m[field]]
        roles_to_merge.update(roles)
        # logging.info('Roles in message: {}'.format(roles))

        # Queue all RELATION relationships
        try:
            from_person = m['from'][0]
        except IndexError:
            continue

        to_people = m['to'] + m['cc'] + m['bcc']
        relations = [(
            from_person,
            RELATIONS['unknown'],
            person
        ) for person in to_people]
        relations_to_merge.update(relations)
        # logging.info('Relations in message: {}'.format(relations))

        # Queue all HEARD relationships
        heards = [(
            to_person,
            freq,
            from_person,
            word
        ) for word, freq in word_freqs.items() for to_person in to_people]
        heards_to_merge.update(heards)
        # logging.info('Heards in message: {}'.format(heards))

    messages_to_merge_data = [('Message', {
        'category': category,
        'date': date,
        'text': text,
        #'uuid': uuid
    }) for category, date, text in messages_to_merge]

    words_to_merge_data = [('Word', {
        'value': word,
        'active': True
    }) for word in words_to_merge]

    people_to_merge_data = [('Person', {
        'address': address
    }) for address in people_to_merge]

    message_nodes = merge_nodes_in_batches(messages_to_merge_data)
    message_dict = dict(zip(messages_to_merge, message_nodes))

    word_nodes = merge_nodes_in_batches(words_to_merge_data)
    word_dict = dict(zip(words_to_merge, word_nodes))

    person_nodes = merge_nodes_in_batches(people_to_merge_data)
    person_dict = dict(zip(people_to_merge, person_nodes))

    roles_to_merge_data = [(
        person_dict[person],
        'ROLE',
        message_dict[message],
        {'category': role}
    ) for person, role, message in roles_to_merge]
    role_nodes = get_or_create_relationships_in_batches(roles_to_merge_data)
    role_dict = dict(zip(roles_to_merge, role_nodes))

    relations_to_merge_data = [(
        person_dict[from_person],
        'RELATION',
        person_dict[to_person],
        {'category': category}
    ) for from_person, category, to_person in relations_to_merge]
    relation_nodes = get_or_create_relationships_in_batches(relations_to_merge_data)
    relation_dict = dict(zip(relations_to_merge, relation_nodes))

    heards_to_merge_data = [(
        person_dict[to_person],
        'HEARD',
        word_dict[word],
        {'frequency': freq, 'name': from_person}
    ) for to_person, freq, from_person, word in heards_to_merge]
    heard_nodes = get_or_create_relationships_in_batches(heards_to_merge_data)
    heard_dict = dict(zip(heards_to_merge, heard_nodes))

if __name__ == '__main__':

    import sys
    import pickle

    in_file = sys.argv[1]

    range_inx = None
    if len(sys.argv) == 4:
        range_inx = [int(sys.argv[2]), int(sys.argv[3])]

    with open(in_file, 'rb') as file:
        messages = pickle.loads(file.read())
        load_data(messages, range_inx=range_inx)
