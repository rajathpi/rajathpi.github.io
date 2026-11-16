---
title: Pokémon TCG AI: Search Can't Fix a Bad Value Function
description: Notes from my Kaggle Pokémon TCG strategy write-up: a search agent that beat itself 97% of the time, lost 1–15 to a simple rule bot, and what 4,650 real games say about deck, pilot and luck.
meta: Pokémon TCG AI Battle Challenge, strategy write-up (Kaggle) · 5 min read
date: 2026-09
topic: Game agents
list: Pokémon TCG AI: search can’t fix a bad value function
summary: Strategy write-up: a search agent beat itself 97 %, then lost 1–15 to a rule bot.
home: 97 % against itself, 1–15 against a rule bot.
---

My search agent beat its own no-search version 97 % of the time. Then it lost 1–15 to a simple rule bot.

Kaggle's Pokémon TCG competition had a simulation ladder and a strategy write-up track. I entered only the write-up, so I have no ladder rank. The lesson: search amplifies whatever value function you give it.

## I split a result into deck, pilot and luck

I framed a ladder result as deck strength × piloting × rating luck, and tried to measure each. I used the competition's public export of top-band games and the official engine, run headless. Everything ran on a laptop CPU, about nine core-hours, with no learned weights.

## The endgame meta was a triangle

I parsed all 4,650 games from the final rating day. Three decks had taken over: Dragapult ex (32.0 % of games), Mega Kangaskhan ex / Slowking (23.7 %) and Hydrapple ex / Teal Mask Ogerpon (19.0 %). They beat each other in a loop, and no popular deck won more than about 54 % against the field.

The best win rates belonged to rare decks, but each was played almost entirely by one strong team. Win rate mixes up the deck and the person playing it.

## The pilot mattered more than the deck

The first-place team played the most popular deck, Dragapult, and won 69.9 % of its final-day games with it. Same cards, very different results.

I held the pilot fixed (my agent on both sides) and played six deck pairings, 80 games each. Among top teams Dragapult beats Alakazam 67 % of the time. With my agent, Alakazam won 55 games to 25. Matchup tables belong to a (deck, pilot) pair. So I picked the deck my pilot could drive: a single-prize Alakazam list.

## Guess the hidden cards, then search

I used Perfect Information Monte Carlo. Guess a full world that fits what you have seen, play each move out in it with the real rules, repeat over several worlds, and pick the best average.


<figure class="fig">
<ol class="flow"><li><b>Track revealed cards</b><span></span></li><li><b>Guess hidden cards</b><span>from real decklists</span></li><li><b>Sample K worlds</b><span></span></li><li><b>Try each move</b><span>real engine, every world</span></li><li class="hot"><b>Score</b><span>hand-written evaluation</span></li></ol>
<p class="loopback">then pick the best move on average</p>
<figcaption>One turn of search. The highlighted step was the weak link.</figcaption>
</figure>


The guess is the clever part. I match the opponent's revealed cards against the 150 most-played final-day decklists and deal the rest into their hidden zones. A few turns in, the archetype is usually pinned down.

## Search crushed its own no-search twin

I compared the agent against the identical agent with search off, over 60 games per setting.

| Worlds sampled (K) | Wins out of 60 | Time per game |
| --- | --- | --- |
| 0 (no search) | 28 | <0.1 s |
| 1 | 52 | 5.5 s |
| 2 | 58 | 9.3 s |
| 4 | 58 | 19.4 s |
| 8 | 57 | 30.0 s |


<figure class="fig">
<div class="bars"><div class="bar"><span class="l">No search</span><span class="b" style="--v:46.7"></span><span class="n">28 of 60</span></div><div class="bar"><span class="l">K = 1</span><span class="b" style="--v:86.7"></span><span class="n">52 of 60</span></div><div class="bar hot"><span class="l">K = 2</span><span class="b" style="--v:96.7"></span><span class="n">58 of 60</span></div><div class="bar"><span class="l">K = 4</span><span class="b" style="--v:96.7"></span><span class="n">58 of 60</span></div><div class="bar"><span class="l">K = 8</span><span class="b" style="--v:95.0"></span><span class="n">57 of 60</span></div></div>
<figcaption>Wins against the no-search twin. Most of the gain comes by K = 2.</figcaption>
</figure>


One or two worlds do almost all the work. Going second also wins more with my pilot (58 % over 160 mirror games), so the agent goes second when it can.

## Then a rule bot beat it 15–1

I pointed the same agent, piloting Dragapult, at the strongest public rule bot, a hand-coded Alakazam player. It lost 1–15. It never set up Dragapult's key attack, which takes about three turns, and search only looks a turn or so ahead. My evaluation also liked a growing opponent hand, which is exactly what that Alakazam deck turns into damage.

## Every bit of trust I gave search cost wins

To separate search from evaluation, I let the rule bot play and let search override its moves at three confidence levels.

| Search overrides the rule bot | Decisions overridden | Win rate vs rule bot |
| --- | --- | --- |
| Freely | 26 % | 17 % |
| When every world agrees by a wide margin | 6.5 % | 33 % |
| Only on proof: wins outright in every world | 0.5 % | 49 % (100 games) |

The best I could do was parity, by overriding almost never. A 30-game run of the proof-only version showed 60 %. At 100 games it was 49 wins to 51 losses.


<figure class="fig">
<div class="bars"><div class="bar"><span class="l">Override freely</span><span class="b" style="--v:17"></span><span class="n">17 %</span></div><div class="bar"><span class="l">Override when sure</span><span class="b" style="--v:33"></span><span class="n">33 %</span></div><div class="bar hot"><span class="l">Override on proof</span><span class="b" style="--v:49"></span><span class="n">49 %</span></div></div>
<figcaption>Win rate against the rule bot. Less search trust, more wins.</figcaption>
</figure>


## Luck alone gives one agent a threefold rank range

I simulated the ladder with 3,000 agents. A single agent of fixed strength ended up with a rating spread of about ±32 points. An agent whose true rank is about 140 finishes anywhere from roughly 78th to 241st (90 % interval) from match order alone.

## Use this yourself: Perfect Information Monte Carlo for hidden cards

This applies to a turn-based game where you cannot see everything, but you have a real simulator for the rules.

1. Write `sample_world`. It turns what you have seen into one complete, plausible game state, hidden cards included.
2. Write `legal_moves` and `apply`. Use the real engine, so the rules are never your own approximation.
3. Write `evaluate`, a score for a finished position. Search is only as good as this.
4. For each candidate move, apply it in each sampled world, score the result and average over worlds.
5. Play the highest average. Start with a small number of worlds. In my runs most of the gain came by two.

```
def pimc_move(state, sample_world, legal_moves, apply, evaluate, k=8):
    """Pick the move with the best average value over k guessed worlds."""
    worlds = [sample_world(state) for _ in range(k)]
    def avg(move):
        return sum(evaluate(apply(w, move)) for w in worlds) / k
    return max(legal_moves(state), key=avg)
```

The pitfall is the evaluation. PIMC treats each world as fully known, so it never values hiding or gathering information, and a flawed score gets amplified. Test it against a plain rule bot before trusting it.

## What I'd do differently

- **Learn the evaluation.** It is the bottleneck. Distil search decisions and top teams' public games into a small value network, then widen the override gate as it earns it.
- **Use the clue my guesser ignores.** Cards a player didn't play suggest cards they may not hold.
- **Never judge a change on fewer than a few hundred games.** In my tests, 60 games moved the win rate about ±12 points on noise alone.
- **Prefer the lower-variance deck at equal strength.** Spend your last slots on configurations you have already tested.

*Pokémon and all related elements are © Pokémon/Nintendo/Creatures/GAME FREAK, used here only in connection with the competition.*
