from langdetect import detect, DetectorFactory, lang_detect_exception

from describe_reviews import loadData, describeData, getReviewContent

import iso639

def getReviewLanguageDictionary(appID):
    # Returns dictionary: reviewID -> dictionary with (tagged language, detected language)

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

def summarizeReviewLanguageDictionary(language_dict):
    # Returns dictionary: language -> number of reviews for which tagged language coincides with detected language

    summary_dict = dict()

    languages = set([r['tag'] for r in language_dict.values() ])

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
                print([r['detected'] for r in language_dict.values() if r['tag'] == language])
                continue

        summary_dict[language_iso] = sum([1 for r in language_dict.values() if r['detected'] == language_iso])

    return summary_dict

def getReviewLanguageSummary(appID):

    language_dict = getReviewLanguageDictionary(appID)

    summary_dict = summarizeReviewLanguageDictionary(language_dict)

    return summary_dict

def getAllReviewLanguageSummaries(max_num_appID = None):

    with open('idlist.txt') as f:
        d = f.readlines()

    appID_list = [x.strip() for x in d]

    if max_num_appID is not None:
        max_num_appID = min(max_num_appID, len(appID_list))
        appID_list = appID_list[0: max_num_appID]

    result_dict = dict()
    all_languages = set()

    for appID in appID_list:
        summary_dict = getReviewLanguageSummary(appID)

        result_dict[appID] = summary_dict
        all_languages = all_languages.union(summary_dict.keys())

    all_languages = sorted(list(all_languages))

    return (result_dict, all_languages)

def main():
    max_num_appID = None

    (result_dict, all_languages) = getAllReviewLanguageSummaries(max_num_appID)

    print(result_dict)

    print(all_languages)

    return

if __name__ == "__main__":
    main()
