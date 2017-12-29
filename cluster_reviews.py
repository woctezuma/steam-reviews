from describe_reviews import analyzeAppIDinEnglish, getReviewContent

import pandas as pd
import numpy as np

from sklearn.cluster import AffinityPropagation
from sklearn.cluster import Birch
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN
from sklearn.neighbors import kneighbors_graph
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from textblob import TextBlob

def test_imported_module():
    appID = "573170"
    reviewID = "38674426"

    review_content = getReviewContent(appID, reviewID)

    print('Test of review retrieval:')
    printSentimentAnalysis(review_content)

    print(review_content)

    return

def convertFromPandasDataframeToNumpyMatrix(df, excluded_columns = None):

    # Maybe the variable excluded_columns is not needed after all... I just leave it there as a legacy for now.
    if excluded_columns is None:
        D = df
    else:
        # Reference: https://stackoverflow.com/a/32152755
        D = df.ix[:, df.columns.difference(excluded_columns)]

    D_binary = D.ix[:, ['received_for_free', 'steam_purchase', 'voted_up']]
    D_generic = D.ix[:, ['num_games_owned', 'num_reviews', 'playtime_forever', 'votes_up', 'votes_funny', 'comment_count', 'weighted_vote_score']]
    D_length_correlated = D.ix[:, ['character_count', 'syllable_count', 'lexicon_count', 'sentence_count']]
    D_readability_correlated = D.ix[:, ['dale_chall_readability_score', 'flesch_reading_ease', 'difficult_words_count']]
    D_sentiment = D.ix[:, ['polarity','subjectivity']]

    # Convert from Pandas to NumPy arrays
    #Reference: https://stackoverflow.com/a/22653050
    convertFromPandas = lambda data_frame: data_frame.reset_index().values

    X_binary = convertFromPandas(D_binary)
    X_generic = convertFromPandas(D_generic)
    X_length_correlated = convertFromPandas(D_length_correlated)
    X_readability_correlated = convertFromPandas(D_readability_correlated)

    X_readability_correlated = np.nan_to_num(X_readability_correlated)

    X_sentiment = convertFromPandas(D_sentiment)

    scaler = StandardScaler()
    X_generic_new = scaler.fit_transform(X_generic)

    pca_length = PCA(n_components=2)
    X_length_correlated_new = pca_length.fit_transform(X_length_correlated)

    pca_readability = PCA(n_components=2)
    X_readability_correlated_new = pca_readability.fit_transform(X_readability_correlated)

    sentiment_scaler = StandardScaler()
    X_sentiment_new = sentiment_scaler.fit_transform(X_sentiment)

    X = np.concatenate((X_binary, X_generic_new, X_length_correlated_new, X_readability_correlated_new, X_sentiment_new), axis=1)

    return X

def getTopClustersByCount(af, provided_labels = [], verbose = False):

    if (provided_labels is None) or len(provided_labels) == 0:
        # cluster_centers_indices = af.cluster_centers_indices_
        labels = af.labels_
    else:
        labels = provided_labels

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

    (summary_labels, list_of_clusters_by_count) = getTopClustersByCount(af, None, verbose)

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
        printSentimentAnalysis(review_content)

        print(review_content)

    return

def printSentimentAnalysis(text):

    blob = TextBlob(text)

    print('=> Sentiment analysis: '
          + 'polarity({0:.2f})'.format(blob.sentiment.polarity) + ' ; '
          + 'subjectivity({0:.2f})'.format(blob.sentiment.subjectivity) + ')')

    return

def showFixedNumberOfReviewsFromGivenCluster(appID, df, af, cluster_count, provided_labels = [], max_num_reviews_to_print = None):
    # The provided labels can be supplied directly to override the labels found with Affinity Propagation.
    # Typically used to show results obtained with other clustering methods.

    # You can display a given number of reviews per cluster by playing with the variable max_num_reviews_to_print.

    if (provided_labels is None) or len(provided_labels) == 0:
        cluster_centers_indices = af.cluster_centers_indices_
        labels = af.labels_

        (summary_labels, list_of_clusters_by_count) = getTopClustersByCount(af)

        cluster_index = int(list_of_clusters_by_count[cluster_count])
        cluster_representative_ind = cluster_centers_indices[cluster_index]
    else:
        cluster_centers_indices = None
        labels = provided_labels

        (summary_labels, list_of_clusters_by_count) = getTopClustersByCount(None, provided_labels)

        cluster_index = int(list_of_clusters_by_count[cluster_count])
        cluster_representative_ind = None

    cluster_content_indices = [i for i, x in enumerate(list(labels)) if x == cluster_index]

    for (review_count, ind) in enumerate(cluster_content_indices):
        reviewID = list(df["recommendationid"])[ind]
        review_content = getReviewContent(appID, reviewID)

        if (cluster_representative_ind is not None) and (ind == cluster_representative_ind):
            info_str = " (representative)"
        else:
            info_str = ""

        if (max_num_reviews_to_print is not None) and (review_count >= max_num_reviews_to_print):
            break

        # Reference: https://stackoverflow.com/a/18544440
        print("\n ==== Review " + str(review_count+1) + info_str + " in cluster " + chr(cluster_count+65) + " (#reviews = " + str(summary_labels[cluster_count]) + ") ====" )
        printSentimentAnalysis(review_content)

        print(review_content)

    return

def showAllReviewsFromGivenCluster(appID, df, af, cluster_count, provided_labels = []):
    showFixedNumberOfReviewsFromGivenCluster(appID, df, af, cluster_count, provided_labels)
    return

def showDataFrameForClusterCenters(df, af, num_top_clusters = None, verbose = True):

    cluster_centers_indices = af.cluster_centers_indices_
    # labels = af.labels_

    (summary_labels, list_of_clusters_by_count) = getTopClustersByCount(af)

    sorted_cluster_centers_indices = cluster_centers_indices[[int(i) for i in list_of_clusters_by_count]]

    # Reference: https://stackoverflow.com/a/19155860
    df_representative = df.iloc[sorted_cluster_centers_indices, :]

    if verbose:
        if num_top_clusters is None:
            print(df_representative)
        else:
            print(df_representative.iloc[0:num_top_clusters, :])

    return df_representative

def tryAffinityPropagation(appID, df, X, num_top_clusters = 4, verbose = False):
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
    showRepresentativeReviews(appID, df, af, num_top_clusters, verbose)

    # Show all reviews in given cluster (to manually check for cluster homogeneity)

    if verbose:
        cluster_count = 1  # Warning: this starts at 0
        showAllReviewsFromGivenCluster(appID, df, af, cluster_count)

    # Show dataframe limited to cluster centers

    df_representative = showDataFrameForClusterCenters(df, af, num_top_clusters)

    return labels

def tryBirch(appID, df, X, num_clusters_input = 3, num_reviews_to_show_per_cluster = 3):
    # #############################################################################
    # Compute Agglomerative Clustering with Birch as a first step

    brc = Birch(branching_factor=50, n_clusters=num_clusters_input, threshold=0.5, compute_labels = True)
    brc_labels = brc.fit_predict(X)

    # Show Birch results

    for cluster_count in range(num_clusters_input):
        showFixedNumberOfReviewsFromGivenCluster(appID, df, None, cluster_count, brc_labels, num_reviews_to_show_per_cluster)

    # Display number of reviews in each cluster

    getTopClustersByCount(None, brc_labels, True)

    return brc_labels

def tryAgglomerativeClustering(appID, df, X, num_clusters_input = 3, num_reviews_to_show_per_cluster = 3,
                                linkage = 'ward', use_connectivity = True):
    # #############################################################################
    # Compute Agglomerative Clustering without Birch

    # NB: linkage can be any of these: 'average', 'complete', 'ward'

    if use_connectivity:
        knn_graph = kneighbors_graph(X, 30, include_self=False)
        connectivity = knn_graph # one of these: None or knn_graph
    else:
        connectivity = None

    model = AgglomerativeClustering(linkage=linkage, connectivity=connectivity, n_clusters=num_clusters_input)

    agg_labels = model.fit_predict(X)

    # Show Agglomerative Clustering results

    for cluster_count in range(num_clusters_input):
        showFixedNumberOfReviewsFromGivenCluster(appID, df, None, cluster_count, agg_labels, num_reviews_to_show_per_cluster)

    # Display number of reviews in each cluster

    getTopClustersByCount(None, agg_labels, True)

    return agg_labels

def tryDBSCAN(appID, df, X, db_eps = 0.3, db_min_samples=10, num_reviews_to_show_per_cluster = 3):
    # #############################################################################
    # Compute DBSCAN

    # Caveat: It does not seem to be super easy to find adequate parameters.
    # For Fidel Dungeon Rescue, the following allows to at least return a few different clusters:
    # db_eps = 40
    # db_min_samples = 4

    db = DBSCAN(eps=db_eps, min_samples=db_min_samples).fit(X)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    dbscan_labels = db.labels_

    num_clusters_including_noise_cluster = len(set(dbscan_labels))

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = num_clusters_including_noise_cluster - (1 if -1 in dbscan_labels else 0)

    print('Estimated number of clusters: %d' % n_clusters_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(X, dbscan_labels))

    # Show DBSCAN results

    for cluster_count in range(num_clusters_including_noise_cluster):
        showFixedNumberOfReviewsFromGivenCluster(appID, df, None, cluster_count, dbscan_labels, num_reviews_to_show_per_cluster)

    # Display number of reviews in each cluster

    getTopClustersByCount(None, dbscan_labels, True)

    return dbscan_labels

def test_every_clustering_method(appID):
    ## Clustering
    # Reference: http://scikit-learn.org/stable/modules/clustering.html

    # NB: We are not interested in outlier detection:
    # - if the goal were to remove low-quality reviews, a threshold on review lenght should be sufficient,
    # - for some games, the low-quality/"funny meme" reviews are not outliers, they constitute their own sizable cluster

    # Features (columns) to exclude
    excluded_columns = ["language", "recommendationid"]

    # Load Pandas dataframe
    df = analyzeAppIDinEnglish(appID)

    # Convert to NumPy matrix format
    X = convertFromPandasDataframeToNumpyMatrix(df, excluded_columns)


    ## Demo of every clustering method

    ## Affinity Propagation
    # NB: The clusters look consistent, I like the results, but:
    # - there are too many clusters (11) for our application,
    # - and there is no direct control of the number of clusters.
    # I don't want to have to look at each cluster to find one-line joke reviews, so I prefer to go with another method.

    num_top_clusters = 4
    verbose = True

    tryAffinityPropagation(appID, df, X, num_top_clusters, verbose)

    ## Agglomerative Clustering with Birch

    num_clusters_input = 3
    num_reviews_to_show_per_cluster = 3

    tryBirch(appID, df, X, num_clusters_input, num_reviews_to_show_per_cluster)

    ## Agglomerative Clustering without Birch
    # NB: With some parameters, results are similar to Birch's (as expected from scikit-learn documentation of Birch).

    linkage = 'ward'
    use_connectivity = True

    tryAgglomerativeClustering(appID, df, X, num_clusters_input, num_reviews_to_show_per_cluster, linkage, use_connectivity)

    ## DBSCAN
    # NB: Not satisfactory here. Either the parameters, or the data pre-processing, should be changed for DBSCAN.

    db_eps = 40
    db_min_samples = 4

    tryDBSCAN(appID, df, X, db_eps, db_min_samples, num_reviews_to_show_per_cluster)

    return

def applyBirch(appID, num_clusters_input = 3, num_reviews_to_show_per_cluster = 3):
    # Cluster reviews for appID using selected method (Birch and then Agglomerative Clustering)

    # Load Pandas dataframe
    df = analyzeAppIDinEnglish(appID)

    # Convert to NumPy matrix format
    X = convertFromPandasDataframeToNumpyMatrix(df)

    brc_labels = tryBirch(appID, df, X, num_clusters_input, num_reviews_to_show_per_cluster)

    return (df, brc_labels)

def main():
    appID_list = ["723090", "639780", "573170"]

    appID = appID_list[-1]

    # Apply Birch and then Agglomerative Clustering

    num_clusters_input = 3
    num_reviews_to_show_per_cluster = 3

    (df, labels) = applyBirch(appID, num_clusters_input, num_reviews_to_show_per_cluster)

    # Demo of every clustering method

    perform_full_test_suite = False

    if perform_full_test_suite:
        test_every_clustering_method(appID)

    return

if __name__ == "__main__":
    main()
