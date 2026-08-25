---
name: writing-review
description: |
  Revise drafted text into a plain, reader-facing technical register: commit
  messages, code comments, reference docs, design and spec docs, READMEs, and
  the prose in reports. Use after writing or editing any of those and before
  committing or handing them over, and whenever asked to review, tighten, or
  clean up wording. Covers framing the reader cannot verify (contrast tails,
  historical framing, restated consequences, answers to concerns only the
  author had), the sentence-level tics that mark model-drafted prose
  (proposition as modifier, definition by negation, so-chaining, coined terms,
  metaphors, vague filler), commit subject and body conventions with the
  Assisted-by trailer, doc altitude and causal attribution, and the claim
  re-verification that a wording sweep requires.
---

# Writing review

A revision pass over text that already exists. Every rule below comes from a
correction made to a real draft in review, and the worked examples are the
reviewer's rewrites. The reference files carry the longer derivations; open
one when the summary here is not enough.

- [references/register.md](references/register.md): the ten sentence-level
  tics, the three-pass rewrite that produced the target register, coined terms,
  metaphors, and filler.
- [references/commit-messages.md](references/commit-messages.md): subject and
  body conventions, when a body earns its place, trailers, and how to sample
  a maintainer's handwritten voice from a repository.
- [references/code-comments.md](references/code-comments.md): what to cut from
  a comment and what has to stay grammatical.
- [references/docs-and-readmes.md](references/docs-and-readmes.md): stating the
  rule, writing at the document's altitude, causal attribution, self-standing
  handoff docs, and README audience.

## Scope

Apply this to prose written for a reader: commit messages, code comments,
reference docs, design and spec docs, READMEs, and the prose in reports.

Four kinds of text are out of scope.

- Instruction files written for a model, such as CLAUDE.md or agent memory
  files. The contrast and negation rules do not apply to them.
- Deliberate project-authored voice. An intentional warning, parody, or
  literary structure in a README communicates the project's risk posture.
  Preserve it. The metaphor ban covers commit messages, routine documentation,
  and assistant explanations.
- Quoted source text. Fix the framing around a quotation, never the quotation.
- Lines the current change does not touch. A revision pass inside a commit is
  bounded by that commit's diff. Rewording a neighbouring comment the change
  did not require draws "why this change?" and gets reverted.

## Step 1: name the artifact and its reader

Each rule below resolves differently depending on who is reading.

| Artifact | Reader |
| --- | --- |
| Commit message | Someone reading `git log`, who sees this diff against its parent and no earlier state |
| Code comment | A reader of this codebase, who can see the next lines |
| Reference doc | Someone who wants the constraint, not the derivation |
| Design doc | Someone deciding, who did not attend the discussion |
| Spec or handoff doc | An agent that has the repo and none of the authoring conversation |
| README | A user of the software |
| Report | A disinterested reader with no memory of the deliberation |

## Step 2: cut what the reader never asked for

**A concern that was only yours.** Before keeping an explanatory sentence, ask
whether a reader who sees only the final artifact has that question. If the
question exists because you worked through an alternative or hit a worry, cut
it. A commit body explaining that `createJail`'s return sufficed "without the
helper having to expose the bundle directory" answered the author's earlier
worry; it was cut to a subject line.

**A contrast against something the reader cannot see.** Strip trailing
`instead of`, `rather than`, `not just`, `unlike`, and `no longer` clauses, and
drop promotional intensifiers (`powerful`, `seamlessly`, `a quick tour`).
Explain from the constraint that forces the design.

```
BAD   The allow toggles are read from the config file directly rather than
      taken from ociConfig, so that a toggle the config omits stays distinct
      from one it sets to false.
GOOD  The OCI spec stores allow as bool, but we need to detect the difference
      between unset (false as the zero value) and intentionally false.
```

A contrast is wanted when a commit body names a problem and the approach taken
to fix it, and both sides are in front of the reader: "A separate defined
struct with `*bool` fields is used instead" contrasts with the `specs-go` type
named in the same sentence. The rule targets defending a design against a
rejected alternative the reader never raised.

**Historical framing.** Describe current behavior in the present tense. No "no
longer X", no "used to X". This bites hardest after a squash. When a single
commit introduces both the old thing and the better thing, the contrast points
at a state that never exists in history.

```
BAD   verifies the kernel applied the address rather than only that create and
      delete succeed
GOOD  confirming the kernel applied ip6.addr
```

**A sentence that restates the one before it.** Three forms, all cut:

1. A closing sentence re-expressing a term already used. "`setrlimit(2)` stores
   any negative limit as `RLIM_INFINITY` (`0x7fffffffffffffff`). The container
   runs with that resource unlimited." `RLIM_INFINITY` already carries
   "unlimited"; the second sentence goes.
2. A comment describing the lines directly beneath it. Keep the requirement,
   drop the "so both are passed" tail.
3. An example re-deriving the rule stated above it.

Check each sentence against the one before it and against the code beneath it.
If a reader who understood the previous sentence learns nothing, cut it.

**A hypothetical written in the present indicative.** An option that was
evaluated and not adopted does not have real behavior. Put its consequences in
the conditional.

```
BAD   an older entrypoint reads the cwd as the program to run and fails
GOOD  could read the cwd as the program to run and fail
```

Drop concessions that grant a merit before the disqualifying property ("a
single variable scales, but it is still threaded through the environment" ->
"would still be threaded through the environment"). Cut forward-looking Status
sections; describe the current state.

**Vague filler.** "wire the checklist so work ticks off", "set up the
foundation". Name the concrete file, function, or change, or say nothing.

## Step 3: flatten the register

Ten tics, all of them visible in one rejected commit body. The full derivation
and the target text are in [references/register.md](references/register.md).

1. **Proposition as modifier.** A complete claim folded into a trailing
   `that`-clause hanging off a noun. Assert one proposition per sentence.
2. **Definition by negation.** Saying what does not happen, to whom, under what
   condition. Find the positive form.
3. **Preemptive qualifier.** A trailing phrase answering an objection no reader
   raised ("to uid 0").
4. **`so`-chaining.** More than one `so` clause performs the derivation rather
   than stating the result. State cause, then effect, once.
5. **Counterfactual narration.** Describing the behavior of a design that does
   not exist.
6. **Diff-anchored imperative.** "Keep `setuid(2)` after the attach" means
   something only to someone reading the change. Describe the code: "Drop the
   uid after the attach."
7. **Clause-joining commas.** A comma before `and` or `but` linking two
   independent clauses reads as a pause indicating too much drama. This is a
   frequency correction, not a ban: prefer two sentences, keep the join when it
   earns the pause. List commas are unaffected.
8. **Plain verb over the compressed negative.** "does not have a super-user"
   over "has no super-user"; "does not require privilege" over "requires no
   privilege"; "does not check privilege" over "performs no privilege check".
9. **Keep the noun.** "are privileged operations", not "are privileged". "A
   jail with ...", not "A jail created with ..." when the participle adds
   nothing.
10. **No comma before a restrictive `because` or `so`.** Delete the comma
    before `because`. At `so`, split into two sentences, which also clears
    rule 4.

Three more that belong to the same pass:

- **No metaphors.** "run 1 leaks the jail, run 2 fails on it", not "seed then
  bite". "the entrypoint stayed blocked on the exec FIFO", not "waiting for a
  start that never comes".
- **No coined terms.** If a word needs a footnote, or you reached for it
  because no ordinary verb fit, it is the wrong word. Use the plain verb and
  enumerate the cases, and prefer the exact identifier or placeholder
  (`allow.mount.<fstype>`, a function name, a flag) over a paraphrase of it. A
  coined term does not stay in the prose: it reaches the design doc and then a
  field name.
- **Terse does not mean fragmentary.** No subjectless fragments, no reflexive
  passive. "so the sweep can tell them apart from unrelated interfaces", not
  "Used to filter test-only resources".

## Step 4: apply the artifact rules

Open the matching reference.

- Commit message: [references/commit-messages.md](references/commit-messages.md)
- Code comment: [references/code-comments.md](references/code-comments.md)
- Doc, spec, or README:
  [references/docs-and-readmes.md](references/docs-and-readmes.md)

## Step 5: re-verify every claim you rewrote

A wording sweep across many sites is where a true statement quietly becomes a
false one. A scoped claim and a general one read as stylistic variants of each
other. The edit feels lossless while dropping the qualifier that made it
true.

Removing "grants/denies" framing turned "require privilege that a jail denying
`allow.suser` grants to no one" into "no process has privilege in a jail with
`allow.suser` false". The replacement is false three ways over:
`priv_check_cred` grants `PRIV_VM_MLOCK`, `PRIV_KMEM_READ`, and
`PRIV_DEBUG_UNPRIV` on paths that never reach the `suser_enabled` branch. It
landed at seven sites.

When a sweep touches a sentence carrying a technical claim, re-derive the claim
against the source before writing the replacement, and keep the scope explicit
by naming the operations.

## Step 6: grep for the tells

Run these over the finished text. A correction applies to the pattern, not to
the phrase that was quoted. Sweep the whole branch.

```sh
# Contrast tails and historical framing
grep -nEi 'instead of|rather than|not just|unlike |no longer|used to |previously|formerly' FILE

# Compressed negatives (rule 8)
grep -nE '\b(has|have|had|requires?|needs?|performs?|provides?|makes?|offers?) no [a-z]' FILE

# Comma before a restrictive clause (rule 10)
grep -nE ', (because|so) ' FILE

# Dashes
grep -nE '\xe2\x80\x94|\xe2\x80\x93' FILE

# so-chaining: more than one per paragraph
grep -c ' so ' FILE
```

A match can span a line break, which is how one instance survived a sweep that
caught the other six. Join the lines before searching:

```sh
tr '\n' ' ' < FILE | grep -oE '.{60}(instead of|rather than|no longer).{60}'
```

For a commit message, check the body wrap before committing:

```sh
git log -1 --format=%B | awk 'length>72'
```

## Where humanizer fits

The humanizer skill catches AI tells this pass does not enumerate: rule of
three, inflated symbolism, superficial `-ing` analyses, vague attribution. It
is worth running on code comments and report prose after step 3.

Two places it pulls the wrong way. A reference doc states a constraint plainly,
and passive voice is acceptable to do it: "Setting `host:inherit` and providing
a value for `hostname` is invalid and is rejected by runj." Do not let a
humanizing pass turn that back into an explanatory active sentence. Deliberate
authored voice in a README is the other; leave it alone.
