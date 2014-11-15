"""

"""

from neomodel import StructuredNode, StructuredRel
from neomodel import RelationshipTo, RelationshipFrom, Relationship
from neomodel import IntegerProperty, FloatProperty, StringProperty, BooleanProperty


class Heard(StructuredRel):

    frequency = IntegerProperty(default=0)
    name = StringProperty()


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

    address = StringProperty()
    phone = StringProperty()

    contacts = Relationship('Person', 'RELATION', model=Relation)
    messages = Relationship('Message', 'ROLE', model=Role)
    words = Relationship('Word', 'HEARD', model=Heard)


class Message(StructuredNode):

    CATEGORIES = {
        'email': 0,
        'sms': 1
    }

    category = IntegerProperty(required=True)
    processed = BooleanProperty(default=False)
    date = StringProperty()
    text = StringProperty()

    words = Relationship('Word', 'CONTAINS', model=Contains)


class Word(StructuredNode):

    value = StringProperty()
    active = BooleanProperty(default=True)
