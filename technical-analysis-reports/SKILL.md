---
name: technical-analysis-reports
description: |
  Write and review technical analysis, investigation, audit, benchmark, or
  recommendation/priority reports so they are accurate, grounded in evidence,
  and readable. Use when producing or editing a findings report, a
  code/design review writeup, a performance study, a ranked list of proposed
  changes, or any document that makes technical claims and recommendations.
  Covers grounding claims in data and demonstration, surfacing unstated
  assumptions, layered adversarial review, single-axis scoring traps,
  presentation conventions, and a consistency-pass checklist for
  heavily-edited documents.
---

# Writing and reviewing technical analysis reports

A report that investigates something and recommends action has three ways to
fail: it can be wrong, it can be right but unconvincing, or it can be right and
convincing but unreadable. Each rule below names the failure it prevents.

## Grounding: make claims defensible

**Ground every load-bearing claim in data or demonstration.** An assertion the
reader has to take on faith is a liability. Prefer, in order: a measured number
with provenance, a concrete artifact (list the actual call sites, quote the
file:line, show the code), or a worked example. Forcing a vague claim to become
concrete is also how you find out it was wrong: an actual code sketch of a
"write-behind cache" proposal can expose a race between eviction and flush
that the prose hid.

```
BAD   There are about ten database queries per request.
GOOD  Seven handlers on the request path issue ten database queries per
      request: <handler, file:line, queries> for each of the seven.
```

**Demonstrate failure-safety, do not assert it.** When a change claims to be
safe (atomic, rollback-clean, crash-consistent), show the mechanism doing the
safe thing. A short example where the error path leaves no broken state is
worth a paragraph of reassurance.

```
BAD   The batch is atomic, so a failure leaves no partial state.
GOOD  If the third write fails, the transaction aborts at <file:line>; the
      first two writes are never visible (worked trace below).
```

**State the load-bearing assumption.** For every benefit or mechanism, ask what
the reader needs to know for it to make sense that you have not said. Benefits
especially rest on a silent condition ("this only helps under concurrent load,"
"only for uploads that include an image," "only when the cache misses"). If a
reader could compute a contradiction from what you wrote (removing one of ten
steps saves the time of all ten), you omitted the fact that resolves it. Say
it.

```
BAD   Skipping the image-resize step cuts upload latency by <N>ms.
GOOD  For uploads that include an image, skipping the resize step cuts
      upload latency by <N>ms. Other uploads never run that step.
```

**Do not score on a single axis.** A benefit/effort or cost/value ranking that
counts only the headline metric (latency, lines saved, dollars) assumes nothing
else matters. Durability, supportability, security, operational risk, and blast
radius can each dominate a change that is positive on the metric. A proposal
that saves 10ms but adds a second JSON parser to track for CVEs, or that skips
the authorization check on a cached path, is not a win the number can see.
Surface the other axes explicitly, and let them veto.

```
BAD   P07: saves 10ms, effort low. Rank 1.
GOOD  P07: saves 10ms, effort low; adds a second JSON parser to track for
      CVEs. Vetoed on supportability.
```

## Review: layer it

When a reader says "I do not see how this works," treat it as a possible
defect; see working-with-sam, "When he challenges a claim."

**Different reviewers catch different classes of error, so layer them.** A
code-level adversarial review (re-derive the arithmetic, read the cited code
for crash-consistency and rollback) reliably catches falsified premises and bad
numbers. It reliably misses correctness in context: how the change behaves
given the operational semantics of the system around it (a load balancer's
retry policy, the connection-draining window during a deploy, a cold cache
after a restart). Get both a code-level pass and a domain or
operational-semantics pass. When no human domain expert is available, spawn a
reviewer prompted specifically to reason about the surrounding system's
behavior, not the function in isolation.

```
BAD   One reviewer: "Review the write-behind cache proposal for
      correctness."
GOOD  Reviewer 1: "Re-derive the latency arithmetic and read the cited code
      for rollback and crash-consistency."
      Reviewer 2: "How does this behave under the load balancer's retries,
      the connection-draining window during a deploy, and a cold cache
      after a restart?"
```

**Investigation and measurement adjudicate each other.** Static analysis and
reasoning generate hypotheses, and they over-predict: static analysis can flag
suspects (lock contention in a connection pool, a slow TLS handshake, a
misconfigured timeout) that live measurement then refutes. Label
pre-measurement claims as hypotheses and let the measurement decide. When a
"confirmed" finding was inferred while setting up an experiment, not observed,
correct the record.

```
BAD   Confirmed: connection-pool lock contention causes the p99 tail.
GOOD  Hypothesis (static analysis, not measured): connection-pool lock
      contention causes the p99 tail. Measurement: <run>, result below.
```

## Presentation: right and readable

For prose (jargon, edit-history narration, dashes, and other tells), run the
writing-review skill.

- **One identifier scheme, defined.** Two parallel numbering schemes (a stable
  ID and a rank, say) confuse when they do not match. Pick one for the running
  text, or define both explicitly and keep cross-references to the stable one.
- **Lead with a summary line; break enumerable content into sub-bullets.** A
  bullet that crams `(1)(2)(3)` or `(a)(b)(c)` into one breathless sentence
  is a wall. Open with a plain statement of what it says, then list the
  items. Reserve prose for linear arguments, and do not force those into
  bullets.

## Consistency pass (run after heavy editing)

A document edited many times, especially by several hands or subagents,
accumulates drift that no single edit introduced. Before calling it done, audit
the whole against itself:

- **Scores and totals match their inputs.** Every stated score equals what its
  own formula and stated inputs produce; the value in a heading matches the
  value in the body.
- **Recurring numbers agree everywhere.** The same measured quantity cited in
  five places is the same number in all five. Watch for two legitimately
  different measurements (a client-wall mean and a server-side span, say)
  getting conflated or labeled as each other.
- **Cross-references resolve.** Every "see section N item M," every "as X
  shows," every "P04's fallback path" points at something that exists and
  says what you claim. Directional references (above, below) survive
  reordering.
- **Counts match enumerations.** "Seven call sites," "three fixes," "22
  proposals" equal the number of items actually listed.
- **Summary matches body.** The executive summary's figures, scores, and claims
  agree with the detailed entries.
- **Ordering invariants hold.** If the list claims to be sorted, it is.

```
BAD   Heading: "P04 (score 12)". Body: benefit 3, effort 3, score = 3 x 3.
GOOD  Heading: "P04 (score 9)". Body: benefit 3, effort 3, score = 3 x 3.

BAD   "Seven call sites:" followed by six bullets.
GOOD  "Seven call sites:" followed by seven bullets, or the count fixed.
```

A script over the file finds score and heading mismatches, arithmetic drift,
cross-reference existence, dashes, and ordering cheaply. Reserve a careful read
for what a script cannot judge: whether a recurring number means the same thing
in two places, and whether the summary faithfully represents the body.

## Process

Delegating the codebase reading while you edit a large report, and asking
subagents for text to apply yourself: see running-rounds. Asking the user to
run something: see working-with-sam, "Reporting."
