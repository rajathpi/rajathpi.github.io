---
title: Teaching DeBERTa to Read Student Math Mistakes
description: Turning a student's written math explanation into a top-3 misconception prediction with DeBERTa-v3 — LB 0.925 / CV 0.930+ and a multi-model ensemble.
meta: MAP — Charting Student Math Misunderstandings · 4 min read
date: 2025-07
topic: Applied ML
list: Teaching DeBERTa to read student math mistakes
summary: Misconception prediction from written explanations; the starter notebook has 105+ upvotes.
---

The largest model I trained scored worse than the base one. It still earned its place in the final blend.

The Kaggle MAP competition asks you to predict a student's math misconception from their written explanation. I let DeBERTa-v3 read the text instead of using TF-IDF. My public starter notebook reached LB 0.925 and earned 105+ upvotes, and a blend of four checkpoints finished the work.

## A ranking problem on text

Each row has a math question, the student's chosen answer and a short explanation. The label is one `Category:Misconception` string.

The metric is MAP@3. You submit three labels per row: full credit if the first is right, half for the second, a third for the third. So the job is ranking, not single-label classification.

## One string in, three labels out

I joined the two label columns into one class and fed DeBERTa a plain string of question, answer and explanation.

```
train['target'] = train.Category + ":" + train.Misconception
```

Missing misconceptions become the token `NA`, so a correct answer is just another class. I left correctness out of the starter text so the model had to infer it.


<figure class="fig">
<ol class="flow">
<li><b>Question + answer + explanation</b><span>one plain string</span></li>
<li><b>DeBERTa-v3</b><span>max length 256</span></li>
<li><b>Softmax</b><span>over classes</span></li>
<li class="hot"><b>Top-3 labels</b><span>scored by MAP@3</span></li>
</ol>
</figure>


## Choose checkpoints on the real metric

I wrote a custom MAP@3 function so the Trainer picks checkpoints on the competition metric, not accuracy. Other settings were learning rate 5e-5, a cosine schedule and dynamic padding.

- DeBERTa-v3-xsmall, 10 epochs: CV 0.920+.
- DeBERTa-v3-base, 6 epochs: CV 0.930+.

## Large lost to base

I tried richer prompts with all answer options and a correctness flag. I also trained DeBERTa-v3-large, using gradient accumulation and checkpointing to fit memory. One large run landed near CV 0.926, below base.


<figure class="fig">
<div class="vs">
<div><b class="k">Base, CV 0.930+</b><p>Scored higher on its own.</p></div>
<div class="hot"><b class="k">Large, CV ~0.926</b><p>Scored lower, but added diversity to the blend.</p></div>
</div>
</figure>


Its value showed up later, as diversity in the ensemble. I also built a TF-IDF feature notebook for anyone who wants a light model in the blend.

## Four checkpoints, one blend

An inference-only notebook loads four fine-tuned models and blends their probabilities.

| Model | Reported score |
| --- | --- |
| xsmall (run 1) | LB 0.925 |
| xsmall (run 2) | LB 0.931 |
| large | LB 0.927 |
| base | 0.920 |

I tried ten blending rules. The default is performance-squared weighting, which leans on the strong models and keeps some diversity. The notebook times itself to stay inside the roughly 9-hour inference limit.

## Use this yourself: A weaker model can still earn a blend slot

This applies when you can train several models and out-of-fold predictions are cheap to keep.

1. Save out-of-fold probabilities for every model, scored on the real metric.
2. Take your best model as the base. Add the weaker one at a small weight, such as 0.3.
3. Compare the blend's CV score with the base alone. Keep the model only if it rises.
4. Check how often both models are wrong on the same rows. A low overlap means the weaker model is adding something new.
5. Use CV to set the weights, never the public board.

```
import numpy as np

def map3(p, y):
    top3 = np.argsort(-p, axis=1)[:, :3]
    hit = top3 == y[:, None]
    return (hit / np.array([1, 2, 3])).sum(1).mean()

def blend_gain(p_strong, p_weak, y, w=0.3):
    """Return (blend - strong) MAP@3 on out-of-fold probs, and wrong-answer overlap."""
    blend = (1 - w) * p_strong + w * p_weak
    wrong = (p_strong.argmax(1) != y) & (p_weak.argmax(1) != y)
    both = wrong.sum() / max(1, (p_strong.argmax(1) != y).sum())
    return map3(blend, y) - map3(p_strong, y), both  # both near 1 = no diversity
```

This fails when the weak model is just a worse copy of the strong one, with the same mistakes. Then the blend only adds noise.

## What I'd do differently

- Report one tuned final submission. These scores are per-run numbers from my notebooks, not a single final result.
- Test the richer prompt on the base model before scaling to large.
- Keep splitting work: train in one notebook, save the model, run internet-off inference in another.
- Keep choosing checkpoints on MAP@3, since the metric rewards a good top 3.
