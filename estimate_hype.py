# Objective: rank games according to their hype (percentage of joke reviews among all reviews written in English).

import steamspypi


def get_num_reviews(review_dict):
    import numpy as np

    num_reviews = np.sum([len(review_dict[keyword]) for keyword in review_dict.keys()])

    return num_reviews


def get_hype(joke_reviews_dict, acceptable_reviews_dict):
    num_reviews_acceptable_only = get_num_reviews(acceptable_reviews_dict)
    num_reviews_joke_only = get_num_reviews(joke_reviews_dict)

    num_reviews = num_reviews_acceptable_only + num_reviews_joke_only

    # Hype is the percentage of joke reviews among all reviews.
    # NB: There could be a small bias du to the fact that only reviews which are written in English are considered.
    if num_reviews > 0:
        hype = num_reviews_joke_only / num_reviews
    else:
        hype = -1

    return hype


def get_wilson_score_deviation(review_dict, acceptable_reviews_dict):
    from identify_joke_reviews import get_dictionary_wilson_score

    wilson_score_raw = get_dictionary_wilson_score(review_dict)
    wilson_score_acceptable_only = get_dictionary_wilson_score(acceptable_reviews_dict)

    try:
        wilson_score_deviation = wilson_score_raw - wilson_score_acceptable_only
    except TypeError:
        wilson_score_deviation = -1

    return wilson_score_deviation


def compute_hype_and_wilson_score_deviation(app_id):
    from identify_joke_reviews import get_review_sentiment_dictionary, classify_reviews

    # Only reviews written in English are considered, for sentiment analysis to work.
    accepted_languages = ['english']

    accepted_languages_as_concatenated_str = ' '.join(l.capitalize() for l in accepted_languages)

    perform_language_detection_with_google_tool = True
    verbose_reviews_wrongly_tagged_as_written_in_english = False
    review_dict = get_review_sentiment_dictionary(app_id, accepted_languages,
                                                  perform_language_detection_with_google_tool,
                                                  verbose_reviews_wrongly_tagged_as_written_in_english)

    prct_english_tags = review_dict['language_tag']['prct_English_tags']
    prct_confirmed_english_tags_among_all_tags = review_dict['language_tag'][
        'prct_confirmed_English_tags_among_all_tags']

    (acceptable_reviews_dict, joke_reviews_dict) = classify_reviews(review_dict)

    num_reviews_acceptable_only = get_num_reviews(acceptable_reviews_dict)
    num_reviews_joke_only = get_num_reviews(joke_reviews_dict)

    num_reviews = num_reviews_acceptable_only + num_reviews_joke_only

    hype = get_hype(joke_reviews_dict, acceptable_reviews_dict)

    wilson_score_deviation = get_wilson_score_deviation(review_dict, acceptable_reviews_dict)

    sentence = 'Number of reviews in ' + accepted_languages_as_concatenated_str + ': {0} ({1} joke ; {2} acceptable)'
    print(sentence.format(num_reviews, num_reviews_joke_only, num_reviews_acceptable_only))

    sentence = 'Hype: {0:.3f} ; Wilson score deviation: {1:.3f}'
    print(sentence.format(hype, wilson_score_deviation))

    return hype, wilson_score_deviation, prct_english_tags, prct_confirmed_english_tags_among_all_tags


def print_ranking_according_to_keyword(hype_dict, keyword='hype'):
    # Download latest SteamSpy data to have access to the matching between appID and game name
    steam_spy_data = steamspypi.load()

    hype_ranking = sorted(hype_dict.keys(), key=lambda x: hype_dict[x][keyword], reverse=True)

    formatted_keyword = keyword.capitalize().replace('_', ' ')

    print('\n' + formatted_keyword + ' output_ranking:')
    for (rank, appID) in enumerate(hype_ranking):
        try:
            app_name = steam_spy_data[appID]['name']
        except KeyError:
            app_name = 'unknown'
        sentence = '{0:3}. AppID: ' + appID + '\t' + formatted_keyword + ': {1:.3f}' + '\t(' + app_name + ')'
        print(sentence.format(rank + 1, hype_dict[appID][keyword]))

    return


def main():
    with open('idlist.txt') as f:
        d = f.readlines()

    app_id_list = [x.strip() for x in d]

    result_dict = dict()
    for appID in app_id_list:
        (hype, wilson_score_deviation, prct_English_tags,
         prct_confirmed_English_tags_among_all_tags) = compute_hype_and_wilson_score_deviation(appID)
        result_dict[appID] = dict()
        result_dict[appID]['hype'] = hype
        result_dict[appID]['wilson_score_deviation'] = wilson_score_deviation
        result_dict[appID]['proportion_English-tags'] = prct_English_tags
        result_dict[appID]['proportion_confirmed-English-tags'] = prct_confirmed_English_tags_among_all_tags

    print_ranking_according_to_keyword(result_dict, 'hype')

    print_ranking_according_to_keyword(result_dict, 'wilson_score_deviation')

    print_ranking_according_to_keyword(result_dict, 'proportion_English-tags')

    print_ranking_according_to_keyword(result_dict, 'proportion_confirmed-English-tags')

    return True


if __name__ == "__main__":
    main()
