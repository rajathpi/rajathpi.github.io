---
title: ARC Prize 2025: Solving Puzzles With No Pretraining
description: My ARC Prize 2025 entry trained a tiny network from scratch on each puzzle at test time — a per-puzzle CompressARC solver engineered to fit thousands of steps into Kaggle's 12-hour limit.
meta: ARC Prize 2025 · 5 min read
date: 2025-11
topic: Reasoning (ARC Prize)
list: ARC Prize 2025: solving puzzles with no pretraining
summary: 124 of 1,455 (top 9 %) with a per-puzzle CompressARC solver fitted into 12 hours.
home: A tiny network trained per puzzle at test time.
---

The notebook I ran for ARC Prize 2025 finished 124 of 1,455 (top 9%) on ARC-AGI-2. The solver was adapted from a public CompressARC-based notebook that trains a small network from scratch on each puzzle. The hard part was throughput, not the model. The plan wanted about 2300 steps per puzzle, and the cell that ran used a small fraction of that.

## One tiny network per puzzle

Most strong ARC entries lean on scale. This one uses no pretraining, no external data and no search. For each puzzle it starts a small network from random weights, trains it on that puzzle's train pairs only, and predicts the test output.

CompressARC (Liao and Pari, 2025) frames this as [minimum-description-length compression](https://iliao2345.github.io/blog_posts/arc_agi_without_pretraining/arc_agi_without_pretraining.html). A tiny network of about 76K parameters is fit per task with a VAE-style loss, so gradient descent does the reasoning.

## The original blew the clock

The [competition](https://www.kaggle.com/competitions/arc-prize-2025) runs a Kaggle notebook offline, within 12 hours, scored pass@2. CompressARC's original setup solved puzzles in series, underused a single GPU and, as the notebook admits, "blew past the time budget". A per-puzzle method is parallel only if you schedule it that way.

So the notebook is a scheduler. The network internals live in imported modules from the `compressarc` dataset. The notebook calls `solve_task.solve_task(...)` once per puzzle and handles memory probing, parallelism, timing and `submission.json`. One model-side change was rewriting `layers.direction_share()`, for a 5 to 10% speedup.

## Probe, then pack


<figure class="fig">
<ol class="flow">
<li><b>Memory probe</b><span>2 steps of every puzzle</span></li>
<li><b>Timing probe</b><span>10 steps at chosen parallelism</span></li>
<li class="hot"><b>Pick step budget</b><span>largest that fits 12 hours</span></li>
<li><b>Launch puzzles</b><span>while memory and CPU allow</span></li>
</ol>
<figcaption>The planned scheduler.</figcaption>
</figure>


First a memory probe runs 2 steps of every puzzle to measure its GPU memory. Then a timing probe runs 10 steps at the chosen parallelism to measure seconds per step. The main run picks the largest step budget that fits 12 hours. For 120 puzzles the plan estimates about 2300 steps each.

The scheduler reads free GPU memory, subtracts a 6 GB buffer, and launches puzzles while memory and CPU count allow. A 600 s timeout kills runaway puzzles, and a global end-time check stops the run before the deadline.

## What the notebook actually ran

The active cell is more conservative than the plan. It runs a 5-step estimate and a 20-step main run with a flat 1 GB per task, far below the 2300-step target. It is safe, but it costs fit quality.


<figure class="fig">
<div class="vs">
<div><b class="k">The plan</b><p>Probe memory and timing, then about 2300 steps per puzzle.</p></div>
<div class="hot"><b class="k">What ran</b><p>A 5-step estimate, then a 20-step main run.</p></div>
</div>
</figure>


I won't dress the rest up. The notebook prints no score; for calibration, CompressARC reports about 20% on ARC-AGI-1 eval and about 4% on ARC-AGI-2. Augmentation and the two predictions come from the imported `solve_task`, not from cells I wrote, so I describe them only at the method level.

## Use this yourself: fit test-time training to the clock

This applies when you train or adapt a model per task at test time under a hard time limit, as in a Kaggle notebook with a fixed number of hours.

1. Probe memory first: run a couple of steps of every task and record its peak GPU memory.
2. Work out how many tasks fit in parallel from free memory minus a safety buffer.
3. Probe time: run a few steps at that parallelism and measure seconds per step.
4. Pick the largest step count per task that fits the limit, with a reserve for slow tasks and for writing the submission.
5. Add a per-task timeout and a global end-time check so one bad task cannot sink the run.

```
def parallel_for(free_gb, per_task_gb, buffer_gb=6):
    return max(1, int((free_gb - buffer_gb) // per_task_gb))

def pick_steps(n_tasks, total_s, sec_per_step, parallel, reserve=0.1):
    rounds = -(-n_tasks // parallel)           # ceil: batches of tasks
    return int(total_s * (1 - reserve) / rounds / sec_per_step)

# probes said ~1.2 GB per task and 4 s per step; 20 GB free
p = parallel_for(20, 1.2)
print(p, pick_steps(120, 12 * 3600, 4.0, p))   # 11 883
```

Seconds per step usually grows with parallelism, so measure at the width you will really use, not on one task alone.

## What I'd do differently

- **Run the full probe-then-pack plan.** Quality scales with steps per puzzle, and the fallback used a tiny fraction of the plan.
- **Replace the flat 1 GB assumption** with the measured memory probe.
- **Save the score inside the notebook,** so the run can be judged from its own output.
- **Treat packing as the lever.** The ceiling is memory-limited parallelism inside 12 hours.
