"""

"""


from selfgraph.algorithms import k_means


def execute_kmeans(data_filename, num_features):
    word_list, people_list, X = k_means.import_CSV(data_filename)
    k_means.execute(X, num_features)


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

    algo_names = ['kmeans']

    if len(sys.argv) != 4:
        print("Error! Wrong number of input arguments. \n"
              "USAGE: unsupervised.py [ALGORITHM: {}] [DATA FILENAME] [NUMBER FEATURES]".format(', '.join(algo_names)))

    algorithm = sys.argv[1]
    data_filename = sys.argv[2]
    num_features = sys.argv[3]

    if algorithm == 'kmeans':
        #print_results(*execute_kmeans(data_filename, num_features))
        execute_kmeans(data_filename, num_features)
    else:
        print("{} is not a valid algorithm name. Valid names are: {}".format(', '.join(algo_names)))
