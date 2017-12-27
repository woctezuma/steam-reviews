import json
import re
from textstat.textstat import textstat

def load_data(appID):

    # Data folder
    data_path = "data/"

    json_filename = "review_" + appID + ".json"

    data_filename = data_path + json_filename

    with open(data_filename, 'r', encoding="utf8") as in_json_file:
        data = json.load(in_json_file)

    return data

def analyze(appID):

    data = load_data(appID)

    query_summary = data['query_summary']

    sentence = 'Number of reviews: {0} ({1} up ; {2} down)'
    sentence = sentence.format(query_summary["total_reviews"], query_summary["total_positive"], query_summary["total_negative"])
    print(sentence)

    reviews = list(data['reviews'].values())

    sentence = 'Number of downloaded reviews: ' + str(len(reviews))
    print(sentence)

    review_example = reviews[0]

    review_stats = dict()

    ##

    # Meta-data regarding the reviewers
    review_stats['num_games_owned'] = []
    review_stats['num_reviews'] = []
    review_stats['playtime_forever'] = []

    # Meta-data regarding the reviews themselves
    review_stats['language'] = []
    review_stats['voted_up'] = []
    review_stats['votes_up'] = []
    review_stats['votes_funny'] = []
    review_stats['weighted_vote_score'] = []
    review_stats['comment_count'] = []
    review_stats['steam_purchase'] = []
    review_stats['received_for_free'] = []

    # Stats regarding the reviews themselves
    review_stats['character_count'] = []
    review_stats['syllable_count'] = []
    review_stats['lexicon_count'] = []
    review_stats['sentence_count'] = []
    review_stats['difficult_words_count'] = []
    review_stats['flesch_reading_ease'] = []
    review_stats['dale_chall_readability_score'] = []

    ##

    for review in reviews:
        review_content = review['review']

        # Meta-data regarding the reviewers
        review_stats['num_games_owned'].append(review['author']['num_games_owned'])
        review_stats['num_reviews'].append(review['author']['num_reviews'])
        review_stats['playtime_forever'].append(review['author']['playtime_forever'])

        # Meta-data regarding the reviews themselves
        review_stats['language'].append(review['language'])
        review_stats['voted_up'].append(review['voted_up'])
        review_stats['votes_up'].append(review['votes_up'])
        review_stats['votes_funny'].append(review['votes_funny'])
        review_stats['weighted_vote_score'].append(review['weighted_vote_score'])
        review_stats['comment_count'].append(review['comment_count'])
        review_stats['steam_purchase'].append(review['steam_purchase'])
        review_stats['received_for_free'].append(review['received_for_free'])

        # Stats regarding the reviews themselves
        review_stats['character_count'].append(len(review_content))
        review_stats['syllable_count'].append(textstat.syllable_count(review_content))
        review_stats['lexicon_count'].append(textstat.lexicon_count(review_content))
        review_stats['sentence_count'].append(textstat.sentence_count(review_content))
        review_stats['difficult_words_count'].append(textstat.difficult_words(review_content))
        try:
            review_stats['flesch_reading_ease'].append(textstat.flesch_reading_ease(review_content))
        except TypeError:
            review_stats['flesch_reading_ease'].append(None)
        review_stats['dale_chall_readability_score'].append(textstat.dale_chall_readability_score(review_content))

    return review_stats

def main():
    appID = "639780"

    review_stats = analyze(appID)

    print(review_stats)

    return

if __name__ == "__main__":
    main()
