# Register

The first ten of the seventeen tics in the parent skill all appear in one
commit body on runj's `root-allow` branch, "Set the group list before attaching
to the jail". The register is wrong everywhere: in commit messages, in code
comments, and in docs.

## The sentence

```
BAD   setgroups(2) and setgid(2) require privilege that a jail with
      allow.suser disabled does not grant to uid 0.
GOOD  setgroups(2), setgid(2), and raising a hard limit are privileged
      operations. A jail with allow.suser disabled does not have a
      super-user.
```

The BAD sentence is accurate, and accuracy does not excuse the register. Fix
the register, then re-check the claim against the source.

Six tics in the BAD sentence:

1. **Proposition as modifier.** "that a jail with `allow.suser` disabled does
   not grant to uid 0" is a complete claim (condition, negation, and the party
   negated) folded into a trailing `that`-clause hanging off `privilege`, so
   the sentence can keep moving. Assert one proposition per sentence.

2. **Definition by negation.** "does not grant" says what fails to happen, to
   whom, under what condition. The positive form replaces all of it: "a jail
   with `allow.suser` disabled does not have a super-user". That also matches
   the kernel's own framing, `security.bsd.suser_enabled`: "Processes with uid
   0 have privilege."

3. **Preemptive qualifier.** "to uid 0" answers an objection no reader raised.

4. **`so`-chaining.** Three `so` clauses in six lines performs the derivation
   instead of stating the result.

5. **Counterfactual narration.** "nothing in the jail can set the group list"
   and "would leave nothing able to attach" describe a design that does not
   exist.

6. **Diff-anchored imperative.** "Keep `setuid(2)` after the attach" means
   something only to a reader of the change. "Drop the uid after the attach"
   describes the code.

The same body carried an intensifier tail:

```
BAD   whatever the jail allows
GOOD  in a jail with allow.suser disabled
```

## Four more rules

These apply to text that has already cleared the first six.

7. **Clause-joining commas, used sparingly.** A comma before `and` or `but`
   joining two independent clauses marks a pause, and the pause reads as too
   much drama. Independent clauses can be used, but with taste, and model
   training reaches for them more often than is tasteful. Prefer two
   sentences. Keep the join when it genuinely earns the pause. List commas
   ("the real, effective, and saved uids") are unaffected.

8. **Plain verb over the compressed negative.** Applies to any `no <noun>`
   object:

   ```
   BAD   has no super-user            GOOD  does not have a super-user
   BAD   requires no privilege        GOOD  does not require privilege
   BAD   performs no privilege check  GOOD  does not check privilege
   BAD   needs no privilege           GOOD  does not need privilege
   ```

   This is the rule most often under-applied. The last three stood in the same
   branch after the first was fixed. When fixing one instance, grep the branch
   for the pattern, not the phrase.

9. **Keep the noun.** "are privileged operations", not "are privileged". "A
   jail with ...", not "A jail created with ..." when the participle adds
   nothing.

10. **No comma before a restrictive `because` or `so` clause.** Delete the
    comma before `because`. At `so`, split into two sentences, which also
    clears rule 4.

    ```
    BAD   calls it before it attaches to the jail, because jail_attach(2)
          checks ...
    GOOD  calls it before it attaches to the jail because jail_attach(2)
          checks ...

    BAD   calls it inside the jail, because attaching to a jail is itself
          privileged
    GOOD  calls it inside the jail because attaching to a jail is itself
          privileged

    BAD   saved uids, so applyUser can then ...
    GOOD  saved uids. applyUser can then ...

    BAD   drops the effective uid after, so the drop does not need privilege
    GOOD  drops the effective uid after. The drop does not need privilege.
    ```

The GOOD form of the sentence at the top is flat positive assertions, one
proposition each, with no subordination carrying the claim.

## Why the register matters

Each tic compresses reasoning into syntax. The text then reads as a model
showing its work rather than a description of the system.

## Metaphors

No metaphorical or flowery language in commit messages, docs, or explanations.
The reader has to decode a metaphor back into the literal fact.

```
BAD   seed then bite
GOOD  run 1 leaks the jail, run 2 fails on it

BAD   blocked forever waiting for a start that never comes
GOOD  the entrypoint stayed blocked on the exec FIFO
```

A warning or parody a human deliberately wrote into a project is not
rewritten by this pass (see "Text that may not be yours" in the parent skill).
That voice does not extend into routine docs, commit messages, or
explanations.

## Coined terms

Write with the plain verb and the name the domain already uses. Do not invent a
word to cover several cases at once.

Wanting one verb for "pass `allow.X` to grant or `allow.noX` to deny" produced
"state". It reached a commit subject and `docs/jail-parameters.md`.

```
BAD   runj states every toggle.
GOOD  runj explicitly passes every allow.* toggle. If the toggle is true, it
      is passed as allow.<name>. If the toggle is false, it is passed as
      allow.no<name>.

BAD   Pass allow.mount with the per-filesystem parameters
GOOD  Pass allow.mount and allow.mount.<fstype>
```

The first GOOD uses the plain verb and spells out both cases. The second uses
the placeholder the kernel and `jail(8)` use rather than a prose paraphrase of
it.

If a word needs a footnote, or you reached for it because no ordinary verb fit,
it is the wrong word. Coining a label for something that already has a name (a
function, a file, a command, a message) forces the reader to ask what you mean,
and the answer is always the real name. Say "`Fill`'s error branch", not "the
refusal path".

**A coined term does not stay in the prose.** While designing a library, "axis"
was coined for the group of two validation checks it performs. It ran across a
dozen messages and then appeared as an `Axis` field in a proposed error struct.
Two things follow. The cost is not one confusing sentence: the term reaches the
design document, then the requirements, then the code. And coining a word for a
grouping is often the tell that the grouping is not real. `Reason` already said
which check failed. `Axis` was a redundant field.

In the same session "declare", "anchor", and "pin" were the same fault. What
worked was one concrete scenario in the reader's own words.

## Method vocabulary is jargon

A skill's or a subagent's internal vocabulary is not shared vocabulary. A
subagent's report is written for the orchestrating agent, so translate its
terms before they reach Sam. Describe the technique in the words it is made
of.

```
BAD   the kill matrix shows TestX is the sole catcher for two mutations
GOOD  I broke the code on purpose and recorded which tests noticed. For two
      of the breaks, TestX is the only test that fails.

BAD   a test with a kill count of zero
GOOD  a test that no broken version of the code makes fail
```

## Use the settled verb

Software has settled verbs for what software does: a function returns, a field
is declared, assigned, or copied, a request gets a response, a page is parsed.
A softer substitute for a settled verb is the same fault as a coined term and
reads as evasive about what the code does.

```
BAD   the rebuild names the fields one at a time
GOOD  the rebuild declares and assigns each field

BAD   the function answered false
GOOD  the function returned false
```

## Vague filler

Do not use filler that sounds meaningful and is not: "wire the checklist so
work ticks off", "set up the foundation". Name the concrete action, file, or
change, or say nothing. When offering a next step, name the specific file or
function.

## Chat replies

Replies to Sam in the terminal get the same pass. One explanation of a table's
sort order carried these tics beyond the ones above:

```
BAD   So whatever the corpus order is, the table is.
GOOD  The table follows the corpus order.

BAD   The order is deterministic without being meaningful.
GOOD  The order is stable and arbitrary.

BAD   It is behaving as specified, and the specification is the problem.
GOOD  (end the reply after the answer)

BAD   ... which is where your expectations probably come from.
GOOD  (cut: do not tell him what he thinks)

BAD   Say the word and I'll write that up.
GOOD  (cut: no offer to build something he did not ask for)
```

Also cut bolded fragment headers used as decoration on a short answer.

The same reply asserted an unverified fact that one API call would have
settled. Check the claim as well as the sentence.

**Do not narrate the revision.** Apply corrections silently.

```
BAD   the rewritten answer, followed by a list of the tics it removed
GOOD  the rewritten answer
```

## Spelling

Sam writes American English. This covers prose, comments, commit messages, and
code: a `colourOf` helper or a `-colour-` CSS class carries the wrong spelling
into the codebase permanently.

color, behavior, canceled and canceling, center, gray, initialize and
normalize, license (noun and verb), catalog, dialog, analog, neighbor.

## Learning the register from a repository

Sample the commits that person actually wrote: filter by author, and filter out
commits carrying an `Assisted-by` trailer. See
[commit-messages.md](commit-messages.md) for the script and why both filters
are needed.
