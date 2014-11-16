"""

"""

import yaml
import logging
from collections import Counter
from py2neo import neo4j, node, rel

def load_data(filename):
    """
    Creates Messages, People, and Roles for the given file.

    TODO: - clean things up and make it standardized
          - add in proper error handling

    """

    with open(filename) as file:
        data = yaml.load(file.read())

    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    graph_db.clear()

    role = {
        'to': 0,
        'from': 1,
        'cc': 2,
        'bcc': 3
    }
    relation = {
        'UNKNOWN': 0,
        'FRIEND': 1,
        'COWORKER': 2,
        'ACQUAINTANCE': 3,
        'FAMILY': 4,
        'NEWSLETTER': 5
    }

    message_type = {
        'email': 0,
        'sms': 1
    }

    msg_dict = {}
    word_dict = {}
    person_dict = {}
    word_heard = {}
    person_relation = {}

    batch = neo4j.WriteBatch(graph_db)
    for m in data:
        # create message
        msg = {
            'category': message_type['email'],
            'text': m['text'],
            'date': m['date'],
            'uuid': hash(m['text'] + m['date'])
        }

        logging.debug('Created new Message(uuid={})'.format(msg['uuid']))
        msg_node = batch.create(node(msg))
        msg_dict.update({msg['uuid']: msg_node})
        batch.add_labels(msg_dict[msg['uuid']], "Message")

        # create or find all words in message
        words = Counter(m['text'].split())
        message_words = {}
        for word, freq in words.items():
            logging.debug('Parsing word {}: {}'.format(word, freq))
            word_node = word_dict.get(word)

            if word_node is None:
                logging.debug('Created new Word(value={})'.format(word))
                word_node = batch.create(node({'value': word, 'active': True}))
                word_dict.update({word: word_node})
                batch.add_labels(word_node, "Word")

            batch.create(rel(msg_node, ("CONTAINS", {'frequency': freq}), word_node))
            message_words.update({word: freq})

        # find or add the from person
        # build relationship to current message
        from_person_name = m['from'][0]
        from_person = person_dict.get(from_person_name)
        if from_person is None:
            logging.debug('Created new person(address={})'.format(from_person_name))
            from_person = batch.create(node({'address': from_person_name}))
            person_dict.update({from_person_name: from_person})
            batch.add_labels(from_person, "Person")
        batch.create(rel(from_person, ("ROLE", {'role': role['from']}), msg_node))

        if person_relation.get(from_person_name) is None:
            person_relation.update({from_person_name: set()})
        # find or add all the to, cc & bcc people
        # build relationship to current message
        to_people = []
        for field in ['to', 'cc', 'bcc']:
            for address in m[field]:
                person = person_dict.get(address)
                if person is None:
                    logging.debug('Created new person(address={})'.format(address))
                    person = batch.create(node({'address': address}))
                    person_dict.update({address: person})
                    batch.add_labels(person, "Person")

                batch.create(rel(person, ("ROLE", {'role': role[field]}), msg_node))
                to_people.append(address)

                # collect all person to person relationships
                current_person_relation = person_relation.get(address)
                if current_person_relation is None:
                    person_relation[from_person_name].add(address)
                else:
                    if current_person_relation.issuperset(set([from_person_name])):
                        pass
                    else:
                        person_relation[from_person_name].add(address)

        # collect all the heard words and there frequencies
        for word in message_words:
            for person in to_people:
                logging.debug('Creating new heard relationship between person:{} and word:{}'.format(person, word))
                freq = message_words[word]
                if word_heard.get(word) is None:
                    word_heard.update({word: {person: {from_person_name: freq}}})
                else:
                    if word_heard[word].get(person) is None:
                        word_heard[word].update({person: {from_person_name: freq}})
                    else:
                        if word_heard[word][person].get(from_person_name) is None:
                            word_heard[word][person].update({from_person_name: freq})
                        else:
                            old_freq = word_heard[word][person][from_person_name]
                            word_heard[word][person].update({from_person_name: freq+old_freq})

    # create all the heard relationships
    for word in word_heard:
        word_id = word_dict.get(word)
        if word_id is None:
            logging.debug('Error word:{} id not found'.format(word))
        people_who_heard = word_heard.get(word)
        for heard_person in people_who_heard:
            heard_person_id = person_dict.get(heard_person)
            if heard_person_id is None:
                logging.debug('Error person:{} id not found'.format(heard_person))
            people_who_said = people_who_heard.get(heard_person)
            for said_person in people_who_said:
                frequency = people_who_said.get(said_person)
                batch.create(rel(heard_person_id, ("HEARD", {'frequency': frequency, 'name': said_person}), word_id))

    # create all person to person relationships
    for from_person in person_relation:
        from_person_id = person_dict.get(from_person)
        for to_person in person_relation[from_person]:
            to_person_id = person_dict.get(to_person)
            batch.create(rel(from_person_id, ("RELATION", {'category': relation['UNKNOWN']}), to_person_id))

    # submit the batch
    batch.submit()

if __name__ == '__main__':

    import sys

    in_file = sys.argv[1]
    load_data(in_file)


