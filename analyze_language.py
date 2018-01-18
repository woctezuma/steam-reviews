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

    game_feature_dict = dict()
    all_languages = set()

    for appID in appID_list:
        summary_dict = getReviewLanguageSummary(appID)

        game_feature_dict[appID] = summary_dict
        all_languages = all_languages.union(summary_dict.keys())

    all_languages = sorted(list(all_languages))

    return (game_feature_dict, all_languages)

def getAllLanguages(language_filename = "list_all_languages.txt"):
    # Obtained by running getAllReviewLanguageSummaries() on the top 250 hidden gems.

    # Import the list of languages from a text file
    with open(language_filename, 'r', encoding="utf8") as infile:
        lines = infile.readlines()
        # The list is on the first line
        all_languages = eval(lines[0])

    print('List of languages loaded from disk.')

    return all_languages

def getGameFeaturesAsReviewLanguage(dict_filename ="dict_review_languages.txt",
                                    language_filename ="list_all_languages.txt"):
    # Obtained by running getAllReviewLanguageSummaries() on the top 250 hidden gems.

    try:

        # Import the dictionary of game features from a text file
        with open(dict_filename, 'r', encoding="utf8") as infile:
            lines = infile.readlines()
            # The dictionary is on the first line
            game_feature_dict = eval(lines[0])

            print('Dictionary of language features loaded from disk.')

    except FileNotFoundError:

        print('Computing dictonary of language features from scratch.')

        max_num_appID = None
        (game_feature_dict, all_languages) = getAllReviewLanguageSummaries(max_num_appID)

        # Export the dictionary of game features to a text file
        with open(dict_filename, 'w', encoding="utf8") as outfile:
            print(game_feature_dict, file=outfile)

        print('Dictionary of language features written to disk.')

        # Export the list of languages to a text file
        with open(language_filename, 'w', encoding="utf8") as outfile:
            print(all_languages, file=outfile)

        print('List of languages written to disk.')

    return game_feature_dict

def main():
    dict_filename = "dict_review_languages.txt"
    language_filename = "list_all_languages.txt"

    game_feature_dict = getGameFeaturesAsReviewLanguage(dict_filename, language_filename)
    all_languages = getAllLanguages(language_filename)

    return

if __name__ == "__main__":
    main()
