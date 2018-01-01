# Objective: rank games according to their hype (percentage of joke reviews among all reviews written in English).

def getNumReviews(review_dict):
    import numpy as np

    num_reviews = np.sum([ len(review_dict[keyword]) for keyword in review_dict.keys() ])

    return num_reviews

def getHype(appID, verbose = True):
    from identify_joke_reviews import getReviewSubjectivityDictionary, classifyReviews

    # Only reviews written in English are considered, for sentiment analysis to work.
    accepted_languages = ['english']

    # Threshold to distinguish between acceptable and joke reviews
    subjectivity_threshold = 0.36

    review_dict = getReviewSubjectivityDictionary(appID, accepted_languages)

    (acceptable_reviews_dict, joke_reviews_dict) = classifyReviews(review_dict, subjectivity_threshold)

    num_reviews_acceptable_only = getNumReviews(acceptable_reviews_dict)
    num_reviews_joke_only = getNumReviews(joke_reviews_dict)

    num_reviews = num_reviews_acceptable_only + num_reviews_joke_only

    # Hype is the percentage of joke reviews among all reviews.
    # NB: There could be a small bias du to the fact that only reviews which are written in English are considered.
    if num_reviews>0:
        hype = num_reviews_joke_only / num_reviews
    else:
        hype = -1

    if verbose:
        sentence = '\nAppID: ' + appID + '\tNumber of joke reviews: {0} ; Number of reviews: {1} ; Hype: {2:.3f}'
        print(sentence.format(num_reviews_joke_only, num_reviews, hype))

    return hype

def printHypeRanking(hype_dict):
    from download_json import getTodaysSteamSpyData

    # Download latest SteamSpy data to have access to the matching between appID and game name
    SteamSpyData = getTodaysSteamSpyData()

    hype_ranking = sorted(hype_dict.keys(), key=lambda x: hype_dict[x], reverse=True)

    print('\nHype ranking:')
    for (rank, appID) in enumerate(hype_ranking):
        try:
            appName = SteamSpyData[appID]['name']
        except KeyError:
            appName = 'unknown'
        sentence = '{0:3}. AppID: ' + appID + '\tHype: {1:.3f}' + '\t(' + appName + ')'
        print( sentence.format(rank, hype_dict[appID]) )

    return

def main():
    from download_reviews import previous_results

    hype_dict = dict()
    for appID_int in previous_results():
        appID = str(appID_int)
        hype_dict[appID] = getHype(appID)

    printHypeRanking(hype_dict)

    return

if __name__ == "__main__":
    main()
