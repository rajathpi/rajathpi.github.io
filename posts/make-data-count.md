---
title: Finding Data in the Footnotes with Constrained Decoding
description: From a regex-and-random-forest classifier to a Qwen-32B pipeline that extracts dataset DOIs from scientific papers and forces a Primary/Secondary decision with constrained decoding.
meta: Make Data Count — Finding Data References · 4 min read
date: 2025-06
topic: Applied ML
list: Finding data in the footnotes with constrained decoding
summary: 186 of 1,282. Regex finds dataset DOIs; an LLM with one-token decoding classifies them.
---

My LLM kept breaking its own JSON, so I let it answer with one letter. That fixed it.

Make Data Count asks which datasets a scientific paper cites, and whether each is Primary (the authors made it) or Secondary (reused). I finished 186 of 1,282. The one lesson: a multiple-choice answer forced to a single token beat free-form JSON from an LLM.

## Exact tuples, no partial credit

For each paper you emit `(article_id, dataset_id, type)` tuples. The id is a DOI or an accession such as GEO or PDB. Scoring is F1 on exact tuples, so a wrong type or a malformed id costs as much as a miss.

It is hard because dataset references look like ordinary citations. Primary versus Secondary also depends on phrasing like "we collected" versus "obtained from".

## First, no LLM at all

My first versions used regex and a classic classifier. Regex patterns mined candidate ids from the XML or PDF text. A voting ensemble classified each one from cue phrases in a 500-character window.

The useful step was negative sampling. I labelled every regex hit that was not a true citation as `Not_A_Citation`. That taught the classifier to reject the flood of false positives.

## Then the JSON broke

Primary versus Secondary is reading comprehension, so features hit a ceiling and I added an LLM. I cut the text at the references heading, found DOIs by regex, and gave Qwen-3 8B a short context for each. It returned JSON with the DOI and a class.

I dropped any id that appeared in three or more papers, since those are journal and license links. But free-form JSON is fragile. One stray token breaks the parse and the citation is silently lost.

## So I let it say one letter

The final pipeline keeps regex for candidates and uses Qwen2.5-32B-Instruct (AWQ) on vLLM to decide.


<figure class="fig">
<ol class="flow">
<li><b>Regex DOIs</b><span>from text cut at references</span></li>
<li><b>LLM pass 1</b><span>normalize the DOI</span></li>
<li class="hot"><b>LLM pass 2</b><span>choose A, B or C</span></li>
<li><b>Filter, dedup</b><span>by confidence margin</span></li>
<li><b>submission.csv</b><span>one row per dataset</span></li>
</ol>
</figure>


Pass 1 extracts and cleans the DOI. Pass 2 frames Primary, Secondary or None as a choice among A, B and C, and a logits processor allows exactly one of those tokens.

```
mclp = MultipleChoiceLogitsProcessor(tokenizer, choices=["A", "B", "C"])
llm.generate(prompts, vllm.SamplingParams(max_tokens=1,
    logits_processors=[mclp], logprobs=3, temperature=0))
```

There is no JSON to parse and nothing to drop. vLLM's V1 engine rejects logits processors, so I set `VLLM_USE_V1="0"`.


<figure class="fig">
<div class="vs">
<div><b class="k">Free-form JSON</b><p>One stray token breaks the parse; the citation is lost.</p></div>
<div class="hot"><b class="k">One letter, A/B/C</b><p>Nothing to parse, nothing dropped.</p></div>
</div>
</figure>


## Confidence came for free

The three logprobs give a margin between the top two choices. I drop `None` predictions with a margin under 0.5.

I then dedup on article and dataset id. Rows with data-keyword context and higher confidence win ties.

## Use this yourself: Constrain the answer to one token

This applies when an LLM must pick from a small fixed set of answers and a parse failure costs you a row.

1. Rewrite the task as a multiple choice with short labels: A, B, C.
2. Allow only those tokens at the first generation step. Take one token and stop.
3. Read the log-probabilities of the allowed tokens, not just the winner.
4. Use the gap between the top two as a confidence. Drop or flag low-margin answers.
5. Choose the margin cutoff on a labelled sample, not by feel.

With vLLM a logits processor does the masking. The core of the decision is small:

```
import math

def pick(logprobs, allowed=("A", "B", "C")):
    """logprobs: token -> logprob from the model's last step. Returns (choice, margin)."""
    ranked = sorted(((t, logprobs[t]) for t in allowed if t in logprobs),
                    key=lambda x: -x[1])
    if not ranked:
        return None, 0.0
    margin = ranked[0][1] - ranked[1][1] if len(ranked) > 1 else math.inf
    return ranked[0][0], margin
```

This does not suit open-ended answers, such as extracting a string. There you still need free text or a grammar.

## What I'd do differently

- Bring back the accession patterns (GEO, SRA, PDB, UniProt). The final notebook only chases DOIs, which costs recall.
- Sweep the 0.5 threshold and the 150-character window. I tuned both by feel.
- Save a local score. My final notebook does not persist one, so I can't quote a number I can't reproduce.
- Keep the split: code finds candidates, the LLM judges, constrained decoding guards the output.
