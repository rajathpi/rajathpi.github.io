---
title: Kaggriculture: How Switching On One Disabled Setting Beat the Public Bots
description: A Kaggle farming-bot competition where the whole ladder ran one shared action tape, and the only edge I found was a sale-timing gate everyone else shipped switched off.
meta: Kaggriculture (Kaggle) · 6 min read
date: 2026-10
topic: Game agents
list: Kaggriculture: how switching on one disabled setting beat the public bots
summary: 786 of 10,148. The whole ladder ran one shared action tape.
home: The whole ladder ran one shared action tape.
---

Two byte-identical submissions of mine scored 170 points apart. After that I treated the live rating as noise.

Kaggriculture is a Kaggle contest where you submit a farming bot that plays other bots on a ladder. I finished 786th of 10,148, the top 8 percent. I never wrote a farm plan that beat the public ones. What worked was one sale-timing setting that every public bot shipped switched off.

## A farm game where only wins count

Two players each get a 10×10 farm. A season is 30 days of 24 turns. Each turn you plant, water, feed, harvest, hire or place market orders. The player with more coins at the end wins.

A 1-coin win equals a 20,000-coin win. The market is shared, so your rival's sales lower your prices. The engine is deterministic apart from weeds, so a recorded ladder game can be replayed to the coin.

## I wanted a better farm. The ladder was one bot.

I started by mining 3,322 top replays, or 6,644 player-games. Almost everyone replayed the same action tape. I found five dominant variants, and one was shared by 22 of 114 teams.

The median build was identical at every score level: 9 cows, 5 sheep, 12 melon tiles, about 290 hires. Rank 1 to 20 and rank 401 and up looked the same in what a bot controls. Even the top and bottom fifths of games by coins had identical sell schedules, with means of 125k and 53k. The gap came from the opponent and the shop's random draw.

So I set two rules. Optimise win rate, never coins. And trust paired tests over the rating.

## Four ideas that lost

I tested four edge hypotheses in my local arena. All four were refuted.

- Geese for the "untouched" egg market: arena win rate fell from 33 percent to 0.
- Cornering wheat to starve the rival's herd: 50 percent to 0.
- Selling fertilizer early: 50 percent to 12.
- Tuning the clone front-run horizon: it fired 0 times in 717 turns.

My first four home-grown agents, tweaks of the shared tape tuned for coins, all lost rating too.

## The edge was a setting everyone left off

From 12 September I stopped designing and started measuring. Each day I forked the strongest public notebook and swept one constant. I proved the fork tied its parent on every seed first. A value only counted if it won on two seed blocks, weeds on, from both seats, and was not worse against any single opponent.


<figure class="fig">
<ol class="flow"><li><b>Fork best public bot</b><span></span></li><li><b>Prove it ties parent</b><span></span></li><li><b>Sweep one constant</b><span></span></li><li><b>Wins on 2 blocks, both seats?</b><span></span></li><li class="hot"><b>Submit</b><span></span></li></ol>
<p class="loopback">if not: back to the fork</p>
<figcaption>My daily loop. A value only counted if it won on both blocks and both seats.</figcaption>
</figure>


The newest public builds all contained a "sale-now gate". When the rival's estimated stock of a premium product reaches K units, it pulls my planned sales of that product forward into this turn. I bank the money before the rival's sales hit the price curve.

Eight public frontier agents in a row shipped it with K = 0, which turns it off. My guess is that authors tune against clones of themselves, where selling early looks bad. Against a field that is not running it, selling early is worth thousands of coins a game.

At K = 6 with a 48-turn horizon it beat its own raw chassis 82 to 90 percent of the time, on every chassis I tried. K = 6 beat K = 8, 88 to 12. It paid on nine public chassis in a row. My final two submissions won the mirror 74 to 46 over two fresh blocks and never lost a game against the wider field.


<figure class="fig">
<div class="stats"><div class="hot"><b>8</b><span>public agents shipped the gate off</span></div><div><b>82–90 %</b><span>wins vs its raw chassis</span></div><div><b>9</b><span>public chassis in a row it paid on</span></div></div>
<figcaption>The sale-now gate: K = 0 is off, K = 6 is what I shipped.</figcaption>
</figure>


## My test setups lied more than my ideas did

A weeds-off, one-seat screen showed exact draws where the weeds-on, both-seat truth was 65 to 35 against me. One 60-seed block swings a win rate by about 7 points. Two candidates showed +12 on one block and a draw on the next.

On 28 September both new slots sank overnight. The old agent replayed against the same live opponents did no better. The field had moved, not my agent. Two byte-identical slots won 76 percent and 56 percent over 300 games each.

## From rank 85 to 786, and I can't prove why

My peak was rank 85 on 20 September. The day before the deadline I read rank 641 of 10,207. I finished 786th after the post-deadline tournament.


<figure class="fig">
<ol class="timeline"><li><span class="t">20 Sep</span>Peak: rank 85</li><li><span class="t">Day before end</span>Rank 641 of 10,207</li><li class="hot"><span class="t">Final</span>Rank 786 of 10,148</li></ol>
<figcaption>Rank over the last weeks.</figcaption>
</figure>


Two likely reasons. New submissions start with high uncertainty, so lucky early wins inflate the score. And by the last day, 72 of my 80 most recent opponents played my own route tile for tile, so my edge had been copied.

I also decoded a wheat buy-and-sell-back trick that 7 of those 80 opponents used. It won the mirror 106 to 14 but gave back 7 of 480 field games, so I did not ship it. The gap to the top was not a setting. Rivals bought four to eight more animals before day 10 and out-earned me by six to nine thousand coins every three days. I never built that planner.

I built on public Apache-2.0 notebooks and kept every upstream notice. The organisers confirmed that was allowed. Their habit of shipping the gate off was the whole opening.

## Use this yourself: Prove a fork ties its parent, then sweep one constant

This applies when a contest ships strong public notebooks and the ladder rating is too noisy to judge small changes.

1. Mine the top replays first. Find what every high-scoring bot does the same, and what only the opponent or luck explains.
2. Fork the strongest public bot unchanged.
3. Run the fork against its parent on many fixed seeds, from both seats. Do not touch anything until the gap is zero.
4. Change one constant. Run the same seeds again and compare per seed, not as two separate averages.
5. Keep the value only if the confidence interval of the paired difference stays above zero on a second, fresh block of seeds.

Pairing cancels the seed luck, so a small edge shows up with far fewer games.

```
def paired_diff(a, b):
    """a[i], b[i]: 1 if bot A / bot B won seed i (same seeds, same seat)."""
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    m = sum(d) / n
    var = sum((x - m) ** 2 for x in d) / (n - 1)
    se = (var / n) ** 0.5
    return m, m - 1.96 * se, m + 1.96 * se
```

It does not help when your opponents change under you. A paired test says nothing about a field that moves, as mine did on 28 September.

## What I'd do differently

- Build the early-herd planner. It is the durable edge. A one-line setting is rented, not owned.
- Ask what the field switched off, before asking what to add.
- Never trust one seed block or one seat.
- Don't retire your last proven slot on the day a challenger goes in.
