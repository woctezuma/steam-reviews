import sys

from langdetect import detect, DetectorFactory, lang_detect_exception
from textblob import TextBlob, exceptions

from cluster_reviews import print_sentiment_analysis
from compute_wilson_score import compute_wilson_score
from describe_reviews import load_data, describe_data, get_review_content


def detect_language(review_content, blob=None, call_google_translate=False):
    try:

        if call_google_translate:
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


def get_review_sentiment_dictionary(app_id, accepted_languages=None,
                                    perform_language_detection_with_google_tool=False,
                                    verbose_reviews_wrongly_tagged_as_written_in_english=False):
    # A light version of aggregate_reviews() from describe_reviews.py
    # NB: Only reviews marked on Steam as being written in English are accepted for sentiment analysis to work properly.

    if accepted_languages is None:
        accepted_languages = ['english']
    review_data = load_data(app_id)

    print('\nAppID: ' + app_id)

    (query_summary, reviews) = describe_data(review_data)

    wrongly_tagged_review_id = []
    count_reviews_wrongly_tagged_as_written_in_english = 0
    count_reviews_tagged_as_written_in_english = 0

    review_dict = dict()
    review_dict['positive'] = dict()
    review_dict['negative'] = dict()

    for review in reviews:
        if review['language'] in accepted_languages:
            # Review ID
            review_id = review["recommendationid"]

            # Whether the review is marked on Steam as positive
            is_positive_review = bool(review['voted_up'])

            # Review text
            review_content = review['review']

            count_reviews_tagged_as_written_in_english += 1

            # Sentiment analysis
            blob = TextBlob(review_content)

            # Check language with a tool by Google to detect reviews WRONGLY tagged as English
            if perform_language_detection_with_google_tool:
                detected_language = detect_language(review_content, blob)
            else:
                detected_language = 'en'

            # Hard-coded check for English language
            accepted_languages_iso = ['en']
            # TODO For generality, one would need to match accepted_languages to accepted_languages_iso (ISO 639-1)
            # cf. https://en.wikipedia.org/wiki/ISO_639-1
            # cf. https://gist.github.com/carlopires/1262033
            if not (detected_language in accepted_languages_iso):
                count_reviews_wrongly_tagged_as_written_in_english += 1
                wrongly_tagged_review_id.append(review_id)
                if verbose_reviews_wrongly_tagged_as_written_in_english:
                    print('\nReview #' + str(count_reviews_wrongly_tagged_as_written_in_english)
                          + ' detected as being written in ' + detected_language + ' instead of English:')
                    print(review_content + '\n')
                continue

            if is_positive_review:
                keyword = 'positive'
            else:
                keyword = 'negative'

            review_dict[keyword][review_id] = dict()
            review_dict[keyword][review_id]['polarity'] = blob.sentiment.polarity
            review_dict[keyword][review_id]['subjectivity'] = blob.sentiment.subjectivity

    review_dict['language_tag'] = dict()
    review_dict['language_tag']['reviews_wrongly_tagged_English'] = wrongly_tagged_review_id
    review_dict['language_tag'][
        'num_reviews_wrongly_tagged_English'] = count_reviews_wrongly_tagged_as_written_in_english
    review_dict['language_tag']['num_reviews_tagged_English'] = count_reviews_tagged_as_written_in_english
    review_dict['language_tag']['num_reviews'] = len(reviews)

    # Mostly display

    try:
        percentage_reviews_tagged_as_written_in_english = review_dict['language_tag']['num_reviews_tagged_English'] / \
                                                          review_dict['language_tag']['num_reviews']
        end_of_sentence = ' Percentage of English tags: {0:.2f}'.format(percentage_reviews_tagged_as_written_in_english)
    except ZeroDivisionError:
        percentage_reviews_tagged_as_written_in_english = -1
        end_of_sentence = ''

    review_dict['language_tag']['prct_English_tags'] = percentage_reviews_tagged_as_written_in_english

    sentence = 'Number of reviews: {0} ({1} with English tag ; {2} with another language tag).'
    print(sentence.format(review_dict['language_tag']['num_reviews'],
                          review_dict['language_tag']['num_reviews_tagged_English'],
                          review_dict['language_tag']['num_reviews'] - review_dict['language_tag'][
                              'num_reviews_tagged_English'])
          + end_of_sentence)

    # Mostly display

    # noinspection PyPep8
    num_confirmed_english_tags = review_dict['language_tag']['num_reviews_tagged_English'] - \
                                 review_dict['language_tag']['num_reviews_wrongly_tagged_English']

    try:
        percentage_confirmed_english_tags = num_confirmed_english_tags / review_dict['language_tag'][
            'num_reviews_tagged_English']
        end_of_sentence = ' Percentage of confirmed English tags: {0:.2f}\n'.format(percentage_confirmed_english_tags)
    except ZeroDivisionError:
        percentage_confirmed_english_tags = -1
        end_of_sentence = '\n'

    review_dict['language_tag']['prct_confirmed_English_tags_among_English_tags'] = percentage_confirmed_english_tags
    # noinspection PyPep8
    review_dict['language_tag']['prct_confirmed_English_tags_among_all_tags'] = max(0,
                                                                                    percentage_confirmed_english_tags) * \
                                                                                max(0,
                                                                                    percentage_reviews_tagged_as_written_in_english)

    accepted_languages_as_concatenated_str = ' '.join(l.capitalize() for l in accepted_languages)
    sentence = 'Number of reviews tagged as in ' + accepted_languages_as_concatenated_str + \
               ': {0} ({1} with dubious tag ; {2} with tag confirmed by language detection).'
    print(sentence.format(review_dict['language_tag']['num_reviews_tagged_English'],
                          review_dict['language_tag']['num_reviews_wrongly_tagged_English'],
                          num_confirmed_english_tags)
          + end_of_sentence)

    return review_dict


def classify_reviews(review_dict, sentiment_threshold=None, verbose=False):
    # The variable sentiment_threshold is a Python dictionary, which describes the criterion to distinguish between
    # acceptable and joke reviews, based on Sentiment Analysis.
    if (sentiment_threshold is None) or bool(len(sentiment_threshold) == 0):
        sentiment_threshold = {'polarity': [-0.2, 0.2], 'subjectivity': [0.36, 1]}

    # NB: If thresholds for polarity and subjectivity are set to the following values,
    #     then the classification cannot be performed, i.e. every review is marked as ACCEPTABLE.
    # - polarity threshold:     [-1, 1] to avoid any polarity-based criterion (therefore solely rely on subjectivity)
    # - subjectivity threshold: [ 0, 1] to avoid any subjectivity-based criterion (therefore solely rely on polarity)

    acceptable_reviews_dict = dict()
    joke_reviews_dict = dict()

    for keyword in ['positive', 'negative']:
        current_review_ids = review_dict[keyword].keys()

        # Polarity set used with OR: joke reviews necessarily have a polarity INSIDE the interval!
        # noinspection PyPep8
        acceptable_review_ids_wrt_polarity = [reviewID for reviewID in current_review_ids
                                              if bool(
                review_dict[keyword][reviewID]['polarity'] < sentiment_threshold['polarity'][0]
                or review_dict[keyword][reviewID]['polarity'] > sentiment_threshold['polarity'][1])]

        # Subjectivity interval used with AND: joke reviews necessarily have a subjectivity OUTSIDE the interval!
        # noinspection PyPep8,PyPep8
        acceptable_review_ids_wrt_subjectivity = [reviewID for reviewID in current_review_ids
                                                  if bool(
                sentiment_threshold['subjectivity'][0] <= review_dict[keyword][reviewID]['subjectivity'] <=
                sentiment_threshold['subjectivity'][1])]

        acceptable_review_ids = set(acceptable_review_ids_wrt_polarity).union(
            set(acceptable_review_ids_wrt_subjectivity))

        acceptable_reviews_dict[keyword] = acceptable_review_ids
        joke_reviews_dict[keyword] = current_review_ids - acceptable_review_ids

    if verbose:
        print('A review is acceptable if it is acceptable with respect to either polarity or subjectivity.')
        print('Set for being acceptable w.r.t. polarity: [-1.00, {0:.2f}[ U ]{1:.2f}, 1.00]'.format(
            sentiment_threshold['polarity'][0],
            sentiment_threshold['polarity'][1]))
        print('Interval for being acceptable w.r.t. subjectivity: [{0:.2f}, {1:.2f}]'.format(
            sentiment_threshold['subjectivity'][0],
            sentiment_threshold['subjectivity'][1]))

    return acceptable_reviews_dict, joke_reviews_dict


def get_dictionary_wilson_score(review_dict, verbose=False):
    num_pos = len(review_dict['positive'])
    num_neg = len(review_dict['negative'])
    wilson_score = compute_wilson_score(num_pos, num_neg)

    if verbose:
        num_reviews = num_pos + num_neg
        if num_reviews > 0:
            sentence = 'Number of reviews: {0} ({1} up ; {2} down) ; Wilson score: {3:.2f}'
            print(sentence.format(num_reviews, num_pos, num_neg, wilson_score))
        else:
            sentence = 'Number of reviews: {0}'
            print(sentence.format(num_reviews))

    return wilson_score


def show_reviews(app_id, review_id_list, max_num_reviews_to_print=None):
    # Adapted from show_fixed_number_of_reviews_from_given_cluster() in cluster_reviews.py

    for (review_count, reviewID) in enumerate(review_id_list):
        review_content = get_review_content(app_id, reviewID)

        if (max_num_reviews_to_print is not None) and (review_count >= max_num_reviews_to_print):
            break

        # Reference: https://stackoverflow.com/a/18544440
        print("\n ==== Review " + str(review_count + 1) + " (#reviews = " + str(len(review_id_list)) + ") ====")
        print_sentiment_analysis(review_content)

        try:
            print(review_content)
        except UnicodeEncodeError:
            # Reference: https://stackoverflow.com/a/3224300
            print(review_content.encode('ascii', 'ignore'))

    return


def main(argv):
    app_id_list = ["723090", "639780", "573170"]

    if len(argv) == 0:
        app_id = app_id_list[-1]
        print("No input detected. AppID automatically set to " + app_id)
    else:
        app_id = argv[0]
        print("Input appID detected as " + app_id)

    accepted_languages = ['english']
    perform_language_detection_with_google_tool = True
    verbose_reviews_wrongly_tagged_as_written_in_english = True
    review_dict = get_review_sentiment_dictionary(app_id, accepted_languages,
                                                  perform_language_detection_with_google_tool,
                                                  verbose_reviews_wrongly_tagged_as_written_in_english)

    sentiment_verbose = True
    # noinspection PyTypeChecker
    (acceptable_reviews_dict, joke_reviews_dict) = classify_reviews(review_dict,
                                                                    sentiment_threshold=None,
                                                                    verbose=sentiment_verbose)

    print_wilson_score = True

    print('\nStats for all reviews available in ' + ' '.join([l.capitalize() for l in accepted_languages]))
    wilson_score_raw = get_dictionary_wilson_score(review_dict, print_wilson_score)

    max_num_reviews_to_print = 5

    for keyword in ['positive', 'negative']:
        review_id_list = acceptable_reviews_dict[keyword]
        if len(review_id_list) > 0:
            print('\n\t[ ========================================== ]')
            print('\t[ ====== Acceptable ' + keyword + ' reviews ======= ]')
            show_reviews(app_id, review_id_list, max_num_reviews_to_print)

    for keyword in ['positive', 'negative']:
        review_id_list = joke_reviews_dict[keyword]
        if len(review_id_list) > 0:
            print('\n\t[ ==================================== ]')
            print('\t[ ====== Joke ' + keyword + ' reviews ======= ]')
            show_reviews(app_id, review_id_list, max_num_reviews_to_print)

    print('\n\t[ ==================================== ]')

    print('\nStats for all acceptable reviews (subjectivity >= threshold)')
    wilson_score_acceptable_only = get_dictionary_wilson_score(acceptable_reviews_dict, print_wilson_score)

    print('\nStats for detected joke reviews (subjectivity < threshold)')
    # noinspection PyUnusedLocal
    _ = get_dictionary_wilson_score(joke_reviews_dict, print_wilson_score)

    wilson_score_deviation = wilson_score_raw - wilson_score_acceptable_only
    print(
        '\nConclusion: estimated deviation of Wilson score due to joke reviews: {0:.2f}'.format(wilson_score_deviation))

    return True


if __name__ == "__main__":
    main(sys.argv[1:])
