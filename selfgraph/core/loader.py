"""

"""

import yaml
import logging
from neomodel import db
from collections import Counter

from ..core.graph import Person, Message, Word
from ..core.graph import Role, Heard


def delete_data():

    Message.delete_all()
    Person.delete_all()
    Word.delete_all()


def load_data(filename):
    """
    Creates Messages, People, and Roles for the given file.

    """

    delete_data()

    with open(filename) as file:
        data = yaml.load(file.read())

    # messages_to_create = tuple({
    #     'category': Message.CATEGORIES['email'],
    #     'text': m['text'],
    #     'date': m['date'],
    #     'uuid': hash(m['text'] + m['date'])
    # } for m in data)
    # Message.create(*messages_to_create)

    # TODO batch inserts
    for m in data:

        msg = Message(
            category=Message.CATEGORIES['email'],
            text=m['text'],
            date=m['date'],
            uuid=hash(m['text'] + m['date'])
        )
        msg.save()
        # msg = Message.nodes.get(uuid=hash(m['text'] + m['date']))

        word_dict = {}
        words = Counter(m['text'].split())
        for word, freq in words.items():
            logging.debug('Parsing word {}: {}'.format(word, freq))
            word_node = Word.get_or_create(word=word)
            word_node.save()
            word_dict[word] = word_node, freq
            msg.words.connect(word_node, {'frequency': freq})

        from_person = Person.get_or_create(m['from'][0])
        from_person.save()
        from_person.messages.connect(msg, {'category': Role.CATEGORIES['FROM']})

        to_people = []
        for field in ['to', 'cc', 'bcc']:
            for address in m[field]:
                person = Person.get_or_create(address)
                person.save()

                person.messages.connect(msg, {'category': Role.CATEGORIES[field.upper()]})
                to_people.append(person)

        for person in to_people:
            for word in word_dict:
                word_node = word_dict[word][0]
                word_freq = word_dict[word][1]
                heard = Heard.get_or_create(person, from_person, word_node)
                heard.frequency += word_freq
                heard.name = from_person.address
                heard.save()

if __name__ == '__main__':

    import sys

    in_file = sys.argv[1]
    load_data(in_file)
