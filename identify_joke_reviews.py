import sys, getopt

from textblob import TextBlob, exceptions
from langdetect import detect, DetectorFactory, lang_detect_exception

from compute_wilson_score import computeWilsonScore
from describe_reviews import loadData, describeData, getReviewContent
from cluster_reviews import printSentimentAnalysis

def detectLanguage(review_content, blob = None, call_Google_Translate = False):

    try:

        if call_Google_Translate:
            # More accurate but requires an active Internet connection, and might result in a slow down of the process.

            if blob is None:
                blob = TextBlob(review_content)
            detected_language = blob.detect_language()

        else:
            # It is up to the user to decide (trade-off accuracy vs. slower running time + Internet requirement).

            DetectorFactory.seed = 0
            detected_language = detect(review_content)

    except exceptions.TranslatorError:
        # This exception can be raised by 'textblob'.
        # The error is typically: TranslatorError('Must provide a string with at least 3 characters.')
        # Since the review is very short, it is likely a joke review, so we won't dismiss it from our study.
        # Example of such a review: http://steamcommunity.com/profiles/76561198169555911/recommended/723090/
        detected_language = 'en'
    except lang_detect_exception.LangDetectException:
        # This exception can be raised by 'langdetect'.
        detected_language = 'en'

    return detected_language

def getReviewSentimentDictionary(appID, accepted_languages = ['english'],
                                 perform_language_detection_with_Google_Tool = False,
                                 verbose_reviews_wrongly_tagged_as_written_in_English = False):
    # A light version of aggregateReviews() from describe_reviews.py
    # NB: Only reviews marked on Steam as being written in English are accepted for sentiment analysis to work properly.

    review_data = loadData(appID)

    print('\nAppID: ' + appID)

    (query_summary, reviews) = describeData(review_data)

    count_reviews_wrongly_tagged_as_written_in_English = 0

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

            # Check language with a tool by Google to detect reviews WRONGLY tagged as English
            if perform_language_detection_with_Google_Tool:
                detected_language = detectLanguage(review_content, blob)
            else:
                detected_language = 'en'

            # Hard-coded check for English language
            accepted_languages_iso = ['en']
            # TODO For generality, one would need to match accepted_languages to accepted_languages_iso (ISO 639-1)
            # cf. https://en.wikipedia.org/wiki/ISO_639-1
            # cf. https://gist.github.com/carlopires/1262033
            if not(detected_language in accepted_languages_iso):
                count_reviews_wrongly_tagged_as_written_in_English += 1
                if verbose_reviews_wrongly_tagged_as_written_in_English:
                    print('\nReview #' + str(count_reviews_wrongly_tagged_as_written_in_English)
                          + ' detected as being written in ' + detected_language + ' instead of English:')
                    print(review_content + '\n')
                continue

            if is_positive_review:
                keyword = 'positive'
            else:
                keyword = 'negative'

            review_dict[keyword][reviewID] = dict()
            review_dict[keyword][reviewID]['polarity'] = blob.sentiment.polarity
            review_dict[keyword][reviewID]['subjectivity'] = blob.sentiment.subjectivity

    sentence = 'Number of reviews wrongly tagged as written in English: {0}\n'
    print(sentence.format(count_reviews_wrongly_tagged_as_written_in_English))

    return review_dict

def classifyReviews(review_dict, sentiment_threshold = None, verbose = False):

    # The variable sentiment_threshold is a Python dictionary, which describes the criterion to distinguish between
    # acceptable and joke reviews, based on Sentiment Analysis.
    if (sentiment_threshold is None) or bool(len(sentiment_threshold) == 0):
        sentiment_threshold = {'polarity': [-0.2, 0.2], 'subjectivity': [0.36, 1]}

    # NB: If thresholds for polarity and subjectivity are set to the following values,
    #     then the classification cannot be performed, i.e. every review is marked as ACCEPTABLE.
    # - polarity threshold:     [-1, 1] to avoid using a criterion based on polarity (and therefore solely rely on subjectivity)
    # - subjectivity threshold: [ 0, 1] to avoid using a criterion based on subjectivity (and therefore solely rely on polarity)

    acceptable_reviews_dict = dict()
    joke_reviews_dict = dict()

    for keyword in ['positive', 'negative']:
        current_reviewIDs = review_dict[keyword].keys()

        # Polarity set used with OR: joke reviews necessarily have a polarity INSIDE the interval!
        acceptable_reviewIDs_wrt_polarity = [ reviewID for reviewID in current_reviewIDs
                                 if bool(review_dict[keyword][reviewID]['polarity'] < sentiment_threshold['polarity'][0]
                                      or review_dict[keyword][reviewID]['polarity'] > sentiment_threshold['polarity'][1]) ]

        # Subjectivity interval used with AND: joke reviews necessarily have a subjectivity OUTSIDE the interval!
        acceptable_reviewIDs_wrt_subjectivity = [ reviewID for reviewID in current_reviewIDs
                                 if bool(review_dict[keyword][reviewID]['subjectivity'] >= sentiment_threshold['subjectivity'][0]
                                     and review_dict[keyword][reviewID]['subjectivity'] <= sentiment_threshold['subjectivity'][1]) ]

        acceptable_reviewIDs = set(acceptable_reviewIDs_wrt_polarity).union(set(acceptable_reviewIDs_wrt_subjectivity))

        acceptable_reviews_dict[keyword] = acceptable_reviewIDs
        joke_reviews_dict[keyword] = current_reviewIDs - acceptable_reviewIDs

    if verbose:
        print('A review is acceptable if it is acceptable with respect to either polarity or subjectivity.')
        print('Set for being acceptable w.r.t. polarity: [-1.00, {0:.2f}[ U ]{1:.2f}, 1.00]'.format(sentiment_threshold['polarity'][0],
                                                                                                    sentiment_threshold['polarity'][1]))
        print('Interval for being acceptable w.r.t. subjectivity: [{0:.2f}, {1:.2f}]'.format(sentiment_threshold['subjectivity'][0],
                                                                                             sentiment_threshold['subjectivity'][1]))

    return (acceptable_reviews_dict, joke_reviews_dict)

def getDictionaryWilsonScore(review_dict, verbose = False):

    num_pos = len(review_dict['positive'])
    num_neg = len(review_dict['negative'])
    wilson_score = computeWilsonScore(num_pos, num_neg)

    if verbose:
        num_reviews = num_pos+num_neg
        if num_reviews>0:
            sentence = 'Number of reviews: {0} ({1} up ; {2} down) ; Wilson score: {3:.2f}'
            print(sentence.format(num_reviews, num_pos, num_neg, wilson_score))
        else:
            sentence = 'Number of reviews: {0}'
            print(sentence.format(num_reviews))

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
    perform_language_detection_with_Google_Tool = True
    review_dict = getReviewSentimentDictionary(appID, accepted_languages, perform_language_detection_with_Google_Tool)

    sentiment_verbose = True
    (acceptable_reviews_dict, joke_reviews_dict) = classifyReviews(review_dict, None, sentiment_verbose)

    print_Wilson_score = True

    print('\nStats for all reviews available in ' + ' '.join([l.capitalize() for l in accepted_languages]))
    wilson_score_raw = getDictionaryWilsonScore(review_dict, print_Wilson_score)

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
