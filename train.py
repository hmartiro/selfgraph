#from selfgraph.core.prepare import *
#build_training_and_testing_sets('ryan houlihan <ryan@rhoulihan.com>')

from selfgraph.core.train import *
from selfgraph.core.test import *

import sys

train_name = sys.argv[1]
words, friend_words, acquaint_words, num_people = matrix_read_train(train_name)
friend_phi, friend_prior, acquaint_phi, acquaint_prior = naive_bayes(words, friend_words, acquaint_words, num_people)

#test_name = sys.argv[2]
#word_list, people_list, frequency_matrix = matrix_read_test(test_name)
#test_naive_bayes(word_list, people_list, frequency_matrix, friend_phi, friend_prior, acquaint_phi, acquaint_prior)
