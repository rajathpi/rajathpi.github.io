---
title: Symbolic Search Scored 0 on ARC-AGI-2 Eval
description: A three-engine hybrid symbolic + neural solver for the ARC Prize 2026 (ARC-AGI-2), and an honest account of why symbolic search scores zero on it.
meta: ARC Prize 2026 (ARC-AGI-2) · 5 min read
date: 2026-06
topic: Reasoning (ARC Prize)
list: Symbolic search scored 0 on ARC-AGI-2 eval
summary: Weeks on 19 families of rule-finders: about 6 % of training tasks, none of the evaluation set.
---

I spent weeks on 19 families of symbolic rule-finders for ARC-AGI-2. They solve about 6% of the 1,000 training tasks and **0** of the 120 public-eval tasks. So the ARC Prize 2026 solver I designed is a three-engine hybrid where the neural model carries the score. I have no GPU score yet.

## The bar is 24%

In 2025 the best self-contained Kaggle solution was NVARC at **24.03%**. It used a Qwen3-4B model with a 16-token vocabulary, about 100k synthetic tasks and test-time training. Humans score about 66%. The $1M grand prize needs 85%.

The rules: a Kaggle notebook under 12 hours, no internet, no API models, open source under CC0/MIT-0. The metric is pass@2, and a task counts only if every test input is solved.

## Why the symbolic zero

Each inducer only emits a rule that reproduces every training pair, so precision is near 100%. The families cover colormaps, symmetry, tiling, gravity, compositional chains and more. Eval still sits at 0%.

Depth explains it. I run my DSL primitives generatively: sample a program, sample random input grids, apply the program. Every task is correct by construction, at 0.5 ms per task. My symbolic solver recovers the rule 81% of the time at program depth 1, then 14%, 3% and 1% at depths 2 to 4. Depth is what defeats pattern-matching, so I skew the synthetic curriculum toward depth 3 and 4 to force the neural model to learn composition.


<figure class="fig">
<div class="bars">
<div class="bar"><span class="l">Depth 1</span><span class="b" style="--v:81"></span><span class="n">81 %</span></div>
<div class="bar"><span class="l">Depth 2</span><span class="b" style="--v:14"></span><span class="n">14 %</span></div>
<div class="bar"><span class="l">Depth 3</span><span class="b" style="--v:3"></span><span class="n">3 %</span></div>
<div class="bar hot"><span class="l">Depth 4</span><span class="b" style="--v:1"></span><span class="n">1 %</span></div>
</div>
<figcaption>How often my symbolic solver recovers the rule, by program depth.</figcaption>
</figure>


## The model knows more than it says

The TRM paper reports pass@1 of about 18% but pass@128 of about 30%. The model often produces the right grid and fails to rank it in the top 2. A strong selection layer is worth several points.


<figure class="fig">
<div class="stats">
<div><b>18%</b><span>TRM pass@1</span></div>
<div class="hot"><b>30%</b><span>TRM pass@128</span></div>
<div><b>24.03%</b><span>NVARC, the 2025 bar</span></div>
</div>
</figure>


## Three engines, one selector


<figure class="fig">
<ol class="flow">
<li><b>Task</b><span>train pairs + test input</span></li>
<li><b>C: augment</b><span>8 dihedral × colour perms</span></li>
<li><b>A + B solve</b><span>symbolic rules, neural TTT</span></li>
<li class="hot"><b>D: selector</b><span>verify, consensus, likelihood</span></li>
<li><b>Final</b><span>two pass@2 attempts</span></li>
</ol>
<figcaption>Three engines, one selector.</figcaption>
</figure>


Engine A rarely fires on eval, but each hit is a near-certain slot at no GPU cost. Engine B fine-tunes a LoRA on each task's own augmented pairs, then samples. Engine C is shared: it expands the training data and gives A and B diverse frames. Engine D picks the final two attempts.

Selection works by consensus. I sample many candidates across the 8 dihedral frames and colour permutations, map each back to the original frame, and pick the grid produced most consistently. The aim is to turn the pass@128 ceiling into real pass@2. The logic is unit-tested.

Symbolic can only help. If the battery finds a rule that fits all train pairs, it takes attempt slot 1 and neural consensus fills slot 2. I checked locally that a symbolic rule rescues a task even when a mock neural model votes mostly wrong.

## The 2025 attempt was a different animal

My 2025 kernel was per-puzzle, no pretraining, in the CompressARC lineage. The work there was throughput. It profiled each puzzle's memory and packed about 2300 steps per puzzle on 120 tasks into 12 hours. It has no synthetic pretraining, symbolic layer or consensus.

## Use this yourself: measure your solver on eval, by depth

This applies when you build a hand-written solver for a benchmark whose train and eval sets differ in difficulty.

1. Never judge the solver by its train-set solve rate. Run it on the eval split as early as you can, even on a handful of tasks.
2. Generate synthetic tasks from your own primitives at known program depth 1, 2, 3 and more.
3. Run the solver on each depth and print the solve rate per depth.
4. If the rate collapses after depth 1, the solver is pattern-matching, and eval tasks that need composition will score near zero.
5. Move your effort to what covers deeper tasks, such as a learned model trained on deep synthetic data.

```
import random

PRIMS = [lambda g: [list(r) for r in zip(*g[::-1])],        # rotate 90
         lambda g: [[(c + 1) % 10 for c in r] for r in g],  # recolour
         lambda g: g[1:] + g[:1]]                           # roll rows

def make_task(depth, n_pairs=3):
    prog = [random.choice(PRIMS) for _ in range(depth)]
    pairs = []
    for _ in range(n_pairs):
        g = [[random.randrange(10) for _ in range(5)] for _ in range(5)]
        out = g
        for p in prog:
            out = p(out)
        pairs.append((g, out))
    return pairs

def coverage(solver, max_depth=4, n=200):
    for d in range(1, max_depth + 1):
        hits = sum(solver(make_task(d)) for _ in range(n))
        print(f"depth {d}: {hits / n:.0%}")  # solver(pairs) returns True if solved
```

This only measures depth, not whether your primitives match the real eval tasks, so it cannot replace a real eval number.

## What I'd do differently

- **Get a GPU number first.** Engines A and C alone score about 0% on eval. Whether Edges 1 and 2 add points can only be shown by Kaggle GPU runs, not on my Mac.
- **Check candidate diversity before trusting consensus.** If the neural candidates are all alike, consensus adds little.
- **Budget time early.** Test-time training a 4B model on 120 tasks in 12 hours is tight, so keep LoRA, few steps and a symbolic-only fallback.
- **Aim to approach 24%, not beat it.** That is the realistic floor once the pipeline runs.
