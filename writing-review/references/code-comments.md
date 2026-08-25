# Code comments

Two rules that pull in different directions: cut hard, and keep what remains
grammatical.

## Cut noise

Concrete removals from a review pass over runj's `integ-test-rootfs-reclaim`:

- **Meta-commentary about why code is structured for testing.** Deleted from
  `isIntegTestJail` and `mountpointsUnder`: "It is pure so the sweep's matching
  decision can be unit-tested without root or FreeBSD." Do not explain that a
  helper was factored out to be testable.
- **Repeated caveats.** "It is best-effort: it logs failures and never fails
  the run" was removed from the individual helpers and stated once at the
  orchestrator.
- **A doc comment on an obvious test function.** `TestIsIntegTestJail` did not
  need one; test names are self-documenting.
- **Incidental asides.** A note about serializing runs on the test host and a
  pf "marker" scoping rationale the code already made obvious.

A comment earns its place by saying something a reader of this codebase cannot
infer.

## Do not describe the lines below

A comment that narrates the next few lines is a restatement. Above two calls
that pass a pair of parameters together, "the kernel requires both ... together,
so both are passed" keeps the requirement and drops the tail.

## Explain from the constraint

A comment explaining why a mechanism exists is where contrast framing bites
hardest.

```
BAD   The allow toggles are read from the config file directly rather than
      taken from ociConfig, so that a toggle the config omits stays distinct
      from one it sets to false.
GOOD  The OCI spec stores allow as bool, but we need to detect the difference
      between unset (false as the zero value) and intentionally false.
```

The rewrite drops the road not taken and states the data-model fact that forces
the design.

## Name the actor

Attribute a behavior to the component that performs it, and check the actor
sentence by sentence rather than once per paragraph. A paragraph whose subject
is runj will carry runj into a sentence about behavior the kernel performs.

```
BAD   runj applies any limit of 2^63 or greater as unlimited
GOOD  runj converts the spec's uint64 to a signed rlim_t; the FreeBSD kernel
      maps a negative limit onto RLIM_INFINITY
```

Name the call that changes state, not the one you happened to observe it
through: `setrlimit(2)` stores the value, `getrlimit(2)` only reports it.

Anchor a behavior to the concrete resulting value where one exists: "specifying
a hostname causes the kernel to give the jail its own UTS information (i.e.,
`host: new`)".

## Stay grammatical

A humanizing pass over the trimmed comments fixed the opposite failure. Terse
does not mean fragmentary.

```
BAD   Used to filter test-only resources
GOOD  so the sweep can tell them apart from unrelated interfaces

BAD   any filesystem left mounted is unmounted first
GOOD  it unmounts anything left mounted
```

No subjectless fragments, no reflexive passive, no em or en dashes. State what
a thing is, or why it is non-obvious, once, in a plain active sentence.
