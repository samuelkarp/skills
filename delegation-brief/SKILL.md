---
name: delegation-brief
description: |
  Write the brief for a subagent so it produces work you can trust and act on.
  Use whenever dispatching an agent to implement, analyze, review, or rewrite
  anything, and when a delegated round comes back wrong in a way the brief
  caused. Covers the constraints that must appear every time, the standard of
  evidence to demand, giving an agent permission to disagree and to stop, and
  the brief-side mistakes that produce confident wrong answers: budgets that
  force guessing, invented categories, prescribed method, and omitted
  prohibitions.
---

# Writing a delegation brief

An agent's output is shaped more by the brief than by the agent. Most bad
rounds trace to a sentence in the brief, not to the work.

## Constraints that go in every brief

Omitting one is how it gets violated. A standing rule that lives only in your
head is not a rule.

- **Safety limits of the machine.** Memory, concurrency, what may not be run.
- **Private data.** When the workspace holds private data, name it and say do
  not read it. Moving the file out of the agent's reach is the durable fix;
  until then the line goes in every brief.

  ```
  BAD   Review the parser in src/capture/ and report defects.
  GOOD  Review the parser in src/capture/ and report defects. Do not read
        captures/session.har: it holds private data.
  ```

- **What must not be touched.** Deferred work, another agent's files, history
  that must not be rewritten.
- **Whether to push.** Say it explicitly. An agent that has been told to
  report and clean up may read a later instruction as lifting an earlier
  constraint.

Where these repeat across many briefs, move them into a file the agent loads
automatically. Retyping is where they get dropped.

Two other skills hold the lines for their own situations. Add them where they
apply:

- running-rounds, "Mechanics that hold every time": the stalled-agent
  paragraph for long-running work, keeping large fixtures out of context,
  and a scratchpad prefix per parallel agent. Its "Rounds and commits are
  separate questions" covers naming the commits in the brief, and "Folding
  fixes and rewriting the series" covers the published boundary.
- test-standards, "Briefing implementers and reviewers": the lines for any
  brief that writes or reviews tests.

## Demand evidence, not assertion

Ask for the check, not the conclusion. The difference between "confirm the
tests pass" and "make the code misbehave the way a real bug could (not delete
it), confirm the test fails, and say which" is the difference between a round
you can trust and one you cannot. running-rounds, "Checking a subagent's
claim", sets how much each kind of reported result is believed; ask for the
kind it trusts.

Useful forms:

- For a fix: show the defect first, then fix it.
- For a rewrite: state the invariant that must hold, and require the command
  and its output. A tree that must be unchanged is checkable; "carefully" is
  not.
- For an analysis: require the evidence per finding, in a form someone else
  can act on without redoing the work.
- For a deletion: require what covered it before and what covers it now.

## Give permission to disagree and to stop

An agent told to do nine things will do nine things. Say plainly that finding
one of them wrong is a legitimate result, and that a partial job which is
verified beats a complete one that is not. A round that declines part of its
brief with a reason often brings back the most useful finding.

```
BAD   Do these nine things.
GOOD  Do these nine things. If one of them is wrong, decline it and say
      why; that is a legitimate result. A verified partial job beats an
      unverified complete one.
```

Ask what it declined and why, in the report format, so the judgment surfaces
instead of being silently absorbed.

## The four brief-side mistakes

**A budget that forces guessing.** Constrain cost only where you know the
cost. A run budget too tight for the measurement makes the agent size its
findings by reading. That produces findings that look like evidence and are
not, and every round built on them inherits the error. If the work needs
measurement, either pay for the measurement or say the finding is a guess.

```
BAD   Audit the suite for duplicate tests. Run at most ten test files.
GOOD  Audit the suite for duplicate tests by breaking the code and running
      the tests that reach it. Label any finding you size without a run
      as a guess.
```

**An invented category.** Do not hand an agent a taxonomy the user did not
give. Words like "keeper" or "housekeeping" become the frame the agent works
in, and then come back in its report looking like the user's policy. Quote the
user where the user has spoken; working-with-sam, "Holding scope", anchors
each requirement in a brief to a sentence the user wrote.

```
BAD   Sort the tests into keepers and housekeeping, and cut the
      housekeeping.
GOOD  The request: "<the user's sentence>". For each test, report the
      break only it catches, or that it catches none.
```

**A prescribed method where the user asked for independence.** If the point of
a round is a fresh look, describe the goal and the standard, and let the agent
choose how. Saying how to find the answer determines the answer.

```
BAD   Fresh review of the parser: start at the tokenizer and check each
      state transition against the table in DESIGN.md.
GOOD  Fresh review of the parser. Goal: defects a caller would see.
      Standard: each finding gives the input and the wrong output. Choose
      your own method.
```

**A stale premise.** A brief that names a defect which was already fixed sends
an agent to repair working code, and it will often find a way to comply.
Settle each premise with a cheap command (`git log`, `git status`), or label
it unverified and have the agent confirm it before acting on it.

```
BAD   Fix the off-by-one in pageCount.
GOOD  Unverified: pageCount may drop the last page. Show a failing case
      first; if none fails, report that and stop.
```

## Report format

Ask for a bounded report: a line count, and the specific questions you need
answered. Long reports bury the finding that matters. Require it to name what
it could not do and what it left, so the next brief starts from the truth.
