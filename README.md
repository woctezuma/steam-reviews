# Steam Reviews

This repository contains code to compute statistics of Steam reviews:
* `download_reviews.py` allows to dowload reviews via Steam API,
* `compute_wilson_score.py` is a utility copied from [my hidden-gems repository](https://github.com/woctezuma/hidden-gems),
* `download_json.py` is a utility copied from [my hidden-gems repository](https://github.com/woctezuma/hidden-gems),
* `identify_joke_reviews.py` allows to classify reviews as acceptable vs. joke,
* `estimate_hype.py` allows to rank games according to their hype (percentage of joke reviews),
* `describe_reviews.py` allows to compute text properties, and then aggregate meta-data and review features,
* `cluster_reviews.py` attempts to divide reviews into clusters.

Data can be downloaded from SteamSpy API and Steam API. It is readily available as a snapshot if needs be in [my Steam-Reviews-Data repository](https://github.com/woctezuma/steam-reviews-data).

## Identification of joke reviews, based on the subjectivity feature

We list below examples of identified joke reviews. If you are interested in the classification acceptable vs. joke reviews, please feel free to have a look at examples of acceptable reviews, which are listed in the `output/` folder.

The following was generated by `identify_joke_reviews.py`.

### Fidel Dungeon Rescue

```
Input appID detected as 573170
Number of reviews: 151 (149 up ; 2 down)
Number of downloaded reviews: 151

Stats for all reviews available in English
Number of reviews: 130 (128 up ; 2 down) ; Wilson score: 0.95

Threshold for subjectivity: 0.36

        [ ==================================== ]
	[ ====== Joke positive reviews ======= ]

 ==== Review 1 (#reviews = 9) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
You awoo when you level up.

 ==== Review 2 (#reviews = 9) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.33))
Love the game! Please give us a Daily Challange! BARK, BARK!

 ==== Review 3 (#reviews = 9) ====
=> Sentiment analysis: polarity(-0.21) ; subjectivity(0.31))
If you ever found yourself structuring your daily routine to maximize "your efficiency" this is the game for you.

This game's main menu can get an IGF award itself. 

"Dog bless this game."

 ==== Review 4 (#reviews = 9) ====
=> Sentiment analysis: polarity(-0.05) ; subjectivity(0.27))
The first game that killed me in the main menu, 10/10.

 ==== Review 5 (#reviews = 9) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
Press Ctrl to bark
[spoiler]Dead dog can't bark[/spoiler]

	[ ==================================== ]
	[ ====== Joke negative reviews ======= ]

 ==== Review 1 (#reviews = 1) ====
=> Sentiment analysis: polarity(0.38) ; subjectivity(0.15))
Almost fun. The gripesome ghost chase is well worth a refund, though!!

	[ ==================================== ]

Stats for all acceptable reviews (subjectivity >= threshold)
Number of reviews: 120 (119 up ; 1 down) ; Wilson score: 0.95

Stats for detected joke reviews (subjectivity < threshold)
Number of reviews: 10 (9 up ; 1 down) ; Wilson score: 0.60

Conclusion: estimated deviation of Wilson score due to joke reviews: -0.01
```

### Deep Space Waifu

```
Input appID detected as 639780
Number of reviews: 347 (338 up ; 9 down)
Number of downloaded reviews: 332

Stats for all reviews available in English
Number of reviews: 209 (204 up ; 5 down) ; Wilson score: 0.95

Threshold for subjectivity: 0.36


	[ ==================================== ]
	[ ====== Joke positive reviews ======= ]

 ==== Review 1 (#reviews = 49) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
I dont need to explain anything.

 ==== Review 2 (#reviews = 49) ====
=> Sentiment analysis: polarity(-0.28) ; subjectivity(0.28))
10/10 expansion to the previous game. Would write a longer review but I think I need to go to church now

 ==== Review 3 (#reviews = 49) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
Bless the devs for creating a standalone version of DSW with flat-chested females.

 ==== Review 4 (#reviews = 49) ====
=> Sentiment analysis: polarity(0.44) ; subjectivity(0.30))
Keep up the good work guys!

How about adding moving waifus in the next one? You know some moving animated lolis who try to dodge my bullets while I'm trying to rip off their clothes and salivating on my keyboard?

 ==== Review 5 (#reviews = 49) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
A$$ and Tiddies.

	[ ==================================== ]
	[ ====== Joke negative reviews ======= ]

 ==== Review 1 (#reviews = 4) ====
=> Sentiment analysis: polarity(0.10) ; subjectivity(0.30))
i love this game but its buggy and glitchy like for example i would swipe no one the first girl and its still stuck on the same girl or if you choose another waifu it still takes you to the level with the first girl and i also notice if i quit and go back the screen is stuck. I hope the creators fix this soon

 ==== Review 2 (#reviews = 4) ====
=> Sentiment analysis: polarity(-0.12) ; subjectivity(0.35))
b' \n\nAs of Dec 09 2017, 12:54 AM in PST +09:00, this review has been flagged by developers because my korean review was not related with topic.\n\nWhat I wrote is I hate flat chest. And I haven\'t thought those "Flat Justice" in game title means flat boobies of girls in game.\n\nIt\'s my personal opinion how I can tell about boobies god damn it\n\nDec 15th, 02:28 AM  in PST +09:00, I\'m finally able to show this review. Shame on you dev teams, it\'s my freedom to talk about how I think about flat chest!'

 ==== Review 3 (#reviews = 4) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
THIS ONE IS UNPAYABLE WITHOUT MOUSE CONTROL

 ==== Review 4 (#reviews = 4) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
y is ther no cheevo for beeting tha gam on gentalmanne moed and being a gud christiaen boyo?

	[ ==================================== ]

Stats for all acceptable reviews (subjectivity >= threshold)
Number of reviews: 156 (155 up ; 1 down) ; Wilson score: 0.96

Stats for detected joke reviews (subjectivity < threshold)
Number of reviews: 53 (49 up ; 4 down) ; Wilson score: 0.82

Conclusion: estimated deviation of Wilson score due to joke reviews: -0.02
```

### Meltys Quest

```

Input appID detected as 723090
Number of reviews: 294 (288 up ; 6 down)
Number of downloaded reviews: 290

Stats for all reviews available in English
Number of reviews: 186 (184 up ; 2 down) ; Wilson score: 0.96

Threshold for subjectivity: 0.36


	[ ==================================== ]
	[ ====== Joke positive reviews ======= ]

 ==== Review 1 (#reviews = 50) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
The time has come, and so have I.

 ==== Review 2 (#reviews = 50) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
Bu Kawk E Tsunami

 ==== Review 3 (#reviews = 50) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
Well made product. The devs knew what they were doing.

 ==== Review 4 (#reviews = 50) ====
=> Sentiment analysis: polarity(0.40) ; subjectivity(0.35))
good story, multiple ending, rpg element really freaking good, 

and here i am
trying to achieve 100% achievement before runs out of tissue

 ==== Review 5 (#reviews = 50) ====
=> Sentiment analysis: polarity(1.00) ; subjectivity(0.30))
Best ero RPG I played.

	[ ==================================== ]

Stats for all acceptable reviews (subjectivity >= threshold)
Number of reviews: 136 (134 up ; 2 down) ; Wilson score: 0.95

Stats for detected joke reviews (subjectivity < threshold)
Number of reviews: 50 (50 up ; 0 down) ; Wilson score: 0.93

Conclusion: estimated deviation of Wilson score due to joke reviews: 0.01
```

## Review description for Fidel Dungeon Rescue, i.e. features for clustering

The following was generated by `describe_reviews.py`.

```
Input appID detected as 573170
Number of reviews: 151 (149 up ; 2 down)
Number of downloaded reviews: 151

Most popular languages:
['english', 'schinese', 'spanish']
```

![Lexicon count](https://tof.cx/images/2017/12/29/56eb3d6d465d425db194d6bc11d3d40d.png)

![Boxplots per language](https://tof.cx/images/2017/12/29/e7053368be1c49abf45209dd2be9ab45.png)

```
          character_count  comment_count  dale_chall_readability_score  \
language                                                                 
english        288.846154       0.100000                      6.789000   
schinese       212.222222       0.888889                      4.865556   
spanish        349.500000       0.000000                     11.438750   

          difficult_words_count  flesch_reading_ease  lexicon_count  \
language                                                              
english                9.376923            77.535231      51.576923   
schinese               1.444444           136.487778       7.777778   
spanish               23.375000            45.555000      58.875000   

          num_games_owned  num_reviews  playtime_forever  polarity  \
language                                                             
english        257.707692    16.353846        646.338462  0.161304   
schinese       319.777778    25.222222        347.666667  0.111111   
spanish        213.875000     8.250000        485.000000  0.138281   

          received_for_free  sentence_count  steam_purchase  subjectivity  \
language                                                                    
english                 0.0        3.561538             1.0      0.537878   
schinese                0.0        1.111111             1.0      0.111111   
spanish                 0.0        3.625000             1.0      0.434821   

          syllable_count  voted_up  votes_funny  votes_up  weighted_vote_score  
language                                                                        
english        70.684615  0.984615     0.561538  1.930769             0.223770  
schinese        6.111111  1.000000     1.000000  3.777778             0.497366  
spanish        95.125000  1.000000     0.000000  0.875000             0.203655  
```

## Review clustering for Meltys Quest

The following was generated by `cluster_reviews.py`.

### Number of reviews per cluster

```
Cluster stats: 
A    131
B     47
C      8
```

### Cluster A
```
 ==== Review 1 in cluster A (#reviews = 131) ====
=> Sentiment analysis: polarity(0.40) ; subjectivity(0.35))
good story, multiple ending, rpg element really freaking good, 

and here i am
trying to achieve 100% achievement before runs out of tissue

 ==== Review 2 in cluster A (#reviews = 131) ====
=> Sentiment analysis: polarity(0.34) ; subjectivity(0.35))
Fun & Family friendly RPG.

 ==== Review 3 in cluster A (#reviews = 131) ====
=> Sentiment analysis: polarity(0.00) ; subjectivity(0.00))
A masterpiece.
```

### Cluster B
```
 ==== Review 1 in cluster B (#reviews = 47) ====
=> Sentiment analysis: polarity(0.14) ; subjectivity(0.60))
Melty's Quest is an honest god good RPG. The art is amazing, the music is good, the story is actually nice, there multiple endings, lewd patch is free, being pure is difficult but fun as hell, and you can play the entire game one handed.

If you buy this game get the free lewd patch since i'm sure that is why you buying it but do actually play the game. The gameplay is actually nice and simple. 

Be a man and play the game on online mode you fuck. Also tell your friends you bought it. They'll be filled with envy knowing they don't have the guts to buy it and play it. Also one hand mode.

Sidenote: I picked this game for Mom's Spaghetti award... it didn't get it

 ==== Review 2 in cluster B (#reviews = 47) ====
=> Sentiment analysis: polarity(0.21) ; subjectivity(0.38))
I'ts ok, if you patched it it gets a little bit  more interesting but what do you expect? You get exactly what you paid for, nothing more, nothing less. gets kinda grindy and repetitive after a while though

 ==== Review 3 in cluster B (#reviews = 47) ====
=> Sentiment analysis: polarity(0.22) ; subjectivity(0.50))
Even though I have strong Christian beliefs, there were a bunch of things of the game I liked. I really enjoyed some of the music. The Noosel Plains music is one of the best songs in the game in my honest opinion. The story was also pretty good. Meltys' style of play reminded me of the old JRPG dungeon crawlers I played as a kid and teen. If you're offended by hentai viewing, then I suggest you not play this game. If you want a retro JRPG dungeon crawler experience with a good story and soundtrack to boot, but don't care about the hentai, then go ahead and get this game.
```

### Cluster C
```
 ==== Review 1 in cluster C (#reviews = 8) ====
=> Sentiment analysis: polarity(-0.08) ; subjectivity(0.49))
i will start off by pointing out the absurd price for what the author likes to point out as an "RPG MAKER GAME" and for those that dont understand this it means that he is taking credit for a program that takes 4/5ths the work out of his game and does it for him providing a amature level programing set up along with the ability to import your own pictures and scenes.

so basically taking the program that is basically an infinite amount of legos for him to play with he still has managed to cock this up. after only 7 mins of playing this game i noticed how poorly used the assets that were given to him. you have open shower currents you cant go behind, path ways purly defined by lake tiles and pit tiles  with random games that you would believe to be able to go through but cant. and not this is just the first area, after grinding for 5 of my 7 mins to get past all the one hit kill enemys and "boss" which literally is programed to kill itself with a critical player hit once its clothes fall off i was able to commision a birdge to get past his greated plot device, a hole in the ground. 

after getting past the pit you are put in an event which is basically a scrpit made from sudo code that are linked to menus so you dont have to type. and it goes off with what i refuse to call writing. the writing is that equal to "the room" aka YOUR TEARING ME APART LISA.

after you get past the shit writing and even shiter map design which i frankly find to be very lazy. where if you leave a section you go to a world map and then walk to the next place. unlike something like pokemon where you actually go on an quest. please remember this is all the happens in the first 7 mins of a game you beat 2 bosses and already 1/4 the way done because there are 8 main bosses.

so if you can complete 1/4 of the game in 7 mins you have to ask "is this game short ?"  and to reply i would have to tell you no. after i refunded this game because having it sit in my library made me feel like a fool and cheated out of my money for medicro what i heasitate to call a game.

but no from what i can tell after looking into it more as i still had files and maps to look at because it was still installed on my pc i was able to find out that it is just more fluff than anything. 

but the final straw for this is that all this "hard work" that the author say he put in didnt even work at first until i rebooted it and fixed the graphical glitches of meltys body not showing up, the hardness selection screen remaining on during the game and the lag and poor response time. which the author will most likely defend by blaming the engine he claims in comments is comparable to the unreal engine.

so let me just get to the closing point if you you got this game here you wanted it for tits and thats all after looking at the other reviews that would be the case for why ever good review it got. but the game is censored in a way that is the laziest thing i have ever seen in my life. all this so he can force it through steams content filter and sell you a .99 cent game for 20 bucks


tldr 
not worth the money
shit teir rpg maker game
only thing the game is hentai
and that is even tumblr esk quality art 


i highly recommend not buying this game. also i tryed to keep this in a short sweet review previously but the author who can not take critisim arugued with me until i decided to put up a legit  review.

 ==== Review 2 in cluster C (#reviews = 8) ====
=> Sentiment analysis: polarity(0.02) ; subjectivity(0.41))
In short, not for the morally strict, or morally weak or easily peer shamed.

Game is not grindy if one plays the Kougai mode first and knows that the flow of the quests will give all the gold a player can use. Over the course of actual traversing the game, a player will get the needed castle resources and armor materials.

Game is very much completable with one hand on a mouse... for obvious reasons. (except Alfredo's part... where it makes mockery in comparison to "traditional" hack and slash RPGs, a blatant call out to Zelda games, fitting in with an Hentai RPG)

This game mocks some RPG economy tropes all over. See the owner of that mansion and his quests leading to Meltys' and his conversation about "effort"...

This game wil throw confusing boners. Be warned of the bait. Hence not for the morally weak.

This game will play with sexuality on all playing sides. Not for the morally strict.

This game will play on RPG tropes, lampshades, and subverts many of them.

The art for the most part is fine... except Garnet's princess dress. How does she shoulder? Or for that matter, the starting point of her breasts are literally at her collar bones. It looks like there is no shoulder at all. During this time of review, the only real bug I encountered is  one where I did not skip the initial cutscenes, but the kougai selection box remains "stuck". To begin a game with it cleared, I had to skip the very first cutscene.

Best played with New Game + on True Princess mode, I don't think the game scales in relation to your previous equipment, and you do not need to worry about slut levels anymore for your useful armors already obtained from kougai mode.

The actual combat? Earthbound-esq, but with a single character, no rolling health meter but a fixed bar - the rolling does not allow the Earthbound reaction and it is not needed with a single character in play. Art shifts as you progress in a boss battle adding to that "final climax"... Combat shifts though once a player plays with Alfredo, a mockery of the standard fare hero.

Short and sweet. Be sure to clean up after. /s

Also, Steam - I used this product for more than five minutes : just look at the cheesements I have. This is concerning "offline mode" interactions and your review restrictions to stop junk data in bias.

 ==== Review 3 in cluster C (#reviews = 8) ====
=> Sentiment analysis: polarity(0.21) ; subjectivity(0.50))
Meltys Quest is the latest HRPG by Happy Life (in collaboration with Remtairy), brought to the English speaking fanbase thanks to Remtairy.

The first thing to note about this game is that, unlike the latest HRPGs releases from other publishers on Steam, this one offers a pretty good English translation (which keeps getting tweaked and fixed to correct some typos/grammar), constant updates to fix all the issues pointed out by users and a free and complete uncensor patch (i.e. no mosaic) downloadable from [url=https://www.patreon.com/posts/meltys-quest-15008521]Remtairy's patreon page[/url].

The CGs in the game are pretty well drawn and the naughty situations cover a wide range of fetishes, some managed better than other. Meltys is quite the charming lady, look wise and, in my opinion, personality wise. She's not the sharpest but she's got a nice heart and that's what I love about her.

The combat is turn based and is shown in a first person style, with just the enemies on screen. The way to learn skills by accruing experience fighting with a specific dress until the dress skill gets unlocked is interesting and gives the dresses another use other than just to unlock some sex scenes or complete some quests.

Last in comes a consideration about the price of this release. Compared to other games of this kind on Steam, this game is pricey. We've got used to 2-4€ affairs while this one came out with a 19,99€ price tag. This is because this game launched on Steam concurrently with its Japanese release and because it offers a true English localization instead of a stream of gibberish.
With that in mind, the 20€ price makes sense and I think it's more than worthwhile for what is offered here. Add to it the great launch discount bringing the price down to 11,99€, the level of support shown from day 1, a free uncensoring patch which even removes mosaic and I can do nothing else but recommend it wholeheartedly to anyone who's interested in these type of games.
```
