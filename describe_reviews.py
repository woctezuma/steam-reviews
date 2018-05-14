import json
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from textblob import TextBlob
from textstat.textstat import textstat

sns.set(color_codes=True)

np.random.seed(sum(map(ord, "distributions")))


def load_data(app_id):
    # Data folder
    data_path = "data/"

    json_filename = "review_" + app_id + ".json"

    data_filename = data_path + json_filename

    with open(data_filename, 'r', encoding="utf8") as in_json_file:
        review_data = json.load(in_json_file)

    return review_data


def describe_data(review_data):
    try:
        query_summary = review_data['query_summary']

        sentence = 'Number of reviews: {0} ({1} up ; {2} down)'
        sentence = sentence.format(query_summary["total_reviews"], query_summary["total_positive"],
                                   query_summary["total_negative"])
    except KeyError:
        query_summary = None

        sentence = 'Query summary cannot be found in the JSON file.'

    print(sentence)

    reviews = list(review_data['reviews'].values())

    sentence = 'Number of downloaded reviews: ' + str(len(reviews))
    print(sentence)

    return query_summary, reviews


def aggregate_reviews(app_id):
    review_data = load_data(app_id)

    (query_summary, reviews) = describe_data(review_data)

    review_stats = dict()

    ##

    # Review ID
    review_stats['recommendationid'] = []

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

    # Sentiment analysis
    review_stats['polarity'] = []
    review_stats['subjectivity'] = []

    ##

    for review in reviews:
        review_content = review['review']

        # Review ID
        review_stats['recommendationid'].append(review["recommendationid"])

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

        # Sentiment analysis
        blob = TextBlob(review_content)
        review_stats['polarity'].append(blob.sentiment.polarity)
        review_stats['subjectivity'].append(blob.sentiment.subjectivity)

    return review_stats


def aggregate_reviews_to_pandas(app_id):
    review_stats = aggregate_reviews(app_id)

    df = pd.DataFrame(data=review_stats)

    # Correction for an inconsistency which I discovered when running df.mean(). These 2 columns did not appear in the
    # output of mean(). I don't think it has any real impact for clustering and other purposes, but just to be sure...
    if "comment_count" in df.columns:
        df["comment_count"] = df["comment_count"].astype('int')
    if "weighted_vote_score" in df.columns:
        df["weighted_vote_score"] = df["weighted_vote_score"].astype('float')

    return df


def find_top_languages_by_review_number(df, num_top_languages=3, verbose=True):
    # Extract a dataframe for reviews written in top languages (by review numbers)

    sorted_languages = df["language"].value_counts().index.tolist()

    top_languages = sorted_languages[0:num_top_languages]

    if verbose:
        print(top_languages)
        print(df["language"].describe())

    return top_languages


def extract_reviews_for_top_languages_only(df, top_languages, verbose=True):
    # Extract a dataframe for reviews written in top languages (by review numbers)

    s = pd.Series([lang in top_languages for lang in df["language"]], name='language')
    df_extracted = df[s.values]

    if verbose:
        print(df_extracted.groupby("language").mean())

    return df_extracted


def plot_univariate_distribution(data_frame, str_x="votes_up"):
    # Reference: https://seaborn.pydata.org/tutorial/distributions.html

    sns.distplot(data_frame[str_x], kde=False, fit=stats.lognorm)
    plt.show()

    return


def plot_box_plot(data_frame, str_x="language", str_y="votes_up"):
    # Reference: https://seaborn.pydata.org/examples/grouped_boxplot.html

    sns.boxplot(x=str_x, y=str_y, data=data_frame, palette="PRGn")
    plt.show()

    # NB: Discriminating between positive and negative reviews (with "voted_up") is not super useful in our case,
    # since we will only consider games with mostly positive reviews.

    return


def analyze_app_id(app_id, languages_to_extract=None, create_separate_plots=True):
    df = aggregate_reviews_to_pandas(app_id)

    num_top_languages = 3
    if languages_to_extract is None:
        top_languages = find_top_languages_by_review_number(df, num_top_languages)
    else:
        top_languages = languages_to_extract

    df_extracted = extract_reviews_for_top_languages_only(df, top_languages)

    # All the possible variables are listed here:
    variables = df_extracted.keys()
    print(variables)

    if create_separate_plots:
        variable_to_plot = "lexicon_count"
        plot_univariate_distribution(df_extracted, variable_to_plot)

        if num_top_languages > 1:
            plot_box_plot(df_extracted, "language", variable_to_plot)

    return df_extracted


def analyze_app_id_in_english(app_id):
    df = analyze_app_id(app_id, ['english'], False)
    return df


def get_review_content(app_id, review_id):
    data = load_data(app_id)

    reviews = list(data['reviews'].values())

    review_content = "-1"

    for review in reviews:
        if review['recommendationid'] == review_id:
            review_content = review['review']
            break

    return review_content


def plot_overlays_of_univariate_distribution(app_id_list, variable_to_plot="lexicon_count", languages_to_extract=None):
    # By definition, we want to overlay plots with this function, hence the following variable is set to False:
    if languages_to_extract is None:
        languages_to_extract = ['english']
    create_separate_plots = False

    current_palette = sns.color_palette(n_colors=len(app_id_list))

    for (iter_count, appID) in enumerate(app_id_list):
        print(appID)

        df = analyze_app_id(appID, languages_to_extract, create_separate_plots)

        sns.distplot(df[variable_to_plot], kde=False, fit=stats.beta,
                     color=current_palette[iter_count],
                     label=appID,
                     fit_kws={"label": appID + " fit", "color": current_palette[iter_count], "alpha": 0.25})

    plt.legend()
    plt.show()

    return


def main(argv):
    app_id_list = ["723090", "639780", "573170"]

    if len(argv) == 0:
        app_id = app_id_list[-1]
        print("No input detected. AppID automatically set to " + app_id)
        compare_app_ids_in_default_list = True
    else:
        app_id = argv[0]
        print("Input appID detected as " + app_id)
        compare_app_ids_in_default_list = False

    # Analyze one appID

    analyze_app_id(app_id)

    # Compare different appIDs

    if compare_app_ids_in_default_list:
        plot_overlays_of_univariate_distribution(app_id_list)

    return


if __name__ == "__main__":
    main(sys.argv[1:])
