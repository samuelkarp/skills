---
name: writing-review
description: |
  Revise drafted text into a plain, reader-facing technical register: commit
  messages, code comments, reference docs, design and spec docs, READMEs,
  release notes, CLI error text, the prose in reports, and replies written to
  Sam in the terminal. Use after writing or editing any of those and before
  committing, sending, or handing them over, and whenever asked to review,
  tighten, or clean up wording. Covers framing the reader cannot verify
  (contrast tails, historical framing, restated consequences, answers to
  concerns only the author had), the sentence-level tics that mark
  model-drafted prose (proposition as modifier, definition by negation,
  so-chaining, coined terms, method jargon, metaphors, vague filler, fragments
  and epigram closers), commit subject and body conventions with the
  Assisted-by trailer, doc altitude and causal attribution, American spelling,
  how far a review pass should reach, and the claim re-verification that a
  wording sweep requires.
---

# Writing review

A revision pass over text that already exists. Each rule comes from a real
draft, and each GOOD example is target text. The purpose behind all of them:
the reader sees only the finished text, so it should say what the thing is, in
plain words, and every claim in it should be true as written. The reference
files carry the longer derivations; open one when the summary here is not
enough.

- [references/register.md](references/register.md): the derivation of the first
  ten tics, chat tics, coined terms, method jargon, settled verbs, metaphors,
  filler, spelling.
- [references/commit-messages.md](references/commit-messages.md): subject and
  body conventions, trailers, and how to sample Sam's handwritten voice.
- [references/code-comments.md](references/code-comments.md): what to cut from
  a comment and what has to stay grammatical and self-contained.
- [references/docs-and-readmes.md](references/docs-and-readmes.md): stating the
  rule, altitude, causal attribution, handoff docs, README audience, text that
  may not be agent-authored.
- [references/short-forms.md](references/short-forms.md): release notes and
  CLI error notes.
- [references/claims.md](references/claims.md): how true claims become false
  in a sweep or survive a review unchecked.

## Scope

Apply this to prose written for a reader: commit messages, code comments,
docs, READMEs, release notes, error text, report prose, and replies to Sam in
conversation. Chat replies get the same pass as a commit body; most of the
words he reads are written there.

Out of scope:

- Instruction files written for a model, such as CLAUDE.md, skills, or agent
  memory files. The contrast and negation rules do not apply to them.
- Quoted source text. Fix the framing around a quotation, never the quotation.
- Text that a human may have chosen deliberately. See "Text that may not be
  yours" below.

## Step 0: settle how far the pass reaches

**Do not reword lines the change does not need.** A pass inside a commit is
bounded by that commit's diff. Rewording a neighboring comment the change did
not require gets reverted.

**Further instances of the same rule are a question for Sam.** When the pass
finds the rule it is applying violated elsewhere (other files, earlier
commits, lines outside the diff), report them and ask whether he wants every
instance corrected. Do not fix them automatically, and do not silently leave
them. A yes usually means rewriting history to fold each fix into the commit
that introduced the text; that comes up often with code comments.

**Text that may not be yours.** Writing-review usually runs on documents an
agent mostly wrote, but some sections may be Sam's or carry legal or project
weight: license details, security policy, provenance of the code, a warning
written in a deliberate voice. `git blame` and the `Assisted-by` trailer do
not settle who chose the wording. Leave those sections alone when they look
deliberate, and ask when unsure. A section that merely resembles an
intentional warning is not evidence a human wrote it.

When dispatching a pass to another agent, have it report any instance it
judges a legitimate exception, and stop and report anything factually wrong
rather than smoothing the wording over it.

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
| Release notes | Someone deciding whether an update matters to them |
| Report or chat reply | A disinterested reader with no memory of the deliberation |

## Step 2: cut what the reader never asked for

**A concern that was only yours.** Before keeping an explanatory sentence, ask
whether a reader who sees only the final artifact has that question. If the
question exists because you worked through an alternative or hit a worry, cut
it. The same goes for justifying why a change is safe when the diff already
shows it.

```
BAD   Use createJail in TestJailHostMode

      createJail's return suffices without the helper having to expose the
      bundle directory.
GOOD  Use createJail in TestJailHostMode
```

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
named in the same sentence. Two things that both exist in the current tree can
be contrasted the same way. The rule targets defending a design against a
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

**An outcome tail.** A note that states a fact does not also state the
documented consequence (`not fully merged`, not `not fully merged, kept`).

**Vague filler.** "wire the checklist so work ticks off", "set up the
foundation". Name the concrete file, function, or change, or say nothing.

## Step 3: flatten the register

Seventeen tics. The first ten all appear in one commit body; the full
derivation and the target text are in
[references/register.md](references/register.md), along with the longer
examples for the rest.

1. **Proposition as modifier.** A complete claim folded into a trailing
   `that`-clause hanging off a noun. Assert one proposition per sentence.
2. **Definition by negation.** Saying what does not happen, to whom, under what
   condition. Find the positive form.
3. **Preemptive qualifier.** A trailing phrase answering an objection no reader
   raised ("to uid 0").
4. **`so`-chaining.** More than one `so` clause performs the derivation rather
   than stating the result. Look for the shape `X, so Y, so Z` across a
   paragraph, and state cause, then effect, once.
5. **Counterfactual narration.** Describing the behavior of a design that does
   not exist ("would leave nothing able to attach").
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
   Existential "There is no X" is outside this rule.
9. **Keep the noun.** "are privileged operations", not "are privileged". "A
   jail with ...", not "A jail created with ..." when the participle adds
   nothing.
10. **No comma before a restrictive `because` or `so`.** Delete the comma
    before `because`. At `so`, split into two sentences. The split also clears
    rule 4.
11. **No metaphors.** "run 1 leaks the jail, run 2 fails on it", not "seed then
    bite". "the entrypoint stayed blocked on the exec FIFO", not "waiting for a
    start that never comes".
12. **No coined terms.** If a word needs a footnote, or you reached for it
    because no ordinary verb fit, it is the wrong word. Use the plain verb and
    enumerate the cases, and prefer the exact identifier or placeholder
    (`allow.mount.<fstype>`, a function name, a flag) over a paraphrase of it.
    A coined term does not stay in the prose: it reaches the design doc and
    then a field name.
13. **No method jargon.** A skill's or subagent's internal vocabulary is not
    shared with Sam. Describe the technique in the words it is made of:
    "mutations" are "breaking the code on purpose to see which tests notice",
    and a "sole catcher" is "the only test that catches a given break".
14. **The settled verb.** A function returns, a field is declared, assigned, or
    copied. Code that declares and assigns each field does not "name the fields
    one at a time", and a function that returns a value has not "answered".
15. **Terse does not mean fragmentary.** No subjectless fragments, no reflexive
    passive, no fragments for effect. "so the sweep can tell them apart from
    unrelated interfaces", not "Used to filter test-only resources". "So
    whatever the corpus order is, the table is." is a fragment for effect.
16. **No performance in chat.** No epigram closers ("it is behaving as
    specified, and the specification is the problem"), no telling Sam what he
    thinks ("which is where your expectations probably come from"), no closing
    offer to build something he did not ask for, no bolded fragment headers on
    a short answer, and no narration of how the text was revised. Apply a
    correction silently; the reply carries the answer and stops.
17. **American spelling, no em or en dashes.** color, behavior, canceled, gray,
    initialize, license, dialog. Spelling includes identifiers and class names:
    a `colourOf` helper carries the wrong spelling into the codebase.

## Step 4: apply the artifact rules

Open the matching reference.

- Commit message:
  [references/commit-messages.md](references/commit-messages.md)
- Code comment: [references/code-comments.md](references/code-comments.md)
- Doc, spec, or README:
  [references/docs-and-readmes.md](references/docs-and-readmes.md)
- Release notes or error text:
  [references/short-forms.md](references/short-forms.md)

## Step 5: re-verify every claim you touched

Two failure points, both in [references/claims.md](references/claims.md):

- A wording sweep turns a scoped claim into a general one, because the two read
  as stylistic variants. Re-derive the claim against the source before writing
  the replacement, and name the operations it covers.
- A checkable constant draws the reviewer's check and the quantifier around it
  goes unverified. For each sentence, ask which caller, construction path, or
  request shape it holds for. Any sentence saying every, always, or never gets
  checked against the code before it ships.

## Step 6: read every sentence, then grep as an aid

The review is a reading. When handed a text or a whole diff, read all of it,
sentence by sentence, against Steps 2 to 5. A correction applies to the
pattern, not the phrase that was quoted, and most of the patterns above (a
restated sentence, a coined term, a metaphor, a dropped scope) have no
searchable string. Ask per Step 0 before going beyond the text handed over.

The searches below catch some instances a reading missed. They are never the
check itself, and a clean run does not mean the text passes. Their known blind
spots: the verb list in the rule 8 pattern is incomplete, `grep -c` counts `so`
per file and not per paragraph, and a match can span a line break.

```sh
# Contrast tails and historical framing
grep -nEi 'instead of|rather than|not just|unlike |no longer|used to |previously|formerly' FILE
# Compressed negatives (rule 8)
grep -nE '\b(has|have|had|requires?|needs?|performs?|provides?|makes?|offers?) no [a-z]' FILE
# Comma before a restrictive clause (rule 10)
grep -nE ', (because|so) ' FILE
# Dashes
grep -nE '\xe2\x80\x94|\xe2\x80\x93' FILE
# British spellings
grep -nEi 'colour|behaviour|cancell|centre|grey|licence|catalogue|dialogue|neighbour|(initiali|normali|organi|recogni|reali|seriali|optimi|summari)s' FILE
# so-chaining: more than one per paragraph
grep -c ' so ' FILE
```

One instance survived a sweep that caught the other six because it spanned a
line break. Join lines before searching:

```sh
tr '\n' ' ' < FILE | grep -oE '.{60}(instead of|rather than|no longer).{60}'
```

For a commit message: `git log -1 --format=%B | awk 'length>72'`.

## Where humanizer fits

The humanizer skill catches AI tells this pass does not enumerate: rule of
three, inflated symbolism, superficial `-ing` analyses, vague attribution. Run
it on code comments and report prose after Step 3. It pulls the wrong way on a
reference doc that states a constraint in the passive ("is invalid and is
rejected by runj"); keep that passive.
