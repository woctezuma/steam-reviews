# Objective: compute a score for each Steam game and then rank all the games while favoring hidden gems.

from appids import appidContradiction


def compute_score_generic(my_tuple, parameter_list, chosen_language=None,
                          popularity_measure_as_str=None,
                          quality_measure_as_str=None):
    # Objective: compute a score for one Steam game.
    #
    # Input:    - a my_tuple is a list consisting of all retrieved information regarding one game
    #           - parameter_list is a list of parameters to calibrate the output_ranking.
    #             Currently, there is only one parameter, alpha, which could be chosen up to one's tastes, or optimized.
    #           - optional language to allow to compute regional rankings of hidden gems. cf. steam-reviews repository
    # Output:   game score

    alpha = parameter_list[0]

    if chosen_language is None:

        # noinspection PyUnusedLocal
        game_name = my_tuple[0]
        wilson_score = my_tuple[1]
        bayesian_rating = my_tuple[2]
        num_owners = my_tuple[3]
        num_players = my_tuple[4]
        median_playtime = my_tuple[5]
        average_playtime = my_tuple[6]
        num_positive_reviews = my_tuple[7]
        num_negative_reviews = my_tuple[8]

        # noinspection PyUnusedLocal
        bool_game_should_appear_in_ranking = my_tuple[-1]

        # noinspection PyUnusedLocal
        num_owners = float(num_owners)
        num_players = float(num_players)
        # noinspection PyUnusedLocal
        median_playtime = float(median_playtime)
        # noinspection PyUnusedLocal
        average_playtime = float(average_playtime)
        num_positive_reviews = float(num_positive_reviews)
        num_negative_reviews = float(num_negative_reviews)

        num_reviews = num_positive_reviews + num_negative_reviews

    else:

        wilson_score = my_tuple[chosen_language]['wilson_score']
        bayesian_rating = my_tuple[chosen_language]['bayesian_rating']
        num_players = my_tuple[chosen_language]['num_players']
        num_reviews = my_tuple[chosen_language]['num_reviews']

    if quality_measure_as_str is None or quality_measure_as_str == 'wilson_score':
        quality_measure = wilson_score
    else:
        quality_measure = bayesian_rating

    if popularity_measure_as_str is None or popularity_measure_as_str == 'num_players':
        popularity_measure = num_players
    else:
        popularity_measure = num_reviews

    # Decreasing function
    def decreasing_fun(x):
        return alpha / (alpha + x)

    score = quality_measure * decreasing_fun(popularity_measure)

    return score


# noinspection PyPep8Naming
def rank_games(dictionary_d, parameter_list, is_verbose=False, appid_reference_set={appidContradiction},
               chosen_language=None,
               popularity_measure_as_str=None,
               quality_measure_as_str=None,
               num_top_games_to_display=1000, filtered_app_ids_to_show=set(), filtered_app_ids_to_hide=set()):
    # Objective: rank all the Steam games, given a parameter alpha.
    #
    # Input:    - local dictionary of data extracted from SteamSpy
    #           - parameter_list is a list of parameters to calibrate the output_ranking.
    #           - optional verbosity boolean
    #           - optional set of appID of games chosen as references of hidden gems. By default, only "Contradiction".
    #           - optional language to allow to compute regional rankings of hidden gems. cf. steam-reviews repository
    #           - optional choice of popularity measure: either 'num_players' or 'num_reviews'
    #           - optional number of top games to print if the output_ranking is only partially displayed
    #             By default, only the top 1000 games are displayed.
    #             If set to None, the output_ranking will be fully displayed.
    #           - optional set of appID of games to show (and only these games are shown).
    #             Typically used to focus on appIDs for specific genres or tags.
    #             If None, the behavior is unintuitive yet exceptional: every game is shown, appIDs are not filtered-in.
    #           - optional set of appID of games to hide.
    #             Typically used to exclude appIDs for specific genres or tags.
    #             If None, the behavior is intuitive: no game is specifically hidden, appIDs are not filtered-out.
    # Output:   a 2-tuple consisting of:
    #           - a scalar value summarizing ranks of games used as references of "hidden gems"
    #           - the output_ranking to be ultimately displayed. A list of 3-tuple: (rank, game_name, appid).
    #             If is_verbose was set to None, the returned output_ranking is empty.

    import numpy as np

    # Boolean to decide whether printing the ranking of the top 1000 games, rather than the ranking of the whole Steam
    # catalog. It makes the script finish faster, and usually, we are only interested in the top games anyway.
    print_subset_of_top_games = bool(not (num_top_games_to_display is None))

    # Boolean to decide whether there is a filtering-in of appIDs (typically to filter-in genres or tags).
    print_filtered_app_ids_only = bool(not (filtered_app_ids_to_show is None)
                                       and not (len(filtered_app_ids_to_show) == 0))

    # Boolean to decide whether there is a filtering-out of appIDs (typically to filter-out genres or tags).
    hide_filtered_app_ids_only = bool(not (filtered_app_ids_to_hide is None)
                                      and not (len(filtered_app_ids_to_hide) == 0))

    def compute_score(x):
        return compute_score_generic(x, parameter_list, chosen_language,
                                     popularity_measure_as_str, quality_measure_as_str)

    # Rank all the Steam games
    sorted_values = sorted(dictionary_d.values(), key=compute_score, reverse=True)

    if chosen_language is None:
        name_index = 0
    else:
        name_index = 'name'

    sorted_game_names = list(map(lambda x: x[name_index], sorted_values))

    reference_dict = {}
    for appid_reference in appid_reference_set:
        try:
            # Find the rank of this game used as a reference of a "hidden gem"
            name_game_ref_for_hidden_gem = dictionary_d[appid_reference][name_index]
            rank_game_used_as_reference_for_hidden_gem = sorted_game_names.index(name_game_ref_for_hidden_gem) + 1

            # Find whether the reference game should appear in the output_ranking (it might not due to tag filters)
            if chosen_language is None:
                bool_reference_game_should_appear_in_ranking = dictionary_d[appid_reference][-1]
            else:
                bool_reference_game_should_appear_in_ranking = True

            reference_dict[appid_reference] = [rank_game_used_as_reference_for_hidden_gem,
                                               bool_reference_game_should_appear_in_ranking]
        except KeyError:
            continue

    ranks_of_reference_hidden_gems = [v[0] for k, v in reference_dict.items()]

    def summarizing_function(x):
        return np.average(x)

    scalar_summarizing_ranks_of_reference_hidden_gems = summarizing_function(ranks_of_reference_hidden_gems)

    # Save the output_ranking for later display
    ranking_list = []
    if is_verbose:
        print('Objective function to minimize:\t', scalar_summarizing_ranks_of_reference_hidden_gems)

        # Populate the variable ranking_list
        num_games_to_print = len(sorted_game_names)
        if print_subset_of_top_games:
            num_games_to_print = min(num_top_games_to_display, num_games_to_print)

        for appid_reference in reference_dict.keys():
            rank_game_used_as_reference_for_hidden_gem = reference_dict[appid_reference][0]
            bool_reference_game_should_appear_in_ranking = reference_dict[appid_reference][1]
            if (not bool_reference_game_should_appear_in_ranking) and bool(
                    rank_game_used_as_reference_for_hidden_gem <= num_games_to_print):
                num_games_to_print += 1

        # Check
        num_games_to_print = min(len(sorted_game_names), num_games_to_print)

        rank_decrease = 0

        for i in range(num_games_to_print):
            game_name = sorted_game_names[i]
            appid = [k for k, v in dictionary_d.items() if v[name_index] == game_name][0]

            current_rank = i + 1

            if appid in reference_dict.keys():
                rank_game_used_as_reference_for_hidden_gem = reference_dict[appid][0]
                bool_reference_game_should_appear_in_ranking = reference_dict[appid][1]
                if not bool_reference_game_should_appear_in_ranking:
                    assert (current_rank == rank_game_used_as_reference_for_hidden_gem)
                    rank_decrease += 1
                    continue

            current_rank -= rank_decrease

            if not print_filtered_app_ids_only or bool(appid in filtered_app_ids_to_show):
                if not hide_filtered_app_ids_only or bool(not (appid in filtered_app_ids_to_hide)):
                    # Append the output_ranking info
                    ranking_list.append([current_rank, game_name, appid])

    return scalar_summarizing_ranks_of_reference_hidden_gems, ranking_list


# noinspection PyPep8Naming
def optimize_for_alpha(dictionary_d, is_verbose=True, appid_reference_set={appidContradiction},
                       chosen_language=None,
                       popularity_measure_as_str=None,
                       quality_measure_as_str=None,
                       lower_search_bound=1,  # minimal possible value of alpha is 1 people
                       upper_search_bound=pow(10, 8)  # maximal possible value of alpha is 8 billion people
                       ):
    # Objective: find the optimal value of the parameter alpha
    #
    # Input:    - local dictionary of data extracted from SteamSpy
    #           - optional verbosity boolean
    #           - optional set of appID of games chosen as references of hidden gems. By default, only "Contradiction".
    #           - optional language to allow to compute regional rankings of hidden gems. cf. steam-reviews repository
    #           - optional choice of popularity measure: either 'num_players' or 'num_reviews'
    #           - optional lower bound for the optimization procedure of the parameter alpha
    #           - optional upper bound for the optimization procedure of the parameter alpha
    # Output:   list of optimal parameters (by default, only one parameter is optimized: alpha)

    from math import log10
    from scipy.optimize import differential_evolution

    # Goal: find the optimal value for alpha by minimizing the rank of games chosen as references of "hidden gems"
    def function_to_minimize(x):
        return rank_games(dictionary_d, [x], False, appid_reference_set, chosen_language,
                          popularity_measure_as_str, quality_measure_as_str)[0]

    # Bounds for the optimization procedure of the parameter alpha
    my_bounds = [(lower_search_bound, upper_search_bound)]

    res = differential_evolution(function_to_minimize, bounds=my_bounds)

    if len(res.x) == 1:
        optimal_parameters = [res.x]
    else:
        optimal_parameters = res.x
        if is_verbose:
            print(optimal_parameters)

    if is_verbose:
        # Quick print in order to check that the upper search bound is not too close to our optimal alpha
        # Otherwise, it could indicate the search has been biased by a poor choice of the upper search bound.
        alpha_optim = optimal_parameters[0]
        print("alpha = 10^%.2f" % log10(alpha_optim))

    return optimal_parameters


def save_ranking_to_file(out_filename, ranking_list, only_display_appid=False, is_verbose=False, width=40):
    # Save the output_ranking to the output text file

    base_steam_store_url = "http://store.steampowered.com/app/"

    with open(out_filename, 'w', encoding="utf8") as outfile:
        for current_ranking_info in ranking_list:
            current_rank = current_ranking_info[0]
            game_name = current_ranking_info[1]
            appid = current_ranking_info[-1]

            store_url = base_steam_store_url + appid
            store_url_fixed_width = f'{store_url: <{width}}'

            if only_display_appid:
                print(appid, file=outfile)
                if is_verbose:
                    print(appid)
            else:
                sentence = '{:05}'.format(current_rank) + ".\t[" + game_name + "](" + store_url_fixed_width + ")"
                print(sentence, file=outfile)
                if is_verbose:
                    print(sentence)


# noinspection PyPep8Naming
def compute_ranking(dictionary_d, num_top_games_to_display=None, included_keywords=list(), excluded_keywords=list(),
                    chosen_language=None,
                    perform_optimization_during_runtime=True,
                    popularity_measure_as_str=None,
                    quality_measure_as_str=None):
    # Objective: compute a output_ranking of hidden gems
    #
    # Input:    - local dictionary of data extracted from SteamSpy
    #           - maximal length of the output_ranking
    #               The higher the value, the longer it takes to compute and print the output_ranking.
    #               If set to None, there is no limit, so the whole Steam catalog is ranked.
    #           - tags to filter-in
    #               Warning because unintuitive: to avoid filtering-in, please use an empty list.
    #           - tags to filter-out
    #           - optional language to allow to compute regional rankings of hidden gems. cf. steam-reviews repository
    #           - bool to decide whether to optimize alpha at run-time, or to rely on a hard-coded value instead
    #           - optional choice of popularity measure: either 'num_players' or 'num_reviews'
    #
    # Output:   output_ranking of hidden gems

    from appids import appid_hidden_gems_reference_set
    from download_json import get_appid_by_keyword_list_to_include, get_appid_by_keyword_list_to_exclude

    if perform_optimization_during_runtime:
        if chosen_language is None:
            index_num_players = 4
            index_num_positive_reviews = 7
            index_num_negative_reviews = 8

            if popularity_measure_as_str is None or popularity_measure_as_str == 'num_players':
                vec = [int(game[index_num_players]) for game in dictionary_d.values()]
            else:
                assert (popularity_measure_as_str == 'num_reviews')

                def get_num_reviews(game):
                    return int(game[index_num_positive_reviews]) + int(game[index_num_negative_reviews])

                vec = [get_num_reviews(game) for game in dictionary_d.values()]

        else:
            vec = [game[chosen_language][popularity_measure_as_str] for game in dictionary_d.values()]

        lower_search_bound = 1 + max(vec)
        optimal_parameters = optimize_for_alpha(dictionary_d, True, appid_hidden_gems_reference_set, chosen_language,
                                                popularity_measure_as_str, quality_measure_as_str, lower_search_bound)
    else:
        if popularity_measure_as_str is None or popularity_measure_as_str == 'num_players':
            if quality_measure_as_str is None or quality_measure_as_str == 'wilson_score':
                # Optimal parameter as computed on December 18, 2017
                optimal_parameters = [pow(10, 6.40)]
            else:
                assert (quality_measure_as_str == 'bayesian_rating')
                # Optimal parameter as computed on March 22, 2018
                optimal_parameters = [pow(10, 6.47)]
        else:
            assert (popularity_measure_as_str == 'num_reviews')
            if quality_measure_as_str is None or quality_measure_as_str == 'wilson_score':
                # Optimal parameter as computed on February 22, 2018
                optimal_parameters = [pow(10, 4.65)]
            else:
                assert (quality_measure_as_str == 'bayesian_rating')
                # Optimal parameter as computed on March 22, 2018
                optimal_parameters = [pow(10, 4.75)]

    # Filter-in games which meta-data includes ALL the following keywords
    # Caveat: the more keywords, the fewer games are filtered-in! cf. intersection of sets in the code
    filtered_in_app_ids = get_appid_by_keyword_list_to_include(included_keywords)

    # Filter-out games which meta-data includes ANY of the following keywords
    # NB: the more keywords, the more games are excluded. cf. union of sets in the code
    filtered_out_app_ids = get_appid_by_keyword_list_to_exclude(excluded_keywords)

    (objective_function, ranking) = rank_games(dictionary_d, optimal_parameters, True, appid_hidden_gems_reference_set,
                                               chosen_language,
                                               popularity_measure_as_str,
                                               quality_measure_as_str,
                                               num_top_games_to_display, filtered_in_app_ids, filtered_out_app_ids)

    return ranking


if __name__ == "__main__":
    # A local dictionary was stored in the following text file
    input_filename = "dict_top_rated_games_on_steam.txt"

    # A output_ranking, in a format parsable by Github Gist, will be stored in the following text file
    output_filename = "hidden_gems.md"

    # A output_ranking, as a list of appids, will be stored in the following text file
    output_filename_only_appids = "idlist.txt"

    # Import the local dictionary from the input file
    with open(input_filename, 'r', encoding="utf8") as infile:
        lines = infile.readlines()
        # The dictionary is on the second line
        D = eval(lines[1])

    # Maximal length of the output_ranking. The higher the value, the longer it takes to compute and print the ranking.
    # If set to None, there is no limit, so the whole Steam catalog is ranked.
    num_top_games_to_print = 1000

    # Filtering-in
    # Warning because unintuitive: to avoid filtering-in, please use an empty list!
    keywords_to_include = []  # ["Rogue-Like"]

    # Filtering-out
    keywords_to_exclude = []  # ["Visual Novel", "Anime"]

    language = None
    perform_optimization_at_runtime = True
    popularity_measure_str = 'num_players'  # Either 'num_players' or 'num_reviews'
    quality_measure_str = 'wilson_score'  # Either 'wilson_score' or 'bayesian_rating'

    output_ranking = compute_ranking(D, num_top_games_to_print, keywords_to_include, keywords_to_exclude,
                                     language, perform_optimization_at_runtime,
                                     popularity_measure_str, quality_measure_str)

    # If set to True, print to current display (useful with Travis integration on Github)
    verbose = True

    only_show_appid = False
    save_ranking_to_file(output_filename, output_ranking, only_show_appid, verbose)

    only_show_appid = True
    save_ranking_to_file(output_filename_only_appids, output_ranking, only_show_appid)
