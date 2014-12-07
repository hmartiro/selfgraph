import re
import difflib
from pprint import pprint
from py2neo import neo4j, node, rel

graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")


def add_not_an_alias(p1, p2, not_an_alias, person_alias):
    # check for alias group head name
    p1_alias = [p1]
    p2_alias = [p2]
    for aliases in person_alias:
        if p1 in aliases:
            p1_alias = aliases
        if p2 in aliases:
            p2_alias = aliases

    # add relations to not_an_alias dict for p1_alias and p2_alias
    if p1_alias[0] in not_an_alias:
        not_an_alias[p1_alias[0]].add(p2_alias[0])
    else:
        not_an_alias[p1_alias[0]] = set([p2_alias[0]])

    if p2_alias[0] in not_an_alias:
        not_an_alias[p2_alias[0]].add(p1_alias[0])
    else:
        not_an_alias[p2_alias[0]] = set([p1_alias[0]])


def is_not_an_alias(p1, p2, not_an_alias, person_alias):
    # check for alias group head name
    p1_alias = p1
    p2_alias = p2
    for aliases in person_alias:
        if p1 in aliases:
            p1_alias = aliases[0]
        if p2 in aliases:
            p2_alias = aliases[0]
    if p1_alias in not_an_alias:
        if p2_alias in not_an_alias[p1_alias]:
            return True

    return False


def update_not_an_alias(p_alias, p, not_an_alias):

    if p_alias == p:
        return

    if p in not_an_alias:
        for person in not_an_alias[p]:
            not_an_alias[person].remove(p)
            not_an_alias[person].add(p_alias)

        if p_alias not in not_an_alias:
            not_an_alias[p_alias] = set()

        not_an_alias[p_alias] = not_an_alias[p_alias] | not_an_alias[p]
        del not_an_alias[p]


def update_alias(p, alias_header, person_alias, not_an_alias):
    for alias in person_alias:
        if alias_header == alias[0]:
            alias.append(p)

    update_not_an_alias(alias_header, p, not_an_alias)


def add_new_alias(p1, p2, person_alias, not_an_alias):
    person_alias.append([p1, p2])
    update_not_an_alias(p1, p2, not_an_alias)


def update_relationships_with_alias(person_alias, relations, heards, roles):
    """
    Update existing relationships replacing person names with their aliases

    """

    new_relations = set()
    new_heards = set()
    new_roles = set()

    for relation in relations:
        for x in person_alias:
            for y in x:
                if relation[0] == y:
                    tmp = list(relation)
                    tmp[0] = x[0]
                    relation = tuple(tmp)
                    break
        for x in person_alias:
            for y in x:
                if relation[2] == y:
                    tmp = list(relation)
                    tmp[2] = x[0]
                    relation = tuple(tmp)
                    break
        new_relations.add(relation)

    for heard in heards:
        for x in person_alias:
            for y in x:
                if heard[0] == y:
                    tmp = list(heard)
                    tmp[0] = x[0]
                    heard = tuple(tmp)
                    break
        for x in person_alias:
            for y in x:
                if heard[2] == y:
                    tmp = list(heard)
                    tmp[2] = x[0]
                    heard = tuple(tmp)
                    break
        new_heards.add(heard)

    for role in roles:
        for x in person_alias:
            for y in x:
                if role[0] == y:
                    tmp = list(role)
                    tmp[0] = x[0]
                    role = tuple(tmp)
                    break
        new_roles.add(role)

    return new_relations, new_heards, new_roles

def eliminate_frequent_email_servers(people):
    """
    Email servers that appear very frequently should be removed
    before comparing similarity to reduce false positives

    """
    # eliminate frequent email server names
    email_servers = {}
    for p in people:
        m = re.search('(?<=@)\w+.\w+', p)
        if m is not None:
            a = m.group(0)
            if a in email_servers:
                email_servers[a] += 1
            else:
                email_servers[a] = 1

    mean = 0
    for key, item in email_servers.items():
        mean += int(item)
    mean /= len(email_servers)

    excluded_emails = []
    for key, item in email_servers.items():
        if int(item) >= mean:
            excluded_emails.append(key)

    for i in range(len(people)):
        for x in excluded_emails:
            people[i] = people[i].replace(x, '')

    return people


def eliminate_by_name(p1, p2):
    """
    Check for standard format [last] [first] <____@__.___>
    if last and first are both different it is safe to say they
    are not the same and add it to the not_an_alias list

    """
    p1_format = re.search('(?=\A)\w+\s\w+\s<[^@]*@[^.]*.[^>]*>', p1)
    p2_format = re.search('(?=\A)\w+\s\w+\s<[^@]*@[^.]*.[^>]*>', p2)
    if p1_format is not None and p2_format is not None:
            p1_first = re.search('\w+', p1).group()
            p1_last = re.search('(?<=\s)\w+', p1).group()

            p2_first = re.search('\w+', p2).group()
            p2_last = re.search('(?<=\s)\w+', p2).group()

            #if (p1_first != p2_first and p1_last != p2_last) and (p1_first != p2_last and p1_last != p2_first):
            if p1_first != p2_first or p1_last != p2_last:
                return True

    return False


def check_for_same_email_address(p, person_alias, not_an_alias):
    """
    If p has the same email as someone in person_alias add it as an alias

    """
    p1_addr = re.search('(?<=<)[^>]*', p)
    if p1_addr is None:
        p1_addr = re.search('[^\s^@]*@[^\s^.]*.\w+', p)
        if p1_addr is None:
            return False

    for x in person_alias:
        if p not in x:
            for y in x:
                y_addr = re.search('(?<=<)[^>]*', y)
                if y_addr is None:
                    y_addr = re.search('[^\s^@]*@[^\s^.]*.\w+', y)
                    if y_addr is None:
                        continue
                if y_addr.group() == p1_addr.group():
                    update_alias(p, x[0], person_alias, not_an_alias)
                    return True
        else:
            break

    return False

def group_by_email_address(p1, p2, person_alias, not_an_alias):
    """
    If p1 and p2 email address are the same then they are the same person.

    """

    if p1 not in (x for r in person_alias for x in r):
        p1_addr = re.search('(?<=<)[^>]*', p1)
        if p1_addr is None:
            p1_addr = re.search('[^\s^@]*@[^\s^.]*.\w+', p1)
            if p1_addr is None:
                return False

        p2_addr = re.search('(?<=<)[^>]*', p2)
        if p2_addr is None:
            p2_addr = re.search('[^\s^@]*@[^\s^.]*.\w+', p2)
            if p2_addr is None:
                return False

        if p1_addr.group() == p2_addr.group():
            add_new_alias(p1, p2, person_alias, not_an_alias)
            return True

    return check_for_same_email_address(p2, person_alias, not_an_alias)

# def eliminate_auto_generated_email(p1, p2):
#
#     p1_format = re.search('((?<=<)|(?=\A))[a-zA-Z]*\d+(?=@temple.edu)', p1)
#     p2_format = re.search('((?<=<)|(?=\A))[a-zA-Z]*\d+(?=@temple.edu)', p2)
#     if p1_format is None or p2_format is None:
#         return False
#
#     p1_number = re.search('(?=[a-zA-Z]*)\d+', p1_format.group())
#     p2_number = re.search('(?=[a-zA-Z]*)\d+', p2_format.group())
#
#     if p1_number.group() != p2_number.group():
#             return True
#
#     return False

def all_substring_of_size(string, size):
    split_strs = re.split(r'(?:[<\s])|\@.*\..*\>|\@.*\..*|\@', string)
    #split_strs = re.split(r'(?:[<>@\s])', string)

    a = set()
    for str in split_strs:
        if len(str) > size:
            for i in range(len(str)-size+1):
                a.add(str[i:i+size])
    return a

def find_high_frequency_match(people_full, people_truncated, not_an_alias, person_alias):
    """
    List people in order of predicted matches. This allows for faster grouping
    and less user input to eliminate non matches.

    """

    people_full_optimized = [0]*len(people_full)
    saved_ratios = set()
    for x in range(len(people_full)):
        for y in range(len(people_full)):
            if (people_full[x], people_full[y]) in saved_ratios:
                print("Skipped")
                continue
            if is_not_an_alias(people_full[x], people_full[y], not_an_alias, person_alias):
                continue

            match = False
            for substr in all_substring_of_size(people_truncated[x], 3):
                if substr in people_truncated[y]:
                    match = True
                    break
            if match is False:
                add_not_an_alias(people_full[x], people_full[y], not_an_alias, person_alias)
                continue

            s = difflib.SequenceMatcher(None, people_truncated[x], people_truncated[y])
            if s.ratio() > 0.5:
                saved_ratios.add((people_full[x], people_full[y]))
                people_full_optimized[x] += 1
                people_full_optimized[y] += 1

    index = sorted(range(len(people_full_optimized)), key=lambda k: people_full_optimized[k])[::-1]

    return [people_full[index[x]] for x in range(len(index))], saved_ratios


def ask_user_if_match(p1, p2, person_alias, not_an_alias):
    """
    If we can not figure out whether two people are the same person
    automatically prompt the user and ask if they are a match

    """
    
    correct_input = False
    while correct_input is False:
        match = input('{} **==** {} ??? (y/n): '.format(p1, p2))
        if match == 'y':
            if (p1 not in (x for r in person_alias for x in r) and
                    p2 not in (x for r in person_alias for x in r)):

                add_new_alias(p1, p2, person_alias, not_an_alias)
            else:
                for x in person_alias:
                    if p1 in x:
                        update_alias(p2, x[0], person_alias, not_an_alias)
                    elif p2 in x:
                        update_alias(p1, x[0], person_alias, not_an_alias)
            correct_input = True
        elif match == 'n':
            add_not_an_alias(p1, p2, not_an_alias, person_alias)
            correct_input = True
        else:
            print('Wrong input. Please enter \'y\' for yes and \'n\' for no')


def group_people(person_alias, not_an_alias, people_full, people_truncated):
    """
    Try and group together email addresses if they
    are from the same person

    """
    # optimize checking to check those with the highest frequency first
    people_full_optimized, saved_ratios = \
        find_high_frequency_match(people_full, people_truncated, not_an_alias, person_alias)

    for p1 in people_full_optimized:

        if check_for_same_email_address(p1, person_alias, not_an_alias) is True:
            continue

        for p2 in people_full_optimized:

            # skip classified people or the same people
            classified = False
            if p1 is p2:
                continue
            for alias in person_alias:
                if p1 in alias and p2 in alias:
                    classified = True
                    break
            if classified is True:
                continue

            # skip if p1 and p2 have already been said to be different
            if is_not_an_alias(p1, p2, not_an_alias, person_alias):
                continue

            # eliminate no matches by name format
            if eliminate_by_name(p1, p2) is True:
                add_not_an_alias(p1, p2, not_an_alias, person_alias)
                continue

            # if email address is the same they are the same
            if group_by_email_address(p1, p2, person_alias, not_an_alias) is True:
                add_not_an_alias(p1, p2, not_an_alias, person_alias)
                continue

            # if they are different auto generated emails they are different
            # match_addr = eliminate_auto_generated_email(p1, p2)

            # ask usr whether the emails are the same if they meet a certain threshold of similarity
            if (p1, p2) in saved_ratios:
                ask_user_if_match(p1, p2, person_alias, not_an_alias)


def create_alias(people):
    """
    Create a list of all aliases and then pass then back to the loader
    to be integrated into the database

    """

    not_an_alias = {}
    person_alias = []

    # get existing alias info and people
    query_str = 'match (p1:Person) return p1.address, p1.alias'
    query_result = neo4j.CypherQuery(graph_db, query_str).execute()

    if len(query_result) > 0:
        additional_people = [x.values[0] for x in query_result]
        alias_marker = [x.values[1] for x in query_result]

        alias_extraction = []
        for x in range(len(alias_marker)):
            if not alias_marker[x]:
                query_str = 'match (p1:Person {{address: \'{}\'}})-[:ALIAS]-(p2:Person) ' \
                            'return p2.address'.format(additional_people[x])
                query_result = neo4j.CypherQuery(graph_db, query_str).execute()
                alias = [a.values[0] for a in query_result]
                alias = list(set(alias))
                if len(alias) > 0:
                    person_alias.append([additional_people[x]] + alias)

        not_an_alias = {}
        # if you are not in the alias list you are not an alias
        for p1 in additional_people:
            p1_alias = [p1]
            for x in person_alias:
                if p1 in x:
                    p1_alias = x
            for p2 in additional_people:
                if p2 not in p1_alias:
                    add_not_an_alias(p1, p2, not_an_alias, person_alias)

        people = list(set(people + additional_people))

    # eliminated redundant email servers
    people_full = people[:]
    people_truncated = eliminate_frequent_email_servers(people)

    # group people
    group_people(person_alias, not_an_alias, people_full, people_truncated)

    for alias in person_alias:
        print(alias)

    return person_alias
