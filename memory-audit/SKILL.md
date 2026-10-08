---
name: memory-audit
description: |
  Audit and restructure Sam's standing guidance: the global memory store,
  project memories, CLAUDE.md, and the skills that hold his rules. Run only
  when Sam invokes it. Covers where each kind of guidance belongs, finding
  contradictions and settling them with Sam, the rule format (purpose,
  constants, BAD/GOOD examples), what published skills must not contain,
  drafting on a review branch, and installing after approval.
disable-model-invocation: true
---

# Memory audit

## Purpose

Guidance only helps if a session applies it. A rule applies when it is loaded
at the moment it matters and reads as something to do. The audit moves each
piece of guidance to where it loads and rewrites it into a form a model
follows.

Where guidance lives:

| Kind | Home | Why |
| --- | --- | --- |
| How to work (asking, reporting, writing, testing, orchestrating) | The matching skill | The harness offers a skill when its trigger matches |
| The few rules that apply to every reply | CLAUDE.md, one line each | Always loaded |
| Durable facts across projects (host limits, remotes, tool locations, identities) | Global memory | Read on demand from the index |
| Facts about one project | That project's memory | Loaded in that project |

A correction about how to work is never a memory file. It is an edit to the
matching skill.

## The audit, in order

1. **Back up first.** Copy the memory directory and CLAUDE.md to dated
   backups before reading anything else. Nothing is deleted until the end.

   ```
   BAD   rm ~/.claude/memory/old-rule.md   # covered by a skill now
   GOOD  cp -a ~/.claude/memory ~/.claude/memory.bak-<date>
         cp -a ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.bak-<date>
   ```

2. **Inventory.** List every memory file, its size, and its index line; the
   project memories; CLAUDE.md; and each skill, noting which ones are under
   version control. Read every file in full. Check mechanically:
   - files missing from the index, and index lines with no file
   - `[[links]]` that point at nothing
   - frontmatter fields outside the format
   - files with several dated incident sections or several "How to apply"
     sections (these are incident logs)
   - memory files newer than the last audit's backup: sessions still writing
     memories for corrections

3. **Classify each memory** into one of the four homes above, or "obsolete".
   Ask before dropping anything as obsolete.

4. **Find contradictions** between memories, skills, and CLAUDE.md. Two hard
   rules written from different situations often look contradictory when
   both are judgment calls. Bring each one to Sam as a concrete situation:
   what happened in each case, what each rule says, and your guess at the
   real boundary. Never name a memory file he has not read.

   ```
   BAD   commit-granularity says merge planner chunks; dispatch-the-plan-
         as-given says ask first. Which stands? A / B
   GOOD  When a planner splits work finer than you'd want: in one case I
         merged two dispatch rounds without asking and you objected; in
         another you told me to merge three parse commits. My guess: rounds
         are yours to reshape, commit size is judgment. Is that the line?
   ```

   Expect "it depends". Record the purpose and the deciding factor, not a
   new hard rule.

5. **Draft on a review branch.** Create a branch in the skills repository
   through `git worktree add`, so the live skills keep working. Use one
   commit per skill. Agents draft into separate directories and return
   reports; see running-rounds. Give every drafting agent the decisions Sam
   made during the audit, verbatim: the backup predates them, and an agent
   working only from the backup reintroduces rules he has already
   corrected.

6. **Check coverage mechanically** before anything is deleted. Every file on
   the delete list maps to a draft that reports absorbing it, and no draft
   points at a file being deleted.

7. **Hand back for review** on Sam's development remote, then fold each
   review comment into the commit it belongs to. Apply each comment to other
   places only when they share its reason (see "Extending a correction").

8. **Show proposed CLAUDE.md and memory changes as readable text**: the new
   section in full, the lines added, the files kept, the count deleted. A
   unified diff sent earlier in the conversation is not something he can
   act on.

9. **Install after approval:** move the reviewed branch onto the skills
   repository's main branch, link any new skill into `~/.claude/skills`,
   replace the memory files with the kept set, move project facts into their
   project memory and index, install CLAUDE.md, and remove the review
   worktree. If other sessions committed skill edits to main meanwhile,
   replay them and fold each into the commit for its skill; everything above
   the published tip may be rewritten. Push main to Sam's development remote
   when he asks; he publishes from there.

   ```
   BAD   main: <reviewed commits>, then seven one-rule commits from other
         sessions on top
   GOOD  main: one commit per skill, with the other sessions' edits folded
         into the commits for working-with-sam and running-rounds
   ```

## Writing a rule

Each rule states its purpose, the few things that hold every time, and one or
two BAD/GOOD pairs placed directly beside it. Models follow examples better
than descriptions.

- **Examples are the agent's own output or action.** A BAD message and its
  GOOD rewrite; a BAD command and the GOOD one. At most one clause of
  setting.
- **Never quote Sam's corrections.** The rule carries the guidance. Text Sam
  wrote as a target (his rewrite of a commit body) is a GOOD example, without
  attribution. His statement of a rule is written as the rule.
- **No dates, no incident narration, no history of the rule's own edits.**
- **Judgment stays judgment.** Where Sam's answer is "it depends", write what
  it depends on.
- **When a correction reverses an overcorrection**, write the final boundary
  with both sides.

```
BAD   On <project>'s <branch> work, a question about <function> was the
      last paragraph of a long message. Sam: "<his correction, verbatim>"
GOOD  BAD   <findings> ... <review summary> ... Should applyUser call
            setgroups first?
      GOOD  Should applyUser call setgroups before the attach? (yes/no)
            Findings follow in the next message.
```

- **Do not invent constraints** such as a size cap per file, and do not
  attribute one you set to Sam. Effectiveness decides length. Minimize words
  around the rules, never the examples.
- **Keep examples beside their rules** in SKILL.md. A references file holds
  only long derivations or third and later examples, because a session reads
  it only if it decides to open it.
- **Use real identifiers** where they say nothing sensitive. A concrete name
  gives a model more to match than a placeholder. Use a placeholder only
  where the real text was never recorded or must not be published.

## What published skills must not contain

Skills are published. Check every draft for:

- **Names of Sam's personal infrastructure:** hosts, remotes, personal
  paths, and skill names that embed a host name. Use role names ("Sam's
  development remote", "the remote CI host").
- **Text that reveals what unreleased work is about.** The test is what a
  reader could infer about the subject, not whether a name came from that
  work. An identifier such as a field or test name that says nothing about
  the subject can stay.

```
BAD   Rename every identifier from the unreleased project.
GOOD  Remove the passages that reveal its subject (what it connects to,
      what protocol or system it works on); keep identifiers that do not.
```

Global memory and CLAUDE.md are private and may name infrastructure.

## Extending a correction

When Sam flags one line, find the reason that line is a problem and extend
the fix only to places that share the reason. A shared surface feature (same
project, same file, same kind of word) is not the reason. When the reason is
unclear, ask.

```
BAD   (flagged: examples quote Sam's criticism) Remove every quote from
      every file, including Sam's rewritten commit bodies.
GOOD  Remove the criticism quotes; keep his rewrites as GOOD examples.
```

## Reporting during the audit

Follow working-with-sam. In particular:

- Lead with the state and what Sam has to do. A problem you hit and fixed,
  whose end state is fine, is not mentioned.
- Questions carry the concrete situation in his words. A memory file name,
  a category you made up, or a count of items is not something he can
  answer.

```
BAD   Done, at <sha>. A slip on the way: the rebase conflicted and I
      rebuilt the folds.
GOOD  Done, at <sha>.
```

## Writing memories between audits

The memory instructions in CLAUDE.md route corrections into skills. A new
memory file that records a correction means a session did not follow them;
absorb it into the matching skill at the next audit and add its lesson as a
BAD/GOOD pair.
