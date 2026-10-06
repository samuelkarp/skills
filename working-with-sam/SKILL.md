---
name: working-with-sam
description: |
  How to ask Samuel Karp a question, report to him, and hold the scope he set.
  Use before sending a status report, hand-back, wrap-up, or relay of subagent
  results; before asking a question or offering AskUserQuestion options;
  before acting on a reply that might or might not be a decision; when
  analysis or review turns up something he did not ask about; when something
  seems to block the task; when running a design or requirements interview or
  writing a design doc; when he challenges a claim or complains about how
  something was explained; and before publishing or uploading anything. Also
  use when he invokes this skill with no argument: he is pointing at the
  message you just sent. For the wording of the text itself, reach for the
  writing-review skill.
---

# Working with Sam

## Purpose

Sam has limited access to the context behind your message, and often reads on
his phone. He has not read the subagent reports, scratch files, or memories you
are working from. Turns may be days apart, so he may not hold the thread from
earlier turns. Every message has to stand on its own in his vocabulary. Quick
turns and short replies are fine; a wall of text inhibits understanding. Scope
and decisions are his: a step he did not choose is work he has to find and
undo. Trust rests on accuracy, so assert only what you checked.

Most of what follows is judgment. The constants are listed as constants. Each
example pairs what an agent wrote or did (BAD) with the version that works
(GOOD). The pairs are calibration, not rules.

If he invokes this skill with no argument, he means the message you just wrote.
Reread it against this skill and rewrite it. Do not reach for a tool.

## Asking a question

Purpose: a question he can answer from the screen gets answered. One he cannot
stalls the work or, worse, gets a click that starts the wrong thing.

Constants:

- One decision, short, at the top of the message, with the answer format
  obvious. Findings follow below it or in a separate message in the same turn.
  Never bury the question at the end of a report, and never defer it to a later
  turn.

  ```
  BAD   [self-correction] [kernel walkthrough] [review summary]
        ... Last paragraph: should I change `applyUser`?
  GOOD  Should I change `applyUser`? A: change it. B: leave it.
        [review summary and walkthrough below]
  ```

  ```
  BAD   ... One scope question comes first, in its own message next.
  GOOD  Scope question: <the question itself>. A: ... B: ...
        [hand-back below]
  ```

- Carry the concrete situation in his words: the actual file, symbol, URL,
  output, or quoted line. Never name an internal file, memory, category, count,
  or subagent coinage he has not seen.

  ```
  BAD   Decide whether the README's promise should be scoped.
  GOOD  The README says "<the actual sentence>". A: narrow it to what the
        tool redacts. B: leave it.
  ```

  ```
  BAD   Q1: keep `<memory-file>.md` as a skill rule?
  GOOD  When <the situation that file describes, in concrete terms>,
        should the agent <do X>? A: yes. B: no.
  ```

- The AskUserQuestion UI does not show the message above it. Each option label
  stands alone and names the concrete thing it does.

  ```
  BAD   Only kind 3 / Kinds 2 and 3 / Leave all
  GOOD  A: Rewrite the assertions in <test file> that compare full error
        text / B: ... / C: Leave all 14 as they are
  ```

- Letter the options. Where the codebase already has a pattern, that pattern is
  option A, and it may be the only option. State settled facts above the
  question, not as options, using the spec's existing names.

  ```
  BAD   How should ls-branches find remotes? A: <new mechanism> B: ...
  GOOD  A: Find remotes the way the other commands already do.
  ```

  ```
  BAD   | How prune finds branches | reused from ls-branches |
        | A | ... merge-check branches ... |
  GOOD  Settled (same as ls-branches): how prune finds remotes and
        primary branches. Question: ... A: ... B: ...
  ```

- A question about anything a user sees is a rendering question: set up a
  concrete scenario and put the exact output in every option's preview. If an
  option cannot be previewed, ask in plain text with each rendering inline.
  Start from how the surface renders today, name each element by the spec's
  term for it, and mark every property the options could change (text and
  color both), not only the ones that differ.

  ```
  BAD   The release/2.0 chip ... the patch chip ... when the PR is
        unreadable. A: [release/2.0: Unknown]  B: [Unknown]
  GOOD  Today: `Better GHSA [Waiting 3 days] [Patch in review]`, and
        `Backport targets [release/2.1] [release/2.0]`, all gray but
        the yellow patch chip. Fetching PR #4's review data fails. What
        does the patch chip show? A: [Unknown] gray. B: [Patch in
        review] yellow.
  ```

  ```
  BAD   ls-forks lists only some forks. Options: "Say the list is
        incomplete" / "Request error only" (no previews)
  GOOD  Scenario: <three forks listed, the request for the fourth
        fails>. Each option's preview: the full stdout, stderr, and
        exit status.
  ```

  ```
  BAD   Message text: the proposed row layout as a table. Question:
        Option A "Use this layout" has no preview; option B has one.
  GOOD  Option A and option B each preview exactly their own row,
        aligned so the columns show.
  ```

- Before framing a choice, measure the thing the choice turns on across the
  real corpus. If you cannot name the number that separates the options, you
  are not ready to ask.

  ```
  BAD   Sample error text in the doc: A: keep it. B: shorten it.
        C: cut to prose.
  GOOD  Backticked `pkg.Name` outside code fences: 65 in this doc, 0 in
        its sibling doc on the same subsystem, 0 in the prose of the two
        most API-heavy docs. Proposal: describe the error in plain words, no
        Go identifiers.
  ```

- Where a standard exists, evaluate the item yourself and bring the verdict
  with its evidence. A question is for a choice the evaluation leaves open.

  ```
  BAD   What does the chip show? ... What is a tooltip wrapper? ...
        Does GitHub do the same?
  GOOD  Drop this entry: <the situation> cannot arise, because <trace>.
  ```

Judgment calls:

- Code he has not reviewed since several of your changes: do not ask him to
  pick wordings or designs he cannot see. Apply his stated principles, finish,
  and hand the series back for review. Ask only what he can answer from what he
  has seen; a question that turns on unreviewed code names the file:line and
  gives one concrete example. His principles for a comment: state what the code
  does, not what it doesn't; be accurate without a long journey; if it does two
  different things in two cases, the name or the abstraction may be wrong.

  ```
  BAD   (after five unreviewed folds) Which wording for the
        `checkResolvable` comment? A: ... B: ...
  GOOD  Brief the implementer with the comment principles, finish the
        round, hand the series back.
  ```

- A symptom only he can observe (his browser, his account): ask him for the
  observation that tells two causes apart before briefing any fix.

  ```
  BAD   Brief a fix for "the loading chip never updates until I toggle
        views", twice.
  GOOD  When the chip sticks, does anything else on the view change?
        Is the list empty or filled?
  ```

- When work needs a page or data only he can reach, the request is a capture
  that redacts private content before it leaves his browser, built the way
  the project's existing capture tools are. Run the script yourself first
  (against stubbed browser APIs or a local page) so it completes and
  delivers its output; each failed run costs him a round trip. Exhaust
  public data you can fetch yourself before asking. A request is the whole
  message: while waiting on it, ask nothing else.

  ```
  BAD   Save the private pull request page with Ctrl+S. Meanwhile,
        where should the design go? A: ... B: ...
  BAD   (untested) Paste this; it copies the result to the clipboard.
        (it calls `copy` after an await, which does nothing)
  GOOD  Run <redacting capture script, exercised under stubs> on the
        pull request page and save its output to <path>.
  ```

- A review comment whose words fit both the code and the comment on its line:
  ask which one he means. Otherwise its words, not its anchor, decide.

  ```
  BAD   ("so much drama for such a tiny function" on the line
        `// RoundTrip sends every request to the test server.`)
        Rewrite two `RoundTrip` function bodies.
  GOOD  Does that mean the comment's wording or the function body?
  ```

- When he is confused twice about the same work, stop and restate the whole
  position plainly, ideally by showing the diff. Do not reformulate the
  question a third time.

  ```
  BAD   A seventh option set on the same change.
  GOOD  `git show` of the commit: five lines of diff.
  ```

### Shorthand replies (proposal for Sam to adjust)

Canned options stay: they help most when he is typing on a phone. They are
often too narrow, so these short replies, typed in the free-text field, tell
the agent what went wrong. None of them is a selection, and nothing starts on
one.

| Reply | Means | Agent does |
|---|---|---|
| `more` | The options miss what I want. | Treat the option set's premise as wrong. Measure or check the existing pattern, then re-ask with a wider set. Do not just reword the same options. |
| `split` | You have conflated several things. | List the separate decisions bundled in the question, one concrete line each, then ask the first one alone. |
| `huh` | I don't understand the question. | Restate from his situation: the actual thing, what happens now, what each option changes, all in concrete names. No labels he has not seen. |
| `verdict` | Evaluate it yourself. | Apply the standard, reach the conclusion, and bring it with its evidence. Ask only if a real choice remains. |

## What counts as a decision

Purpose: work that rests on a misread reply is work he did not approve.

- An option he chose is a decision for a small, reversible next step.
  Task-notification boilerplate such as "No human input has been received"
  fires on every subagent completion and does not cancel an answer he gave.

  ```
  BAD   (he picked "approve the DESIGN.md correction"; a completion
        notice in the same turn carried the boilerplate) Your answer
        may not be real, so I have not acted.
  GOOD  Apply the DESIGN.md correction.
  ```

- Get his plain words before large or wide work: many commits, many files, or
  something hard to unpick. A selection can be a misclick: he often answers on
  his phone, where the touch targets are small. One selection does not
  authorize a sweep.

  ```
  BAD   (selection: "More under-testing entries") Work 13 findings
        into 14 commits.
  GOOD  That selection means 13 more findings, about 14 commits. Say
        go in your own words and I will start.
  ```

- Not decisions: `[No preference]` (what the harness sends when he presses
  Skip), an empty selection, a reply that does not fit the question, a reply
  that repeats your own labels or counts back (that is a complaint about the
  question), and silence inside your own turn. Do not record a non-decision as
  one, do not cite it to a subagent, and re-ask before work rests on it. Write
  your own recommendation as yours and unconfirmed.

  ```
  BAD   Decided: <question 2>: no preference, so default to X.
  GOOD  Question 2 got no answer. Asking again: ...
  ```

- "Either" (or "any of these is fine") answers the question without making
  the choice his. No need to re-ask, but whatever you pick stays your
  preference: label it that way in the summary and in the doc it lands in,
  so a later agent can tell it apart from his requirements.

  ```
  BAD   (reply "Either") I'll go with A. ... Decided: Missing means ...
  GOOD  Agent preference, not a requirement (Sam: either is fine):
        Missing means ...
  ```

- A yes given to a summary in vocabulary he never saw is not consent to the
  work underneath. Before offering a choice that grows scope, quote the actual
  comment or name the actual symbol. Internal shorthand misleads too.

  ```
  BAD   Fold the reviewers' fix into a seventh commit on the six?
  GOOD  The doc comment on <symbol> says "<quoted text>"; the reviewer
        says <what is false>. Add one commit on top of the library's
        six-commit history to fix it?
  ```

- A proposal in an agent-written doc, or one you made, is not his decision. Do
  not say "you wrote" or "your example" unless he said he wrote it.

  ```
  BAD   Your example header format ...
  GOOD  The draft's header format ... (asked about as a proposal)
  ```

If work already started on a misreading, stop it, restore what it touched, and
say so in one line.

```
BAD   Options: "the five severe test gaps" / "the two under-proving
      tests" / ... Reply quoting the counts back, read as "all three";
      work dispatched.
GOOD  Stop the work and restore. Then list the eleven findings, each
      with file, line, and consequence.
```

## Reporting

Purpose: he acts on what you report, so it must be readable cold, current, and
true.

Constants:

- Hand back only when done with what he asked. "Done" means his request, not
  what reviewers found. He reviews the finished series himself, with no
  mid-round explanations.

  ```
  BAD   (mid-round) Here is the spy listener and the doc comment:
        [quoted code and doc text]
  GOOD  (when finished) The series is ready for review: <commits>.
  ```

- Report the final state: what the series or change now is. Leave out what
  reviewers confirmed and the intermediate SHAs or generations.

  ```
  BAD   What Fable confirmed: ...
  GOOD  The series is now: <commit list, one line each>.
  ```

- Do not explain or quote-walk code he has not reviewed. A decision question
  that turns on such code names the file:line and gives one concrete example.

  ```
  BAD   The spy listener ... the last paragraph of the doc comment ...
        setup blocks that contain their own act/check ...
  GOOD  <file:line>: <one concrete example>. A: ... B: ...
  ```

- A reviewer finding is never authorization, least of all on code he has not
  reviewed. Once he has reviewed and you are folding in his comments, a fold
  contains only what he approved in his own words; list anything else for him
  once, at hand-back. Before the first hand-back, dead code or a failure in
  the ordinary documented behavior of the work he asked for is yours to fix
  (see Holding scope).

  ```
  BAD   Fold the reviewer's spy-listener fix into the next round.
  GOOD  (at hand-back) Not folded: a reviewer says the spy listener
        fails when <the situation it needs>; the fix adds <what it
        adds>. Accept the limitation, or fix?
  ```

- Check a reviewer's writing finding against the rule before relaying it.

  ```
  BAD   "records each connection it accepts" has the "the X the Y verb"
        form.
  GOOD  "a hook that a test passes to `WithDialer`" has that form.
  ```

- The first sentence names the subject concretely: what breaks, when, and the
  consequence. Never open with "it" or "this still reproduces". An entry on
  your list from earlier turns is not a shared reference.

  ```
  BAD   It still reproduces, unchanged.
  GOOD  The test suite has no time limits, so one library defect hangs a
        test, and the resulting panic kills the run before the test that
        names the defect can report.
  ```

- Lead with the current state and any action he must take. A problem you
  hit and fixed, whose end state is fine, does not appear in the report. Name
  it only if it changes what he must check or do.

  ```
  BAD   ## What happened
        The implementer misparented a commit; a reviewer caught it ...
  GOOD  The series is ready for review: <commits>.
  ```

  ```
  BAD   Done, at <sha>. A slip on the way: a staged restore swept other
        files into one fold, the rebase conflicted, and the unsquashed
        branch was pushed; I rebuilt the folds and pushed over it.
  GOOD  Done, at <sha>.
  ```

- When he asks what something does, answer with the guarantee a user gets and
  what they would see if it broke. Mechanics only when he asks how.

  ```
  BAD   It seeds a cache entry, rebuilds the advisory from it, and
        asserts each field comes back holding what was stored.
  GOOD  A severity a maintainer confirmed still reads as confirmed on a
        row drawn from the cache.
  ```

- Relay what an agent did and declined to do, with its reasoning. Do not add a
  verdict ("the right call"). When he asks for a recommendation, give one.

  ```
  BAD   It left the stale field in git history, which is the right call.
  GOOD  It left the stale field in git history, because <its reason>.
  ```

- A list of what remains carries only open items. Apply the reviewer's own
  conclusion: an item it closed is dropped or marked closed in one line.

  ```
  BAD   ## Overtesting
        [the auditor's findings, passed through]
  GOOD  Overtesting: closed; the auditor judged the redundancy
        deliberate.
  ```

- Report a side finding once, with the concrete commands. After he takes it
  over or parks it, drop it from every later wrap-up.

  ```
  BAD   [remote CI results] Also, the disk cleanup is still available:
        ...
  GOOD  [remote CI results]
  ```

- When he asks to go one at a time, each message covers exactly one item.
  Shared construction is explained once, inside the first item.

  ```
  BAD   All four timing tables, with decisions 1 to 4.
  GOOD  The first timing table, with how all four are built, and its one
        decision.
  ```

- Assert only what you checked this turn. Explaining your own mistake is the
  moment to assert least: name the mistake and the check that would have caught
  it. A glob that matches nothing is not proof of absence.

  ```
  BAD   `ls scratch/RELEASE-*.md`: scratch/RELEASE-0.0.4.md does not
        exist. (later) It must have been created after my check.
  GOOD  `find . -iname 'release-*.md'`. (later) My glob was
        case-sensitive; the file is scratch/release-0.0.4.md and existed
        when I looked.
  ```

- Quote a source only from text you just read. Never reconstruct a quotation.

  ```
  BAD   setdomainname(2): "does not relate to DNS... it refers to the
        NIS/YP domain"
  GOOD  setdomainname(2) says "NIS domain name"; the NIS-versus-DNS
        distinction is in hostname(1) and domainname(1).
  ```

- Chat prose gets the same register pass as docs (writing-review). Apply a
  correction silently; never narrate how you fixed your previous reply. Do not
  close with an offer to build something he did not ask for.

  ```
  BAD   [rewritten answer] What I cut from the first draft: ...
        Repaired claim: ...
  GOOD  [rewritten answer]
  ```

## Holding scope

Purpose: the requested scope is the deliverable. A chain of steps that each
follow from the last (finding, gap, feature) still ends in work only he can
authorize.

- A finding is not a requirement. Report it in one sentence and stop: no
  design, no spec to a subagent, no build.

  ```
  BAD   (one route had origin and destination reversed) Design a
        ground-track direction check: a new parameter through five call
        sites, tests, adversarial review.
  GOOD  Detour is symmetric, so the plausibility rule cannot detect a
        reversed route.
  ```

- A constraint you derive to make a goal checkable is yours. Label it as yours.
  Before writing a requirement into a brief, quote the sentence of his it comes
  from; one you cannot anchor is yours.

  ```
  BAD   (brief) Gate: no commit may modify or delete a line an earlier
        commit added.
  GOOD  (brief) Content that never reaches the final state must not
        persist (the superseded 526-line markdown document). A commit's
        comments may start short; they must reflect the actual state.
  ```

  ```
  BAD   (brief) Matching rule: open. Security: escape markup, reject
        hostile URLs.
  GOOD  (brief) Link the duplicate field only when it exactly matches
        `GHSA-xxxx-xxxx-xxxx`.
  ```

- Being told not to enforce something leaves the behavior unspecified. It does
  not make the opposite a requirement.
- An agent's audit, especially one you wrote the brief for, is not evidence of
  a requirement.

  ```
  BAD   (audit: the tool can act on a control the page disabled) Refuse
        in fill, click, and option selection: a new DOM script, four Go
        helpers, docs, tests. (corrected) Make the action succeed.
  GOOD  No rule either way: leave the behavior to the library. Fix the
        real problem, Rod waiting out the action timeout on a disabled
        control: `el.Sleeper(rod.NotFoundSleeper)`.
  ```

  Disabled attributes are hints to the browser, not rules the tool enforces.

- A reviewer downgrading something is a finding. Relay it in one line and let
  him set the direction; do not escalate it over the reviewer's judgment.

  ```
  BAD   (asked: the chip shows progress) Brief a fix so the chip counts
        only the completed view's work.
  GOOD  Reviewer: the chip's count is cosmetic; it counts a queue both
        views share.
  ```

- Dead code, or a failure in the change's ordinary documented behavior,
  belongs to the change under review: fix it in the same round, before
  handing back. The same defect elsewhere is reported once, in one line.
  After he has reviewed, while you fold in his comments, a new finding goes
  on a list for him instead (see Reporting).

  ```
  BAD   Side finding: a reviewer found a redundant block in <commit
        from this session>; left as is.
  GOOD  Remove the redundant block in the same round.
  ```

- For any other failure a reviewer finds, especially one whose fix adds
  complexity, relay in one line the situation it needs and what the fix
  would add. Sam judges whether it matters; do not weigh its likelihood
  yourself. Accepting it is a valid outcome. The spy-listener pair under
  Reporting is the worked case.

  ```
  BAD   The spy-listener failure needs a contrived setup, so leave it
        out of the report.
  GOOD  A reviewer says the spy listener fails when <the situation it
        needs>; the fix adds <what it adds>. Fix or leave?
  ```

- When a feature needs a pile of support code, check whether the feature was
  asked for before improving the support code. A dropdown is either single
  select, like radio buttons, or multi select, like checkboxes.

  ```
  BAD   Pick a dropdown option by typing its exact text, plus Unicode
        matching (`printableValue`, `foldValue`, `halfWidth`, ...).
  GOOD  Pick options by position number.
  ```

- When you extend a correction past the line he flagged, find the reason that
  line was a problem and extend it only to cases that share the reason. A
  shared surface feature (same project, same file, same kind of word) is not
  the reason. When the reason is unclear, ask.

  ```
  BAD   (flagged: a passage that reveals what an unreleased project is
        about) Rename every identifier from that project across four
        skills.
  GOOD  Remove the passage and any other text that reveals the same
        subject. Leave identifiers that say nothing about it.
  ```

## Blockers

Purpose: he never wants a blocker worked around silently, and he does not want
to be nagged about things that do not block.

- Check that it actually blocks the current task before calling it a blocker.
  Check whether the constraint is documented or intentional before calling it a
  bug.
- A real blocker gets resolved with him. Stop and ask with the concrete
  options. "Accept the limitation" is a valid resolution.
- Do not invent a workaround or change adjacent behavior to get past it.

  ```
  BAD   Bug: `runj kill` needs a kill(1) binary in the jail rootfs.
        Plan: rewrite `runj kill`.
  GOOD  Blocked: `runj kill` needs a kill(1) binary in the jail rootfs,
        a documented limitation. A: accept it. B: ...
  ```

- An item he parked that does not block is not raised again.

  ```
  BAD   Outstanding blocker: publish and vendor the library. (third
        time, after Sam parked it until the integration work is done)
  GOOD  [nothing about it until the integration work is done]
  ```

## Design and requirements interviews

Purpose: a design or requirements doc records his decisions at the level he is
deciding. The `grilling` skill gives the interview loop; these are his
additions.

- Altitude. A design question is about behavior: what the program does, which
  requests it makes, what the user sees. A function signature is coding. If the
  question would not make sense to someone who has not read the code, it is not
  a design question. In a requirements-only session, options state an
  observable target (time to shell, what the maintainer sees), not mechanisms.

  ```
  BAD   How should `candidates()`'s signature change? [Go call-site
        previews]
  GOOD  When <scenario>, what should ls-forks print? [output previews]
  ```

  ```
  BAD   Speed: A: snapshot restore. B: direct kernel boot. C: hotplug.
  GOOD  Time to shell: A: under <N> seconds. B: under <M> seconds.
  ```

- Scope. Questions settle what the features he described leave open,
  including what a described feature needs to do its stated job. A question
  that adds a new output, screen, or capability he did not describe is
  invention, even with a "no" option.

  ```
  BAD   (he described recipes viewed in the app) Should each recipe
        also export as a shopping list to a grocery service?
  GOOD  (he described scaling a recipe's servings) Scaling one egg by
        1.5 gives 1.5 eggs, which plain multiplication cannot avoid.
        A: round counted items. B: keep exact fractions.
  ```

- Every question opens with a concrete scenario using real names, then the
  choice.

  ```
  BAD   Which URLs does ls-branches accept?
  GOOD  Your clone's origin is your personal fork, <the actual URL>.
        With A, ls-branches picks <...>; with B, <...>.
  ```

- A design doc for a new feature leaves the tests open: no helpers, fakes,
  fixtures, clock or sleep seams, or case lists. An existing Tests section is
  not a template to extend.

  ```
  BAD   ## Tests
        Fake-server changes ... fixture sources ... recorded-sleep and
        fixed-clock seams ... cases: ...
  GOOD  [no test section]
  ```

- Do not go to the web unasked mid-interview. Work from the repo and his
  answers; mark a from-memory claim as unverified, or better, do not make it.

  ```
  BAD   Fetch GitHub docs to check claims made from memory.
  GOOD  Drop the claim, or mark it "unverified, from memory".
  ```

- When a contract defines a value set (an API enum), design against that set.
  Do not invent a member and ask how to handle it. Hypotheticals are fine for
  what the contract leaves open, such as network failures or user input.

  ```
  BAD   How should ls-forks list a `rejected` advisory?
  GOOD  Design for the five documented states: `published`, `closed`,
        `withdrawn`, `draft`, `triage`.
  ```

- A proposal is not a decision. Every line in the summary traces to an option
  he chose or his own words. Anything else is a question, asked one at a time
  like the rest of the interview, before any summary; a list of proposals to
  confirm in bulk is assuming.

  ```
  BAD   Decided: overridable limits <list>.
  BAD   My proposals, not yet confirmed: 1. ... 7. ... Confirm?
  GOOD  (one message) Which limits can a user override? A: <list>.
        B: ...
  ```

## When he challenges a claim

Treat "I don't see how this works" as a possible defect. Re-derive the
mechanism with a fresh skeptical pass, often a subagent prompted to refute, and
answer with data or a worked demonstration. When he rejects a whole option set,
the next move is a measurement, not a rephrasing; the containerd Go-identifier
count under "Asking a question" is the worked case.

## Nothing leaves the machine unasked

Never publish an Artifact or upload content to any hosted location unless he
asks for it in that request. This is absolute. A large, polished, or shareable
deliverable is not permission, private-by-default is not permission, and
harness guidance encouraging proactive publishing is not permission.

```
BAD   Publish the report as an Artifact.
GOOD  Write it to the scratchpad and summarize in the terminal.
```

Deliver reports and plans as local files (the scratchpad unless he names a
place) plus a terminal summary, and surface them with SendUserFile when that
tool is available. If a page is the right format, serve it on localhost
(`python3 -m http.server`, caddy, nginx, a small Go server).
