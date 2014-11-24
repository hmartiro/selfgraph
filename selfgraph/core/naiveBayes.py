
def matrix_read_train(file_name):
    matrix = []
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            matrix.append(row)

    people_list = matrix[0]
    word_list = matrix[1]
    frequency = []
    for i in range(2, len(matrix)):
        frequency.append(list(map(int, matrix[i])))

    options = {}
    options.update({'acquaintance': Relation.CATEGORIES['acquaintance']})
    options.update({'friend': Relation.CATEGORIES['friend']})

    friend = [0]*len(frequency[0])
    acquaint = [0]*len(frequency[0])
    print(options['friend'])
    for row in frequency:
        if row[0] == options['friend']:
            friend = list(map(operator.add, friend, row))
        if row[0] == options['acquaintance']:
            acquaint = list(map(operator.add, acquaint, row))

    return word_list, friend, acquaint, len(frequency)


def naive_bayes(words, friends, acquaintances, num_people):
    ttl_num_words = len(words)

    num_friend_words = sum([1 if i else 0 for i in friends])
    ttl_num_friend_words = sum(friends)

    num_acquaint_words = sum([1 if i else 0 for i in acquaintances])
    ttl_num_acquaint_words = sum(acquaintances)

    friend_prior = math.log(num_friend_words / num_people)
    acquaint_prior = math.log(num_acquaint_words / num_people)

    friend_phi = []
    acquaint_phi = []
    for i in range(len(words)):
        friend_phi.append(math.log((friends[i]+1)/(ttl_num_friend_words + ttl_num_words)))
        acquaint_phi.append(math.log((acquaintances[i]+1)/(ttl_num_acquaint_words + ttl_num_words)))

    # print top friend words
    logging.debug("Friend words")
    old_i = 0
    for i in sorted(friend_phi)[:5]:
        if i == old_i:
            continue
        old_i = i
        index = [k for k, v in enumerate(friend_phi) if v == i]
        for j in index:
            logging.debug("{} {}".format(words[j], i))

    # print top acquaint words
    logging.debug("Acquaintance Words")
    old_i = 0
    for i in sorted(acquaint_phi)[:5]:
        if i == old_i:
            continue
        old_i = i
        index = [k for k, v in enumerate(acquaint_phi) if v == i]
        for j in index:
            logging.debug("{} {}".format(words[j], i))

    return friend_phi, friend_prior, acquaint_phi, acquaint_prior

def matrix_read_test(file_name):
    matrix = []
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            matrix.append(row)

    people = matrix[0]
    word = matrix[1]
    frequency = []
    for i in range(2, len(matrix)):
        frequency.append(list(map(int, matrix[i])))

    return word, people, frequency

def test_naive_bayes(words, people, frequency, friend_phi, friend_prior, acquaint_phi, acquaint_prior):
    ttl_num_words = len(words)

    for i in range(len(frequency)):
        friend_prob = sum(list(map(operator.mul, frequency[i], friend_phi))) + friend_prior
        acquaint_prob = sum(list(map(operator.mul, frequency[i], acquaint_phi))) + acquaint_prior

        print(friend_prior)
        print(acquaint_prior)
        if(friend_prob > acquaint_prob):
            print("{} is a friend with {} to {}".format(people[i], friend_prob, acquaint_prob))
        elif(friend_prob < acquaint_prob):
            print("{} is a acquaintance with {} to {}".format(people[i], acquaint_prob, friend_prob))
        else:
            print("Can not decide relationship for {}".format(people[i]))
