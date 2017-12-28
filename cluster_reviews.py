from describe_reviews import analyzeAppIDinEnglish, getReviewContent

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn import cluster, covariance, manifold
from sklearn.cluster import AffinityPropagation
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from sklearn_pandas import DataFrameMapper, gen_features
import sklearn.preprocessing, sklearn.decomposition, sklearn.linear_model, sklearn.pipeline, sklearn.metrics
from sklearn.feature_extraction.text import CountVectorizer

def test_imported_module():
    appID = "573170"
    reviewID = "38674426"

    review_content = getReviewContent(appID, reviewID)

    print(review_content)

    return

def convertFromPandasDataframeToNumpyMatrix(df, excluded_columns):

    # Reference: https://stackoverflow.com/a/32152755
    D = df.ix[:, df.columns.difference(excluded_columns)]

    D_binary = D.ix[:, ['received_for_free', 'steam_purchase', 'voted_up']]
    D_generic = D.ix[:, ['num_games_owned', 'num_reviews', 'playtime_forever', 'votes_up', 'votes_funny', 'comment_count', 'weighted_vote_score']]
    D_length_correlated = D.ix[:, ['character_count', 'syllable_count', 'lexicon_count', 'sentence_count']]
    D_readability_correlated = D.ix[:, ['dale_chall_readability_score', 'flesch_reading_ease', 'difficult_words_count']]

    # Convert from Pandas to NumPy arrays
    #Reference: https://stackoverflow.com/a/22653050
    convertFromPandas = lambda data_frame: data_frame.reset_index().values

    X_binary = convertFromPandas(D_binary)
    X_generic = convertFromPandas(D_generic)
    X_length_correlated = convertFromPandas(D_length_correlated)
    X_readability_correlated = convertFromPandas(D_readability_correlated)

    X_readability_correlated = np.nan_to_num(X_readability_correlated)

    scaler = StandardScaler()
    X_generic_new = scaler.fit_transform(X_generic)

    pca_length = PCA(n_components=2)
    X_length_correlated_new = pca_length.fit_transform(X_length_correlated)

    pca_readability = PCA(n_components=2)
    X_readability_correlated_new = pca_readability.fit_transform(X_readability_correlated)

    X = np.concatenate((X_binary, X_generic_new, X_length_correlated_new, X_readability_correlated_new), axis=1)

    return X

def getTopClustersByCount(af, verbose = False):

    # cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    summary_labels = pd.Series(labels).apply(str).value_counts()

    if verbose:
        print("\nCluster stats: ")
        print(summary_labels)

    list_of_clusters_by_count = summary_labels.index.tolist()

    return (summary_labels, list_of_clusters_by_count)

def showRepresentativeReviews(appID, df, af, num_top_clusters = None, verbose = False):
    # Show representative reviews, i.e. the reviews used as cluster centers for Affinity Propagation
    # df: dataframe
    # af: affinity propagation model

    cluster_centers_indices = af.cluster_centers_indices_
    # labels = af.labels_

    (summary_labels, list_of_clusters_by_count) = getTopClustersByCount(af, verbose)

    if num_top_clusters is None:
        top_clusters = list_of_clusters_by_count
    else:
        top_clusters = list_of_clusters_by_count[0:num_top_clusters]

    for (cluster_count, cluster_iter) in enumerate(top_clusters):
        ind = cluster_centers_indices[int(cluster_iter)]
        reviewID = list(df["recommendationid"])[ind]
        review_content = getReviewContent(appID, reviewID)
        # Reference: https://stackoverflow.com/a/18544440
        print("\n ==== Cluster " + chr(cluster_count+65) + " (#reviews = " + str(summary_labels[cluster_count]) + ") ====" )
        print(review_content)

    return

def showAllReviewsFromGivenCluster(appID, df, af, cluster_count):

    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    (summary_labels, list_of_clusters_by_count) = getTopClustersByCount(af)

    cluster_index = int(list_of_clusters_by_count[cluster_count])

    cluster_representative_ind = cluster_centers_indices[cluster_index]
    cluster_content_indices = [i for i, x in enumerate(list(labels)) if x == cluster_index]

    for (review_count, ind) in enumerate(cluster_content_indices):
        reviewID = list(df["recommendationid"])[ind]
        review_content = getReviewContent(appID, reviewID)

        if ind == cluster_representative_ind:
            info_str = " (representative)"
        else:
            info_str = ""

        # Reference: https://stackoverflow.com/a/18544440
        print("\n ==== Review " + str(review_count+1) + info_str + " in cluster " + chr(cluster_count+65) + " (#reviews = " + str(summary_labels[cluster_count]) + ") ====" )

        print(review_content)

    return

def main():
    appID_list = ["723090", "639780", "573170"]

    appID = appID_list[-1]


    # Features (columns) to exclude
    excluded_columns = ["language", "recommendationid"]

    # Load Pandas dataframe
    df = analyzeAppIDinEnglish(appID)

    # Convert to NumPy matrix format
    X = convertFromPandasDataframeToNumpyMatrix(df, excluded_columns)


    ## Processing
    # Reference: http://scikit-learn.org/stable/modules/clustering.html

    # NB: We are not interested in outlier detection:
    # - if the goal were to remove low-quality reviews, a threshold on review lenght should be sufficient,
    # - for some games, the low-quality/"funny meme" reviews are not outliers, they constitute their own sizable cluster


    # #############################################################################
    # Compute Affinity Propagation
    af = AffinityPropagation().fit(X)
    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    # Show reviews used as cluster centers (for all clusters)
    showRepresentativeReviews(appID, df, af)

    # Print additional info

    n_clusters_ = len(cluster_centers_indices)

    print('\nEstimated number of clusters: %d' % n_clusters_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(X, labels, metric='sqeuclidean'))

    # Show reviews used as cluster centers of the top clusters
    num_top_clusters = 4
    verbose = True
    showRepresentativeReviews(appID, df, af, num_top_clusters, verbose)

    # Show all reviews in given cluster (to manually check for cluster homogeneity)

    cluster_count = 1 # Warning: this starts at 0
    showAllReviewsFromGivenCluster(appID, df, af, cluster_count)

    return

if __name__ == "__main__":
    main()
