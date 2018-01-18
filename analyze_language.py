import sys

from langdetect import detect, DetectorFactory, lang_detect_exception

from describe_reviews import loadData, describeData, getReviewContent

def getReviewLanguageDictionary(appID):

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

def main(argv):
    appID_list = ["723090", "639780", "573170"]

    if len(argv) == 0:
        appID = appID_list[-1]
        print("No input detected. AppID automatically set to " + appID)
    else:
        appID = argv[0]
        print("Input appID detected as " + appID)

    language_dict = getReviewLanguageDictionary(appID)

    #TODO

    print(language_dict)

    return

if __name__ == "__main__":
    main(sys.argv[1:])
