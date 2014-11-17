"""

"""

import logging

import statistics
from neomodel import db
from .graph import *


def select_words():
    # find all words and total frequency
    min_freq = 5
    stdev_weight = 3
    words, query_items = db.cypher_query('match (w:Word)-[h:HEARD]-(p:Person)  return w.value, count(h.frequency)')

    # remove words with freq too low
    appended_freq_list = []
    ttl_freq_list = []
    for word in list(words):
        word_freq = word[1]
        ttl_freq_list.append(word_freq)
        if word_freq < min_freq:
            words.remove(word)
        else:
            appended_freq_list.append(word_freq)

    # find mean of words
    stdev = statistics.stdev(ttl_freq_list)
    mean = statistics.mean(appended_freq_list)

    print('stdev:{} and mean:{}'.format(stdev, mean))

    # remove words with freq too high
    for word in list(words):
        word_freq = word[1]
        if word_freq > mean+stdev_weight*stdev:
            word.remove(word_freq)

    return words

if __name__ == '__main__':
    pass
