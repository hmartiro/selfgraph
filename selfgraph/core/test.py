"""

"""

from selfgraph.algorithms import SVM, naive_bayes


def test_naive_bayes(train_name, test_name):
    words, friend_words, acquaint_words, num_people = naive_bayes.import_train_CSV(train_name)
    friend_phi, friend_prior, acquaint_phi, acquaint_prior = naive_bayes.train_naive_bayes(words, friend_words,
                                                                                          acquaint_words, num_people)

    print('friend_phi: {}'.format(friend_phi))
    print('friend_prior: {}'.format(friend_prior))
    print('acquaint_phi: {}'.format(acquaint_phi))
    print('acquaint_prior: {}'.format(acquaint_prior))

    word_list, people_list, frequency_matrix = naive_bayes.import_read_CSV(test_name)
    friend_prob, acquaint_prob = naive_bayes.test_naive_bayes(frequency_matrix, friend_phi, friend_prior,
                                                              acquaint_phi, acquaint_prior)

    naive_bayes.output_results(friend_prob, acquaint_prob, people_list)


def test_SVM(train_name, test_name):
    people_list, word_list, X, Y = SVM.import_CSV(train_name)
    clf = SVM.train_SVM(X, Y)

    people_list, word_list, X_test, Y_test = SVM.import_CSV(test_name)
    Y_test = SVM.test_SVM(clf, X_test)
    SVM.output_results(people_list, Y_test)


if __name__ == '__main__':
    import sys

    algo_names = ['nb', 'linSVM']

    if(len(sys.argv) != 4):
        print("Error! Wrong number of input arguments. \n"
              "USAGE: train.py [TRAIN TYPE: {}] [TRAIN FILENAME] [TEST FILENAME".format(', '.join(algo_names)))

    algorithm = sys.argv[1]
    train_name = sys.argv[2]
    test_name = sys.argv[3]

    if algorithm == 'nb':
        test_naive_bayes(train_name, test_name)
    elif algorithm == 'linSVM':
        test_SVM(train_name, test_name)
    else:
        print("{} is not a valid algorithm name. Valid names are: {}".format(', '.join(algo_names)))