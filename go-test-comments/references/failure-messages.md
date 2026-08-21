# Failure messages

Source: https://go.dev/wiki/TestComments, sections "Identify the Function",
"Identify the Input", "Got before Want", "Print Diffs", and "Choose
Human-Readable Subtest Names".

## The four questions a failure message answers

1. Which function failed.
2. What input it was given.
3. What it returned.
4. What was expected.

The usual format carries all four:

```go
t.Errorf("YourFunc(%v) = %v, want %v", in, got, want)
```

## Identify the function

Include the name of the function under test even when it seems obvious from the
name of the test function. Failure output is read in build logs, in CI
summaries, and in bug reports, away from the source.

```go
// BAD
t.Errorf("got %v, want %v", got, want)

// GOOD
t.Errorf("YourFunc(%v) = %v, want %v", in, got, want)
```

For a method or a field of a returned struct, say so in the message:

```go
t.Errorf("New(%q).Timeout = %v, want %v", cfg, got.Timeout, want.Timeout)
```

## Identify the input

Print the function inputs when they are short.

```go
t.Errorf("ParseDuration(%q) = %v, want %v", tc.in, got, want)
```

When the relevant properties of the input are not obvious, because the input is
large or opaque, name the test case with a description of what is being tested
and print that description.

```go
tests := []struct {
    name string // "config with no default region"
    in   *Config
    want string
}{ /* ... */ }

for _, tc := range tests {
    got, err := Resolve(tc.in)
    if err != nil {
        t.Errorf("Resolve(%s) failed: %v", tc.name, err)
        continue
    }
    if got != tc.want {
        t.Errorf("Resolve(%s) = %q, want %q", tc.name, got, tc.want)
    }
}
```

The index of the entry in the test table is not a substitute for a name or for
the inputs. A reader should not have to count table entries to find the failing
case.

```go
// BAD
t.Errorf("case %d: got %v, want %v", i, got, want)
```

## Got before want

Print the value the function actually returned before the value that was
expected: `YourFunc(%v) = %v, want %v`.

Whichever order a message uses, it must say which is which, because existing Go
code is inconsistent about the ordering. The trailing `want %v` does that for a
plain comparison. For a diff, direction is less apparent, so the message needs a
key.

## Print diffs

Large output makes a two-value failure message hard to read. Print a diff.

```go
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("Parse(%q) mismatch (-want +got):\n%s", in, diff)
}
```

Three things matter here:

- The explanatory text gives the direction of the diff.
- `-want +got` matches the argument order `cmp.Diff(want, got)`, so the `-` and
  `+` in the key line up with the `-` and `+` at the start of the diff lines.
- The `\n` before `%s` puts the multi-line diff on its own lines.

If the arguments are passed the other way, the key changes to match:

```go
if diff := cmp.Diff(got, want); diff != "" {
    t.Errorf("Parse(%q) mismatch (-got +want):\n%s", in, diff)
}
```

## Human-readable subtest names

The first argument to `t.Run` becomes a descriptive name for the subtest. The
test runner replaces spaces with underscores and escapes non-printing
characters, so pick names that stay useful and readable after that escaping.

```go
// BAD: the escaped name is unreadable in the log.
t.Run(fmt.Sprintf("%q", tc.in), func(t *testing.T) { /* ... */ })

// GOOD
t.Run("input with trailing newline", func(t *testing.T) {
    t.Logf("input: %q", tc.in)
    // ...
})
```

Identify the inputs with `t.Log` in the subtest body, or in the subtest's
failure messages. Neither is escaped by the test runner.
