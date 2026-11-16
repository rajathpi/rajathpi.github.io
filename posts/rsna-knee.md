---
title: The Silver Medal I Didn't Pick: RSNA Knee
description: A near-miss write-up of the RSNA Knee MRI competition: one of my unselected submissions would have been silver, because I picked my final two by the public leaderboard alone.
meta: RSNA Knee Abnormality Detection (Kaggle) · 3 min read
date: 2026-10
topic: Applied ML
list: The silver medal I didn’t pick: RSNA Knee
summary: Top 12 %, no medal. An unselected blend was silver; I picked finals by the public board alone.
home: How I chose my final submissions, and why that cost a medal.
---

Both of my final submissions scored 0.942. One I left unselected scored 0.944, which was silver.

RSNA Knee Abnormality Detection asks for a probability for each of 12 findings on knee MRI studies, scored by mean AUC. I finished 730th of 6,299 teams (top 12 %), no medal. I had picked both finals by the public leaderboard alone.

## A public notebook, then 127 submissions

It is a code competition. Kaggle re-ran my notebook on a hidden test set of about 1,300 studies, which took 5 to 7 hours of the 9-hour GPU budget. Only the ranking of studies matters, not calibration.

I started from a public 0.943 notebook and treated everything after it as an experiment. Each one got a branch, a README (what, why, results) and a PR. A script listed all 127 submissions with date, description and public score.

The visible test set is only 3 studies, so two different methods can write identical output files. I read each run's log to confirm the extra model really ran. Three "extra model" runs had silently fallen back to the base model after a missing checkpoint.

## Other people's models moved the board, not mine

My first score, on 29 August, was 0.936. My own tweaks to the fork (re-weighting arms, flip augmentation, extra backbones) read 0.940 to 0.941 or worse. What moved the board was stronger public models, which I blended in. By mid-October my best was 0.958, tied with hundreds of teams at three decimals.


<figure class="fig">
<ol class="timeline">
<li><span class="t">29 Aug</span>First submission: 0.936</li>
<li><span class="t">Mid-Oct</span>Best on the public board: 0.958</li>
<li class="hot"><span class="t">Final</span>Private board, both picks: 0.942</li>
</ol>
</figure>


## I had a second ruler, and I overruled it

The public board scores about 390 hidden studies, roughly 30 % of the test set. My second ruler was a 58-study holdout with radiologist labels that no public model had trained on. Everything else trains on labels parsed from reports, which are noisy.

The holdout correctly vetoed ideas that were also flat on the board. On blend weights it disagreed. The board read my weight variants at 0.955 to 0.958 against a 0.958 base, and the holdout showed gains of up to +0.0048.

I wrote that the holdout was "wrong-signed" and "a veto, never a compass". Then I picked both finals by the public board.


<figure class="fig">
<ol class="flow">
<li><b>Candidate blends</b><span>scored on two rulers</span></li>
<li><b>Public board</b><span>390 studies, 3 decimals</span></li>
<li><b>Gold set</b><span>58 expert-labelled studies</span></li>
<li class="hot"><b>They disagree</b><span>I picked both finals by the board</span></li>
</ol>
<figcaption>Should have been: one final from each ruler.</figcaption>
</figure>


## The private board sided with the holdout

The private board scores the other 910 studies. Both my finals scored 0.942. Silver started at 0.943 (top 321), gold at 0.954.

| Submission | Public (390) | Private (910) | Selected? |
| --- | --- | --- | --- |
| My two finals | 0.958 | 0.942 | yes |
| Logit-mean blend | 0.957 | **0.944** (silver) | no |
| Two holdout-guided weight variants | 0.958 and 0.957 | 0.943 | no |

The board had called these about 0.001 worse than my picks. The private board said about 0.002 better, the direction the holdout had pointed.

## Three decimals were noise

Every public notebook I had submitted as-is also fell to 0.942. I had ranked variants in 0.001 steps on 390 studies, where noise is easily that large. In one family of experiments the displayed score was called right 3 times in 5, and "this beats my best" was right 0 times in 5.

## Use this yourself: Pick finals with two rulers

This applies when a public leaderboard scores a small slice of the test set and you have a second, independent check, such as a clean holdout.

1. Before you see any scores, write down your rule for choosing finals.
2. Build a holdout the public models never trained on, with the cleanest labels you can get.
3. Score every candidate on both rulers. Mark the ones where the rulers disagree.
4. Take final one from the public board's top. Take final two from the holdout's top among the rest.
5. If the rulers agree, spend the second final on the most different candidate, not a near copy.

```
def pick_finals(rows):
    """rows: (name, public_score, holdout_score). Returns two finals, one per ruler."""
    by_public = max(rows, key=lambda r: r[1])
    rest = [r for r in rows if r is not by_public]
    by_holdout = max(rest, key=lambda r: r[2])
    return by_public[0], by_holdout[0]
```

Skip this when the holdout is tiny and noisy, or when it was used to tune the same candidates. Then it is just a second board you have fitted.

## What I'd do differently

- **Pick finals from two independent rulers.** If they disagree and the independent one has a mechanism behind it, take one final from each. I spent both on the same bet.
- **Don't call a signal "wrong" because it disagrees with the board you tuned on.** The more you fit a ruler, the less it tells you.
- **Write the final-selection rule before you see scores.** I improvised it on the last afternoon.
- **In a tie block, expect noise to decide.** Pick the entries most likely to be robust, not the ones that read highest today.
