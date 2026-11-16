---
title: Orbit Wars: Self-Play Lied, a Stronger Base Won
description: An honest write-up of a Kaggle RTS competition where the ladder repeatedly demolished my self-play improvements, and the best move was adopting a stronger base agent.
meta: Orbit Wars (Kaggle) · 6 min read
date: 2026-06
topic: Game agents
list: Orbit Wars: self-play lied, a stronger base won
summary: 505 of 4,729. Self-play wins failed on the ladder; adopting a stronger public agent didn’t.
home: The live ladder vs. my self-play “improvements”.
---

A tweak that beat my base by 8 points in self-play scored 1129.6 live. The base itself scored 1249.6.

Orbit Wars is a Kaggle real-time-strategy competition where your score is your ship count at step 498. I finished 505 of 4,729, top 11 %. My self-play wins did not carry to the ladder, and adopting a stronger public agent beat all my own tuning.

## One number decides the game

Planets orbit a sun and each makes 1–5 ships per turn. You launch fleets to capture planets. Only total ships at the end count.

Bigger fleets move faster, so a trickle of small fleets loses fights. Games are 2-player duels or 4-player free-for-alls on a TrueSkill ladder. Only your last two submissions stay active.

## My planner plateaued

Every agent shared one core. Each turn it shortlists targets, scores one launch per source-target pair, and greedily commits a few waves.


<figure class="fig">
<ol class="flow"><li><b>Observe</b><span></span></li><li><b>Shortlist targets</b><span></span></li><li class="hot"><b>Find spare ships, set floors</b><span>safe_drain, capture_floor</span></li><li><b>Score by ROI</b><span>distance, garrison</span></li><li><b>Greedy waves</b><span>emit moves</span></li></ol>
<figcaption>My planner each turn. Most of the skill sits in the highlighted step.</figcaption>
</figure>


Almost all the skill sits in how the floors and thresholds are chosen. My own line stalled at about 1141–1157 live. More knobs gave no more score.

## A stranger's simpler bot beat my whole line

Then I adopted a public agent, `light` (from `alycemiki/light-ver-1200-simple-orbit-intruder`). It scored about 1249.6 live. It was simpler than mine and smarter in four ways:

- It sends one full safe launch, with no multi-fraction search.
- It raises the capture floor for expected enemy reinforcements, so it skips doomed attacks.
- It ramps aggression smoothly with my strength divided by the leader's.
- It stops attacks that cannot repay their cost before step 498.

## Self-play lied, twice

I tested in an arena with seat-rotated 4-player games. A tweak, `light_o2`, looked +8 points in self-play. Live it scored 1129.6 against 1249.6, and I reverted. Earlier, `comet3_nfpw` looked +12 points in self-play and plateaued at 1141 live.

| Change | Self-play | Live |
| --- | --- | --- |
| Adopt `light` | — | 1249.6 (best) |
| `light_o2` | +8 pp | 1129.6 |
| `comet3_nfpw` | +12 pp | 1141 |


<figure class="fig">
<div class="stats"><div><b>+8 pp</b><span>light_o2 in self-play</span></div><div class="hot"><b>1129.6</b><span>light_o2 live</span></div><div><b>1249.6</b><span>the base, live</span></div></div>
<figcaption>Self-play ranked the ideas wrong.</figcaption>
</figure>


Beating a clone of your own base is not beating the ladder. I now use self-play only to catch regressions, never to rank ideas. New submissions also start with high uncertainty, so an early peak that fades does not mean the agent got worse.

## I was tuning the wrong half

I mined 61 live replays. My 2-player win rate was healthy at 62.5 %. My 4-player rate was about 28 %, barely above the 25 % random baseline.


<figure class="fig">
<div class="bars"><div class="bar"><span class="l">2-player</span><span class="b" style="--v:62.5"></span><span class="n">62.5 %</span></div><div class="bar hot"><span class="l">4-player</span><span class="b" style="--v:28"></span><span class="n">28 %</span></div><div class="bar"><span class="l">Random baseline</span><span class="b" style="--v:25"></span><span class="n">25 %</span></div></div>
<figcaption>My win rate across 61 live replays.</figcaption>
</figure>


I led by step 40, then collapsed by step 80, because the other three players target the leader. The reinforcement floor in `light` already handles this. Adding my own overhead on top over-garrisoned it.

## The real ceiling was RL, and I had none

I read all 20 discussion threads. The top tier, 1500–1788, trains transformer policies with PPO self-play. Every heuristic agent of this family clusters at about 1240–1260.

Cloning the top RL bot lost about 5:1 to a public heuristic. With a week left, no RL pipeline and only CPU, I stopped submitting. Each new submission evicts an active agent that must re-climb from about 700. I kept my two strongest distinct agents.

## Use this yourself: Rank ideas on the ladder, not in self-play

This applies when you can play your own agent locally but the real opponents are a different, changing field.

1. Use self-play only as a regression screen. If a change loses to your old version, drop it.
2. Passing the screen proves nothing. Rank ideas by live ladder score.
3. Before you read a win-rate gap, work out the games needed. Run that many or admit it is noise.
4. Submit one change at a time, so a live score has one cause.
5. Judge it only after the score settles, because a new submission starts with high uncertainty.

```
from math import sqrt

def games_needed(p, diff, z=1.96):
    """Games per version before a win-rate gap of `diff` beats noise."""
    se_per_game = sqrt(2 * p * (1 - p))   # std error of A-minus-B, times sqrt(n)
    return (z * se_per_game / diff) ** 2
```

A gap of 8 points at a 50 percent win rate needs about 300 games per version, and 2 points needs about 4,800. This is a noise check only. It does not fix the bigger problem that a clone of your own base is the wrong opponent, so a clean result can still be wrong live.

## What I'd do differently

- Adopt the strongest public base in week one, not week four.
- Fix the 4-player game first, since it is half the matches.
- Start an RL pipeline early, or accept the heuristic ceiling.
