---
name: test-standards
description: |
  What makes a test worth having, in any language. Use when writing or
  reviewing tests, when briefing an implementer or reviewer about tests, when
  deciding whether a review finding, coverage hole, or surviving mutant (a
  deliberate break no test caught) needs a test, when building a fake server,
  canned response, or fixture for an external API, and when writing runnable
  examples such as Go Example functions. Covers testing behavior over restated
  data, expectations that match what was asked, error assertions, the cost of
  over-testing, fakes built from real responses, waiting on goroutines with a
  signal, examples that cover every path they teach, and how to report test
  findings in plain words.
---

# Test standards

## Purpose

A test exists to catch a defect a user would see, in behavior that is
promised. "Promised" means the requirements, the design doc, or the
documented API. "A user would see" means some value, output, or effect that a
caller or maintainer observes changes when the code is wrong.

Every test is also a cost: it is read, maintained, and updated on every
legitimate change. A test that catches nothing a user would meet is a cost
with no return. Write no tautological tests, no duplicative tests, and no
tests that are too trivial.

Related skills, not repeated here:

- **mutation-test-triage**: the procedure for auditing a whole suite by
  breaking code and recording which tests notice (keep, cut, find holes).
- **go-test-comments**: Go test style (failure messages, table tests, cmp,
  t.Fatal versus t.Error).

Terms used below. *Mutation*: a small deliberate break in the code that a real
bug could cause (invert a condition, return a wrong value, an off-by-one, skip
one step). *Survivor*: a break that no test catches. These are working terms
for you. See "Reporting" before using them with Sam.

The pairs below are examples to reason from, not rules to match.

## What holds every time

These are mechanical. Do them without being asked.

1. **Break the code and watch the test fail.** For every test you add, and
   every test you claim guards something: make the code it exists for
   misbehave in a way a real bug could, run it, confirm it fails, restore. Do
   the break and restore in one command so nothing stays in the tree. The
   break is a plausible bug (a wrong value, an inverted condition, an
   off-by-one, a skipped step), not deleting the function or the covered
   code: a test fails when its subject is gone without proving it checks the
   subject's behavior. A test that still passes with its subject misbehaving
   guards nothing. Before adding a test, ask what plausible bug makes it
   fail.

   ```text
   BAD   add TestApplyRlimitsInfinity, run go test ./..., see it pass,
         report the test added
   BAD   in one command: delete the applyRlimits call, run
         TestApplyRlimitsInfinity, see it fail, restore
   GOOD  in one command: make applyRlimits apply the limit to the wrong
         resource, run TestApplyRlimitsInfinity, see it fail, restore;
         report that break and that it failed
   ```

2. **Re-check against the final tree.** A "this break is caught by test X"
   claim is true only for the tree it was run on. A later commit in the same
   round can move or delete the only test that caught it. Re-run the check
   against the final content of the round, and record caught or survived for
   each row so a survivor has somewhere to go.

   ```text
   BAD   | break chip color | caught by <test> |
         (run at the commit that added the color; the next commit moved
         the test's two closed rows to published)
   GOOD  | break chip color | survived: whole suite passes |
         (re-run on the final tree of the round)
   ```

3. **Assert an error's identity or data, not its wording.** A test checks
   error identity (`errors.Is`, `errors.As`, a sentinel), fields on an error
   type, or that the call fails. It does not compare message strings or match
   phrasing. One exception, from the Go wiki: a test may check that the
   package's own error names the offending parameter or input. When the
   package defines no error kinds to match, checking that the call fails is
   enough; do not add exported error API only for a test.

   ```go
   // BAD: the wording is not contractual.
   if err == nil || !strings.Contains(err.Error(), "denied") {

   // GOOD: asserts the contract. (Sentinel name illustrative: use the one
   // the package exports, or errors.As and a field on its error type.)
   if !errors.Is(err, ErrDenied) {

   // GOOD: the error names the bad parameter, which the caller relies on.
   if err == nil || !strings.Contains(err.Error(), "region") {
   ```

   When one wording check is flagged, sweep every test in scope. The grep
   finds candidates; fix the ones that assert wording, and leave logging and
   parameter-name checks alone.

   ```text
   BAD   fix the message check in the one flagged test
   GOOD  grep -rn 'err.Error()\|\.Error() ==' --include='*_test.go' .
         and fix every hit that asserts wording, in every test file
   ```

4. **Removing an assertion does not remove coverage.** Before you delete a
   message check or a duplicate, break the logic it guarded and confirm some
   other check still fails. If none does, write a replacement that asserts
   data (`errors.Is`, `errors.As`, or error fields).

   ```text
   BAD   delete the strings.Contains(err.Error(), "denied") check; the
         suite passes
   GOOD  break the denial logic and run the suite; if nothing fails, add
         errors.Is(err, ErrDenied) before deleting the message check
   ```

5. **No test copies the implementation's data.** If the expected value is the
   same table, map, or list as the code under test, the test fails only when
   both are edited together, and any wrong entry is copied along with it.
   Test the effect the data has.

   ```go
   // BAD (TestRlimitResources): want is a character-for-character copy of
   // the rlimitResources literal in cmd/runj-entrypoint/main.go. The test
   // asserts the two maps equal, then loops over the same pairs and
   // asserts each again.
   want := map[string]int{ /* same entries as rlimitResources */ }

   // GOOD (TestApplyRlimitsInfinity): call applyRlimits with a limit the
   // signed FreeBSD rlim_t type cannot hold, then assert the value
   // getrlimit(2) reports.
   ```

6. **A fake of an external service uses field names from a real response.**
   See "Fakes and live services".

7. **A runnable example's output covers every path it teaches.** See
   "Examples".

8. **Wait on a signal, never a sleep-and-recheck loop.** When a test waits
   for another goroutine, the code under test or the test double signals the
   event (a channel closed or sent on, a sync primitive). A timeout is only a
   failure bound. Do not propose a polling loop as a simplification of
   signaling code. This is about test code; an agent polling a log file while
   it runs commands is a separate matter.

   ```go
   // BAD: replace the listener's changed channel with a poll.
   for l.accepted() < 2 {
       time.Sleep(time.Millisecond)
   }

   // GOOD: the listener closes and replaces changed on each accept.
   for l.accepted() < 2 {
       select {
       case <-l.changedCh():
       case <-time.After(5 * time.Second):
           t.Fatal("listener: timed out waiting for 2 accepts")
       }
   }
   ```

## Test the behavior, not the setting

A test that a setting was applied must exercise what the setting controls.
Reading the configured value back shows the value was stored. It still passes
if the flag is wired to the wrong capability, ignored, or documented wrongly.
A test with `allow.suser` runs something that depends on `allow.suser`.

For each flag, find the operation it gates and run it, asserting it succeeds
when granted. When the operation needs infrastructure the test host lacks,
look for a distinguishable error (an `EPERM` failure versus an
unsupported-operation failure often separates "denied" from "allowed but
nothing to act on"). Treat "no safe probe exists" as a claim to check against
the source, not a reason to settle for readback.

```text
BAD   run jls(8) and assert allow.quotas comes back as the configured value;
      "readback-only: no in-jail capability probe is safe and non-flaky in
      CI"
GOOD  inside a jail with allow.quotas, run the quota operation it gates
      and assert it is not denied with EPERM
```

## Expectations describe what was asked

An implementer writing a test after a fix pins what its code now does, defect
included, and the test then guards the defect. Read every pinned expectation
as a claim about what the user should see. Two questions:

- Does this expectation describe the behavior that was requested?
- If this test passes, is the user's complaint still true?

Against a complaint that a chip's loading count sits frozen, a test pinned
the chip across three completed reads:

```text
BAD   Loading (3 left), Loading (3 left), Loading (2 left)
GOOD  the count drops by one as each read completes
```

The BAD sequence is the count failing to drop, recorded as expected; at
thirty reads it is the frozen number. An internally accurate number that
does not display is still the defect. Tell reviewers by name to check each
expectation against the complaint:

```text
BAD   brief: "review the tests for correctness"
GOOD  brief: "for each expected value, ask whether the frozen-count
      complaint is still true when the test passes; flag any that is"
```

## When a gap needs a test (it depends)

Coverage is not the standard. Consequence is. Whether a hole needs a test
depends on two things, and you have to establish both:

- **Is the behavior promised?** If the behavior a survivor changes is an
  implementation detail (which of two failing checks reports first, internal
  ordering, a private helper's shape), the survival is not a gap. Do not add
  a test or a doc sentence that turns it into a contract.

  ```text
  BAD   must-fix: moving the scheme check ahead of the address checks
        returns ReasonScheme for a destination failing both; this is now
        part of the contract, add a test and a doc sentence
  GOOD  not a gap: the documented API never promised which reason a
        double failure returns; no test, no doc sentence
  ```

- **Would anyone see it?** Break the code, confirm nothing catches it, then
  trace the broken value to a surface a user or maintainer looks at. If the
  trace dies (the input cannot occur in real data, or the only values that
  change flow from behavior already declared wrong), close the entry.

  ```text
  BAD   bring Sam: "a write could be confirmed by text inside a <script>
        in a comment body"
  GOOD  close it: none of the four real captured pages has a script, style,
        button, select, option, template, or input element in a comment
        body, so the input cannot occur

  BAD   bring Sam: "the check that stops caching a page older than a
        just-posted comment is untested"
  GOOD  close it: the only values that change when it breaks come from
        counting a member's comment as a review, already declared wrong
  ```

Do this before presenting the entry, never after Sam pushes back. Present a
surviving gap as its consequence, in terms of what the user sees.

If the behavior is promised and visible: it is a gap, write the test. If it
is visible but not promised: report it once as "not covered, and not
promised" and let Sam decide whether it should become a promise. If neither:
drop it. An inherited analysis document or a reviewer's survivor list is a
lead, not evidence; its author was not asked these questions.

## Over-testing (it depends)

A case earns its place when it is the only one that fails for some plausible
defect, or it covers a category the spec explicitly lists. Two cases that
fail on exactly the same breaks are duplicates: keep the one whose failure
names the rule best.

```text
BAD   24 rejection rows in the ID parser's tests, several of them
      exercising the same character-class check
GOOD  one row per check the parser makes; rows that fail on the same
      breaks merged into the one whose name states the rule
```

"Plausible" is the judgment. A survivor that no realistic rewrite of the code
would produce does not need a test. Reviewers hunting survivors push test
counts up; a reviewer must flag redundancy as readily as gaps.

**Edges the spec does not name.** When a side concern appears that no
requirement or design names, state it once in one line and let Sam decide. Do
not brief agents to build rigs (custom locales, fake environments) to prove
it, and do not chain a second fix off the first rig's output.

```text
BAD   brief: "prove the English-prefix match with LC_ALL=C under a German
      locale"; then treat "a test asserting English stderr fails under
      German" as a new fix and ask the reviewer to probe more locales
GOOD  one line to Sam: "detecting `fatal: not a git repository` by its
      English prefix misses it under a non-English locale; neither
      REQUIREMENTS nor DESIGN covers locales. Leave it?"
```

## Fakes and live services

A fake built from the spec tests the code against the spec's beliefs about
the API. Before writing a fake server's canned bodies, get one real response
and copy field names and shapes from it. Then run the built program against
the real service once before calling the feature done.

In the advisory fake below, DESIGN.md said `private_fork` carries `ssh_url`.
Every test passed and three reviewers approved; the first live run added the
git remote with an empty URL, because `private_fork` uses GitHub's
simple-repository schema, which has no `ssh_url`.

```text
BAD   canned body written from DESIGN.md:
        "private_fork": {"ssh_url": "git@github.com:OWNER/REPO-ghsa-xxxx.git"}
GOOD  gh api repos/OWNER/REPO/security-advisories/GHSA-xxxx-xxxx-xxxx
      on a known real advisory; copy the private_fork fields it returns
      into the canned body; run the built binary against GitHub once
```

- Get real data from read-only sources: the user's existing integrations
  first, then a read-only GET on a known, real resource. Never invent
  identifiers (IDs, keys, callsigns) to probe a live service: that sends
  garbage to someone else's service.

  ```text
  BAD   POST made-up flight callsigns to the third-party API to learn
        its contract
  GOOD  read the request and response shapes from Sam's existing
        integration with that API
  ```

- A fake cannot confirm a claim about the service. A claim about what a live
  service sends needs a real response. If none can be obtained, the claim
  stays unverified, a spec is never edited on it, and a brief does not
  present it as a "known issue".

  ```text
  BAD   brief: "known spec issue: GitHub's 502 has an HTML body; verify
        and fix if true"; implementer serves an HTML 502 from its own
        httptest fake, sees go-gh print "502 502 Bad Gateway", edits
        DESIGN.md; relayed as what "the test showed"
  GOOD  brief: "unverified: whether GitHub's 502 body is HTML. A fake
        cannot answer this; do not edit DESIGN.md on it."
  ```

## Examples

A runnable example is documentation meant to be copied. Its passing output is
the part the reader trusts. If the code it teaches has two paths and the
output covers one, the example asserts something it never tested; for an
example that is a false statement, not merely a coverage gap.

- List the paths the example claims to teach. Make the checked output cover
  each, so reverting the fix for any path fails the example.
- Make the call the example exists to demonstrate misbehave the way a real
  bug could (install the policy on the wrong client) and confirm the example
  fails.
- Check which assertion carries each property.

`ExampleWithUpdateHostClient` installs a per-host policy, but built a helper
over the unwrapped client before the hook amended it, so the policy never
reached the helper's requests. Its output covered only the main request path,
so it passed while the helper sent a request the policy should have denied:

```go
// BAD: one path checked; the printed denial reads as proof of both.
// Output:
// main request: denied

// GOOD: every path the example teaches appears in the checked output,
// so reverting the fix for either fails it.
// Output:
// main request: denied
// helper request: denied
```

In a sibling example, deleting the policy install left the printed request
count at 2; the denial line was the assertion doing the work.

## Briefing implementers and reviewers

Name the checks:

```text
BAD   brief: "judge whether any test is tautological"
GOOD  brief: "for each test, make the code it covers misbehave the way a
      real bug could (not delete it) and run it; report the break and that
      it failed, re-run against the final tree"
```

Put these in every test-related brief:

- Each test must fail when the code it covers misbehaves the way a real bug
  could; deleting the covered code is not such a break. Report the break used
  and that it failed, re-run against the final tree.
- Read every expected value as what the user should see; flag any that
  records the complained-about behavior.
- No assertions on error wording anywhere in scope (a check that the error
  names the bad parameter is fine); replace with identity or field checks
  without losing coverage.
- Flag redundancy (cases failing on the same breaks) as well as gaps.
- A survivor is a must-fix only when the behavior is in the requirements or
  documented API and a user would see it. Otherwise report it as "not
  covered, not promised".
- Fakes of external APIs use field names from a real response.
- Concerns outside the requirements and design: one line, no rig.

When relaying a reviewer's result as the orchestrating agent, a break the
reviewer ran is trusted as reported; do not rerun it. Check which tree each
row ran on. A row run at an earlier commit is a claim about the final tree,
not a result: ask the reviewer or a separate agent to re-run it on the final
tree before relaying. Relay what was run apart from what was asserted.

```text
BAD   relay the round's table of breaks, every row "caught", as-is
      (the chip-color row ran at the commit that added the color)
BAD   re-run the chip-color break on the final tree yourself
GOOD  ask the reviewer to re-run every row on the final tree; it reports
      the chip-color break survives, and the headline feature is
      unguarded
```

## Reporting test findings to Sam

Do not use "kill count", "sole catcher", or "mutation" in reports. Translate:

| Working term | Say instead |
| --- | --- |
| mutation testing | breaking the code on purpose to see which tests notice |
| mutant survived | I broke X and no test failed |
| killed by test Y | test Y fails when X is broken |
| sole catcher | the only test that notices when X breaks |
| kill matrix | which tests fail for which break |

Lead with the consequence: what a user would see wrong, and whether that
behavior is promised.

```text
BAD   chip-color mutant survived on the final tree; no sole catcher
GOOD  I made the chip show the wrong color and every test still passed; a
      user would see the wrong color, and the color is this round's headline
      feature
```
