"""
Module that interfaces with the Neo4j graph database.

"""

import logging

from py2neo import neo4j, rel, node


class GraphDB():
    """

    """

    BATCH_SIZE = 500
    DB_URL = 'http://localhost:7474/db/data/'

    db = neo4j.GraphDatabaseService(DB_URL)

    def __init__(self):
        self.batch = neo4j.WriteBatch(self.db)

    def create(self, *args):
        """ Create nodes and relationships using the py2neo create method. """
        self.db.create(*args)

    def clear(self):
        """ Delete the contents of the database. """
        self.db.clear()

    def run(self, return_data=True):
        """ Commit the batch, and optionally return data. """

        # for request in self.batch._requests:
        #     logging.info(request._body)

        if return_data:
            result = self.batch.submit()
            self.batch = neo4j.WriteBatch(self.db)
            return result
        else:
            self.batch.run()
            self.batch = neo4j.WriteBatch(self.db)

    def add_query(self, query_str):
        logging.debug('Query:\n{}'.format(query_str))
        self.batch.append_cypher(query_str)

    @staticmethod
    def create_node_str(*labels, **properties):
        """ Query string to create a single node. """

        query_str = 'CREATE (n{} {{{}}}) RETURN n'.format(
            ''.join(':' + l for l in labels),
            ', '.join('{}: {}'.format(k, repr(v)) for k, v in properties.items())
        )

        return query_str

    @staticmethod
    def merge_node_str(match_labels, match_properties, on_create_properties=None, on_match_properties=None):
        """
        Query string to merge a single node, with optional extra properties
        to add on creation or matching.

        """

        query_str = 'MERGE (n{} {{{}}})'.format(
            ''.join(':' + l for l in match_labels),
            ', '.join('{}: {}'.format(k, repr(v)) for k, v in match_properties.items())
        )

        if on_create_properties:
            query_str += ' ON CREATE SET {}'.format(
                ', '.join('n.{} = {}'.format(k, repr(v)) for k, v in on_create_properties.items())
            )

        if on_match_properties:
            query_str += ' ON MATCH SET {}'.format(
                ', '.join('n.{} = {}'.format(k, repr(v)) for k, v in on_match_properties.items())
            )

        query_str += ' RETURN n'

        return query_str

    @staticmethod
    def merge_relationship_str(rel_type, n1_labels, n1_properties, n2_labels, n2_properties,
                               match_properties, on_create_properties=None, on_match_properties=None):
        """
        Query string to merge a single relationship, with optional extra properties
        to add on creation or matching.
        """

        query_str = 'MATCH (n1{} {{{}}}), (n2{} {{{}}})'.format(
            ''.join(':' + l for l in n1_labels),
            ', '.join('{}: {}'.format(k, repr(v)) for k, v in n1_properties.items()),
            ''.join(':' + l for l in n2_labels),
            ', '.join('{}: {}'.format(k, repr(v)) for k, v in n2_properties.items())
        )

        query_str += ' MERGE (n1)-[r:{} {{{}}}]-(n2)'.format(
            rel_type,
            ', '.join('{}: {}'.format(k, repr(v)) for k, v in match_properties.items()),
        )

        if on_create_properties:
            query_str += ' ON CREATE SET {}'.format(
                ', '.join('r.{} = {}'.format(k, repr(v)) for k, v in on_create_properties.items())
            )

        if on_match_properties:
            query_str += ' ON MATCH SET {}'.format(
                ', '.join('r.{} = {}'.format(k, repr(v)) for k, v in on_match_properties.items())
            )

        query_str += ' RETURN r'

        return query_str

    @staticmethod
    def merge_relationship_by_id_str(rel_type, n1_id, n2_id,
                               match_properties, on_create_properties=None, on_match_properties=None):
        """

        """

        query_str = 'MATCH (n1), (n2) WHERE ID(n1) = {} AND ID(n2) = {}'.format(
            n1_id, n2_id
        )

        query_str += ' MERGE (n1)-[r:{} {{{}}}]-(n2)'.format(
            rel_type,
            ', '.join('{}: {}'.format(k, repr(v)) for k, v in match_properties.items()),
        )

        if on_create_properties:
            query_str += ' ON CREATE SET {}'.format(
                ', '.join('r.{} = {}'.format(k, repr(v)) for k, v in on_create_properties.items())
            )

        if on_match_properties:
            query_str += ' ON MATCH SET {}'.format(
                ', '.join('r.{} = {}'.format(k, repr(v)) for k, v in on_match_properties.items())
            )

        query_str += ' RETURN r'

        return query_str

    def create_node(self, *labels, **properties):
        """
        Create a single node with the given labels and properties. Return the
        concrete Node object when created.

        """

        if not labels and not properties:
            logging.warning('Ignoring blank node creation.')
            return

        self.add_query(self.create_node_str(
            *labels,
            **properties
        ))

        result = self.run()
        return result[0]

    def merge_node(self, match_labels, match_properties, on_create_properties=None, on_match_properties=None):
        """
        Merge a single node by matching the given labels and properties, and
        additionally adding the specified properties depending on whether the
        node was matched or created. Returns the node.

        """

        if not match_labels and not match_properties:
            logging.warning('Ignoring blank node creation.')
            return

        self.add_query(self.merge_node_str(
            match_labels,
            match_properties,
            on_create_properties,
            on_match_properties
        ))

        result = self.run()
        return result[0]

    def create_nodes(self, data):
        """
        Create a nodes from the given list of (labels, properties) tuples,
        where labels is a list and properties is a dictionary corresponding
        to the attributes of a single node. Returns a list of nodes.

        Example:

            g.create_nodes([
                (['Person'], {'name': 'Bob', 'age': 12}),
                (['Person', 'Woman'], {'name': 'Alice'})
            ])

        """

        nodes = []

        for i in range(len(data))[::self.BATCH_SIZE]:

                batch_nodes_data = data[i:i+self.BATCH_SIZE]

                for n in batch_nodes_data:
                    self.add_query(self.create_node_str(*n[0], **n[1]))

                batch_nodes = self.run()
                nodes.extend(batch_nodes)

        return nodes

    def merge_nodes(self, data):
        """
        Merge nodes from a list of tuples of the following form:

            (
                match_labels [list],
                match_properties [dict],
                on_create_properties [dict],
                on_match_properties [dict]
            )

        See merge_node to see what these mean. Returns a list of nodes.

        """

        nodes = []

        for i in range(len(data))[::self.BATCH_SIZE]:

                batch_nodes_data = data[i:i+self.BATCH_SIZE]

                for d in batch_nodes_data:
                    self.add_query(self.merge_node_str(*d))

                batch_nodes = self.run()
                nodes.extend(batch_nodes)

        return nodes

    def create_relationships(self, data):
        """
        Create new relationships using the rel() method provided
        by py2neo. The input should be a list of tuples that are
        one of the input formats accepted by py2neo.rel().

        """
        relationships = []

        for i in range(len(data))[::self.BATCH_SIZE]:

                batch_nodes_data = data[i:i+self.BATCH_SIZE]

                for r_data in batch_nodes_data:
                    self.batch.create(rel(r_data))

                batch_rels = self.run()
                relationships.extend(batch_rels)

        return relationships

    def merge_relationships(self, data):

        relationships = []

        for i in range(len(data))[::self.BATCH_SIZE]:

                batch_nodes_data = data[i:i+self.BATCH_SIZE]

                for r_data in batch_nodes_data:
                    self.add_query(self.merge_relationship_str(*r_data))

                batch_rels = self.run()
                relationships.extend(batch_rels)

        return relationships

    def merge_relationships_by_id(self, data):

        relationships = []

        for i in range(len(data))[::self.BATCH_SIZE]:

                batch_nodes_data = data[i:i+self.BATCH_SIZE]

                for r_data in batch_nodes_data:
                    self.add_query(self.merge_relationship_by_id_str(*r_data))

                batch_rels = self.run()
                relationships.extend(batch_rels)

        return relationships

    def create_index(self, label, prop):

        query_str = 'CREATE INDEX ON :{}({})'.format(label, prop)
        self.add_query(query_str)
        self.run(return_data=False)

    def delete_index(self, label, prop):

        query_str = 'DROP INDEX ON :{}({})'.format(label, prop)
        self.add_query(query_str)
        self.run(return_data=False)


if __name__ == '__main__':

    import random
    from selfgraph.utils.timer import time_function

    g = GraphDB()
    g.clear()

    def create_nodes_no_batch(count):
        for i in range(count):
            node = g.create_node('Person', name='Steve{}'.format(i), first=True, age=21)
            logging.debug(node)

    def merge_nodes_no_batch(count):
        for i in range(count):
            node = g.merge_node(
                match_labels=['Person'],
                match_properties=dict(name='Steve{}'.format(i)),
                on_create_properties={},
                on_match_properties={}
            )
            logging.debug(node)

    def create_nodes_batch(count):

        data = []
        for i in range(count):
            data.append((
                ['Person'],
                dict(name='Steve{}'.format(i), first=True, age=21)
            ))

        nodes = g.create_nodes(data)
        for node in nodes:
            logging.debug(node)
        return nodes

    def merge_nodes_batch(count):

        data = []
        for i in range(count):
            data.append((
                ['Person'],
                dict(name='Steve{}'.format(i)),
                dict(first=True, age=21),
                dict(first=False)
            ))

        nodes = g.merge_nodes(data)
        for node in nodes:
            logging.debug(node)
        return nodes

    def create_rels_batch(count, nodes):
        """ Creates random relationships between nodes. """

        data = []
        for i in range(count):
            data.append((
                nodes[random.randint(0, len(nodes)-1)],
                'RANDOM',
                nodes[random.randint(0, len(nodes)-1)],
            ))

        rels = g.create_relationships(data)
        for r in rels:
            logging.debug(r)

    def merge_rels_batch(count, nodes):
        """ Merges random relationships between nodes. """

        data = []
        for i in range(count):
            data.append((
                'RANDOM',
                ['Person'],
                dict(name='Steve{}'.format(random.randint(0, len(nodes)-1))),
                ['Person'],
                dict(name='Steve{}'.format(random.randint(0, len(nodes)-1))),
                dict(),
                dict(),
                dict()
            ))

        rels = g.merge_relationships(data)
        for r in rels:
            logging.debug(r)

    g.create_index('Person', 'name')

    nodes = time_function(create_nodes_batch, 5)
    nodes = time_function(merge_nodes_batch, 5)
    #rels = time_function(create_rels_batch, 50, nodes)
    rels = time_function(merge_rels_batch, 50, nodes)
