---
title: ARC-AGI-3: I Built the Lab; the Score Came from a Public Notebook
description: What I built for ARC Prize 2026's interactive-games track: an offline harness, a planner, one recording format and a journal. And the honest story of why my best score (31.86) rests on a public notebook.
meta: ARC Prize 2026, ARC-AGI-3 (Kaggle) · 5 min read
date: 2026-11
topic: Reasoning (ARC Prize)
list: ARC-AGI-3: I built the lab; the score came from a public notebook
summary: 31.86 is a public notebook plus my startup fix. Here’s the offline lab I built around it.
home: An offline lab for interactive games, and an honest account of the 31.86.
---

My best ARC-AGI-3 score, 31.86, is mostly someone else's work. It is a public notebook by dfranzen plus a small startup fix of mine. What I actually built was the lab around it. The lesson: know which part is yours.

## A game with no instructions

ARC-AGI-3 is the interactive-games track of ARC Prize 2026. You get a 64×64 grid and a few buttons. You press them, watch what changes, work out the rules and win. The next level quietly changes them. (The static-puzzle half, ARC-AGI-2, has [its own post](arc-agi.html).)

The competition ships 25 public games and scores on 110 hidden ones. A completed level scores `min((human_actions / agent_actions)², 1)`; a failed level scores zero. Using twice the human's actions throws away 75% of a level. You get one submission per day, and the deadline was 2 November 2026.

## First I built a lab to see the games myself

The competition bundles an offline engine, so I wrapped tools around it. A small Flask server owns one session, human or model, as the single source of truth. Perception tools find objects, diff frames and measure the board. A BFS planner and a verified walker move the avatar one step at a time and re-plan if it did not move. Every session goes to one JSONL recording format, and an append-only journal logs every experiment, so I can say which conclusions were wrong.

Each tool exists because something broke. I once hardcoded one level's geometry and missed a whole row, including a refuel item, so geometry is now detected per frame. The planner was perfect for a four-way grid until one level turned on gravity and it kept producing routes the game would never follow. A validator now predicts where a move lands and flags the mismatch. Batched actions got dropped while animations played, hence the one-step walker.

## Every hard error was a bad reading

A language model played the first game, `ls20`, through these tools. It solved level 1 in 15 moves while learning the rules, then in 13. Its mistakes were measurement mistakes: hardcoded geometry, a yellow item counted as move budget, a rotator assumed never to respawn (it does). The reasoning on top of each bad reading was sound and confidently wrong.

## My own explorer scored 0.17

I wrote a general explorer that calibrates actions, drops no-ops and prefers unseen frames. Offline on the 25 public games it averaged 6.80 levels. Two obvious ideas hurt: action momentum (5 levels against 8) and coverage by position (2.80 against 6.80).

The real submission scored 0.16. Raising the action cap from 4,000 to 100,000 gave 0.17. In the real run 110 games share one wall clock, so each runs out of time long before it runs out of actions. Offline, each game ran alone, so more budget helped. That did not transfer.

## Public notebooks overtook it

By 8 September the board was led by a 27B model on a 96 GB GPU, with a public harness. I forked a public notebook and scored between 1.99 and 4.62 on the hidden set. That is about fifteen times my explorer, and not my work.

My own experiments each had a pass/fail gate written before the run. Prefix caching did nothing: a hardcoded profile reset my setting, and the gate caught a smoke score of 6.77 that would have looked like a win. A bigger KV cache scored 4.42, but ten hidden draws of that model family had mean 2.86 and sd 0.75, so 4.42 was luck. The "4.33 target" was the best of about 40 runs of someone else's notebook.

## Then one notebook moved the whole field

On 2 October a competitor, `dfranzen`, published a notebook that showed 31.47 on its public page. It used a newer 4-bit model, a quantised draft model for speculative decoding, and an SGLang server running 10 games at once. The whole field jumped within days.


<figure class="fig">
<ol class="flow">
<li><b>My explorer</b><span>0.16 to 0.17</span></li>
<li><b>Public 27B fork</b><span>1.99 to 4.62</span></li>
<li><b>dfranzen notebook</b><span>copies at 24 to 29</span></li>
<li class="hot"><b>My kernel v4</b><span>that plus my startup fix: 31.86</span></li>
</ol>
<figcaption>Where my scores came from. My 14-stream variant of the notebook drew 21.26.</figcaption>
</figure>


**My best score, 31.86, is a public notebook plus a startup fix.** The agent, model, serving stack and patch are Franzen's. The startup fix is the one thing I changed. It was small, and not a better idea about how to play games.

For two weeks I submitted copies of public notebooks, one per day. Five identical copies scored 26.89, 27.67, 29.08, 26.24 and 27.87. At one run per day, small changes drown in that noise. Most public "improvements" came without a before-and-after number.

## The missing points are unfinished levels

A public audit of 100 trajectories, which I recomputed, is my best map. The mean was 46.5 against a completion ceiling of 49.1. Of the 53.5 missing points, 50.9 were unfinished levels and only 2.6 were inefficiency. The constraint is compute per game.


<figure class="fig">
<div class="stats">
<div><b>49.1</b><span>completion ceiling</span></div>
<div class="hot"><b>50.9</b><span>points lost to unfinished levels</span></div>
<div><b>2.6</b><span>points lost to inefficiency</span></div>
</div>
<figcaption>Of the 53.5 missing points in 100 audited trajectories (mean 46.5).</figcaption>
</figure>


So I cut the harness window from 128 Ki to 112 Ki tokens to fit 12 streams. Tokens per second rose from 566 to 614. The aggressive version, 14 streams and an 88K window, scored 21.26, below the 24 to 29 band. My guess is that games lost history before the window trimmed it. I can't prove that with one submission a day.

## Use this yourself: build the offline harness before you submit

This applies to any competition where you get one submission a day but can run the environment locally.

1. Run the official engine locally and wrap it in one `reset` / `step` interface, so a human, a script and a model all use the same door.
2. Write every session to one recording format, one JSON line per step, and never log anywhere else.
3. Build a replay that reads those lines back, so any run, good or bad, can be inspected after the fact.
4. Copy the scoring formula from the official code instead of retyping it from the rules page. Check it on a recording where you know the answer.
5. Keep an append-only journal of each experiment with its pass/fail gate written first.

```
import json

def record(env, actions, path):
    obs = env.reset()
    with open(path, "w") as f:
        for a in actions:
            obs, done = env.step(a)
            f.write(json.dumps({"action": a, "obs": obs, "done": done}) + "\n")
            if done:
                break

def replay(path):
    for line in open(path):
        yield json.loads(line)

# paste the official scorer here; this is the formula from the post
def level_score(human, agent, solved):
    return min((human / agent) ** 2, 1.0) if solved else 0.0
```

The pitfall: the harness runs one game alone, while the real run may share a clock across many, so time and budget results need a shared-clock test before you trust them.

## What I'd do differently

- **Test offline benchmarks against a shared clock.** My action-budget gain was real offline and meaningless online.
- **Never compare to a best-of-N.** A public score is the top of a distribution you can't see.
- **Write the pass/fail gate before the run.** It saved me from a fake caching win.
- **Measure, then reason.** Most hard errors were bad readings of the board.
- **Count the cost as well as the benefit.** I tracked tokens per second and not the history each game lost.

I'm not claiming a final rank. The code, journal and a paper draft are in a private repo.
