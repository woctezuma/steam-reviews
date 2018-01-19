from langdetect import detect, DetectorFactory, lang_detect_exception

from describe_reviews import loadData, describeData, getReviewContent

import iso639

import scipy.sparse as sp

from sklearn.preprocessing import normalize
import numpy as np

def getReviewLanguageDictionary(appID):
    # Returns dictionary: reviewID -> dictionary with (tagged language, detected language)

    review_data = loadData(appID)

    print('\nAppID: ' + appID)

    (query_summary, reviews) = describeData(review_data)

    language_dict = dict()

    for review in reviews:
        # Review ID
        reviewID = review["recommendationid"]

        # Review text
        review_content = review['review']

        # Review language tag
        review_language_tag = review['language']

        # Review's automatically detected language
        try:
            DetectorFactory.seed = 0
            detected_language = detect(review_content)
        except lang_detect_exception.LangDetectException:
            detected_language = 'unknown'

        language_dict[reviewID] = dict()
        language_dict[reviewID]['tag'] = review_language_tag
        language_dict[reviewID]['detected'] = detected_language

    return language_dict

def summarizeReviewLanguageDictionary(language_dict):
    # Returns dictionary: language -> number of reviews for which tagged language coincides with detected language

    summary_dict = dict()

    languages = set([r['tag'] for r in language_dict.values() ])

    for language in languages:
        try:
            language_iso = iso639.to_iso639_1(language)
        except iso639.NonExistentLanguageError:
            if language == 'schinese' or language == 'tchinese':
                language_iso = 'zh-cn'
            elif language == 'brazilian':
                language_iso = 'pt'
            elif language == 'koreana':
                language_iso = 'ko'
            else:
                print('Missing language:' + language)
                print([r['detected'] for r in language_dict.values() if r['tag'] == language])
                continue

        summary_dict[language_iso] = sum([1 for r in language_dict.values() if r['detected'] == language_iso])

    return summary_dict

def getReviewLanguageSummary(appID):

    language_dict = getReviewLanguageDictionary(appID)

    summary_dict = summarizeReviewLanguageDictionary(language_dict)

    return summary_dict

def getAllReviewLanguageSummaries(max_num_appID = None):

    with open('idlist.txt') as f:
        d = f.readlines()

    appID_list = [x.strip() for x in d]

    if max_num_appID is not None:
        max_num_appID = min(max_num_appID, len(appID_list))
        appID_list = appID_list[0: max_num_appID]

    game_feature_dict = dict()
    all_languages = set()

    for appID in appID_list:
        summary_dict = getReviewLanguageSummary(appID)

        game_feature_dict[appID] = summary_dict
        all_languages = all_languages.union(summary_dict.keys())

    all_languages = sorted(list(all_languages))

    return (game_feature_dict, all_languages)

def getAllLanguages(language_filename = "list_all_languages.txt"):
    # Obtained by running getAllReviewLanguageSummaries() on the top 250 hidden gems.

    # Import the list of languages from a text file
    with open(language_filename, 'r', encoding="utf8") as infile:
        lines = infile.readlines()
        # The list is on the first line
        all_languages = eval(lines[0])

    print('List of languages loaded from disk.')

    return all_languages

def getGameFeaturesAsReviewLanguage(dict_filename ="dict_review_languages.txt",
                                    language_filename ="list_all_languages.txt"):
    # Obtained by running getAllReviewLanguageSummaries() on the top 250 hidden gems.

    try:

        # Import the dictionary of game features from a text file
        with open(dict_filename, 'r', encoding="utf8") as infile:
            lines = infile.readlines()
            # The dictionary is on the first line
            game_feature_dict = eval(lines[0])

            print('Dictionary of language features loaded from disk.')

    except FileNotFoundError:

        print('Computing dictonary of language features from scratch.')

        max_num_appID = None
        (game_feature_dict, all_languages) = getAllReviewLanguageSummaries(max_num_appID)

        # Export the dictionary of game features to a text file
        with open(dict_filename, 'w', encoding="utf8") as outfile:
            print(game_feature_dict, file=outfile)

        print('Dictionary of language features written to disk.')

        # Export the list of languages to a text file
        with open(language_filename, 'w', encoding="utf8") as outfile:
            print(all_languages, file=outfile)

        print('List of languages written to disk.')

    return game_feature_dict

def computeGameFeatureMatrix(game_feature_dict, all_languages, verbose = False):
    appIDs = sorted(list(game_feature_dict.keys()))
    languages = sorted(list(all_languages))

    # Reference: https://stackoverflow.com/a/43381974
    map_row_dict = dict(zip(list(appIDs), range(len(appIDs))))
    map_col_dict = dict(zip(list(languages), range(len(languages))))

    rows, cols, vals = [], [], []
    for appID, values in game_feature_dict.items():
        for language, count in values.items():
            rows.append(map_row_dict[appID])
            cols.append(map_col_dict[language])
            vals.append(count)

    game_feature_matrix = sp.csr_matrix((vals, (rows, cols)))

    if verbose:
        print(game_feature_matrix.toarray())

    return game_feature_matrix

def normalizeEachRow(X, verbose = False):

    X_normalized = normalize(X.astype('float64'), norm='l1')

    if verbose:
        print(X_normalized.toarray())

    return X_normalized

def getAppNameList(appID_list):
    from download_json import getTodaysSteamSpyData

    # Download latest SteamSpy data to have access to the matching between appID and game name
    SteamSpyData = getTodaysSteamSpyData()

    appName_list = []

    for appID in appID_list:
        try:
            appName = SteamSpyData[appID]['name']
        except KeyError:
            appName = 'unknown'
        appName_list.append(appName)

    return appName_list

def removeBuggedAppIDs(game_feature_dict, list_bugged_appIDs = ['272670', '34460', '575050']):
    list_bugged_appNames = getAppNameList(list_bugged_appIDs)

    print('\nRemoving bugged appIDs:\t' + ' ; '.join(list_bugged_appNames) + '\n')

    for appID in list_bugged_appIDs:
        game_feature_dict.pop(appID)

    return game_feature_dict

def testKmeansClustering(normalized_game_feature_matrix, appIDs, languages):
    # Cluster hidden gems based on the number of reviews and the language they are written in.
    X = normalized_game_feature_matrix

    import matplotlib.pyplot as plt
    from sklearn.decomposition import TruncatedSVD
    from sklearn.cluster import KMeans
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import Normalizer

    # Truncated SVD for dimensionality reduction (none if set to 0)
    n_components_dim_reduction = 0
    # K-means clustering
    n_clusters_kmeans = 3

    # Reference: http://scikit-learn.org/stable/auto_examples/text/document_clustering.html

    if n_components_dim_reduction:
        svd = TruncatedSVD(n_components_dim_reduction)
        normalizer = Normalizer(copy=False)
        lsa = make_pipeline(svd, normalizer)

        X = lsa.fit_transform(X)

        explained_variance = svd.explained_variance_ratio_.sum()
        print("Explained variance of the SVD step: {}%".format(
            int(explained_variance * 100)))

        plt.figure()
        lw = 2

        plt.scatter(X[:, 0], X[:, 1], alpha=.8, lw=lw)
        plt.title('SVD')
        # plt.show()

    km = KMeans(n_clusters=n_clusters_kmeans, init='k-means++', max_iter=100, n_init=1, verbose=True)

    print("Clustering sparse data with %s" % km)
    km.fit(X)

    if n_components_dim_reduction:
        original_space_centroids = svd.inverse_transform(km.cluster_centers_)
        order_centroids = original_space_centroids.argsort()[:, ::-1]
    else:
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    print()

    for i in range(n_clusters_kmeans):
        print("Cluster %d:" % i, end='')
        indices = np.where(km.labels_ == i)[0]
        print(' %s elements' % len(indices), end='')
        print()

    print()

    terms = languages
    num_features_to_show = 10
    for i in range(n_clusters_kmeans):
        print("Cluster %d:" % i, end='')
        for ind in order_centroids[i, :num_features_to_show]:
            print(' %s ;' % terms[ind], end='')
        print()

    print()

    terms = getAppNameList(appIDs)
    num_appIDs_to_show = 20
    for i in range(n_clusters_kmeans):
        print("Cluster %d:\n\t" % i, end='')
        indices = np.where(km.labels_ == i)[0]
        iter_count = 0
        for ind in indices[:num_appIDs_to_show]:
            iter_count += 1
            if iter_count % 7 == 0:
                print(' %s \n\t' % terms[ind], end='')
            else:
                print(' %s \t' % terms[ind], end='')
        print()

    return

def testAffinityPropagationClustering(normalized_game_feature_matrix, appIDs, languages):
    # Cluster hidden gems based on the number of reviews and the language they are written in.
    X = normalized_game_feature_matrix

    import matplotlib.pyplot as plt
    from sklearn.cluster import AffinityPropagation

    my_af_preference = None
    # If you are lost and cannot find good values for preference, just set it to None and it will be initialized as:
    # from sklearn.metrics.pairwise import euclidean_distances
    # print( np.median( - euclidean_distances(X, squared=True) ) )

    # Reference: http://scikit-learn.org/stable/auto_examples/cluster/plot_affinity_propagation.html

    af = AffinityPropagation(preference=my_af_preference).fit(X)

    n_clusters_ = len(af.cluster_centers_indices_)

    print('Estimated number of clusters: %d' % n_clusters_)

    order_centroids = af.cluster_centers_.toarray().argsort()[:, ::-1]

    if n_clusters_ < 20:

        print()

        for i in range(n_clusters_):
            print("Cluster %d:" % i, end='')
            indices = np.where(af.labels_ == i)[0]
            print(' %s elements' % len(indices), end='')
            print()

        print()

        num_features_to_show = 5
        for i in range(n_clusters_):
            print("Cluster %d:" % i, end='')
            for ind in order_centroids[i, :num_features_to_show]:
                print(' %s ;' % languages[ind], end='')
            print()

        print()

        num_appIDs_to_show = None
        terms = getAppNameList(appIDs)
        for i in range(n_clusters_):
            # Samples
            indices = np.where(af.labels_ == i)[0]

            print("\nCluster {}:\t {} game(s)".format(chr(i+65), len(indices)))

            # Features
            print('Languages by number of reviews:\t', end='')
            for ind in order_centroids[i, :num_features_to_show]:
                print(' %s ;' % languages[ind], end='')
            print(' etc.')

            print('Samples:')
            iter_count = 0
            if num_appIDs_to_show is not None:
                selected_indices_to_display = indices[:num_appIDs_to_show]
            else:
                selected_indices_to_display = indices
            for ind in selected_indices_to_display:
                iter_count += 1
                if iter_count % 5 == 0:
                    print(' %s ;' % terms[ind], end='\n\t')
                else:
                    if iter_count == 1:
                        print('\t %s ;' % terms[ind], end='\t')
                    else:
                        print(' %s ;' % terms[ind], end='\t')
            print()

    return

def main():
    dict_filename = "dict_review_languages.txt"
    language_filename = "list_all_languages.txt"

    game_feature_dict = getGameFeaturesAsReviewLanguage(dict_filename, language_filename)
    all_languages = getAllLanguages(language_filename)

    game_feature_dict = removeBuggedAppIDs(game_feature_dict)

    game_feature_matrix = computeGameFeatureMatrix(game_feature_dict, all_languages)

    normalized_game_feature_matrix = normalizeEachRow(game_feature_matrix)

    appIDs = sorted(list(game_feature_dict.keys()))
    languages = sorted(list(all_languages))

    # Need to know the number of clusters we want in order to use K-means
    # testKmeansClustering(normalized_game_feature_matrix, appIDs, languages)

    # Need to specify the "preference" parameter in order to use Affinity Propagation
    testAffinityPropagationClustering(normalized_game_feature_matrix, appIDs, languages)

    return

if __name__ == "__main__":
    main()
