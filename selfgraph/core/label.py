"""

"""

import logging

from py2neo import neo4j, node, rel
from py2neo.neo4j import Node, Record

from selfgraph.core.categories import RELATIONS

graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")


def label(person_address):

    query_str = 'match (p1:Person)-[r:RELATION {{category: {}}}]-(p2:Person) ' \
                'where p1.address = \'{}\'  return r, p2'.format(
                    RELATIONS['unknown'],
                    person_address
                )
    print(query_str)

    records = neo4j.CypherQuery(graph_db, query_str).execute()

    relationships = [(r.values[0], r.values[1]) for r in records.data]

    for relation, person in relationships:

        options = dict(
            acquaintance=RELATIONS['acquaintance'],
            friend=RELATIONS['friend']
        )

        while True:
            category = input('Enter {} for acquaintance or {} for friend -> {}: '
                             .format(options['acquaintance'], options['friend'], person['address']))

            try:
                category = int(category)
            except ValueError:
                logging.error('Enter a number!')
                continue

            if category not in options.values():
                logging.error('{} is not a valid relation type!'.format(category))
                continue

            relation['category'] = category
            break


if __name__ == '__main__':

    import sys
    label(sys.argv[1])
