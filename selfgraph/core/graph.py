"""

"""
import logging

from neomodel import db
from neomodel import StructuredNode, StructuredRel
from neomodel import RelationshipTo, RelationshipFrom, Relationship
from neomodel import IntegerProperty, FloatProperty, StringProperty, BooleanProperty


class Heard(StructuredRel):

    frequency = IntegerProperty(default=0)
    name = StringProperty()

    @classmethod
    def get_or_create(cls, to_person, from_person, word):

        query = """
            MATCH (p:Person { address:'%s' }),(w:Word { value:'%s' })
            MERGE (p)-[r:HEARD {name:'%s'}]->(w)
            RETURN r
        """ % (to_person.address, word.value, from_person.address)
        print(query)
        results, meta = db.cypher_query(query)
        print(results)
        heards = [Heard.inflate(row[0]) for row in results]
        print('heards: {}'.format(heards))
        return heards[0]


class Contains(StructuredRel):

    frequency = IntegerProperty(default=0)


class Relation(StructuredRel):

    CATEGORIES = {
        'UNKNOWN': 0,
        'FRIEND': 1,
        'COWORKER': 2,
        'ACQUAINTANCE': 3,
        'FAMILY': 4,
        'NEWSLETTER': 5
    }
    category = IntegerProperty(default=CATEGORIES['UNKNOWN'])


class Role(StructuredRel):

    CATEGORIES = {
        'TO': 0,
        'FROM': 1,
        'CC': 2,
        'BCC': 3
    }
    category = IntegerProperty()


class Person(StructuredNode):

    address = StringProperty(unique_index=True)
    phone = StringProperty()

    contacts = Relationship('Person', 'RELATION', model=Relation)
    messages = Relationship('Message', 'ROLE', model=Role)
    words = Relationship('Word', 'HEARD', model=Heard)

    @staticmethod
    def delete_all():
        db.cypher_query('MATCH (n:Person)-[r]-() DELETE r DELETE n')

    @classmethod
    def get_or_create(cls, address):
        try:
            return cls.nodes.get(address=address)
        except cls.DoesNotExist:
            logging.debug('Created new Person(name={})'.format(address))
            return Person(address=address)


class Message(StructuredNode):

    CATEGORIES = {
        'email': 0,
        'sms': 1
    }

    uuid = IntegerProperty(required=True)
    category = IntegerProperty(required=True)
    processed = BooleanProperty(default=False)
    date = StringProperty()
    text = StringProperty()

    words = Relationship('Word', 'CONTAINS', model=Contains)

    @staticmethod
    def delete_all():
        db.cypher_query('MATCH (n:Message)-[r]-() DELETE r DELETE n')

    def message_id(self):
        return hash(self.text + self.date)


class Word(StructuredNode):

    value = StringProperty(unique_index=True)
    active = BooleanProperty(default=True)

    @staticmethod
    def delete_all():
        db.cypher_query('MATCH (n:Word)-[r]-() DELETE r DELETE n')

    @classmethod
    def get_or_create(cls, word):
        try:
            return cls.nodes.get(value=word)
        except cls.DoesNotExist:
            logging.debug('Created new Word(value={})'.format(word))
            return Word(value=word)
