"""

"""
from py2neo import neo4j
from selfgraph.algorithms import linearSVC, naive_bayes
from selfgraph.utils.csv import import_csv
from selfgraph.core.categories import RELATIONS

graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")


def test_naive_bayes(train_name, test_name):

    person, words, word_freq_friends, word_freq_acquaints, Y = naive_bayes.import_train_CSV(train_name)

    print('len words: {}, len friends: {}, len acquaint: {}'.format(
        len(words),
        len(word_freq_friends),
        len(word_freq_acquaints)
    ))

    print('Friend words: {}'.format(word_freq_friends))
    print('Acquaintance words: {}'.format(word_freq_acquaints))

    phi_k_friend, phi_friend, phi_k_acquaint, phi_acquaint = naive_bayes.train(
        words, word_freq_friends, word_freq_acquaints, Y
    )

    print('friend_prior: {}'.format(phi_friend))
    print('acquaint_prior: {}'.format(phi_acquaint))

    word_list, people_list, X = naive_bayes.import_test_CSV(test_name)

    friend_prob, acquaint_prob = naive_bayes.test(
        X, phi_k_friend, phi_friend, phi_k_acquaint, phi_acquaint
    )

    Y_test = naive_bayes.output_results(friend_prob, acquaint_prob, people_list)

    confusion = confusion_matrix(person, people_list, Y_test)

    return person, people_list, confusion


def test_SVM(train_name, test_name):

    person, words, train_people, X, Y = import_csv(train_name)
    person, words, test_people, X_test, Y_test = import_csv(test_name)

    lin_clf = linearSVC.train(X, Y)

    Y_test = linearSVC.test(lin_clf, X_test)
    linearSVC.output_results(test_people, Y_test)

    confusion = confusion_matrix(person, test_people, Y_test)

    return person, test_people, confusion


def confusion_matrix(person, people, Y):

    print('Confusion matrix for classifying {} people in relation to [{}]:'.format(
        len(people), person
    ))
    print(Y)

    query_str = 'match (p:Person {{address: \'{}\'}})-[r:RELATION]-(p1:Person) ' \
                'return p1, r'.format(person)
    print(query_str)

    records = neo4j.CypherQuery(graph_db, query_str).execute()
    results = [(r.values[0]['address'], r.values[1]['category']) for r in records.data]

    results.sort()

    # TODO make sure duplicate relations are gone, shouldn't have to do this
    relation_map = {}
    for p, r in results:
        relation_map[p] = r

    confusion = {
        RELATIONS['friend']: [0, 0],
        RELATIONS['acquaintance']: [0, 0]
    }

    for p, y in zip(people, Y):
        if y == relation_map[p]:
            confusion[y][0] += 1
        else:
            confusion[y][1] += 1

    return confusion


def print_results(person, people, confusion):

    total_correct = sum(v[0] for v in confusion.values())
    total_incorrect = sum(v[1] for v in confusion.values())
    assert(total_correct + total_incorrect == len(people))
    error = total_incorrect / len(people)

    print('')
    print('Results')
    print('-----------------------------------')
    print('Person: {}'.format(person))

    print('')
    print('Confusion Matrix:\n')
    for relation, v in confusion.items():
        print('  Relation {}:'.format(relation))
        print('      Correct: {}'.format(v[0]))
        print('    Incorrect: {}'.format(v[1]))

    print('')
    print('# total classifications:     {}'.format(len(people)))
    print('# correct classifications:   {}'.format(total_correct))
    print('# incorrect classifications: {}'.format(total_incorrect))
    print('')
    print('Error rate: {}'.format(error))


if __name__ == '__main__':
    import sys

    algo_names = ['nb', 'linSVC']

    if len(sys.argv) != 4:
        print("Error! Wrong number of input arguments. \n"
              "USAGE: test.py [TRAIN TYPE: {}] [TRAIN FILENAME] [TEST FILENAME]".format(', '.join(algo_names)))

    algorithm = sys.argv[1]
    train_name = sys.argv[2]
    test_name = sys.argv[3]

    if algorithm == 'nb':
        print_results(*test_naive_bayes(train_name, test_name))
    elif algorithm == 'linSVC':
        print_results(*test_SVM(train_name, test_name))
    else:
        print("{} is not a valid algorithm name. Valid names are: {}".format(', '.join(algo_names)))
