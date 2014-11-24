"""

"""

from selfgraph.algorithms import linearSVC, naive_bayes


def train_naive_bayes(train_name):
    words, friend_words, acquaint_words, num_people = naive_bayes.import_train_CSV(train_name)
    friend_phi, friend_prior, acquaint_phi, acquaint_prior = naive_bayes.train(words, friend_words,
                                                                                           acquaint_words, num_people)

    print('friend_phi: {}'.format(friend_phi))
    print('friend_prior: {}'.format(friend_prior))
    print('acquaint_phi: {}'.format(acquaint_phi))
    print('acquaint_prior: {}'.format(acquaint_prior))


def train_SVM(train_name):
    people_list, word_list, X, Y = linearSVC.import_CSV(train_name)
    lin_clf = linearSVC.train(X, Y)


if __name__ == '__main__':
    import sys

    algo_names = ['nb', 'linSVC']

    if(len(sys.argv) != 3):
        print("Error! Wrong number of input arguments. \n"
              "USAGE: train.py [ALGORITHM: {}] [TRAIN FILENAME]".format(', '.join(algo_names)))

    algorithm = sys.argv[1]
    train_name = sys.argv[2]

    if algorithm == 'nb':
        train_naive_bayes(train_name)
    elif algorithm == 'linSVC':
        train_SVM(train_name)
    else:
        print("{} is not a valid algorithm name. Valid names are: {}".format(', '.join(algo_names)))