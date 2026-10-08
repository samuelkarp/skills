---
name: mutation-test-triage
description: |
  Decide which tests in a suite are worth keeping, by breaking the code and
  recording which tests notice. Use when asked to cut, audit, or assess a test
  suite, when judging whether a test is a duplicate, when a suite feels too
  large for the code it covers, and before deleting any test on the grounds
  that something else covers it. Covers building a kill matrix, reading it
  against the test-standards judgments, sizing clusters without counting
  incidental failures, finding under-tested code from surviving mutants, and
  keeping the runs affordable.
---

# Mutation test triage

Reading a test tells you what it looks like it does. Breaking the code tells
you what it does. Every judgment in this skill rests on the second.

The terms here (kill matrix, sole catcher, mutant) are working terms. In
reports to Sam, translate them as test-standards, "Reporting test findings to
Sam", lays out.

## Why reading fails

A test's name, its setup and its assertions all describe an intent. None of
them establish that the assertion can fail. A test that compares a value to
itself, an assertion that nothing happened against a double that never
records, and a sort test whose fixture is already in order all read as
guards.

```
BAD   Keep "sorts rows by date": its name and assertions cover the
      comparator.
GOOD  In one command: make the comparator return 0, run the file,
      restore. The test still passes because the fixture rows are already
      in order. Report that it guards nothing.
```

```
BAD   Keep the eight "makes no request" tests; they guard the no-network
      rule.
GOOD  Make the code send a request on the path each test exercises, run
      the file, restore. Report the tests that still pass: nothing in
      their file ever causes a request, so the counter never records one.
```

A claim made by reading that a test is a duplicate is often wrong, and wrong
in one direction: the test is the only thing guarding a rule.

```
BAD   Cut TestTrimSpace: TestNormalize covers the same rule.
GOOD  Break the trim rule and run both: only TestTrimSpace fails. Keep
      it.
```

## Who runs it

In a delegation cycle, an implementer or reviewer runs the matrix. The
orchestrating main agent briefs the work and relays the result (see
running-rounds).

```
BAD   (main agent, mid-cycle) Break src/filter.js rule by rule and run
      the tests yourself.
GOOD  Brief the reviewer to build the matrix for src/filter.js and report
      which tests fail for which break.
```

## The procedure

**1. Enumerate rules, not files.** A rule is one branch, guard, comparison or
constant the software depends on. Work from the source, not from the test
names.

**2. Break each rule, one at a time, with a plausible bug.** Invert a
condition, return a wrong value, shift a boundary by one, or skip one step.
Never delete the covered code: a test fails when its subject is gone without
proving it checks the subject's behavior. Break, run, and restore in one
command, so nothing stays in the tree. Keep the break minimal: a broad break
fails everything and tells you nothing.

```
BAD   Delete the `if n > max` block, run the file, restore it later.
GOOD  In one command: change `n > max` to `n >= max`, run the file,
      restore the file.
```

**3. Record which tests fail.** This is the kill matrix: rules down one axis,
tests along the other. Build it from single-file runs where you can; a whole
suite run per mutant is what makes this method look expensive.

**4. Read the matrix.** The matrix is the measurement. What to do with each
result is the judgment in test-standards.

| Result | Judgment (test-standards) |
| --- | --- |
| A test fails under no mutation | It caught none of the breaks tried. A case covering a category the spec lists stays; otherwise it is a candidate to cut ("Over-testing"). |
| A test is the only one failing under some mutation | It alone guards that rule. It stays when the break is a plausible bug ("Over-testing"). |
| Several tests fail under the same mutation and no other | A cluster. Keep the one whose failure message names the rule best ("Over-testing"). |
| A mutation fails no test | A survivor. It needs a test when the behavior is promised and a user would see it; a survivor no realistic rewrite would produce needs no test ("When a gap needs a test", "Over-testing"). |

The last row matters as much as the others. A suite that is smaller and has
unnamed holes is worse than the one you started with.

## Sizing a cluster

The tests that fail under a mutation are not the cluster. Most of them fail
incidentally: they touch the mutated code on the way to asserting something
else.

Before treating a set as a cluster, ask of each member what it would still
assert if the mutated rule were removed from the software. If the answer is
"something else", it is not a member.

```
BAD   Fourteen tests fail under the filter break: a cluster of fourteen,
      cut thirteen.
GOOD  Eight of the fourteen still assert other rules with the filter rule
      gone. The cluster is the other six; keep the one that names the
      filter rule best.
```

```
BAD   Ten tests fail under the track break: cut nine.
GOOD  Break each branch of track separately. Each of the ten is the only
      test failing for its branch; keep all ten.
```

## Cost, and how to keep it affordable

A full suite run per mutant is the trap. Two hundred mutants at thirty seconds
is nearly two hours, serially, and parallel test processes are often barred by
memory limits.

- Run only the test files that can reach the mutated code. A single file is
  usually one to three seconds.
- Where cross-file duplication is the question, a whole-suite run is worth it,
  but sample: a hundred well-chosen mutants beat three hundred mechanical ones.

The rule on run budgets for whoever briefs this work is in delegation-brief,
"A budget that forces guessing".

## Removing a test

Say, for each removal, what the test asserted and which surviving test fails
under the mutation that names that rule. That sentence is the evidence, and it
lets someone else act on the decision without redoing the work.

When a test survives against a proposal to cut it, say why in the same form:
the mutation it alone catches.

## Adding a test

A test added to close a gap is checked the same way. Reopen the gap, run the
file, and confirm the new test fails. A test written for a hole that still
passes when the hole is reopened has closed nothing.
