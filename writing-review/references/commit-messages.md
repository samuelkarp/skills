# Commit messages

Follow the chris.beams style, https://chris.beams.io/posts/git-commit/.

## Subject

- Imperative mood, capitalized, no trailing period, 50 characters or fewer.
- The subject verb names the literal action.
- Blank line between subject and body.

## Default to a subject only

The subject plus the diff usually convey the change, and a body that restates
them gets deleted.

A body earns its place only for a fact a reader cannot infer from the subject
and the diff: a lint rule ID being fixed, a specific value being replaced, a
production change made to enable a test. Keep the body to that fact.

Do not write a body that justifies why the change works or is safe when the
diff shows it, and never answer a concern raised only in the working
conversation. For "Use createJail in TestJailHostMode" a paragraph explained
that the helper's return sufficed because the test needs only the jail id after
create. It was inferable from the diff and answered the author's own earlier
worry. The commit went back to a subject line.

Wrap the body at 72 characters and count before committing:

```sh
git log -1 --format=%B | awk 'length>72'
```

## Body style

Review rewrote a body on runj's `root-allow` ("Handle unset allow fields").
The differences are the style to copy.

Before:

> Pass an allow.* parameter only for a field the container configuration
> sets.  A field set true is passed as allow.<name> and one set false as
> allow.no<name>; a field the configuration omits is not passed at all,
> so the jail takes the kernel's default for it.
>
> Telling a field the configuration omits from one it sets to false needs
> a second read of config.json.  The runtime-spec Go binding types the
> toggles as bools tagged omitempty, which collapses the two, so
> oci.LoadJailAllow reads the block again through pointer-typed fields.

After:

> Only pass allow.* parameters for explicitly set fields. True values are
> passed as allow.<name> and false values are passed as allow.no<name>. Do
> not pass unset fields as that would override kernel defaults.
>
> The specs-go package represents the allow fields as bool, which makes it
> impossible to distinguish unset from explicit false using the
> encoding/json Marshal or Unmarshal. A separate defined struct with *bool
> fields is used instead.

What to carry over:

- **Stay in the imperative the subject sets.** "Only pass...", "Do not
  pass...". Not a narration of what happens ("a field set true is passed as").
- **Give a rule its reason, and put an untaken path in the conditional.** "Do
  not pass unset fields as that would override kernel defaults" says what would
  go wrong.
- **Name real identifiers over descriptions of them.** `specs-go`,
  `encoding/json`, `Marshal`, `Unmarshal`, not "the runtime-spec Go binding" or
  "tagged omitempty".
- **Cause before effect.** Lead with the constraint (the type is a bool), then
  what it makes impossible, then what the change does about it. Do not lead
  with the need and arrive at the cause last.
- **Drop the function name when the shape is the point.** The rewrite cut
  `oci.LoadJailAllow` for "A separate defined struct with *bool fields is used
  instead"; the diff supplies the location.

Two boundaries, both confirmed in review:

- **A contrast is wanted when the body describes a problem and the approach
  taken to fix it.** "is used instead" contrasts with the `specs-go` type named
  in the same sentence, which the reader can see. The no-contrast rule targets
  defending a design against a rejected alternative the reader never raised.
- **Sentence spacing is not part of this style.** Authors are inconsistent
  about one space or two after a period, and it carries no meaning. Do not
  normalize it in either direction. Wrap at 72.

## No phantom historical contrast

Do not frame a change as an improvement over a prior state that a reader of the
history will not see: "X rather than only Y", "instead of the old Y", "no
longer does Y". The diff against the parent already shows what changed.

This bites hardest after squashing or amending. A squashed commit added both a
create/delete test and a behavioral test, and the message said the behavioral
test verifies the kernel "rather than only that create and delete succeed". No
create/delete-only state exists in history. It became "confirming the kernel
applied ip6.addr".

Contrasting two things that both exist in the current tree, such as two
coexisting tests, is fine.

## Trailers

Never credit Claude with `Co-authored-by` or `Signed-off-by`. AI tools do not
hold copyright. `Assisted-by` is the correct attribution, per the Linux kernel
coding-assistants guide
(`Documentation/process/coding-assistants.rst`):

```
Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL]
```

For example `Assisted-by: Claude Code:claude-opus-5`. Name the model that
authored the code, not the orchestrating model. When more than one model
authored parts of a commit, name the one that wrote the bulk of it.

`Co-authored-by` is correct for a human whose work the commit carries. When a
commit takes code or a test case from someone else's branch, credit them with
`Co-authored-by: NAME <EMAIL>` taken from their commit's author field, in the
same trailer block as `Assisted-by`. runj's `root-allow` took the `boolIovec`
helper and a test case from a contributor's independent branch and carries that
credit.

## Sampling a maintainer's handwritten voice

To learn a register from a repository's history, sample the commits that one
person actually wrote. Both filters below are required, and each one alone
produces a misleading sample.

**Filter by author.** A repository with more than one contributor mixes
voices, and an unfiltered sample averages them into a register nobody writes
in. Match on the commit email rather than the display name, which varies
across a person's machines. List the candidates first:

```sh
git log --format='%an <%ae>' | sort | uniq -c | sort -rn
```

**Filter out assisted commits.** A message carrying an `Assisted-by` trailer
was drafted by a model and was only good enough for the author to accept. It
records what they tolerated, not how they write. Filter per record, not per
line: `git log --format=%B | grep -v Assisted-by` strips the trailer line and
keeps the record, which silently leaves the assisted bodies in the sample.

```sh
for c in $(git rev-list --no-merges --author='<email>' <ref>); do
  git log -1 --format=%B $c | grep -qi 'Assisted-by' && continue
  git log -1 --format='### %h%n%B' $c
done
```

Expect the handwritten sample to be shorter and plainer than the assisted one.
In a runj sample the author's own bodies ran two to five plain lines, stating
the situation and then what the change does, with no source citations and no
stacked subordinate clauses. Aim drafts at that sample. Sampling the assisted
commits inflates the target register.
