---
name: sys-spec
description: Use when the user asks to build, design, or describe a system, model, pipeline, agent, or feature. Rewrites intent in anthropomorphism-free systems terms, emits the SYS 8-slot spec (IN/OUT/STATE/MAP/OBJ/C/FAIL/EVAL), and builds only against that spec — asking, never inventing, when a slot is unspecified.
---

# SYS — Systems Spec Discipline

Follow this before writing any code for a system/model/pipeline/agent request.

## 1. Rewrite intent (anthropomorphism-free)

Scan the request for mind-verbs and rewrite them to systems verbs. Report any hits as a `lint:` line.

| banned | rewrite to |
|---|---|
| understands / understand | encodes / maps; encode / map |
| knows / know | has representation of; store representation of |
| wants to / want to / wants | is optimized to; optimize to; is scored toward |
| tries to / try to | applies map to; apply map to |
| decides / decide | maps to a label / samples from; map to a label / sample from |
| chooses / choose | selects via argmax or sample; select via argmax or sample |
| thinks / believes | assigns score; has posterior / score |
| remembers / remember | stores in state; store in state |
| sees / see | observes; observe |
| is smart / is creative | has lower held-out loss; samples from a higher-entropy proposal |
| should / ought to | is constrained to |
| handles errors / handle errors | maps exception class to recovery; map exception class to recovery |
| user-friendly | meets latency / error / schema budgets |
| AI that / an AI that | map F that; a map F that |

## 2. Emit the 8-slot spec

```
# SPEC <Name>

## IN            what the system takes (typed)
## OUT           what it emits (typed)
## STATE         persisted/none
## MAP           y = F(x) or dataflow, no mind-verbs
## OBJ           what is minimized/optimized
## C             hard constraints
## FAIL          failure → recovery behavior
## EVAL          concrete metrics with thresholds
## status        complete | incomplete: <missing slots>
```

Every slot filled with a typed, testable claim. Example:

```
## IN
ticket : Record{text: str, meta: Record}

## OUT
result : Record{urgency: enum, reply: str, conf: float[0,1]}

## STATE
none

## MAP
embed(text) → classify(urgency) → decode(reply); conf from predictive entropy

## OBJ
minimize CE(urgency) + toxicity(reply) + latency

## C
low-confidence → route human; no PII in reply

## FAIL
empty_text → reject; model_timeout → fallback + human

## EVAL
macro-F1(urgency); PII_leak_rate == 0
```

## 3. Ask, don't invent

If any slot (IN, OUT, OBJ, C, FAIL, EVAL — rare: STATE, MAP) cannot be filled from the request, mark it `UNSPECIFIED` in the spec and ASK the user for it before writing code. Never guess a type, metric, or constraint. Never silently drop a slot.

## 4. Build against the spec

Hold the spec in context and implement only what it says. Prefer small pure functions, explicit types, and tests derived from EVAL + FAIL. Do not add behavior not in the spec.