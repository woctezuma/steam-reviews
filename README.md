# Steam Reviews

This repository contains Python code to compute statistics of Steam reviews.

### Definitions

A "joke review" is a review which does not try to express the reviewer's opinion. Typically, a joke review is a funny reference to the game's themes or characters.

"Hype" is the percentage of joke reviews for a given game.

## Goal

The goal is to filter Steam reviews in order to find out:

* which game has the highest percentage of joke reviews,
* which game benefits the most from joke reviews in terms of Wilson score,
* which game has the highest percentage of English reviews.

## Data source

Data can be downloaded from SteamSpy API and Steam API. It is also available as a snapshot in [a data repository](https://github.com/woctezuma/steam-reviews-data).

### Limitations

The analysis of Steam reviews requires to download data through Steam API, which has a rate limit of about 10 reviews per second.

Sentiment analysis is performed on reviews written in English. The language is available with Steam's meta-data, but it is not always accurate because it requires the reviewers to correctly specify their language at the time the review is published. To try to be as robust as possible against mistagging, the language of each review is confirmed by [a tool running locally](https://github.com/Mimino666/langdetect), which used to be provided by Google. The limitation of this tool is that there are occasional false negatives (reviews which are written in English, but only consist of 3-5 words, with typos, so the algorithm might not recognize the English language). If you are looking for a better accuracy, at the expense of a slower running time and numerous pings to Google Translate, you could directly use the language detection function provided by [TextBlob](https://github.com/sloria/TextBlob).

## Usage

If you are running Windows, you could call the main functions using the `steamReviews.bat` script.

The main functions are structured as follows:
* `download_reviews.py` allows to download reviews via Steam API,
* `identify_joke_reviews.py` allows to focus on a single game, and classify its reviews as acceptable vs. joke,
* `estimate_hype.py` allows to rank games according to their hype (percentage of joke reviews), Wilson score bonus (due to hype), or percentage of Steam reviews in English (as given by Steam's meta-data and confirmed by Google Translate),

Additional functions are called from:
* `download_json.py` is a utility copied from [my hidden-gems repository](https://github.com/woctezuma/hidden-gems),
* `compute_wilson_score.py` is a utility copied from [my hidden-gems repository](https://github.com/woctezuma/hidden-gems),
* `describe_reviews.py` allows to compute text properties, and then aggregate meta-data and review features,
* `cluster_reviews.py` attempts to divide reviews into clusters.

## Results as of January 18, 2018

[A list of 250 hidden gems](https://github.com/woctezuma/steam-reviews/blob/master/hidden_gems.md) has been processed. Here is an excerpt of the input:

00001.	[Short Stories Collection of Class Tangerine](http://store.steampowered.com/app/701930)
00002.	[BLUE REVOLVER](http://store.steampowered.com/app/439490)
00003.	[planetarian HD](http://store.steampowered.com/app/623080)
00004.	[  Hidden Star in Four Seasons.](http://store.steampowered.com/app/745880)
00005.	[Tayutama2 -you're the only one- CHI ver.](http://store.steampowered.com/app/552280)
00006.	[DUSK](http://store.steampowered.com/app/519860)
00007.	[Muv-Luv Alternative](http://store.steampowered.com/app/449840)
00008.	[Paint it Back](http://store.steampowered.com/app/385250)
00009.	[Linelight](http://store.steampowered.com/app/469790)
00010.	[Monolith](http://store.steampowered.com/app/603960)

Here are the results as [output](https://raw.githubusercontent.com/woctezuma/steam-reviews/master/output/output_rankings.md) by `estimate_hype.py`.

Unexpectedly, Deep Space Waifu and Meltys Quest do not benefit that much from joke reviews: without the joke reviews, the Wilson score is more or less the same (respectively 0.4% and 1.1% lower).

### Ranking by hype

A hype of 0.300 means that 30.0% of the reviews are classified as joke reviews.

  0. AppID: 623080	Hype: 0.300	(planetarian HD)
  1. AppID: 410830	Hype: 0.281	(ARENA GODS)
  2. AppID: 502800	Hype: 0.270	(SENRAN KAGURA ESTIVAL VERSUS)
  3. AppID: 283960	Hype: 0.264	(Pajama Sam: No Need to Hide When It's Dark Outside)
  4. AppID: 733990	Hype: 0.247	(I Can't Believe It's Not Gambling)
  5. AppID: 745880	Hype: 0.246	(  Hidden Star in Four Seasons.)
  6. AppID: 639790	Hype: 0.239	(DEEP SPACE WAIFU)
  7. AppID: 294530	Hype: 0.238	(Freddi Fish 2: The Case of the Haunted Schoolhouse)
  8. AppID: 260750	Hype: 0.237	(Neighbours from Hell Compilation)
  9. AppID: 689580	Hype: 0.225	(TurnSignal)
 10. AppID: 723090	Hype: 0.213	(Meltys Quest)
 11. AppID: 407310	Hype: 0.213	(NEKO-NIN exHeart)
 12. AppID: 664180	Hype: 0.211	(Draw Puzzle)
 13. AppID: 441050	Hype: 0.209	(Polandball: Can into Space!)
 14. AppID: 658560	Hype: 0.200	(Zup! 7)
 15. AppID: 357330	Hype: 0.200	(Space Beast Terror Fright)
 16. AppID: 448370	Hype: 0.199	(IS Defense)
 17. AppID: 639780	Hype: 0.193	(deep space waifu: FLAT JUSTICE VERSION)
 18. AppID: 472870	Hype: 0.185	(Higurashi When They Cry Hou - Ch.3 Tatarigoroshi)
 19. AppID: 658620	Hype: 0.183	(Wonderful Everyday Down the Rabbit-Hole)
 20. AppID: 426690	Hype: 0.178	(Narcissu 10th Anniversary Anthology Project)

### Ranking by Wilson score bonus due to unexpectedly positive hype

A Wilson score bonus (or deviation) of 0.077 means that the game's Wilson score (95% confidence) is improved by 7.7% thanks to the joke reviews.

  0. AppID: 623080	Wilson score deviation: 0.077	(planetarian HD)
  1. AppID: 357330	Wilson score deviation: 0.075	(Space Beast Terror Fright)
  2. AppID: 410830	Wilson score deviation: 0.036	(ARENA GODS)
  3. AppID: 664180	Wilson score deviation: 0.036	(Draw Puzzle)
  4. AppID: 368570	Wilson score deviation: 0.034	(Beat Da Beat)
  5. AppID: 588040	Wilson score deviation: 0.033	(WILL: A Wonderful World / WILL)
  6. AppID: 496350	Wilson score deviation: 0.028	(Supipara - Chapter 1 Spring Has Come!)
  7. AppID: 658620	Wilson score deviation: 0.025	(Wonderful Everyday Down the Rabbit-Hole)
  8. AppID: 689580	Wilson score deviation: 0.023	(TurnSignal)
  9. AppID: 745850	Wilson score deviation: 0.022	(KARAKARA2)
 10. AppID: 640380	Wilson score deviation: 0.014	(UBERMOSH Vol.5)
 11. AppID: 427700	Wilson score deviation: 0.014	(Zwei: The Ilvard Insurrection)
 12. AppID: 370280	Wilson score deviation: 0.014	(Season of 12 Colors)
 13. AppID: 534290	Wilson score deviation: 0.013	(Cursed Castilla (Maldita Castilla EX))
 14. AppID: 462990	Wilson score deviation: 0.013	(Tomoyo After ~It's a Wonderful Life~ English Edition)
 15. AppID: 348430	Wilson score deviation: 0.013	(Quell Reflect)
 16. AppID: 441050	Wilson score deviation: 0.012	(Polandball: Can into Space!)
 17. AppID: 421660	Wilson score deviation: 0.012	(Harmonia)
 18. AppID: 546080	Wilson score deviation: 0.011	(Coffin of Ashes)
 19. AppID: 410980	Wilson score deviation: 0.011	(Master of Orion 2)
 20. AppID: 723090	Wilson score deviation: 0.011	(Meltys Quest)

