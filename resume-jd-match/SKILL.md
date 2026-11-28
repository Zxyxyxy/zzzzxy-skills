---
name: resume-jd-match
description: Evaluate how well a resume matches a job description by splitting JD requirements deterministically, asking an LLM only for per-requirement judgments, validating evidence against source text, and deriving the final score by rules.
---

# Resume JD Match

Use this skill when the user asks to compare a resume/CV with a JD, explain fit/gaps, score a candidate against job requirements, or run the existing WhatAJob-style resume/JD evaluation flow.

## Core Method

The important invariant is that the JD requirement list is an external truth, not something the model invents.

1. Split the JD into requirement items before calling any model. Prefer `scripts/jd.py` and its `split_requirements(raw)` function.
2. Give the model the numbered requirement list and the exact requirement count. The output must contain the same number of items in the same order, with each `requirement` copied from the split JD text.
3. Let the model judge only each requirement's status: `matched`, `gap`, or `unknown`. Do not trust the model's final score.
4. Validate the returned JSON with `scripts/validate.py`. Treat validation errors as a failed result that needs correction or rerun.
5. Derive the final `score` and `verdict` with `scripts/verdict.py`, using the per-requirement statuses and gap severities.

## Output Contract

The model-facing JSON should follow this shape:

```json
{
  "overall": {
    "score": 0,
    "verdict": "mismatch",
    "oneLine": "short explanation"
  },
  "requirements": [
    {
      "requirement": "exact JD requirement text",
      "status": "matched",
      "evidence": {
        "section": "resume section name",
        "quote": "exact quote from resume"
      }
    }
  ],
  "meta": {
    "jdRequirementCount": 0
  }
}
```

For `gap`, include `severity` as `blocking`, `major`, or `minor`, plus a concrete `suggestion`. For `unknown`, include `whyUnclear`.

Evidence quotes must be copied from the resume text. The validator compares after NFKC normalization and whitespace collapsing, so layout whitespace from PDF extraction is tolerated but hallucinated quotes are not.

## Scripts

The skill includes the original zero-dependency Python execution layer in `scripts/`:

- `jd.py` splits JD requirements deterministically.
- `llm.py` calls Bailian/Qwen through the OpenAI-compatible endpoint using only the Python standard library.
- `validate.py` checks coverage, exact JD requirements, and exact resume evidence.
- `verdict.py` derives score and verdict from per-requirement statuses.
- `check_key.py` performs a cheap Bailian connectivity check.
- `run_eval.py` runs fixture-based evaluation using the included synthetic `fixtures/`.
- `pick_jds.py` can create JD fixtures from a local `jobs.db` using an explicitly supplied `--db` path (opened read-only); use `--output` to keep private fixtures outside the repository.

If using Bailian/Qwen, require `DASHSCOPE_API_KEY`; optional overrides are `QWEN_BASE_URL` and `QWEN_MODEL`. See `scripts/env-example.txt` for the expected environment variables.

## Reporting

When answering the user, make clear that the displayed score/verdict is rule-derived. If the model's self-reported `overall` disagrees with `scripts/verdict.py`, report the rule-derived result and mention the disagreement only when useful.

## Offline check

Run `python3 scripts/run_eval.py --dry` from this Skill directory. It checks pre-split synthetic fixtures against the validator and scoring rules; it does not call a model or measure model accuracy. Run without `--dry` only when a configured model call is intended.
