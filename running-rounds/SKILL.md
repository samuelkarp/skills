---
name: running-rounds
description: |
  Run implement and review rounds through subagents as the orchestrating main
  agent, and keep the resulting commit series clean and reviewable. Use when
  Sam sets a delegation cycle (implementer, reviewer, main agent
  orchestrating), before dispatching an implementer or reviewer subagent, when
  a subagent's report comes back and you are deciding whether to believe it,
  when folding review fixes into a commit series or rebuilding or rewriting
  one, and when handing work back to Sam for review. Invoked as /running-rounds
  with a task, it runs the default cycle. Covers the default cycle, what the
  main agent does itself, how much to check a subagent's claim, the shared
  working tree hazards, rounds versus commits, rewrite safety, and the
  hand-back push. For writing the brief itself, use the delegation-brief skill.
---

# Running implement and review rounds

## Purpose

The delegation cycle exists to preserve the main agent's context, which is
the context Sam is talking to. Verifying everything a subagent reports, or
troubleshooting code, fills that context fast. Judge each piece of work by
what it costs this context, not by how small the edit looks.

The counterweight: every agent can hallucinate or misunderstand, so apply a
degree of skepticism. Not every finding is a fact.

Both hold at once. Do not redo the subagent's work, and do not relay its
report as established.

For the content of each brief (constraints, evidence to demand, permission
to disagree), see the `delegation-brief` skill. This skill covers the cycle
around the briefs.

## Who does what

While the cycle is in force:

- **Delegated:** every edit that stays in the tree, including one-line and
  prescribed fixes and commit-message rewords; reading code to answer a
  question; repairing a tree an agent left behind.
- **Main agent:** git operations (commits of others' work when needed,
  rebases, ref moves, pushes), dispatching, relaying. The main agent does not
  run test suites; the implementer and reviewer run them.

The cycle is Sam's review process, so the size of the edit is not the test.
Batch a tiny edit into the next implementer round. A harness default such as
"do not use the Agent tool unless asked" does not lift the cycle; the
delegation rule in project memory is Sam's instruction and outranks it.

```
BAD   Reword a commit message and fix two doc citations directly, each
      judged too small to dispatch.
GOOD  Put the reword and both citation fixes in the next implementer
      round, and send that round to the reviewer.
```

```
BAD   With "Do not use the Agent tool unless ..." in the session prompt,
      edit test/table.test.js directly.
GOOD  Dispatch an implementer for the test/table.test.js change.
```

```
BAD   Stop the reviewer, read the diff it left in src/list/table.js,
      restore the file by hand, and trace the code to answer Sam.
GOOD  Answer from what agents already reported. Dispatch an agent to
      restore src/list/table.js and another to trace the code.
```

## The default cycle

When Sam invokes this skill with a task and names no other cycle, run this
one. When he names a different cycle, his wins.

1. **Planner (Fable).** A Fable subagent breaks the task into chunks.
   Dispatch the chunks as given (see "Rounds and commits are separate
   questions").
2. For each chunk:
   1. **Implementer (Opus or Sonnet)** does the work and commits it
      (explicit paths staged).
   2. **Reviewer (Fable)** reviews the round adversarially. Every
      implementation round gets its review before you report done.
   3. **Writing review (Sonnet)** whenever the round added new sentences
      (docs, comments, error strings, test failure messages): a separate
      read-only agent runs the `writing-review` skill on the added prose and
      returns findings as text. The implementer loading the skill itself does
      not count.
   4. **Fixes** from the review and the writing review go to the
      implementer, folded into the commits that own them.
3. **Hand back** to Sam (below).

```
BAD   Implement the whole task in one Opus round, then report done.
GOOD  Fable planner -> chunks. Per chunk: Opus implements, Fable reviews
      adversarially, Sonnet runs writing-review if the chunk added any
      new sentences, fixes fold in. Then hand back.
```

```
BAD   Implementer brief: "Load the writing-review skill and follow it
      for every comment you write."
GOOD  After the implementer commits, a read-only Sonnet agent: "Run the
      writing-review skill on the sentences added in <base>..HEAD and
      return findings as text." The findings go to the implementer.
```

```
BAD   Implementer reports the round committed; report it done to Sam.
GOOD  Dispatch the reviewer on the round's commits; report after the
      review and its fixes land.
```

## Rounds and commits are separate questions

A round is how work is split for dispatch. A commit is a unit a reviewer
reads. They need not match: rounds may be smaller than commits (fold later
rounds in with fixups), and one round may carry several commits.

- **Dispatch a planner's breakdown as given** when Sam asked for one. The
  round size decides how much each reviewer checks, so merging or splitting
  rounds is a scope decision. If a chunk looks wrong, ask Sam before
  dispatching.

  ```
  BAD   The planner returns three ls-forks rounds. Merge rounds 1 and 2
        (both in internal/github) into one implementer round and tell
        Sam after dispatching.
  GOOD  Dispatch round 1 as planned, or first ask: "Rounds 1 and 2 both
        touch internal/github. Merge them into one round?"
  ```

- **A brief carries Sam's design, not a rule of your own.** When resolving
  the points a planner flags, a behavior his design states governs wherever
  the requirements are silent; "requirements win" settles only a real
  conflict. A behavior neither document states is a question for him before
  dispatch, not a line in the brief.

  ```
  BAD   The design says review results refresh on the advisory's
        schedule; the requirements say nothing. Brief: "Request only for
        pull requests whose results are missing."
  GOOD  Brief: "Results refresh on the advisory's schedule (design §15)."
  ```

- **Commit granularity is judgment.** The constant: code, tests, and docs
  for "the thing" go in the same commit. "The thing" is the unit of
  granularity, and there is no hard rule that defines it. Ask whether this
  is a self-contained unit a reviewer would want to see whole. When one
  agent carries several distinct changes, name the commits in the brief and
  require the suite to pass at each.

  *Too fine.* A feature adding three jail parameters is one commit per
  parameter, each with its implementation, unit tests, docs, and behavior
  tests, the negative test paired with the positive one. A shared test
  helper arrives in the commit that first uses it, with every consumer
  calling it from the start.

  ```
  BAD   Support X
        Test X
        Document X
        Prove X fails
        Reword the comment on X
  GOOD  Support X        (code, unit tests, docs, positive and negative
                          behavior tests, final comment wording)
  ```

  ```
  BAD   Support X   (its tests spell out their setup)
        Support Y   (same setup, copied)
        Extract a test helper
  GOOD  Support X   (introduces the helper; its tests call it)
        Support Y   (its tests call the helper)
  ```

  *Too coarse.* Distinct changes stay distinct however small, and however
  convenient one round makes bundling them.

  ```
  BAD   One commit: cut prose from the comment body, match comments by
        marker and nonce, normalize the dedup key's case, edit the docs.
  GOOD  Four commits, one per change:
        cut prose from the comment body
        match comments by marker and nonce
        normalize the dedup key's case
        <the doc edit>
  ```

  More calibration cases (planner over-splits, splits along package lines,
  legitimately separate commits):
  [references/commit-granularity.md](references/commit-granularity.md).

## Mechanics that hold every time

These are properties of git and the harness, not judgment calls.

- **One implementer at a time.** Subagents share one working tree and one
  index. An agent that commits takes everything staged, not only what it
  wrote, and its suite run sees the other agent's half-finished edits.
  Disjoint directories do not make it safe. Queue the second implementer.
  If two must run, the second gets no commit instruction and you commit its
  work after the first finishes.

  ```
  BAD   Run a README agent and an implementer in src/ at once, both told
        to commit. The implementer's commit takes the README agent's
        REQUIREMENTS.md edit into a commit named for a banner fix.
  GOOD  Queue the README agent until the implementer reports, or run it
        with no commit instruction and commit its paths yourself after.
  ```

- **Read-only reviewers may run alongside an implementer**, pinned to a
  commit. Tell them the branch will move under them.

  ```
  BAD   The reviewer reads the live tree while the implementer edits it.
  GOOD  git archive <sha> | tar -x -C <dir>   # reviewer reads <dir>
  ```

- **Stage explicit paths.** `git add -A` sweeps in scratch files and other
  agents' edits.

  ```
  BAD   git add -A && git commit
  GOOD  git add src/list/table.js test/table.test.js && git commit
  ```

- **Never `git checkout <sha> -- .` on the live tree.** It overwrites every
  uncommitted change, including files the brief said not to touch. For
  per-commit verification, the brief names the method. After any round that
  reports touching the tree this way, check the restored content yourself.

  ```
  BAD   git checkout <sha> -- .   # to test each commit; destroys an
                                  # uncommitted DESIGN.md edit
  GOOD  git worktree add ../verify <sha>   # test there, then remove it
  GOOD  git stash push --include-untracked; ...; git stash pop
  ```

- **Do not leave your own edits uncommitted under an implementer.** Spec or
  planning edits held in the tree get committed with the change they specify
  (by the implementer, in that change's commit), not left sitting and not
  committed alone.

  ```
  BAD   Standing line in every implementer brief: "First commit the
        uncommitted REQUIREMENTS.md edit by itself, then start the code."
  GOOD  "The uncommitted REQUIREMENTS.md edit specifies this change.
        Commit it in this change's commit."
  ```

- **Parallel agents share one scratchpad.** Give each a filename prefix or
  its own subdirectory. Collisions are silent.

  ```
  BAD   Three parallel eval agents, each told "write your scripts in the
        scratchpad". Two write build.py; one runs its sibling's script.
  GOOD  "Write only under <scratchpad>/evals-a/."
  ```

- **The implementer runs the suite as its gate**, on a clean tree with no
  other agent writing to it. The main agent trusts that run and does not
  repeat it.

  ```
  BAD   git status --short; make test   # main agent re-runs the gate
  GOOD  "The implementer ran make test on a clean tree at <sha>: pass."
  ```

- **Host memory.** Memory-heavy runs (node test suites, Chromium-backed
  suites) go one agent at a time. Before starting the next, confirm the
  previous agent's child processes actually exited; a completion notice does
  not prove it. Commands and limits are in the `workstation-limits` memory.
  Pairing one implementer with one reviewer usually keeps one browser at a
  time.

  ```
  BAD   On the first agent's completion notice, dispatch the next suite.
  GOOD  Confirm pgrep finds none of the first agent's node or Chromium
        processes, then dispatch.
  ```

- **Large fixtures stay out of context.** No agent reads a large fixture
  (for example a 300 to 750 KB HTML capture) into its context. Say so
  explicitly in the brief.

  ```
  BAD   A brief that names the fixture and says nothing about reading it.
  GOOD  "Do not read <fixture>.html into your context. Search it with
        grep, and quote only matching lines."
  ```

- **Stalled agents.** Subagents park waiting for a notification that never
  comes, including for a command they backgrounded themselves. Committed
  work survives; the report is lost. Put this in every long-running brief:

  > If you start a long-running command, either run it in the foreground and
  > read its output, or write it to a log file and poll that file with a
  > bounded loop. Never wait for a notification. When your work is committed
  > and verified, produce your final report immediately.

  ```
  BAD   Brief: "Do not wait on anything you did not start."
        Agent's last line: "I'll continue when the completion
        notification arrives."
  GOOD  Brief carries the paragraph above.
  ```

  When one goes quiet, check its state, its output file's mtime and size (not
  the contents), `git log`, and `pgrep` before assuming it died; it has
  usually finished. Prod it by `SendMessage` naming what to deliver, and ask
  which parts it completed.

  ```
  BAD   Assume the agent died and dispatch a replacement.
  GOOD  stat <output file>; git log --oneline -3; pgrep -f <its command>
        SendMessage: "Deliver your final report now. Which commits did
        you complete?"
  ```

## Checking a subagent's claim

The cycle keeps this context small, so the checks you run yourself are the
cheap ones: a `git rev-parse`, a `git status`, reading the SHA in a CI
output. What a claim deserves depends on what the agent did to support it.

- A result the agent actually ran (a test, a demonstration, a diff of two
  trees) is trusted as reported. Do not rerun it.
- A claim the agent asserted without running anything gets the skepticism:
  "the backup branch exists"; "this test guards the feature" when no break
  was run; a claim about a live service checked only against a fake. Settle
  it with a cheap command when one exists. When it needs a break and a run,
  or code reading, ask the reviewer or a separate agent for it. A break
  inside a branch the case never enters proves nothing; ask for the break on
  the line the feature lives on.
- Relay with the right status: what the agent ran, what it asserted, and
  what nobody checked.

```
BAD   Relay the mutation table: "the headline feature is guarded by a
      test." (no break was run for that feature)
BAD   Delete the feature's line, run the named test, restore the file,
      check git status, then relay.
GOOD  Ask the reviewer: "Make <feature> misbehave the way a real bug
      could (a wrong value, an inverted condition), run <test>, restore the
      file, and report the output." Relay what it ran.
```

```
BAD   "The fold agent created a backup branch."
GOOD  git rev-parse backup <intended sha>   # match, then report it
```

```
BAD   "The fix is verified."
BAD   Rerun the reviewer's demonstration against the fixed code before
      relaying it.
GOOD  "The reviewer ran its demonstration against the fixed code and it
      passes. Not checked: the page in a real browser."
```

```
BAD   "The implementer confirmed the API returns the advisory's fork."
      (its test ran against a fake server)
GOOD  "The implementer's test passes against a fake server. Not checked:
      the live API."
```

## Relaying findings

- A reviewer's finding goes to Sam at the reviewer's own weight. Do not
  escalate it over the reviewer's judgment: if the reviewer called something
  cosmetic or not a defect, relay that in one line and let Sam set the
  direction.

  ```
  BAD   "The reviewer found a serious problem in the error wording."
  GOOD  "The reviewer notes the error wording as cosmetic, not a defect."
  ```

- Dead code, or a failure in the change's ordinary documented behavior,
  belongs to the change under review. Before the first hand-back, fix it in
  the same round, folded into the commit that introduced it (when above the
  published boundary). After Sam has reviewed, see the hand-back rule on
  folds below. For any other failure a reviewer finds, especially one whose
  fix adds complexity, relay in one line the situation it needs and what the
  fix would add, and let Sam judge whether it matters (working-with-sam,
  Holding scope).

  ```
  BAD   Fold a fix for the reviewer's spy-listener finding, or drop the
        finding as unlikely.
  GOOD  "The reviewer found the spy-listener test passes when <the
        situation it needs>. Covering it adds <what the fix adds>. Fix
        or leave?"
  ```

## Folding fixes and rewriting the series

The goal is a consistent, reviewable series Sam can publish.

- **Finish every consequence of an edit** in the commit it belongs to, for
  example rewrapping a paragraph whose lines went short. Do not offer
  "smaller diff" as a trade-off.

  ```
  BAD   Remove planning-doc tags from comments across the series and
        leave the shortened lines unwrapped to keep the diffs small.
  GOOD  Remove the tags and rewrap each touched paragraph, in the commit
        that owns it.
  ```

- **Lines the change does not need stay untouched.** A paragraph the change
  touched is rewrapped; a paragraph it did not touch is left alone.

  ```
  BAD   -	// ... denies ...
        +	// ... refuses ...
        (a test comment the commit was not otherwise editing)
  BAD   A new paragraph in the _FLAG_CREATE comment justifying why runj
        never sets JAIL_UPDATE, added while deleting an unrelated helper.
  GOOD  Neither hunk.
  ```

- **Splitting hunks** across the commits that own them: use the `git-hunk`
  CLI (memory `git-hunk` has the commands). Interactive git flags are
  blocked in this harness.

  ```
  BAD   git add -p
  GOOD  git-hunk   # commands in the git-hunk memory
  ```

- **Published boundary first.** Before choosing the base of any rebase, fold,
  or autosquash, find the newest commit reachable from a public remote branch
  or a pushed release tag (`git fetch`, `git merge-base --is-ancestor`,
  `git tag --contains`, `git ls-remote --tags`). Nothing at or below it is
  rewritten; write the boundary into the fold brief as a hard constraint.
  "What this session wrote" is not a boundary. A push to Sam's development
  remote does not make a commit published. Edits below the boundary: ask how
  to land them.

  ```
  BAD   Base the writing-review fold at 798479f9 (0.0.5), where the
        session's prose began. It rewrites 24 commits, crossing the
        pushed v0.0.6 tag.
  GOOD  git ls-remote --tags origin   # v0.0.6 is pushed
        Fold brief: "Do not rewrite 8b281f86 or any commit below it.
        Prose fixes below it: list them for Sam."
  ```

- **No undirected destructive rewrite.** An amend or small rebase covers
  most fixes on an unpublished branch. A directed scrub of every commit uses
  `git filter-repo`, never `git filter-branch`; verify every commit after,
  and do not delete backups or expire reflogs as a reflex.

  ```
  BAD   git filter-branch --msg-filter ... -- --all   # to fix trailers
        rm -rf .git/refs/original
  GOOD  git commit --amend   # the trailers were on the tip commit
  ```

- **Every instance, or this one?** If a wording fix could apply across the
  series, ask Sam. Every instance usually means folding into the originating
  commits.

  ```
  BAD   Fix the wording at the one line the review named.
  GOOD  "The same wording appears in four commits. Fix every instance
        (folded into each originating commit), or only this one?"
  ```

### Verifying a rebuilt branch

- **Move the branch ref** after a detached rebuild, then compare
  `git rev-parse` against the intended tip. A CI script given the branch name
  otherwise tests the old tip and reports green for the wrong commit.
- **Read the SHA from the CI output** (the remote CI host prints
  `>> pushing <branch> @ <sha>`) and match it before reporting a result.

  ```
  BAD   Cherry-pick root-allow onto a detached HEAD to drop one comma,
        start the remote CI run, report the pass.
  GOOD  git checkout -B root-allow HEAD
        git rev-parse root-allow   # equals the intended tip
        Start the remote CI run; match ">> pushing root-allow @ <sha>"
        to that SHA.
  ```

- **Diff the whole tree**, old tip against new, with no path list. A
  path-scoped check confirms only what you already suspected, and a scope
  taken from a commit's subject misses what its diff carried.

  ```
  BAD   git diff <old> <new> -- <the two doc files>
        (the dissolved commit also carried about 30 lines of Go doc
        comments in four source files, all lost)
  GOOD  git diff <old> <new>
  ```

- **Check intermediate commits**, not only the tip. A bad conflict
  resolution repaired by a later commit is invisible at the tip.

  ```
  BAD   Check only the tip of the rebuilt series.
  GOOD  for c in $(git rev-list --reverse <base>..HEAD); do
          git show "$c"   # read every commit's diff
        done
        (catches a duplicated bullet that exists at one commit only)
  ```

## Handing back

- **Hand back only when done** with what Sam asked, not with what reviewers
  found. He reviews the finished series on his development remote and wants
  no mid-round explanations.

  ```
  BAD   Mid-round report quoting code and a doc comment Sam has not
        reviewed.
  GOOD  "Done. <branch> is on the development remote at <sha>."
        (after the last round's review, fixes, and push)
  ```

- **A fold contains only what Sam approved in his own words.** This applies
  once he has reviewed and the round is folding in his comments: a
  reviewer's fix beyond those comments goes on a list for him at hand-back,
  not into the fold. Before the first hand-back, defects inside the
  asked-for work are fixed in the round.

  ```
  BAD   Fold Sam's comments plus a reviewer's fix to the spy listener,
        which he has not reviewed.
  GOOD  Fold only Sam's comments. Hand-back list: "Not folded: reviewer
        finding on the spy listener test (it needs <situation>; the fix
        adds <what it adds>)."
  ```

- **Push to Sam's development remote** when a round or fold is verified, in
  the same turn: `--force-with-lease` pinned to the old remote tip for a
  rewritten series, confirm local and remote refs match, report the pushed
  SHA. The development remote is private; he reviews from it, and pushing
  there is not publishing. Implementers still do not push. Any other remote
  needs his explicit request.

  ```
  BAD   "Ready for review." (nothing pushed)
  GOOD  git push --force-with-lease=<branch>:<old tip> <dev remote> <branch>
        git ls-remote <dev remote> <branch>   # equals git rev-parse <branch>
        "Pushed <branch> to the development remote at <sha>."
  ```

- **Keep the folds between his reviews few.** After several unreviewed
  folds, do not ask him to choose wording or design for code he has not
  seen; he lacks the context to answer. Apply his stated principles, finish,
  and hand the series back. If a comment needs two cases to stay accurate,
  report it as a possible naming or abstraction problem.

  ```
  BAD   After three unreviewed folds: "Should this comment say X or Y?"
  GOOD  Apply his stated principles, finish, hand back: "This comment
        needs two cases to stay accurate; the name may be wrong."
  ```

## Assisted-by trailer

Current practice, still an open question for Sam. In one delegation cycle
there is one primary author model: name the implementer's model, not the
orchestrator's. When separate coding agents each made substantive changes,
Sam has kept a trailer for each. Trailer format is in the `writing-review`
skill.

```
BAD   Assisted-by: Claude Code:<orchestrator's model>
GOOD  Assisted-by: Claude Code:claude-opus-5   (the Opus implementer)
```
