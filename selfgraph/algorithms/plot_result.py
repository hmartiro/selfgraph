"""

"""

import matplotlib.pyplot as plt


if __name__ == '__main__':

    min_freq = [10, 20, 40, 60, 80, 100]
    log_reg_test = [.9079, .9183, .9056, .9146, .8945, .8821]
    lin_svc_test = [.898, .9019, .8958, .9075, .8978, .8724]

    plt.plot(min_freq, log_reg_test, 'ro', min_freq, lin_svc_test, 'bs')
    plt.title('Filter Frequency vs Classification Accuracy')
    plt.legend(['Logistic Regression', 'Linear SVC'])
    plt.xlabel('Min. frequency of words used as features')
    plt.ylabel('10-fold cross validation classification accuracy')
    plt.xlim([0, 120])

    plt.show()
