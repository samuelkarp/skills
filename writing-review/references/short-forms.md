# Release notes and error notes

Both are read in a glance by someone deciding what to do next. Draft at the
terse end. Starting from the shortest defensible text costs one round when
more is wanted. Drafting long costs several rounds of deletion.

## Release notes

List the changes a user would act on, one plain line each, with no preamble.
The first draft of the better-ghsa 0.0.2 notes ran seventy lines, with an
explanatory paragraph per change. What to cut:

- **A reassuring preamble.** It answers a concern only the author had.

  ```
  BAD   This release changes nothing about what the extension writes to
        GitHub, what it stores, or the repositories it acts on.
  GOOD  (no preamble; the list starts at the first change)
  ```

  The draft's own review pass had flagged this line, and it was kept anyway.

- **Cosmetic changes, one line each.** A visible change is not automatically a
  change worth a line. Several visual changes get one line between them.

  ```
  BAD   - Chips are drawn filled or faint.
        - <element> moved to another cell.
        - <control> is hidden on rows it does not apply to.
  GOOD  - Restyled chips and rows on both lists, including the
          user-specified triage value.
  ```

- **Progress indicators and error messages as features.** A loading count or
  a banner that names what it could not read does not get a line. A fixed bug
  in one of them still gets a Fixed line ("Fixed loading status for completed
  list").
- **Internal UI vocabulary.** "the waiting chip" is what the code calls it,
  and a reader does not know what it means. Name what the reader sees.
- **Clever phrasing.** Say what the thing does. "The two lists line up" names
  no behavior at all.

  ```
  BAD   A duplicate says what it duplicates.
  GOOD  Duplicates link to the canonical advisory, issue, or pull request.
  ```

Register: impersonal ("user-specified triage value", not "the triage value you
set"). Bug lines are terse noun phrases with the verb once.

The whole of better-ghsa 0.0.2:

    ## New
    - Filters on the completed list, including closed advisories with no reason set.
    - Duplicates link to the canonical advisory, issue, or pull request.
    - Published advisories appear in the closure reason statistics.
    - Restyled chips and rows on both lists, including the user-specified triage value.

    ## Bugs
    - Fixed stale closure reason after saving
    - Fixed loading status for completed list
    - Fixed stale failure banner

What survived: a workflow capability, a link, a statistic that changed
meaning, and one line for every visual change together. Strike every line
that does not change what someone does. Expect a handful of survivors.

## CLI error and hint notes

Offer `<subject>: <fact>` first for new error or hint text. These are from the
git-ghsa design for `ls-branches` (the fork lines) and `prune` (the branch
line):

    fork foo/bar-ghsa-abcd-1234-wxyz: not found or no access
    fork foo/bar-ghsa-abcd-1234-wxyz: requires repo scope or contents:read
    fix-traversal-1.0: not fully merged

Full sentences and shorter narrative sentences are both too long for a note.

```
BAD   GitHub returns 404 both when ... and when ...
GOOD  fork foo/bar-ghsa-abcd-1234-wxyz: not found or no access
```

One fact, no outcome tail. That the branch stays is `prune`'s documented
behavior, so the line does not repeat it.

```
BAD   fix-traversal-1.0: not fully merged, kept
GOOD  fix-traversal-1.0: not fully merged
```

Existing error text in a project keeps its established form unless Sam asks to
change it. The earlier git-ghsa commands keep their sentence-form notes. Match
the surrounding commands.
