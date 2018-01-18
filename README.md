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


### Ranking by hype

A hype of 0.300 means that 30.0% of the English reviews are classified as joke reviews.

NB: For `Planetarian HD`, only 1.4% of reviews are written in English, so 30% hype is only due to very few English reviews.


```
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
[...]
236. AppID: 698260	Hype: 0.015	(Star Shelter)
237. AppID: 691450	Hype: 0.014	(Misao: Definitive Edition)
238. AppID: 665270	Hype: 0.000	(  / Barrage Musical  ~A Fantasy of Tempest~)
239. AppID: 516600	Hype: 0.000	(Bai Qu )
240. AppID: 630060	Hype: 0.000	(Consummate:Missing World)
241. AppID: 637880	Hype: 0.000	(I wanna be The Cat)
242. AppID: 769920	Hype: 0.000	(Odysseus Kosmos and his Robot Quest: Episode 1)
243. AppID: 435970	Hype: 0.000	(RefRain - prism memories -)
244. AppID: 593200	Hype: 0.000	(The Adventures of Fei Duanmu )
245. AppID: 650570	Hype: 0.000	(Code 7)
```

### Ranking by Wilson score bonus due to unexpectedly positive hype

A Wilson score bonus (or deviation) of 0.077 means that the game's Wilson score (95% confidence) is improved by 7.7% thanks to the joke reviews.

NB: The Wilson score depends on the sample size, and may vary widly after small adjustements in case of small sample sizes. The impact of filtering joke reviews is expected to be strong for games with few English reviews.


```
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
[...]
236. AppID: 314180	Wilson score deviation: -0.011	(Deathsmiles)
237. AppID: 635940	Wilson score deviation: -0.011	(Little Busters! English Edition)
238. AppID: 561080	Wilson score deviation: -0.012	(The Price of Freedom)
239. AppID: 624460	Wilson score deviation: -0.012	(Fantasynth: Chez Nous)
240. AppID: 468050	Wilson score deviation: -0.012	(The Last Time)
241. AppID: 586880	Wilson score deviation: -0.014	(Mini Ghost)
242. AppID: 607460	Wilson score deviation: -0.017	(Epic Snails)
243. AppID: 562500	Wilson score deviation: -0.018	(Warstone TD)
244. AppID: 758500	Wilson score deviation: -0.018	(Loot Box Quest)
245. AppID: 372940	Wilson score deviation: -0.021	(Lost Lands: The Four Horsemen)
```

### Ranking by proportion of English reviews

Some games appear at the top of the ranking of hidden gems, yet at the bottom of the ranking by proportion of English reviews: these games are really pushed to the higher ranks by non-English reviewers.

NB: Three games do not appear in this ranking as the download process failed for them: [Out of the Park Baseball 15](https://steamdb.info/app/272670), [Civilization IV: Beyond the Sword](https://steamdb.info/app/34460), [Little Triangle](https://steamdb.info/app/575050).


```
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
```

### Ranking by proportion of English reviews, with confirmation by a language detection tool

After assessing the language with a tool to correct for mistagging, the top 10 ranking is roughly the same: `Total Miner`, `Pajama Sam: No Need to Hide When It's Dark Outside` and `Paradigm` are out, while `Unbreakable Vr Runner`, `Subsurface Circular` and `Champions of Breakfast` are in. The bottom 10 consists of the same games which are a priori popular in Asia, and might not have been translated to English.

The games which are reviewed almost exclusively by English speakers seem to be games heavy on English puns (Metal as Phuk), or textual adventures (Herald to some extent, Open Sorcery, Subsurface Circular).

[Gorogoa](http://store.steampowered.com/app/557600), [Rusty Lake Paradise](http://store.steampowered.com/app/744190) and [Splasher](http://store.steampowered.com/app/446840) feature respectively 20.6%, 18.2% and 17.2% English reviews. For the first two, this might be due to the fact that these games do not require to be able to read English text as most of the instructions are conveyed through drawings. The game store pages indicate respectively that 17 and 14 languages are supported. For the third game, the texts have been translated to 9 languages, including Chinese, Russian, Japanese, and Brazilian Portuguese.

```
  1. AppID: 418520	Proportion confirmed-english-tags: 0.979	(SculptrVR)
  2. AppID: 662210	Proportion confirmed-english-tags: 0.971	(Metal as Phuk)
  3. AppID: 380810	Proportion confirmed-english-tags: 0.934	(Herald: An Interactive Period Drama - Book I & II)
  4. AppID: 634160	Proportion confirmed-english-tags: 0.934	(Cattails | Become a Cat!)
  5. AppID: 494310	Proportion confirmed-english-tags: 0.933	(Unbreakable Vr Runner)
  6. AppID: 529520	Proportion confirmed-english-tags: 0.924	(Mutant Football League)
  7. AppID: 453000	Proportion confirmed-english-tags: 0.922	(TheWaveVR Beta)
  8. AppID: 585180	Proportion confirmed-english-tags: 0.922	(Open Sorcery)
  9. AppID: 676820	Proportion confirmed-english-tags: 0.916	(Subsurface Circular)
 10. AppID: 454380	Proportion confirmed-english-tags: 0.910	(Champions of Breakfast)
[...]
238. AppID: 516600	Proportion confirmed-english-tags: 0.051	(Bai Qu )
239. AppID: 664180	Proportion confirmed-english-tags: 0.049	(Draw Puzzle)
240. AppID: 665270	Proportion confirmed-english-tags: 0.018	(  / Barrage Musical  ~A Fantasy of Tempest~)
241. AppID: 623080	Proportion confirmed-english-tags: 0.014	(planetarian HD)
242. AppID: 630060	Proportion confirmed-english-tags: 0.012	(Consummate:Missing World)
243. AppID: 593200	Proportion confirmed-english-tags: 0.010	(The Adventures of Fei Duanmu )
244. AppID: 588040	Proportion confirmed-english-tags: 0.009	(WILL: A Wonderful World / WILL)
245. AppID: 552280	Proportion confirmed-english-tags: 0.006	(Tayutama2 -you're the only one- CHI ver.)
246. AppID: 701930	Proportion confirmed-english-tags: 0.000	(Short Stories Collection of Class Tangerine)
247. AppID: 713260      Proportion confirmed-english-tags: 0.000        (Beyond the Sunset )
```

### Final remarks

`Deep Space Waifu` and `Meltys Quest` feature respectively 20.7% and 18.6% joke reviews. However, they do not benefit much from joke reviews: their Wilson score is respectively 0.3% and 0.9% lower without the joke reviews.

```
AppID: 639790 (DEEP SPACE WAIFU)
Number of reviews: 4113 (3998 up ; 115 down)
Number of downloaded reviews: 3828
Number of reviews: 3828 (2150 with English tag ; 1678 with another language tag).
Percentage of English tags: 0.56
Number of reviews tagged as in English: 2150 (307 with dubious tag ; 1843 with tag confirmed by language detection).
Percentage of confirmed English tags: 0.86
Number of reviews in English: 1843 (382 joke ; 1461 acceptable)
Hype: 0.207 ; Wilson score deviation: 0.003
```

```
AppID: 723090 (Meltys Quest)
Number of reviews: 317 (311 up ; 6 down)
Number of downloaded reviews: 299
Number of reviews: 299 (191 with English tag ; 108 with another language tag).
Percentage of English tags: 0.64
Number of reviews tagged as in English: 191 (19 with dubious tag ; 172 with tag confirmed by language detection).
Percentage of confirmed English tags: 0.90
Number of reviews in English: 172 (32 joke ; 140 acceptable)
Hype: 0.186 ; Wilson score deviation: 0.009
```

