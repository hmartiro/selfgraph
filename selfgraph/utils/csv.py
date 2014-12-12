"""

"""

import csv
import re
import numpy as np

def import_csv(filename):

    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        data = [row for row in reader]

    person = data[0][0]
    word_list = np.array(data[1])
    people_list = np.array(data[2])

    Y = np.array([int(row[0]) for row in data[3:]])
    X = np.array([[int(x) for x in row[1:]] for row in data[3:]])

    return person, word_list, people_list, X, Y


def export_csv(filename, person, word_list, people_list, X, Y):

    print('Person: {}'.format(person))
    print('Words: {}'.format(word_list))
    print('People: {}'.format(people_list))
    print('Y: {}'.format(Y))

    with open(filename, 'w') as train_file:
        writer = csv.writer(train_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([person])
        writer.writerow(word_list)
        writer.writerow(people_list)

        for y, x in zip(Y, X):
            writer.writerow([y] + list(x))

if __name__ == '__main__':

    import sys

    person, word_list, people_list, X, Y = import_csv(sys.argv[1])

    print('Person: {}'.format(person))
    print('Words: {}'.format(', '.join(word_list)))
    print('People: {}'.format(', '.join(people_list)))

    export_csv(sys.argv[1], person, word_list, people_list, X, Y)
