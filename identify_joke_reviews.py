import sys, getopt

from textblob import TextBlob

from compute_wilson_score import computeWilsonScore
from describe_reviews import loadData, describeData, getReviewContent
from cluster_reviews import printSentimentAnalysis

def getReviewSubjectivityDictionary(appID, accepted_languages = ['english']):
    # A light version of aggregateReviews() from describe_reviews.py
    # NB: Only reviews marked on Steam as being written in English are accepted for sentiment analysis to work properly.

    review_data = loadData(appID)

    print('\nAppID: ' + appID)

    (query_summary, reviews) = describeData(review_data)

    review_dict = dict()
    review_dict['positive'] = dict()
    review_dict['negative'] = dict()

    for review in reviews:
        if review['language'] in accepted_languages:
            # Review ID
            reviewID = review["recommendationid"]

            # Whether the review is marked on Steam as positive
            is_positive_review = bool(review['voted_up'])

            # Review text
            review_content = review['review']

            # Sentiment analysis
            blob = TextBlob(review_content)

            if is_positive_review:
                keyword = 'positive'
            else:
                keyword = 'negative'

            review_dict[keyword][reviewID] = blob.sentiment.subjectivity

    return review_dict

def classifyReviews(review_dict, subjectivity_threshold = 0.36):

    acceptable_reviews_dict = dict()
    joke_reviews_dict = dict()

    for keyword in ['positive', 'negative']:
        current_reviewIDs = review_dict[keyword].keys()

        acceptable_reviewIDs = [ reviewID for reviewID in current_reviewIDs
                                 if review_dict[keyword][reviewID] >= subjectivity_threshold ]

        acceptable_reviews_dict[keyword] = acceptable_reviewIDs
        joke_reviews_dict[keyword] = current_reviewIDs - acceptable_reviewIDs

    return (acceptable_reviews_dict, joke_reviews_dict)

def getDictionaryWilsonScore(review_dict, verbose = False):

    num_pos = len(review_dict['positive'])
    num_neg = len(review_dict['negative'])
    wilson_score = computeWilsonScore(num_pos, num_neg)

    if verbose:
        sentence = 'Number of reviews: {0} ({1} up ; {2} down) ; Wilson score: {3:.2f}'
        print(sentence.format(num_pos+num_neg, num_pos, num_neg, wilson_score))

    return wilson_score

def showReviews(appID, reviewID_list, max_num_reviews_to_print = None):
    # Adapted from showFixedNumberOfReviewsFromGivenCluster() in cluster_reviews.py

    for (review_count, reviewID) in enumerate(reviewID_list):
        review_content = getReviewContent(appID, reviewID)

        if (max_num_reviews_to_print is not None) and (review_count >= max_num_reviews_to_print):
            break

        # Reference: https://stackoverflow.com/a/18544440
        print("\n ==== Review " + str(review_count+1) + " (#reviews = " + str(len(reviewID_list)) + ") ====" )
        printSentimentAnalysis(review_content)

        try:
            print(review_content)
        except UnicodeEncodeError:
            # Reference: https://stackoverflow.com/a/3224300
            print(review_content.encode('ascii', 'ignore'))

    return

def main(argv):
    appID_list = ["723090", "639780", "573170"]

    if len(argv) == 0:
        appID = appID_list[-1]
        print("No input detected. AppID automatically set to " + appID)
    else:
        appID = argv[0]
        print("Input appID detected as " + appID)

    accepted_languages = ['english']
    review_dict = getReviewSubjectivityDictionary(appID, accepted_languages)

    subjectivity_threshold = 0.36
    (acceptable_reviews_dict, joke_reviews_dict) = classifyReviews(review_dict, subjectivity_threshold)

    print_Wilson_score = True

    print('\nStats for all reviews available in ' + ' '.join([l.capitalize() for l in accepted_languages]))
    wilson_score_raw = getDictionaryWilsonScore(review_dict, print_Wilson_score)

    print('\nThreshold for subjectivity: {0:.2f}'.format(subjectivity_threshold))

    max_num_reviews_to_print = 5

    for keyword in ['positive', 'negative']:
        reviewID_list = acceptable_reviews_dict[keyword]
        if len(reviewID_list) > 0:
            print('\n\t[ ========================================== ]')
            print('\t[ ====== Acceptable ' + keyword + ' reviews ======= ]')
            showReviews(appID, reviewID_list, max_num_reviews_to_print)

    for keyword in ['positive', 'negative']:
        reviewID_list = joke_reviews_dict[keyword]
        if len(reviewID_list) > 0:
            print('\n\t[ ==================================== ]')
            print('\t[ ====== Joke ' + keyword + ' reviews ======= ]')
            showReviews(appID, reviewID_list, max_num_reviews_to_print)

    print('\n\t[ ==================================== ]')

    print('\nStats for all acceptable reviews (subjectivity >= threshold)')
    wilson_score_acceptable_only = getDictionaryWilsonScore(acceptable_reviews_dict, print_Wilson_score)

    print('\nStats for detected joke reviews (subjectivity < threshold)')
    wilson_score_joke_only = getDictionaryWilsonScore(joke_reviews_dict, print_Wilson_score)

    wilson_score_deviation = wilson_score_raw - wilson_score_acceptable_only
    print('\nConclusion: estimated deviation of Wilson score due to joke reviews: {0:.2f}'.format(wilson_score_deviation))

    return

if __name__ == "__main__":
    main(sys.argv[1:])
