# Commit granularity: calibration cases

Granularity is judgment. The one constant: code, tests, and docs for "the
thing" go in the same commit, and "the thing" has no hard-rule definition.

These cases add to the ones in the main skill. They calibrate the question
"is this a self-contained unit a reviewer would want to see whole?" and are
not rules to apply mechanically.

## Too fine

- **Planner over-split.** A package introduced whole is one unit, and a
  command plus the resolution step it cannot ship without is one unit. Five
  of a planner's seven commits for git-ghsa:

  ```
  BAD   ghsa: parse advisory IDs
        ghsa: parse advisory URLs
        ghsa: parse OWNER/REPO
        cmd: add remotes from explicit sources
        cmd: add remotes by remote search
  GOOD  ghsa: parse advisory IDs, URLs, and OWNER/REPO
        cmd: add remotes from explicit sources or by remote search
  ```

- **Helpers split by package.** A split along package lines holds up only
  when the lower commit stands on its own: a new package, or code with a
  second consumer. An earlier `git:` then `cmd:` pair in the history is no
  precedent when that `git:` commit introduced a new package.

  ```
  BAD   git: add RemoteConfig and RemoveRemote
        cmd: add the git ghsa remove command
        (both functions added to the existing git package, used only by
        remove)
  GOOD  cmd: add the git ghsa remove command
        (RemoteConfig and RemoveRemote land in the git package here)
  ```

## Legitimately separate

Cross-cutting concerns stay their own commit: a test approach spanning all
units, a handoff doc, an unrelated refactor.

```
GOOD  Support X
      Support Y
      Support Z
      test: <one approach applied to X, Y, and Z>
```
