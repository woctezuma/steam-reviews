import iso639
import numpy as np
import scipy.sparse as sp
from langdetect import detect, DetectorFactory, lang_detect_exception
from sklearn.preprocessing import normalize

from describe_reviews import load_data, describe_data


def get_review_language_dictionary(app_id, previously_detected_languages_dict=None):
    # Returns dictionary: reviewID -> dictionary with (tagged language, detected language)

    review_data = load_data(app_id)

    print('\nAppID: ' + app_id)

    (query_summary, reviews) = describe_data(review_data)

    language_dict = dict()

    if previously_detected_languages_dict is None:
        previously_detected_languages_dict = dict()

    if app_id not in previously_detected_languages_dict.keys():
        previously_detected_languages_dict[app_id] = dict()

    for review in reviews:
        # Review ID
        review_id = review["recommendationid"]

        # Review polarity tag, i.e. either "recommended" or "not recommended"
        is_a_positive_review = review['voted_up']

        # Review text
        review_content = review['review']

        # Review language tag
        review_language_tag = review['language']

        # Review's automatically detected language
        if review_id in previously_detected_languages_dict[app_id].keys():
            detected_language = previously_detected_languages_dict[app_id][review_id]
        else:
            try:
                DetectorFactory.seed = 0
                detected_language = detect(review_content)
            except lang_detect_exception.LangDetectException:
                detected_language = 'unknown'
            previously_detected_languages_dict[app_id][review_id] = detected_language
            previously_detected_languages_dict['has_changed'] = True

        language_dict[review_id] = dict()
        language_dict[review_id]['tag'] = review_language_tag
        language_dict[review_id]['detected'] = detected_language
        language_dict[review_id]['voted_up'] = is_a_positive_review

    return language_dict, previously_detected_languages_dict


# noinspection PyPep8Naming
def most_common(L):
    # Reference: https://stackoverflow.com/a/1518632

    import itertools
    import operator

    # get an iterable of (item, iterable) pairs
    # noinspection PyPep8Naming
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


def convert_review_language_dictionary_to_iso(language_dict):
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


def summarize_review_language_dictionary(language_dict):
    # Returns dictionary: language -> review stats including:
    #                                 - number of reviews for which tagged language coincides with detected language
    #                                 - number of such reviews which are "Recommended"
    #                                 - number of such reviews which are "Not Recommended"

    summary_dict = dict()

    language_iso_dict = convert_review_language_dictionary_to_iso(language_dict)

    for language_iso in set(language_iso_dict.values()):
        reviews_with_matching_languages = [r for r in language_dict.values() if r['detected'] == language_iso]
        num_votes = len(reviews_with_matching_languages)
        positive_reviews_with_matching_languages = [r for r in reviews_with_matching_languages if bool(r['voted_up'])]
        num_upvotes = len(positive_reviews_with_matching_languages)
        num_downvotes = num_votes - num_upvotes

        summary_dict[language_iso] = dict()
        summary_dict[language_iso]['voted'] = num_votes
        summary_dict[language_iso]['voted_up'] = num_upvotes
        summary_dict[language_iso]['voted_down'] = num_downvotes

    return summary_dict


def get_all_review_language_summaries(previously_detected_languages_filename=None,
                                      delta_n_reviews_between_temp_saves=10):
    from appids import appid_hidden_gems_reference_set

    with open('idlist.txt') as f:
        d = f.readlines()

    app_id_list = [x.strip() for x in d]

    app_id_list = list(set(app_id_list).union(appid_hidden_gems_reference_set))

    game_feature_dict = dict()
    all_languages = set()

    # Load the result of language detection for each review
    try:
        with open(previously_detected_languages_filename, 'r', encoding="utf8") as infile:
            lines = infile.readlines()
            # The dictionary is on the first line
            previously_detected_languages = eval(lines[0])
    except FileNotFoundError:
        previously_detected_languages = dict()

    previously_detected_languages['has_changed'] = False

    for count, appID in enumerate(app_id_list):
        (language_dict, previously_detected_languages) = get_review_language_dictionary(appID,
                                                                                        previously_detected_languages)

        summary_dict = summarize_review_language_dictionary(language_dict)

        game_feature_dict[appID] = summary_dict
        all_languages = all_languages.union(summary_dict.keys())

        if delta_n_reviews_between_temp_saves > 0:
            flush_to_file_now = bool(count % delta_n_reviews_between_temp_saves == 0)
        else:
            flush_to_file_now = bool(count == len(app_id_list) - 1)

        # Export the result of language detection for each review, so as to avoid repeating intensive computations.
        if previously_detected_languages_filename is not None and flush_to_file_now and \
                previously_detected_languages['has_changed']:
            with open(previously_detected_languages_filename, 'w', encoding="utf8") as outfile:
                print(previously_detected_languages, file=outfile)
            previously_detected_languages['has_changed'] = False

        print('AppID ' + str(count + 1) + '/' + str(len(app_id_list)) + ' done.')

    all_languages = sorted(list(all_languages))

    return game_feature_dict, all_languages


def load_game_feature_dictionary(dict_filename="dict_review_languages.txt"):
    # Obtained by running get_all_review_language_summaries() on the top hidden gems.

    # Import the dictionary of game features from a text file
    with open(dict_filename, 'r', encoding="utf8") as infile:
        lines = infile.readlines()
        # The dictionary is on the first line
        game_feature_dict = eval(lines[0])

    print('Dictionary of language features loaded from disk.')

    return game_feature_dict


def load_all_languages(language_filename="list_all_languages.txt"):
    # Obtained by running get_all_review_language_summaries() on the top hidden gems.

    # Import the list of languages from a text file
    with open(language_filename, 'r', encoding="utf8") as infile:
        lines = infile.readlines()
        # The list is on the first line
        all_languages = eval(lines[0])

    print('List of languages loaded from disk.')

    return all_languages


def load_game_features_as_review_language(dict_filename="dict_review_languages.txt",
                                          language_filename="list_all_languages.txt"):
    game_feature_dict = load_game_feature_dictionary(dict_filename)

    all_languages = load_all_languages(language_filename)

    return game_feature_dict, all_languages


def write_content_to_disk(content_to_write, filename):
    # Export the content to a text file
    with open(filename, 'w', encoding="utf8") as outfile:
        print(content_to_write, file=outfile)

    return


def get_game_features_as_review_language(dict_filename="dict_review_languages.txt",
                                         language_filename="list_all_languages.txt",
                                         previously_detected_languages_filename="previously_detected_languages.txt"):
    # Run get_all_review_language_summaries() on the top hidden gems.

    print('Computing dictonary of language features from scratch.')

    (game_feature_dict, all_languages) = get_all_review_language_summaries(previously_detected_languages_filename)

    # Export the dictionary of game features to a text file
    write_content_to_disk(game_feature_dict, dict_filename)
    print('Dictionary of language features written to disk.')

    # Export the list of languages to a text file
    write_content_to_disk(all_languages, language_filename)
    print('List of languages written to disk.')

    return game_feature_dict, all_languages


def compute_game_feature_matrix(game_feature_dict, all_languages, verbose=False):
    app_ids = sorted(list(game_feature_dict.keys()))
    languages = sorted(list(all_languages))

    # Reference: https://stackoverflow.com/a/43381974
    map_row_dict = dict(zip(list(app_ids), range(len(app_ids))))
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


# noinspection PyPep8Naming
def normalize_each_row(X, verbose=False):
    # noinspection PyPep8Naming
    X_normalized = normalize(X.astype('float64'), norm='l1')

    if verbose:
        print(X_normalized.toarray())

    return X_normalized


def get_app_name_list(app_id_list):
    from download_json import get_todays_steam_spy_data

    # Download latest SteamSpy data to have access to the matching between appID and game name
    steam_spy_data = get_todays_steam_spy_data()

    app_name_list = []

    for appID in app_id_list:
        try:
            app_name = steam_spy_data[appID]['name']
        except KeyError:
            app_name = 'unknown'
        app_name_list.append(app_name)

    return app_name_list


def remove_bugged_app_ids(game_feature_dict, list_bugged_app_ids=None):
    if list_bugged_app_ids is None:
        list_bugged_app_ids = ['272670', '34460', '575050']
    list_bugged_app_names = get_app_name_list(list_bugged_app_ids)

    print('\nRemoving bugged appIDs:\t' + ' ; '.join(list_bugged_app_names) + '\n')

    for appID in list_bugged_app_ids:
        try:
            game_feature_dict.pop(appID)
        except KeyError:
            continue

    return game_feature_dict


def test_kmeans_clustering(normalized_game_feature_matrix, app_ids, languages):
    # Cluster hidden gems based on the number of reviews and the language they are written in.
    global svd
    # noinspection PyPep8Naming
    X = normalized_game_feature_matrix

    import matplotlib.pyplot as plt
    from sklearn.decomposition import TruncatedSVD
    from sklearn.cluster import KMeans
    # noinspection PyProtectedMember
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

        # noinspection PyPep8Naming
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

    terms = get_app_name_list(app_ids)
    num_app_ids_to_show = 20
    for i in range(n_clusters_kmeans):
        print("Cluster %d:\n\t" % i, end='')
        indices = np.where(km.labels_ == i)[0]
        iter_count = 0
        for ind in indices[:num_app_ids_to_show]:
            iter_count += 1
            if iter_count % 7 == 0:
                print(' %s \n\t' % terms[ind], end='')
            else:
                print(' %s \t' % terms[ind], end='')
        print()

    return


def test_affinity_propagation_clustering(normalized_game_feature_matrix, app_ids, languages):
    # Cluster hidden gems based on the number of reviews and the language they are written in.
    # noinspection PyPep8Naming
    X = normalized_game_feature_matrix

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

        num_app_ids_to_show = None
        terms = get_app_name_list(app_ids)
        for i in range(n_clusters_):
            # Samples
            indices = np.where(af.labels_ == i)[0]

            print("\nCluster {}:\t {} game(s)".format(chr(i + 65), len(indices)))

            # Features
            print('Languages by number of reviews:\t', end='')
            for ind in order_centroids[i, :num_features_to_show]:
                print(' %s ;' % languages[ind], end='')
            print(' etc.')

            print('Samples:')
            iter_count = 0
            if num_app_ids_to_show is not None:
                selected_indices_to_display = indices[:num_app_ids_to_show]
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


def test_clustering(game_feature_dict, all_languages):
    game_feature_dict = remove_bugged_app_ids(game_feature_dict)

    game_feature_matrix = compute_game_feature_matrix(game_feature_dict, all_languages)

    normalized_game_feature_matrix = normalize_each_row(game_feature_matrix)

    app_ids = sorted(list(game_feature_dict.keys()))
    languages = sorted(list(all_languages))

    # Need to know the number of clusters we want in order to use K-means
    # test_kmeans_clustering(normalized_game_feature_matrix, appIDs, languages)

    # Need to specify the "preference" parameter in order to use Affinity Propagation
    test_affinity_propagation_clustering(normalized_game_feature_matrix, app_ids, languages)

    return


def compute_review_language_distribution(game_feature_dict, all_languages):
    # Compute the distribution of review languages among reviewers

    review_language_distribution = dict()

    for appID in game_feature_dict.keys():
        data_for_current_game = game_feature_dict[appID]

        num_reviews = sum([data_for_current_game[language]['voted'] for language in data_for_current_game.keys()])

        review_language_distribution[appID] = dict()
        review_language_distribution[appID]['num_reviews'] = num_reviews
        review_language_distribution[appID]['distribution'] = dict()
        for language in all_languages:
            try:
                review_language_distribution[appID]['distribution'][language] = data_for_current_game[language][
                                                                                    'voted'] / num_reviews
            except KeyError:
                review_language_distribution[appID]['distribution'][language] = 0

    return review_language_distribution


def print_prior(prior, all_languages=None):
    if all_languages is None:
        print(prior)
    else:
        for language in all_languages:
            print(language + ':', end='\t')
            print(prior[language])

    return


def choose_language_independent_prior_based_on_whole_steam_catalog(steam_spy_dict, all_languages, verbose=False):
    from compute_bayesian_rating import choose_prior

    # Construct observation structure used to compute a prior for the inference of a Bayesian rating
    observations = dict()
    for appid in steam_spy_dict.keys():
        num_positive_reviews = steam_spy_dict[appid]['positive']
        num_negative_reviews = steam_spy_dict[appid]['negative']

        num_votes = num_positive_reviews + num_negative_reviews

        if num_votes > 0:
            observations[appid] = dict()
            observations[appid]['num_votes'] = num_votes
            observations[appid]['score'] = num_positive_reviews / num_votes

    common_prior = choose_prior(observations)

    if verbose:
        print_prior(common_prior)

    # For each language, compute the prior to be used for the inference of a Bayesian rating

    language_independent_prior = dict()

    for language in all_languages:
        language_independent_prior[language] = common_prior

    return language_independent_prior


def choose_language_independent_prior_based_on_hidden_gems(game_feature_dict, all_languages, verbose=False):
    from compute_bayesian_rating import choose_prior

    # Construct observation structure used to compute a prior for the inference of a Bayesian rating
    observations = dict()
    for appid in game_feature_dict.keys():
        num_positive_reviews = 0
        num_negative_reviews = 0

        for language in all_languages:
            try:
                num_positive_reviews += game_feature_dict[appid][language]['voted_up']
                num_negative_reviews += game_feature_dict[appid][language]['voted_down']
            except KeyError:
                continue

        num_votes = num_positive_reviews + num_negative_reviews

        if num_votes > 0:
            observations[appid] = dict()
            observations[appid]['num_votes'] = num_votes
            observations[appid]['score'] = num_positive_reviews / num_votes

    common_prior = choose_prior(observations)

    if verbose:
        print_prior(common_prior)

    # For each language, compute the prior to be used for the inference of a Bayesian rating

    language_independent_prior = dict()

    for language in all_languages:
        language_independent_prior[language] = common_prior

    return language_independent_prior


def choose_language_specific_prior_based_on_hidden_gems(game_feature_dict, all_languages, verbose=False):
    from compute_bayesian_rating import choose_prior

    # For each language, compute the prior to be used for the inference of a Bayesian rating
    language_specific_prior = dict()
    for language in all_languages:

        # Construct observation structure used to compute a prior for the inference of a Bayesian rating
        observations = dict()
        for appid in game_feature_dict.keys():

            try:
                num_positive_reviews = game_feature_dict[appid][language]['voted_up']
                num_negative_reviews = game_feature_dict[appid][language]['voted_down']
            except KeyError:
                num_positive_reviews = 0
                num_negative_reviews = 0

            num_votes = num_positive_reviews + num_negative_reviews

            if num_votes > 0:
                observations[appid] = dict()
                observations[appid]['num_votes'] = num_votes
                observations[appid]['score'] = num_positive_reviews / num_votes

        language_specific_prior[language] = choose_prior(observations)

    if verbose:
        print_prior(language_specific_prior, all_languages)

    return language_specific_prior


def prepare_dictionary_for_ranking_of_hidden_gems(steam_spy_dict, game_feature_dict, all_languages,
                                                  compute_prior_on_whole_steam_catalog=True,
                                                  compute_language_specific_prior=False,
                                                  verbose=False,
                                                  quantile_for_our_own_wilson_score=0.95):
    # Prepare dictionary to feed to compute_stats module in hidden-gems repository

    from compute_wilson_score import compute_wilson_score
    from compute_bayesian_rating import compute_bayesian_score

    # noinspection PyPep8Naming
    D = dict()

    review_language_distribution = compute_review_language_distribution(game_feature_dict, all_languages)

    if compute_prior_on_whole_steam_catalog:

        whole_catalog_prior = choose_language_independent_prior_based_on_whole_steam_catalog(steam_spy_dict,
                                                                                             all_languages)

        print('Estimating prior (score and num_votes) on the whole Steam catalog (' + str(
            len(steam_spy_dict)) + ' games.')
        prior = whole_catalog_prior

    else:
        if compute_language_specific_prior:
            subset_catalog_prior = choose_language_specific_prior_based_on_hidden_gems(game_feature_dict, all_languages)
        else:
            subset_catalog_prior = choose_language_independent_prior_based_on_hidden_gems(game_feature_dict,
                                                                                          all_languages)

        print('Estimating prior (score and num_votes) on a pre-computed set of ' + str(
            len(game_feature_dict)) + ' hidden gems.')
        prior = subset_catalog_prior

    if verbose:
        print_prior(prior, all_languages)

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

            num_reviews = num_positive_reviews + num_negative_reviews

            wilson_score = compute_wilson_score(num_positive_reviews, num_negative_reviews,
                                                quantile_for_our_own_wilson_score)

            if wilson_score is None:
                wilson_score = -1

            if num_reviews > 0:
                # Construct game structure used to compute Bayesian rating
                game = dict()
                game['score'] = num_positive_reviews / num_reviews
                game['num_votes'] = num_reviews

                bayesian_rating = compute_bayesian_score(game, prior[language])
            else:
                bayesian_rating = -1

            # Assumption: for every game, players and reviews are distributed among regions in the same proportions.
            num_players = num_players_for_all_languages * review_language_distribution[appID]['distribution'][language]

            if num_players < num_reviews:
                print(
                    "[Warning] Abnormal data detected (" + str(int(num_players)) + " players ; " + str(
                        num_reviews) + " reviews) for language=" + language + " and appID=" + appID + ". Game skipped.")
                wilson_score = -1
                bayesian_rating = -1

            D[appID][language]['wilson_score'] = wilson_score
            D[appID][language]['bayesian_rating'] = bayesian_rating
            D[appID][language]['num_players'] = num_players
            D[appID][language]['num_reviews'] = num_reviews

    return D


def compute_regional_rankings_of_hidden_gems(game_feature_dict, all_languages,
                                             perform_optimization_at_runtime=True,
                                             num_top_games_to_print=1000,
                                             popularity_measure_str=None,
                                             quality_measure_str=None,
                                             compute_prior_on_whole_steam_catalog=True,
                                             compute_language_specific_prior=False,
                                             verbose=False):
    from download_json import get_todays_steam_spy_data
    from compute_stats import compute_ranking, save_ranking_to_file

    import pathlib

    # Output folder for regional rankings of hidden gems
    output_folder = 'regional_rankings/'
    # Reference of the following line: https://stackoverflow.com/a/14364249
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

    steam_spy_dict = get_todays_steam_spy_data()

    # noinspection PyPep8Naming
    D = prepare_dictionary_for_ranking_of_hidden_gems(steam_spy_dict, game_feature_dict, all_languages,
                                                      compute_prior_on_whole_steam_catalog,
                                                      compute_language_specific_prior,
                                                      verbose)

    for language in all_languages:
        output_filename = output_folder + "hidden_gems_" + language + ".md"

        ranking = compute_ranking(D, num_top_games_to_print, [], [], language, perform_optimization_at_runtime,
                                  popularity_measure_str,
                                  quality_measure_str)

        save_ranking_to_file(output_filename, ranking)

    return


def get_input_data(force_update_of_regional_stats=False):
    # If force_update_of_regional_stats is True, the TXT files below will be updated, which might take a lot of time
    # if the last update was done a long time ago. Otherwise, the TXT files will just be loaded as they are.

    dict_filename = "dict_review_languages.txt"
    language_filename = "list_all_languages.txt"
    previously_detected_languages_fname = "previously_detected_languages.txt"

    # In order to update stats regarding reviewers' languages, load_from_disk needs to be set to False.
    # Otherwise, game_feature_dict is loaded from the disk without being updated at all.
    load_from_disk = not force_update_of_regional_stats

    if load_from_disk:
        (game_feature_dict, all_languages) = load_game_features_as_review_language(dict_filename, language_filename)
    else:
        (game_feature_dict, all_languages) = get_game_features_as_review_language(dict_filename, language_filename,
                                                                                  previously_detected_languages_fname)

    return game_feature_dict, all_languages


def main():
    force_update_of_regional_stats = False
    (game_feature_dict, all_languages) = get_input_data(force_update_of_regional_stats)

    # test_clustering(game_feature_dict, all_languages)

    perform_optimization_at_runtime = True
    num_top_games_to_print = 250

    popularity_measure_str = 'num_players'  # Either 'num_players' or 'num_reviews'
    quality_measure_str = 'bayesian_rating'  # Either 'wilson_score' or 'bayesian_rating'

    # Whether to compute a prior for Bayesian rating with the whole Steam catalog,
    # or with a pre-computed set of top-ranked hidden gems
    compute_prior_on_whole_steam_catalog = False

    # Whether to compute a prior for Bayesian rating for each language independently
    compute_language_specific_prior = True
    # NB: This bool is only relevant if the prior is NOT based on the whole Steam catalog. Indeed, language-specific
    #     computation is impossible for the whole catalog since we don't have access to language data for every game.
    if compute_prior_on_whole_steam_catalog:
        assert (not compute_language_specific_prior)

    verbose = True

    compute_regional_rankings_of_hidden_gems(game_feature_dict, all_languages, perform_optimization_at_runtime,
                                             num_top_games_to_print,
                                             popularity_measure_str,
                                             quality_measure_str,
                                             compute_prior_on_whole_steam_catalog,
                                             compute_language_specific_prior,
                                             verbose)

    # Print the top 50 games of output_ranking for French speakers (mainly to check results with Github Travis)
    language = 'fr'
    file_path = 'regional_rankings/hidden_gems_' + language + '.md'
    num_lines_to_print = 50
    with open(file_path) as f:
        for i in range(num_lines_to_print):
            line = f.readline().strip()
            print(line)

    return True


if __name__ == "__main__":
    main()
