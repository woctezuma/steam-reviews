# Objective: rank games according to their hype (percentage of joke reviews among all reviews written in English).

def getNumReviews(review_dict):
    import numpy as np

    num_reviews = np.sum([ len(review_dict[keyword]) for keyword in review_dict.keys() ])

    return num_reviews

def getHype(joke_reviews_dict, acceptable_reviews_dict):

    num_reviews_acceptable_only = getNumReviews(acceptable_reviews_dict)
    num_reviews_joke_only = getNumReviews(joke_reviews_dict)

    num_reviews = num_reviews_acceptable_only + num_reviews_joke_only

    # Hype is the percentage of joke reviews among all reviews.
    # NB: There could be a small bias du to the fact that only reviews which are written in English are considered.
    if num_reviews>0:
        hype = num_reviews_joke_only / num_reviews
    else:
        hype = -1

    return hype

def getWilsonScoreDeviation(review_dict, acceptable_reviews_dict):
    from identify_joke_reviews import getDictionaryWilsonScore

    wilson_score_raw = getDictionaryWilsonScore(review_dict)
    wilson_score_acceptable_only = getDictionaryWilsonScore(acceptable_reviews_dict)

    try:
        wilson_score_deviation = wilson_score_raw - wilson_score_acceptable_only
    except TypeError:
        wilson_score_deviation = -1

    return wilson_score_deviation

def computeHypeAndWilsonScoreDeviation(appID, verbose = True):
    from identify_joke_reviews import getReviewSentimentDictionary, classifyReviews

    # Only reviews written in English are considered, for sentiment analysis to work.
    accepted_languages = ['english']

    accepted_languages_as_concatenated_str = ' '.join(l.capitalize() for l in accepted_languages)

    perform_language_detection_with_Google_Translate = False
    review_dict = getReviewSentimentDictionary(appID, accepted_languages, perform_language_detection_with_Google_Translate)

    (acceptable_reviews_dict, joke_reviews_dict) = classifyReviews(review_dict)

    num_reviews_acceptable_only = getNumReviews(acceptable_reviews_dict)
    num_reviews_joke_only = getNumReviews(joke_reviews_dict)

    num_reviews = num_reviews_acceptable_only + num_reviews_joke_only

    hype = getHype(joke_reviews_dict, acceptable_reviews_dict)

    wilson_score_deviation = getWilsonScoreDeviation(review_dict, acceptable_reviews_dict)

    sentence = 'Number of reviews in ' + accepted_languages_as_concatenated_str + ': {0} ({1} joke ; {2} acceptable)'
    print(sentence.format(num_reviews, num_reviews_joke_only, num_reviews_acceptable_only))

    sentence = 'Hype: {0:.3f} ; Wilson score deviation: {1:.3f}'
    print(sentence.format(hype, wilson_score_deviation))

    return (hype, wilson_score_deviation)

def printRankingAccordingToKeyword(hype_dict, keyword ='hype'):
    from download_json import getTodaysSteamSpyData

    # Download latest SteamSpy data to have access to the matching between appID and game name
    SteamSpyData = getTodaysSteamSpyData()

    hype_ranking = sorted(hype_dict.keys(), key=lambda x: hype_dict[x][keyword], reverse=True)

    formatted_keyword = keyword.capitalize().replace('_', ' ')

    print('\n' + formatted_keyword + ' ranking:')
    for (rank, appID) in enumerate(hype_ranking):
        try:
            appName = SteamSpyData[appID]['name']
        except KeyError:
            appName = 'unknown'
        sentence = '{0:3}. AppID: ' + appID + '\t' + formatted_keyword + ': {1:.3f}' + '\t(' + appName + ')'
        print( sentence.format(rank+1, hype_dict[appID][keyword]) )

    return

def main():
    with open('idlist.txt') as f:
        d = f.readlines()

    appID_list = [x.strip() for x in d]

    result_dict = dict()
    for appID in appID_list:
        (hype, wilson_score_deviation) = computeHypeAndWilsonScoreDeviation(appID)
        result_dict[appID] = dict()
        result_dict[appID]['hype'] = hype
        result_dict[appID]['wilson_score_deviation'] = wilson_score_deviation

    printRankingAccordingToKeyword(result_dict, 'hype')

    printRankingAccordingToKeyword(result_dict, 'wilson_score_deviation')

    return

if __name__ == "__main__":
    main()
