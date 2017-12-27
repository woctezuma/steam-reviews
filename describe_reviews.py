import json
from textstat.textstat import textstat

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

import seaborn as sns
sns.set(color_codes=True)

np.random.seed(sum(map(ord, "distributions")))

def loadData(appID):

    # Data folder
    data_path = "data/"

    json_filename = "review_" + appID + ".json"

    data_filename = data_path + json_filename

    with open(data_filename, 'r', encoding="utf8") as in_json_file:
        data = json.load(in_json_file)

    return data

def aggregateReviews(appID):

    data = loadData(appID)

    query_summary = data['query_summary']

    sentence = 'Number of reviews: {0} ({1} up ; {2} down)'
    sentence = sentence.format(query_summary["total_reviews"], query_summary["total_positive"], query_summary["total_negative"])
    print(sentence)

    reviews = list(data['reviews'].values())

    sentence = 'Number of downloaded reviews: ' + str(len(reviews))
    print(sentence)

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

    return review_stats

def aggregateReviewsToPandas(appID):

    review_stats = aggregateReviews(appID)

    df = pd.DataFrame(data=review_stats)

    return df

def findTopLanguagesByReviewNumber(df, num_top_languages = 3, verbose = True):
    # Extract a dataframe for reviews written in top languages (by review numbers)

    sorted_languages = df["language"].value_counts().index.tolist()

    top_languages = sorted_languages[0:num_top_languages]

    if verbose:
        print(top_languages)
        print(df["language"].describe())

    return top_languages

def extractReviewsForTopLanguagesOnly(df, top_languages, verbose = True):

    # Extract a dataframe for reviews written in top languages (by review numbers)

    s = pd.Series([lang in top_languages for lang in df["language"]], name='language')
    df_extracted = df[s.values]

    if verbose:
        print(df_extracted.groupby("language").mean())

    return df_extracted

def plotUnivariateDistribution(data_frame, strX = "votes_up"):
    # Reference: https://seaborn.pydata.org/tutorial/distributions.html

    sns.distplot(data_frame[strX], kde=False, fit=stats.lognorm)
    plt.show()

    return

def plotBoxPlot(data_frame, strX ="language", strY ="votes_up"):
    # Reference: https://seaborn.pydata.org/examples/grouped_boxplot.html

    sns.boxplot(x = strX, y = strY, data= data_frame, palette="PRGn")
    plt.show()

    # NB: Discriminating between positive and negative reviews (with "voted_up") is not super useful in our case,
    # since we will only consider games with mostly positive reviews.

    return

def analyzeAppID(appID, languages_to_extract = None, create_separate_plots = True):

    df = aggregateReviewsToPandas(appID)

    num_top_languages = 3
    if languages_to_extract is None:
        top_languages = findTopLanguagesByReviewNumber(df, num_top_languages)
    else:
        top_languages = languages_to_extract

    df_extracted = extractReviewsForTopLanguagesOnly(df, top_languages)

    # All the possible variables are listed here:
    variables = df_extracted.keys()
    print( variables )

    if create_separate_plots:
        variable_to_plot = "lexicon_count"
        plotUnivariateDistribution(df_extracted, variable_to_plot)

        if num_top_languages > 1:
            plotBoxPlot(df_extracted, "language", variable_to_plot)

    return df_extracted

def analyzeAppIDinEnglish(appID):
    df = analyzeAppID(appID, ['english'], False)
    return df

def getReviewContent(appID, reviewID):
    data = loadData(appID)

    reviews = list(data['reviews'].values())

    review_content = "-1"

    for review in reviews:
        print(review['recommendationid'])
        if review['recommendationid'] == reviewID:
            review_content = review['review']
            break

    return review_content

def plotOverlaysOfUnivariateDistribution(appID_list, variable_to_plot = "lexicon_count", languages_to_extract = ['english']):
    # By definition, we want to overlay plots with this function, hence the following variable is set to False:
    create_separate_plots = False

    current_palette = sns.color_palette(n_colors=len(appID_list))

    for (iter_count, appID) in enumerate(appID_list):
        print(appID)

        df = analyzeAppID(appID, languages_to_extract, create_separate_plots)

        sns.distplot(df[variable_to_plot], kde=False, fit=stats.beta,
                     color = current_palette[iter_count],
                     label=appID,
                     fit_kws={"label": appID+" fit", "color": current_palette[iter_count], "alpha": 0.25})

    plt.legend()
    plt.show()

    return

def main():
    appID_list = ["723090", "639780", "573170"]

    # Analyze one appID

    appID = appID_list[-1]
    analyzeAppID(appID)

    # Compare different appIDs

    plotOverlaysOfUnivariateDistribution(appID_list)

    return

if __name__ == "__main__":
    main()
