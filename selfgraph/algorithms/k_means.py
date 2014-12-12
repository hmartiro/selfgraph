"""

"""

import csv
import numpy as np
import matplotlib.pyplot as plt

from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

from selfgraph.utils.csv import import_csv


def import_CSV(file_name):

    person, word_list, people_list, X, Y = import_csv(file_name)

    return word_list, people_list, X


def execute(data, num_features, people_list):
    reduced_data = scale(data)
    reduced_data = PCA(n_components=20).fit_transform(reduced_data)
    kmeans = KMeans(init='k-means++', n_clusters=12, n_init=10)
    kmeans.fit(reduced_data)

    # plt.figure()
    # plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'ro')
    # plt.plot(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], 'bo')
    # plt.show()
    #print(list(np.array(data)[8, :]))
    print(kmeans.labels_)
    from pprint import pprint
    results = dict(zip(people_list, kmeans.labels_))
    pprint(sorted(results.items(), key=lambda v: v[1]))

    # plt.plot([1,2,3,4], [1,4,9,16], 'ro')
    # plt.axis([0, 6, 0, 20])
    # plt.show()

    #print(kmeans.cluster_centers_)
    # Step size of the mesh. Decrease to increase the quality of the VQ.
    #h = .02     # point in the mesh [x_min, m_max]x[y_min, y_max].
    #
    # # Plot the decision boundary. For that, we will assign a color to each
    # x_min, x_max = reduced_data[:, 0].min() + 1, reduced_data[:, 0].max() - 1
    # y_min, y_max = reduced_data[:, 1].min() + 1, reduced_data[:, 1].max() - 1
    # xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    #
    # # Obtain labels for each point in mesh. Use last trained model.
    # Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])
    #
    # # Put the result into a color plot
    # Z = Z.reshape(xx.shape)
    # plt.figure(1)
    # plt.clf()
    # plt.imshow(Z, interpolation='nearest',
    #            extent=(xx.min(), xx.max(), yy.min(), yy.max()),
    #            cmap=plt.cm.Paired,
    #            aspect='auto', origin='lower')
    #
    # plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    # # Plot the centroids as a white X
    # centroids = kmeans.cluster_centers_
    # plt.scatter(centroids[:, 0], centroids[:, 1],
    #             marker='x', s=169, linewidths=3,
    #             color='w', zorder=10)
    # plt.title('K-means clustering on the digits dataset (PCA-reduced data)\n'
    #           'Centroids are marked with white cross')
    # plt.xlim(x_min, x_max)
    # plt.ylim(y_min, y_max)
    # plt.xticks(())
    # plt.yticks(())
    # plt.show()