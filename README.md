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

Here are the results as [output](https://raw.githubusercontent.com/woctezuma/steam-reviews/master/output/output_rankings.txt) by `estimate_hype.py`.

Unexpectedly, Deep Space Waifu and Meltys Quest do not benefit that much from joke reviews: without the joke reviews, the Wilson score is more or less the same (respectively 0.4% and 1.1% lower).

### Ranking by hype

A hype of 0.300 means that 30.0% of the reviews are classified as joke reviews.

  1. AppID: 623080	Hype: 0.300	(planetarian HD)
  2. AppID: 410830	Hype: 0.290	(ARENA GODS)
  3. AppID: 733990	Hype: 0.250	(I Can't Believe It's Not Gambling)
  4. AppID: 283960	Hype: 0.237	(Pajama Sam: No Need to Hide When It's Dark Outside)
  5. AppID: 745880	Hype: 0.225	(  Hidden Star in Four Seasons.)
  6. AppID: 502800	Hype: 0.220	(SENRAN KAGURA ESTIVAL VERSUS)
  7. AppID: 260750	Hype: 0.213	(Neighbours from Hell Compilation)
  8. AppID: 639790	Hype: 0.207	(DEEP SPACE WAIFU)
  9. AppID: 294530	Hype: 0.203	(Freddi Fish 2: The Case of the Haunted Schoolhouse)
 10. AppID: 639780	Hype: 0.201	(deep space waifu: FLAT JUSTICE VERSION)

### Ranking by Wilson score bonus due to unexpectedly positive hype

A Wilson score bonus (or deviation) of 0.077 means that the game's Wilson score (95% confidence) is improved by 7.7% thanks to the joke reviews.

  1. AppID: 623080	Wilson score deviation: 0.077	(planetarian HD)
  2. AppID: 552280	Wilson score deviation: 0.061	(Tayutama2 -you're the only one- CHI ver.)
  3. AppID: 438320	Wilson score deviation: 0.039	(Rush Rover)
  4. AppID: 410830	Wilson score deviation: 0.038	(ARENA GODS)
  5. AppID: 664180	Wilson score deviation: 0.036	(Draw Puzzle)
  6. AppID: 368570	Wilson score deviation: 0.028	(Beat Da Beat)
  7. AppID: 496350	Wilson score deviation: 0.025	(Supipara - Chapter 1 Spring Has Come!)
  8. AppID: 588040	Wilson score deviation: 0.023	(WILL: A Wonderful World / WILL)
  9. AppID: 658620	Wilson score deviation: 0.022	(Wonderful Everyday Down the Rabbit-Hole)
 10. AppID: 653950	Wilson score deviation: 0.018	(Your Smile Beyond Twilight:)

### Ranking by proportion of English reviews

  1. AppID: 662210	Proportion english-tags: 0.986	(Metal as Phuk)
  2. AppID: 418520	Proportion english-tags: 0.979	(SculptrVR)
  3. AppID: 453000	Proportion english-tags: 0.959	(TheWaveVR Beta)
  4. AppID: 347600	Proportion english-tags: 0.959	(Total Miner)
  5. AppID: 529520	Proportion english-tags: 0.952	(Mutant Football League)
  6. AppID: 634160	Proportion english-tags: 0.951	(Cattails | Become a Cat!)
  7. AppID: 585180	Proportion english-tags: 0.948	(Open Sorcery)
  8. AppID: 380810	Proportion english-tags: 0.947	(Herald: An Interactive Period Drama - Book I & II)
  9. AppID: 283960	Proportion english-tags: 0.945	(Pajama Sam: No Need to Hide When It's Dark Outside)
 10. AppID: 600370	Proportion english-tags: 0.943	(Paradigm)
[...]
238. AppID: 664180	Proportion english-tags: 0.051	(Draw Puzzle)
239. AppID: 516600	Proportion english-tags: 0.051	(Bai Qu )
240. AppID: 665270	Proportion english-tags: 0.023	(  / Barrage Musical  ~A Fantasy of Tempest~)
241. AppID: 623080	Proportion english-tags: 0.014	(planetarian HD)
242. AppID: 593200	Proportion english-tags: 0.014	(The Adventures of Fei Duanmu )
243. AppID: 588040	Proportion english-tags: 0.012	(WILL: A Wonderful World / WILL)
244. AppID: 630060	Proportion english-tags: 0.012	(Consummate:Missing World)
245. AppID: 552280	Proportion english-tags: 0.010	(Tayutama2 -you're the only one- CHI ver.)
246. AppID: 701930	Proportion english-tags: 0.000	(Short Stories Collection of Class Tangerine)
247. AppID: 713260	Proportion english-tags: 0.000	(Beyond the Sunset )

### Ranking by proportion of English reviews, with confirmation by a language detection tool

  4. AppID: 418520	Proportion confirmed-english-tags: 0.979	(SculptrVR)
  5. AppID: 662210	Proportion confirmed-english-tags: 0.971	(Metal as Phuk)
  6. AppID: 380810	Proportion confirmed-english-tags: 0.934	(Herald: An Interactive Period Drama - Book I & II)
  7. AppID: 634160	Proportion confirmed-english-tags: 0.934	(Cattails | Become a Cat!)
  8. AppID: 494310	Proportion confirmed-english-tags: 0.933	(Unbreakable Vr Runner)
  9. AppID: 529520	Proportion confirmed-english-tags: 0.924	(Mutant Football League)
 10. AppID: 453000	Proportion confirmed-english-tags: 0.922	(TheWaveVR Beta)
 11. AppID: 585180	Proportion confirmed-english-tags: 0.922	(Open Sorcery)
 12. AppID: 676820	Proportion confirmed-english-tags: 0.916	(Subsurface Circular)
 13. AppID: 454380	Proportion confirmed-english-tags: 0.910	(Champions of Breakfast)
[...]
241. AppID: 516600	Proportion confirmed-english-tags: 0.051	(Bai Qu )
242. AppID: 664180	Proportion confirmed-english-tags: 0.049	(Draw Puzzle)
243. AppID: 665270	Proportion confirmed-english-tags: 0.018	(  / Barrage Musical  ~A Fantasy of Tempest~)
244. AppID: 623080	Proportion confirmed-english-tags: 0.014	(planetarian HD)
245. AppID: 630060	Proportion confirmed-english-tags: 0.012	(Consummate:Missing World)
246. AppID: 593200	Proportion confirmed-english-tags: 0.010	(The Adventures of Fei Duanmu )
247. AppID: 588040	Proportion confirmed-english-tags: 0.009	(WILL: A Wonderful World / WILL)
248. AppID: 552280	Proportion confirmed-english-tags: 0.006	(Tayutama2 -you're the only one- CHI ver.)
249. AppID: 701930	Proportion confirmed-english-tags: -0.000	(Short Stories Collection of Class Tangerine)
250. AppID: 713260	Proportion confirmed-english-tags: -0.000	(Beyond the Sunset )

