"""

"""

import logging
import random
from collections import Counter
from nltk.stem.snowball import SnowballStemmer

from selfgraph.core.db import GraphDB
from selfgraph.core.categories import ROLES, RELATIONS, MESSAGES
from selfgraph.core.alias import create_alias, update_relationships_with_alias

db = GraphDB()

MAX_WORDS_PER_MESSAGE = 500


def load_data(data, range_inx=None, clear=False):
    """
    Creates Messages, People, and Roles for the given file.

    """

    logging.info('Total messages in file: {}'.format(len(data)))
    if range_inx:
        data = data[range_inx[0]:range_inx[1]]
    logging.info('Messages to be loaded: {}'.format(len(data)))

    if clear:
        logging.warning('CLEARING DATABASE!')
        input('Press enter if you\'re sure!')
        db.clear()

    db.create_index('Person', 'address')
    db.create_index('Person', 'alias')
    db.create_index('Word', 'value')
    db.create_index('Word', 'active')

    # TODO this doesn't work, indices are currently only for nodes
    db.create_index('HEARD', 'name')
    db.create_index('ROLE', 'category')
    db.create_index('RELATION', 'category')

    messages_to_merge = set()
    words_to_merge = set()
    people_to_merge = set()
    roles_to_merge = set()
    relations_to_merge = set()
    heards_to_merge = list()

    for m in data:

        num_people = 0
        for field in ['to', 'from', 'cc', 'bcc']:
            num_people += len(m[field])

        # Ignore large group emails to avoid having to classify
        if num_people > 30:
            continue

        # Queue all Message data
        msg_data = (
            MESSAGES['email'],
            m['date'],
            m['text'],
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
        logging.info('Roles in message: {}'.format([(r[0], r[1]) for r in roles]))

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

        logging.info('Relations in message: {}'.format(relations))

        # Queue all HEARD relationships
        heards = [[
            to_person,
            freq,
            from_person,
            word
        ] for word, freq in word_freqs.items() for to_person in to_people]
        heards_to_merge.extend(heards)
        # logging.info('Heards in message: {}'.format(heards))

    # Combine heards and sum up their frequencies
    logging.info('Total heards: {}'.format(len(heards_to_merge)))
    heards_to_merge = sorted(heards_to_merge, key=lambda h: (h[3], h[0], h[2]))
    for i in range(len(heards_to_merge) - 1):
        h0 = heards_to_merge[i]
        h1 = heards_to_merge[i+1]
        if h0[0] == h1[0] and h0[2] == h1[2] and h0[3] == h1[3]:
            h0[1] = h0[1] + h1[1]
            h1[1] = h0[1]
            logging.debug('Combined {}, {}, {} {}'.format(h0[0], h0[2], h0[3], h0[1]))
    heards_to_merge = set(tuple(d) for d in heards_to_merge)
    logging.info('Unique heards: {}'.format(len(heards_to_merge)))

    # use alias to update relations, heards, and roles
    person_alias = create_alias(list(people_to_merge))
    relations_to_merge, heards_to_merge, roles_to_merge = \
        update_relationships_with_alias(person_alias, relations_to_merge, heards_to_merge, roles_to_merge)

    messages_to_merge_data = [(
        ['Message'],
        dict(category=category, date=date, text=text),  # Match criteria
        dict(processed=False),  # If created
        dict(),  # If matched
    ) for category, date, text in messages_to_merge]

    words_to_merge_data = [(
        ['Word'],
        dict(value=word),  # Match criteria
        dict(active=True),  # If created
        dict()  # If matched
    ) for word in words_to_merge]

    people_to_merge_data = []
    new_people_to_merge = []
    for address in people_to_merge:
        if address not in (y for x in person_alias for y in x):
            people_to_merge_data.append((
                ['Person'],
                dict(address=address),  # Match criteria
                dict(alias=False),  # If created
                dict()  # If matched
            ))
            new_people_to_merge.append(address)
    for x in person_alias:
        people_to_merge_data.append((
            ['Person'],
            dict(address=x[0]),  # Match criteria
            dict(alias=False),  # If created
            dict()  # If matched
        ))
        new_people_to_merge.append(x[0])
        for y in x[1:]:

            people_to_merge_data.append((
                ['Person'],
                dict(address=y),  # Match criteria
                dict(alias=True),  # If created
                dict(alias=True)  # If matched
            ))
            new_people_to_merge.append(y)

    message_nodes = db.merge_nodes(messages_to_merge_data)
    message_dict = dict(zip(messages_to_merge, message_nodes))

    word_nodes = db.merge_nodes(words_to_merge_data)
    word_dict = dict(zip(words_to_merge, word_nodes))

    person_nodes = db.merge_nodes(people_to_merge_data)
    person_dict = dict(zip(new_people_to_merge, person_nodes))

    roles_to_merge_data = [(
        'ROLE',
        person_dict[person]._id,
        message_dict[message]._id,
        dict(category=role),  # Match criteria
        dict(),  # If created
        dict()  # If matched
    ) for person, role, message in roles_to_merge]

    role_nodes = db.merge_relationships_by_id(roles_to_merge_data)
    role_dict = dict(zip(roles_to_merge, role_nodes))

    relations_to_merge_data = [(
        'RELATION',
        person_dict[from_person]._id,
        person_dict[to_person]._id,
        dict(),  # Match criteria
        dict(category=category),  # If created
        dict()  # If matched
    ) for from_person, category, to_person in relations_to_merge]

    relation_nodes = db.merge_relationships_by_id(relations_to_merge_data)
    relation_dict = dict(zip(relations_to_merge, relation_nodes))

    # Merge heards, creating with 0 frequency if they don't exist
    heards_to_merge_data = [(
        'HEARD',
        person_dict[to_person]._id,
        word_dict[word]._id,
        dict(name=from_person),  # Match criteria
        dict(frequency=0),  # If created
        dict()  # If matched
    ) for to_person, freq, from_person, word in heards_to_merge]

    heard_nodes = db.merge_relationships_by_id(heards_to_merge_data)
    heard_dict = dict(zip(heards_to_merge, heard_nodes))

    # Do heards over again, this time updating the frequencies
    heards_to_merge_data = [(
        'HEARD',
        person_dict[heard_data[0]]._id,
        word_dict[heard_data[3]]._id,
        dict(name=heard_data[2]),  # Match criteria
        dict(),  # If created
        dict(frequency=heard_dict[heard_data].get_cached_properties()['frequency'] + heard_data[1])  # If matched
    ) for heard_data in heards_to_merge]

    heard_nodes = db.merge_relationships_by_id(heards_to_merge_data)
    heard_dict = dict(zip(heards_to_merge, heard_nodes))

    alias_to_merge_data = []
    for x in person_alias:
        for y in x[1:]:
            alias_to_merge_data.append((
                'ALIAS',
                person_dict[x[0]]._id,
                person_dict[y]._id,
                dict(),  # Match criteria
                dict(),  # If created
                dict()  # If matched
            ))
    alias_nodes = db.merge_relationships_by_id(alias_to_merge_data)

if __name__ == '__main__':

    import sys
    import pickle

    in_file = sys.argv[1]

    range_inx = None
    if len(sys.argv) >= 4:
        range_inx = [int(sys.argv[2]), int(sys.argv[3])]

    clear_db = '--clear' in sys.argv

    with open(in_file, 'rb') as file:
        messages = pickle.loads(file.read())
        load_data(messages, range_inx=range_inx, clear=clear_db)
