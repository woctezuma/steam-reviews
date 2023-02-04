import sys

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import Birch
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler
from textblob import TextBlob

from describe_reviews import analyze_app_id_in_english, get_review_content


def test_imported_module():
    app_id = "573170"
    review_id = "38674426"

    review_content = get_review_content(app_id, review_id)

    print('Test of review retrieval:')
    print_sentiment_analysis(review_content)

    try:
        print(review_content)
    except UnicodeEncodeError:
        # Reference: https://stackoverflow.com/a/3224300
        print(review_content.encode('ascii', 'ignore'))

    return


def convert_from_pandas(data_frame):
    # Convert from Pandas to NumPy arrays
    # Reference: https://stackoverflow.com/a/22653050

    return data_frame.reset_index().values


def convert_from_pandas_dataframe_to_numpy_matrix(df, excluded_columns=None):
    # Maybe the variable excluded_columns is not needed after all... I just leave it there as a legacy for now.
    if excluded_columns is None:
        # noinspection PyPep8Naming
        D = df
    else:
        # Reference: https://stackoverflow.com/a/32152755
        # noinspection PyPep8Naming
        D = df.loc[:, df.columns.difference(excluded_columns)]

    # noinspection PyPep8Naming
    D_binary = D.loc[:, ['received_for_free', 'steam_purchase', 'voted_up']]
    # noinspection PyPep8,PyPep8Naming
    D_generic = D.loc[
        :,
        [
            'num_games_owned',
            'num_reviews',
            'playtime_forever',
            'votes_up',
            'votes_funny',
            'comment_count',
            'weighted_vote_score',
        ],
    ]
    # noinspection PyPep8Naming
    D_length_correlated = D.loc[
        :,
        ['character_count', 'syllable_count', 'lexicon_count', 'sentence_count'],
    ]
    # noinspection PyPep8Naming
    D_readability_correlated = D.loc[
        :,
        [
            'dale_chall_readability_score',
            'flesch_reading_ease',
            'difficult_words_count',
        ],
    ]
    # noinspection PyPep8Naming
    D_sentiment = D.loc[:, ['polarity', 'subjectivity']]

    # noinspection PyPep8Naming
    X_binary = convert_from_pandas(D_binary)
    # noinspection PyPep8Naming
    X_generic = convert_from_pandas(D_generic)
    # noinspection PyPep8Naming
    X_length_correlated = convert_from_pandas(D_length_correlated)
    # noinspection PyPep8Naming
    X_readability_correlated = convert_from_pandas(D_readability_correlated)
    # noinspection PyPep8Naming
    X_readability_correlated = np.nan_to_num(X_readability_correlated)

    # noinspection PyPep8Naming
    X_sentiment = convert_from_pandas(D_sentiment)

    scaler = StandardScaler()
    # noinspection PyPep8Naming
    X_generic_new = scaler.fit_transform(X_generic)

    pca_length = PCA(n_components=2)
    # noinspection PyPep8Naming
    X_length_correlated_new = pca_length.fit_transform(X_length_correlated)

    pca_readability = PCA(n_components=2)
    # noinspection PyPep8Naming
    X_readability_correlated_new = pca_readability.fit_transform(
        X_readability_correlated,
    )

    sentiment_scaler = StandardScaler()
    # noinspection PyPep8Naming
    X_sentiment_new = sentiment_scaler.fit_transform(X_sentiment)

    # noinspection PyPep8Naming
    X = np.concatenate(
        (
            X_binary,
            X_generic_new,
            X_length_correlated_new,
            X_readability_correlated_new,
            X_sentiment_new,
        ),
        axis=1,
    )

    return X


def get_top_clusters_by_count(af, provided_labels=None, verbose=False):
    if provided_labels is None:
        provided_labels = []
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

    return summary_labels, list_of_clusters_by_count


def show_representative_reviews(app_id, df, af, num_top_clusters=None, verbose=False):
    # Show representative reviews, i.e. the reviews used as cluster centers for Affinity Propagation
    # df: dataframe
    # af: affinity propagation model

    cluster_centers_indices = af.cluster_centers_indices_
    # labels = af.labels_

    # noinspection PyTypeChecker
    (summary_labels, list_of_clusters_by_count) = get_top_clusters_by_count(
        af,
        provided_labels=None,
        verbose=verbose,
    )

    if num_top_clusters is None:
        top_clusters = list_of_clusters_by_count
    else:
        top_clusters = list_of_clusters_by_count[0:num_top_clusters]

    for (cluster_count, cluster_iter) in enumerate(top_clusters):
        ind = cluster_centers_indices[int(cluster_iter)]
        review_id = list(df["recommendationid"])[ind]
        review_content = get_review_content(app_id, review_id)
        # Reference: https://stackoverflow.com/a/18544440
        print(
            "\n ==== Cluster "
            + chr(cluster_count + 65)
            + " (#reviews = "
            + str(summary_labels[cluster_count])
            + ") ====",
        )
        print_sentiment_analysis(review_content)

        try:
            print(review_content)
        except UnicodeEncodeError:
            # Reference: https://stackoverflow.com/a/3224300
            print(review_content.encode('ascii', 'ignore'))

    return


def print_sentiment_analysis(text):
    blob = TextBlob(text)

    print(
        '=> Sentiment analysis: '
        + 'polarity({0:.2f})'.format(blob.sentiment.polarity)
        + ' ; '
        + 'subjectivity({0:.2f})'.format(blob.sentiment.subjectivity)
        + ')',
    )

    return


def show_fixed_number_of_reviews_from_given_cluster(
    app_id,
    df,
    af,
    cluster_count,
    provided_labels=None,
    max_num_reviews_to_print=None,
):
    # The provided labels can be supplied directly to override the labels found with Affinity Propagation.
    # Typically used to show results obtained with other clustering methods.

    # You can display a given number of reviews per cluster by playing with the variable max_num_reviews_to_print.

    if provided_labels is None:
        provided_labels = []
    if (provided_labels is None) or len(provided_labels) == 0:
        labels = af.labels_

        (summary_labels, list_of_clusters_by_count) = get_top_clusters_by_count(af)
    else:
        labels = provided_labels

        (summary_labels, list_of_clusters_by_count) = get_top_clusters_by_count(
            None,
            provided_labels,
        )

    cluster_index = int(list_of_clusters_by_count[cluster_count])

    if af is not None:
        cluster_centers_indices = af.cluster_centers_indices_
        cluster_representative_ind = cluster_centers_indices[cluster_index]
    else:
        # noinspection PyUnusedLocal
        cluster_centers_indices = None
        cluster_representative_ind = None

    cluster_content_indices = [
        i for i, x in enumerate(list(labels)) if x == cluster_index
    ]

    for (review_count, ind) in enumerate(cluster_content_indices):
        review_id = list(df["recommendationid"])[ind]
        review_content = get_review_content(app_id, review_id)

        if (cluster_representative_ind is not None) and (
            ind == cluster_representative_ind
        ):
            info_str = " (representative)"
        else:
            info_str = ""

        if (max_num_reviews_to_print is not None) and (
            review_count >= max_num_reviews_to_print
        ):
            break

        # Reference: https://stackoverflow.com/a/18544440
        print(
            "\n ==== Review "
            + str(review_count + 1)
            + info_str
            + " in cluster "
            + chr(cluster_count + 65)
            + " (#reviews = "
            + str(summary_labels[cluster_count])
            + ") ====",
        )
        print_sentiment_analysis(review_content)

        try:
            print(review_content)
        except UnicodeEncodeError:
            # Reference: https://stackoverflow.com/a/3224300
            print(review_content.encode('ascii', 'ignore'))

    return


def show_all_reviews_from_given_cluster(
    app_id,
    df,
    af,
    cluster_count,
    provided_labels=None,
):
    if provided_labels is None:
        provided_labels = []
    show_fixed_number_of_reviews_from_given_cluster(
        app_id,
        df,
        af,
        cluster_count,
        provided_labels,
    )
    return


def show_data_frame_for_cluster_centers(df, af, num_top_clusters=None, verbose=True):
    cluster_centers_indices = af.cluster_centers_indices_
    # labels = af.labels_

    (_, list_of_clusters_by_count) = get_top_clusters_by_count(af)

    sorted_cluster_centers_indices = cluster_centers_indices[
        [int(i) for i in list_of_clusters_by_count]
    ]

    # Reference: https://stackoverflow.com/a/19155860
    df_representative = df.iloc[sorted_cluster_centers_indices, :]

    if verbose:
        if num_top_clusters is None:
            print(df_representative)
        else:
            print(df_representative.iloc[0:num_top_clusters, :])

    return df_representative


# noinspection PyPep8Naming
def try_affinity_propagation(app_id, df, X, num_top_clusters=4, verbose=False):
    # #############################################################################
    # Compute Affinity Propagation
    af = AffinityPropagation().fit(X)
    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    # Show reviews used as cluster centers (for all clusters)
    show_representative_reviews(app_id, df, af)

    # Print additional info

    n_clusters_ = len(cluster_centers_indices)

    print('\nEstimated number of clusters: %d' % n_clusters_)
    print(
        "Silhouette Coefficient: %0.3f"
        % metrics.silhouette_score(X, labels, metric='sqeuclidean'),
    )

    # Show reviews used as cluster centers of the top clusters
    show_representative_reviews(app_id, df, af, num_top_clusters, verbose)

    # Show all reviews in given cluster (to manually check for cluster homogeneity)

    if verbose:
        cluster_count = 1  # Warning: this starts at 0
        show_all_reviews_from_given_cluster(app_id, df, af, cluster_count)

    # Show dataframe limited to cluster centers

    _ = show_data_frame_for_cluster_centers(df, af, num_top_clusters)

    return labels


# noinspection PyPep8Naming
def try_birch(app_id, df, X, num_clusters_input=3, num_reviews_to_show_per_cluster=3):
    # #############################################################################
    # Compute Agglomerative Clustering with Birch as a first step

    brc = Birch(
        branching_factor=50,
        n_clusters=num_clusters_input,
        threshold=0.5,
        compute_labels=True,
    )
    brc_labels = brc.fit_predict(X)

    # Show Birch results

    for cluster_count in range(num_clusters_input):
        show_fixed_number_of_reviews_from_given_cluster(
            app_id,
            df,
            None,
            cluster_count,
            brc_labels,
            num_reviews_to_show_per_cluster,
        )

    # Display number of reviews in each cluster

    get_top_clusters_by_count(None, brc_labels, True)

    return brc_labels


# noinspection PyPep8Naming
def try_agglomerative_clustering(
    app_id,
    df,
    X,
    num_clusters_input=3,
    num_reviews_to_show_per_cluster=3,
    linkage='ward',
    use_connectivity=True,
):
    # #############################################################################
    # Compute Agglomerative Clustering without Birch

    # NB: linkage can be any of these: 'average', 'complete', 'ward'

    if use_connectivity:
        knn_graph = kneighbors_graph(X, 30, include_self=False)
        connectivity = knn_graph  # one of these: None or knn_graph
    else:
        connectivity = None

    model = AgglomerativeClustering(
        linkage=linkage,
        connectivity=connectivity,
        n_clusters=num_clusters_input,
    )

    agg_labels = model.fit_predict(X)

    # Show Agglomerative Clustering results

    for cluster_count in range(num_clusters_input):
        show_fixed_number_of_reviews_from_given_cluster(
            app_id,
            df,
            None,
            cluster_count,
            agg_labels,
            num_reviews_to_show_per_cluster,
        )

    # Display number of reviews in each cluster

    get_top_clusters_by_count(None, agg_labels, True)

    return agg_labels


# noinspection PyPep8Naming
def try_dbscan(
    app_id,
    df,
    X,
    db_eps=0.3,
    db_min_samples=10,
    num_reviews_to_show_per_cluster=3,
):
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
    n_clusters_ = num_clusters_including_noise_cluster - (
        1 if -1 in dbscan_labels else 0
    )

    print('Estimated number of clusters: %d' % n_clusters_)
    print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, dbscan_labels))

    # Show DBSCAN results

    for cluster_count in range(num_clusters_including_noise_cluster):
        show_fixed_number_of_reviews_from_given_cluster(
            app_id,
            df,
            None,
            cluster_count,
            dbscan_labels,
            num_reviews_to_show_per_cluster,
        )

    # Display number of reviews in each cluster

    get_top_clusters_by_count(None, dbscan_labels, True)

    return dbscan_labels


def test_every_clustering_method(app_id):
    # Clustering
    # Reference: http://scikit-learn.org/stable/modules/clustering.html

    # NB: We are not interested in outlier detection:
    # - if the goal were to remove low-quality reviews, a threshold on review lenght should be sufficient,
    # - for some games, the low-quality/"funny meme" reviews are not outliers, they constitute their own sizable cluster

    # Features (columns) to exclude
    excluded_columns = ["language", "recommendationid"]

    # Load Pandas dataframe
    df = analyze_app_id_in_english(app_id)

    # Convert to NumPy matrix format
    # noinspection PyPep8Naming
    X = convert_from_pandas_dataframe_to_numpy_matrix(df, excluded_columns)

    # Demo of every clustering method

    # Affinity Propagation
    # NB: The clusters look consistent, I like the results, but:
    # - there are too many clusters (11) for our application,
    # - and there is no direct control of the number of clusters.
    # I don't want to have to look at each cluster to find one-line joke reviews, so I prefer to go with another method.

    num_top_clusters = 4
    verbose = True

    try_affinity_propagation(app_id, df, X, num_top_clusters, verbose)

    # Agglomerative Clustering with Birch

    num_clusters_input = 3
    num_reviews_to_show_per_cluster = 3

    try_birch(app_id, df, X, num_clusters_input, num_reviews_to_show_per_cluster)

    # Agglomerative Clustering without Birch
    # NB: With some parameters, results are similar to Birch's (as expected from scikit-learn documentation of Birch).

    linkage = 'ward'
    use_connectivity = True

    try_agglomerative_clustering(
        app_id,
        df,
        X,
        num_clusters_input,
        num_reviews_to_show_per_cluster,
        linkage,
        use_connectivity,
    )

    # DBSCAN
    # NB: Not satisfactory here. Either the parameters, or the data pre-processing, should be changed for DBSCAN.

    db_eps = 40
    db_min_samples = 4

    try_dbscan(app_id, df, X, db_eps, db_min_samples, num_reviews_to_show_per_cluster)

    return


def apply_affinity_propagation(app_id, num_reviews_to_show_per_cluster=3):
    # Cluster reviews for app_id using Affinity Propagation

    # Load Pandas dataframe
    df = analyze_app_id_in_english(app_id)

    # Convert to NumPy matrix format
    # noinspection PyPep8Naming
    X = convert_from_pandas_dataframe_to_numpy_matrix(df)

    af = AffinityPropagation().fit(X)
    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    # Show reviews used as cluster centers (for all clusters)
    show_representative_reviews(app_id, df, af)

    # Print additional info

    n_clusters_ = len(cluster_centers_indices)

    print('\nEstimated number of clusters: %d' % n_clusters_)
    print(
        "Silhouette Coefficient: %0.3f"
        % metrics.silhouette_score(X, labels, metric='sqeuclidean'),
    )

    # Show Affinity Propagation results

    for cluster_count in range(n_clusters_):
        show_fixed_number_of_reviews_from_given_cluster(
            app_id,
            df,
            af,
            cluster_count,
            labels,
            num_reviews_to_show_per_cluster,
        )

    # Display number of reviews in each cluster

    get_top_clusters_by_count(None, labels, True)

    return df, labels


def apply_birch(app_id, num_clusters_input=3, num_reviews_to_show_per_cluster=3):
    # Cluster reviews for app_id using selected method (Birch and then Agglomerative Clustering)

    # Load Pandas dataframe
    df = analyze_app_id_in_english(app_id)

    # Convert to NumPy matrix format
    # noinspection PyPep8Naming
    X = convert_from_pandas_dataframe_to_numpy_matrix(df)

    brc_labels = try_birch(
        app_id,
        df,
        X,
        num_clusters_input,
        num_reviews_to_show_per_cluster,
    )

    return df, brc_labels


def main(argv):
    app_id_list = ["723090", "639780", "573170"]

    if len(argv) == 0:
        app_id = app_id_list[-1]
        print("No input detected. AppID automatically set to " + app_id)
    else:
        app_id = argv[0]
        print("Input appID detected as " + app_id)

    num_reviews_to_show_per_cluster = 3  # Set to None to show all the reviews

    apply_birch_method = True

    if apply_birch_method:
        # Apply Birch and then Agglomerative Clustering
        num_clusters_input = 3
        (_, _) = apply_birch(
            app_id,
            num_clusters_input,
            num_reviews_to_show_per_cluster,
        )
    else:
        # Apply Affinity Propagation
        (_, _) = apply_affinity_propagation(app_id, num_reviews_to_show_per_cluster)

    # Demo of every clustering method

    perform_full_test_suite = False

    if perform_full_test_suite:
        test_every_clustering_method(app_id)

    return True


if __name__ == "__main__":
    main(sys.argv[1:])
