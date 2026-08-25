# Register

The ten tics in the parent skill all came out of one commit body on runj's
`root-allow` branch, "Set the group list before attaching to the jail". Review
called the phrasing a Claudeism and rejected it everywhere: not in commit
messages, not in code comments, not in docs.

## The rejected sentence

> `setgroups(2)` and `setgid(2)` require privilege that a jail with
> `allow.suser` disabled does not grant to uid 0.

The sentence is accurate. That did not save it. The reviewer rewrote a more
accurate body into a less accurate one purely to escape the register, then
corrected the accuracy separately.

Six tics in that one sentence:

1. **Proposition as modifier.** "that a jail with `allow.suser` disabled does
   not grant to uid 0" is a complete claim (condition, negation, and the party
   negated) folded into a trailing `that`-clause hanging off `privilege`, so
   the sentence can keep moving. Assert one proposition per sentence.

2. **Definition by negation.** "does not grant" says what fails to happen, to
   whom, under what condition. The positive form replaced all of it: "a jail
   created with `allow.suser` disabled has no super-user". That also matches
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

Flagged in the same pass: the intensifier tail "whatever the jail allows",
replaced with the concrete condition "in a jail with `allow.suser` disabled".

## Second pass

The replacement text was still too Claude. Four more rules:

7. **Clause-joining commas, used sparingly.** A comma before `and` or `but`
   joining two independent clauses reads as "a marker of a pause indicating too
   much drama". Independent clauses can be used, but with taste, and model
   training reaches for them more often than is tasteful.
   Prefer two sentences. Keep the join when it genuinely earns the pause. List
   commas ("the real, effective, and saved uids") are unaffected.

8. **Plain verb over the compressed negative.** Applies to any `no <noun>`
   object:

   ```
   BAD   has no super-user            GOOD  does not have a super-user
   BAD   requires no privilege        GOOD  does not require privilege
   BAD   performs no privilege check  GOOD  does not check privilege
   BAD   needs no privilege           GOOD  does not need privilege
   ```

   This is the rule most often under-applied. After the first fix landed,
   "requires no privilege", "needs no privilege", and "performs no privilege
   check" were all still standing in the same branch. When a correction lands,
   grep the branch for the pattern rather than the phrase that was quoted.

9. **Keep the noun.** "are privileged operations", not "are privileged". "A
   jail with ...", not "A jail created with ..." when the participle adds
   nothing.

10. **No comma before a restrictive `because` or `so` clause.** "Why comma"
    came back three times in one review round:

    ```
    BAD   calls it before it attaches to the jail, because jail_attach(2) checks ...
    BAD   calls it inside the jail, because attaching to a jail is itself privileged
    BAD   saved uids, so applyUser can then ...
    BAD   drops the effective uid after, so the drop does not need privilege
    ```

    Delete the comma before `because`. At `so`, split into two sentences, which
    also clears rule 4.

## The target

After three passes, the sentence became two:

> setgroups(2), setgid(2), and raising a hard limit are privileged operations.
> A jail with allow.suser disabled does not have a super-user.

Flat positive assertions, one proposition each, no subordination carrying the
claim.

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

Deliberate project-authored literary content is a scoped exception: an
intentional warning or parody a project chose to communicate risk stays. Do not
extend that voice into routine docs, commit messages, or explanations.

## Coined terms

Write with the plain verb and the name the domain already uses. Do not invent a
word to cover several cases at once.

Wanting one verb for "pass `allow.X` to grant or `allow.noX` to deny" produced
"state" ("runj states every toggle"). It reached a commit subject and
`docs/jail-parameters.md` before review asked "what do you mean 'state them'".
The rewrite: "runj explicitly passes every `allow.*` toggle. If the toggle is
true, it is passed as `allow.<name>`. If the toggle is false, it is passed as
`allow.no<name>`." The plain verb, with both cases spelled out.

Same pass, on names: "Pass allow.mount with the per-filesystem parameters"
became "Pass allow.mount and allow.mount.<fstype>", using the placeholder the
kernel and `jail(8)` use rather than a prose paraphrase of it.

If a word needs a footnote, or you reached for it because no ordinary verb fit,
it is the wrong word. Coining a label for something that already has a name (a
function, a file, a command, a message) forces the reader to ask what you mean,
and the answer is always the real name. Say "`Fill`'s error branch", not "the
refusal path".

**A coined term does not stay in the prose.** While designing a library, "axis"
was coined for the group of two validation checks it performs. It ran across a
dozen messages and then appeared as an `Axis` field in a proposed error struct.
The response: "my point isn't just about this struct, you used that term earlier
and I don't want it to bleed into the ultimate set of full requirements that we
build." Two things follow. The cost is not one confusing sentence: the term
reaches the design document and then the code. And coining a word for a grouping
is often the tell that the grouping is not real. `Reason` already said which
check failed. `Axis` was a redundant field.

In the same session "declare", "anchor", and "pin" each drew "you're confusing
me again" until the vocabulary was dropped in favor of one concrete scenario in
the reader's own words.

## Vague filler

Do not use filler that sounds meaningful and is not: "wire the checklist so
work ticks off", "set up the foundation". Name the concrete action, file, or
change, or say nothing. When offering a next step, name the specific file or
function.

## Learning the register from a repository

Sample the commits that person actually wrote: filter by author, and filter out
commits carrying an `Assisted-by` trailer. See
[commit-messages.md](commit-messages.md) for the script and why both filters
are needed.
