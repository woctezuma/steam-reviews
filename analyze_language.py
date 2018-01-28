from langdetect import detect, DetectorFactory, lang_detect_exception

from describe_reviews import loadData, describeData, getReviewContent

import iso639

import scipy.sparse as sp

from sklearn.preprocessing import normalize
import numpy as np

def getReviewLanguageDictionary(appID, previously_detected_languages_dict = None):
    # Returns dictionary: reviewID -> dictionary with (tagged language, detected language)

    review_data = loadData(appID)

    print('\nAppID: ' + appID)

    (query_summary, reviews) = describeData(review_data)

    language_dict = dict()

    if previously_detected_languages_dict is None:
        previously_detected_languages_dict = dict()

    if appID not in previously_detected_languages_dict.keys():
        previously_detected_languages_dict[appID] = dict()

    for review in reviews:
        # Review ID
        reviewID = review["recommendationid"]

        # Review polarity tag, i.e. either "recommended" or "not recommended"
        is_a_positive_review = review['voted_up']

        # Review text
        review_content = review['review']

        # Review language tag
        review_language_tag = review['language']

        # Review's automatically detected language
        if reviewID in previously_detected_languages_dict[appID].keys():
            detected_language = previously_detected_languages_dict[appID][reviewID]
        else:
            try:
                DetectorFactory.seed = 0
                detected_language = detect(review_content)
            except lang_detect_exception.LangDetectException:
                detected_language = 'unknown'
            previously_detected_languages_dict[appID][reviewID] = detected_language
            previously_detected_languages_dict['has_changed'] = True

        language_dict[reviewID] = dict()
        language_dict[reviewID]['tag'] = review_language_tag
        language_dict[reviewID]['detected'] = detected_language
        language_dict[reviewID]['voted_up'] = is_a_positive_review

    return (language_dict, previously_detected_languages_dict)

def most_common(L):
    # Reference: https://stackoverflow.com/a/1518632

    import itertools
    import operator

    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))

    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index

    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]

def convertReviewLanguageDictionaryToISO(language_dict):

    language_iso_dict = dict()

    languages = set([r['tag'] for r in language_dict.values()])

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

                detected_languages = [r['detected'] for r in language_dict.values() if r['tag'] == language]
                print(detected_languages)

                language_iso = most_common(detected_languages)
                print('Most common match among detected languages: ' + language_iso)

        language_iso_dict[language] = language_iso

    return language_iso_dict

def summarizeReviewLanguageDictionary(language_dict):
    # Returns dictionary: language -> review stats including:
    #                                 - number of reviews for which tagged language coincides with detected language
    #                                 - number of such reviews which are "Recommended"
    #                                 - number of such reviews which are "Not Recommended"

    summary_dict = dict()

    language_iso_dict = convertReviewLanguageDictionaryToISO(language_dict)

    for language_iso in set(language_iso_dict.values()):
        reviews_with_matching_languages = [r for r in language_dict.values() if r['detected'] == language_iso]
        num_votes = len(reviews_with_matching_languages)
        positive_reviews_with_matching_languages = [r for r in reviews_with_matching_languages if bool(r['voted_up']) ]
        num_upvotes = len(positive_reviews_with_matching_languages)
        num_downvotes = num_votes - num_upvotes

        summary_dict[language_iso] = dict()
        summary_dict[language_iso]['voted'] = num_votes
        summary_dict[language_iso]['voted_up'] = num_upvotes
        summary_dict[language_iso]['voted_down'] = num_downvotes

    return summary_dict

def getAllReviewLanguageSummaries(previously_detected_languages_filename = None, delta_n_reviews_between_temp_saves = 10):
    from appids import appid_hidden_gems_reference_set

    with open('idlist.txt') as f:
        d = f.readlines()

    appID_list = [x.strip() for x in d]

    appID_list = list(set(appID_list).union(appid_hidden_gems_reference_set))

    game_feature_dict = dict()
    all_languages = set()

    # Load the result of language detection for each review
    try:
        with open(previously_detected_languages_filename, 'r', encoding="utf8") as infile:
            lines = infile.readlines()
            # The dictionary is on the first line
            previously_detected_languages_dict = eval(lines[0])
    except FileNotFoundError:
        previously_detected_languages_dict = dict()

    previously_detected_languages_dict['has_changed'] = False

    for count, appID in enumerate(appID_list):
        (language_dict, previously_detected_languages_dict) = getReviewLanguageDictionary(appID, previously_detected_languages_dict)

        summary_dict = summarizeReviewLanguageDictionary(language_dict)

        game_feature_dict[appID] = summary_dict
        all_languages = all_languages.union(summary_dict.keys())

        if delta_n_reviews_between_temp_saves > 0:
            flush_to_file_now = bool(count % delta_n_reviews_between_temp_saves == 0)
        else:
            flush_to_file_now = bool(count==len(appID_list)-1)

        # Export the result of language detection for each review, so as to avoid repeating intensive computations.
        if previously_detected_languages_filename is not None and flush_to_file_now and previously_detected_languages_dict['has_changed']:
            with open(previously_detected_languages_filename, 'w', encoding="utf8") as outfile:
                print(previously_detected_languages_dict, file=outfile)
            previously_detected_languages_dict['has_changed'] = False

        print('AppID ' + str(count+1) + '/' + str(len(appID_list)) + ' done.')

    all_languages = sorted(list(all_languages))

    return (game_feature_dict, all_languages)

def loadGameFeatureDictionary(dict_filename ="dict_review_languages.txt"):
    # Obtained by running getAllReviewLanguageSummaries() on the top hidden gems.

    # Import the dictionary of game features from a text file
    with open(dict_filename, 'r', encoding="utf8") as infile:
        lines = infile.readlines()
        # The dictionary is on the first line
        game_feature_dict = eval(lines[0])

    print('Dictionary of language features loaded from disk.')

    return game_feature_dict

def loadAllLanguages(language_filename ="list_all_languages.txt"):
    # Obtained by running getAllReviewLanguageSummaries() on the top hidden gems.

    # Import the list of languages from a text file
    with open(language_filename, 'r', encoding="utf8") as infile:
        lines = infile.readlines()
        # The list is on the first line
        all_languages = eval(lines[0])

    print('List of languages loaded from disk.')

    return all_languages

def loadGameFeaturesAsReviewLanguage(dict_filename ="dict_review_languages.txt",
                                     language_filename ="list_all_languages.txt"):

    game_feature_dict = loadGameFeatureDictionary(dict_filename)

    all_languages = loadAllLanguages(language_filename)

    return (game_feature_dict, all_languages)

def writeContentToDisk(contentToWrite, filename):

    # Export the content to a text file
    with open(filename, 'w', encoding="utf8") as outfile:
        print(contentToWrite, file=outfile)

    return

def getGameFeaturesAsReviewLanguage(dict_filename ="dict_review_languages.txt",
                                    language_filename ="list_all_languages.txt",
                                    previously_detected_languages_filename = "previously_detected_languages.txt"):
    # Run getAllReviewLanguageSummaries() on the top hidden gems.

    print('Computing dictonary of language features from scratch.')

    (game_feature_dict, all_languages) = getAllReviewLanguageSummaries(previously_detected_languages_filename)

    # Export the dictionary of game features to a text file
    writeContentToDisk(game_feature_dict, dict_filename)
    print('Dictionary of language features written to disk.')

    # Export the list of languages to a text file
    writeContentToDisk(all_languages, language_filename)
    print('List of languages written to disk.')

    return (game_feature_dict, all_languages)

def computeGameFeatureMatrix(game_feature_dict, all_languages, verbose = False):
    appIDs = sorted(list(game_feature_dict.keys()))
    languages = sorted(list(all_languages))

    # Reference: https://stackoverflow.com/a/43381974
    map_row_dict = dict(zip(list(appIDs), range(len(appIDs))))
    map_col_dict = dict(zip(list(languages), range(len(languages))))

    rows, cols, vals = [], [], []
    for appID, values in game_feature_dict.items():
        for language, language_stats in values.items():
            count = language_stats['voted']
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
        try:
            game_feature_dict.pop(appID)
        except KeyError:
            continue

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
                if iter_count % 3 == 0:
                    print(' %s ;' % terms[ind], end='\n\t')
                else:
                    if iter_count == 1:
                        print('\t %s ;' % terms[ind], end='\t')
                    else:
                        print(' %s ;' % terms[ind], end='\t')
            print()

    return

def testClustering(game_feature_dict, all_languages):

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

def computeReviewLanguageDistribution(game_feature_dict, all_languages):
    # Compute the distribution of review languages among reviewers

    review_language_distribution = dict()

    for appID in game_feature_dict.keys():
        data_for_current_game = game_feature_dict[appID]

        num_reviews = sum([ data_for_current_game[language]['voted'] for language in data_for_current_game.keys() ])

        review_language_distribution[appID] = dict()
        review_language_distribution[appID]['num_reviews'] = num_reviews
        review_language_distribution[appID]['distribution'] = dict()
        for language in all_languages:
            try:
                review_language_distribution[appID]['distribution'][language] = data_for_current_game[language]['voted'] / num_reviews
            except KeyError:
                review_language_distribution[appID]['distribution'][language] = 0

    return review_language_distribution

def prepareDictionaryForRankingOfHiddenGems(steam_spy_dict, game_feature_dict, all_languages, quantile_for_our_own_wilson_score = 0.95):
    # Prepare dictionary to feed to compute_stats module in hidden-gems repository

    from compute_wilson_score import computeWilsonScore

    D = dict()

    review_language_distribution = computeReviewLanguageDistribution(game_feature_dict, all_languages)

    for appID in game_feature_dict.keys():
        D[appID] = dict()
        try:
            D[appID]['name'] = steam_spy_dict[appID]['name']
        except KeyError:
            D[appID]['name'] = 'Unknown ' + str(appID)

        try:
            num_players_for_all_languages = steam_spy_dict[appID]['players_forever']
        except KeyError:
            num_players_for_all_languages = 0

        for language in all_languages:
            D[appID][language] = dict()

            try:
                num_positive_reviews = game_feature_dict[appID][language]['voted_up']
                num_negative_reviews = game_feature_dict[appID][language]['voted_down']
            except KeyError:
                num_positive_reviews = 0
                num_negative_reviews = 0

            wilson_score = computeWilsonScore(num_positive_reviews, num_negative_reviews, quantile_for_our_own_wilson_score)

            if wilson_score is None:
                wilson_score = -1

            # Assumption: for every game, players and reviews are distributed among regions in the same proportions.
            num_players = num_players_for_all_languages * review_language_distribution[appID]['distribution'][language]

            D[appID][language]['wilson_score'] = wilson_score
            D[appID][language]['num_players'] = num_players

    return D

def computeRegionalRankingsOfHiddenGems(game_feature_dict, all_languages,
                                        perform_optimization_at_runtime = True,
                                        num_top_games_to_print = 1000):
    from download_json import getTodaysSteamSpyData
    from compute_stats import computeRanking, saveRankingToFile

    import pathlib

    # Output folder for regional rankings of hidden gems
    output_folder = 'regional_rankings/'
    # Reference of the following line: https://stackoverflow.com/a/14364249
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

    steam_spy_dict = getTodaysSteamSpyData()

    D = prepareDictionaryForRankingOfHiddenGems(steam_spy_dict, game_feature_dict, all_languages)

    for language in all_languages:
        output_filename = output_folder + "hidden_gems_" + language + ".md"

        ranking = computeRanking(D, num_top_games_to_print, [], [], language, perform_optimization_at_runtime)

        saveRankingToFile(output_filename, ranking)

    return

def getInputData(force_update_of_regional_stats = False):
    # If force_update_of_regional_stats is True, the TXT files below will be updated, which might take a lot of time
    # if the last update was done a long time ago. Otherwise, the TXT files will just be loaded as they are.

    dict_filename = "dict_review_languages.txt"
    language_filename = "list_all_languages.txt"
    previously_detected_languages_filename = "previously_detected_languages.txt"

    # In order to update stats regarding reviewers' languages, load_from_disk needs to be set to False.
    # Otherwise, game_feature_dict is loaded from the disk without being updated at all.
    load_from_disk = not(force_update_of_regional_stats)

    if load_from_disk:
        (game_feature_dict, all_languages) = loadGameFeaturesAsReviewLanguage(dict_filename, language_filename)
    else:
        (game_feature_dict, all_languages) = getGameFeaturesAsReviewLanguage(dict_filename, language_filename, previously_detected_languages_filename)

    return (game_feature_dict, all_languages)

def main():
    force_update_of_regional_stats = False
    (game_feature_dict, all_languages) = getInputData(force_update_of_regional_stats)

    # testClustering(game_feature_dict, all_languages)

    perform_optimization_at_runtime = True
    num_top_games_to_print = 250
    computeRegionalRankingsOfHiddenGems(game_feature_dict, all_languages, perform_optimization_at_runtime, num_top_games_to_print)

    return

if __name__ == "__main__":
    main()
