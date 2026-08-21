---
name: go-test-comments
description: |
  Applies the Go project's "Go Test Comments" wiki guidance to Go test code:
  failure messages that name the function, the input, got, and want; t.Error
  versus t.Fatal; t.Helper; cmp.Equal and cmp.Diff; table-driven tests and
  subtest names; error-semantics testing; the case against assert libraries.
  Use when writing or reviewing Go tests and _test.go files, building
  table-driven tests, wording t.Errorf/t.Fatalf messages, comparing structs or
  JSON output in tests, naming t.Run subtests, checking returned errors, or
  weighing an assertion library such as testify. This is the test-code list; for
  non-test Go style reach for the go-code-review-comments skill.
---

# Go Test Comments

The source is the Go project's wiki page "Go Test Comments" at
https://go.dev/wiki/TestComments, a supplement to Go Code Review Comments aimed
at test code. Follow the rules below when writing Go tests, and cite them by
name in review. Each rule maps to a section of that page. The reference files
carry the longer examples; open one when the summary here is not enough.

- [references/failure-messages.md](references/failure-messages.md): message
  format templates, diff direction keys, subtest-name escaping details.
- [references/comparisons.md](references/comparisons.md): cmp and cmpopts
  usage, `==` semantics, reflect.DeepEqual, protocol buffers, unstable output.
- [references/table-driven-tests.md](references/table-driven-tests.md): fuller
  treatment of table-driven tests, slice and map tables, parallel subtests.
- [references/assert-libraries.md](references/assert-libraries.md): the full
  argument against assert libraries and how to rewrite assertion-style checks.
- [references/error-semantics.md](references/error-semantics.md): testing error
  types, string matching that is acceptable, structuring errors for tests.

Everything outside `_test.go` files, including naming, doc comments, error
strings, receivers, and interface placement, belongs to the parent page; see the
go-code-review-comments skill.

## Failure messages

**Name the function that failed.** A failure message should include the name of
the function under test, even when the test function's own name already implies
it. Logs get read out of context.

```go
// BAD
t.Errorf("got %v, want %v", got, want)

// GOOD
t.Errorf("YourFunc(%v) = %v, want %v", in, got, want)
```

**Print the inputs when they are short.** A reader fixing the test needs to know
which input produced the failure without reading the test source.

```go
// GOOD
t.Errorf("ParseDuration(%q) = %v, want %v", tc.in, got, want)
```

**Name the case and print the name when inputs are large or opaque.** If the
relevant properties of the input are not obvious from printing it, describe what
the case tests and put that description in the failure message.

```go
// GOOD
t.Errorf("Render(%s): got %d bytes, want %d", tc.name, len(got), tc.wantLen)
```

**Never identify a case by its table index.** Nobody wants to count entries in a
test table to work out which case failed.

```go
// BAD
t.Errorf("case %d: got %v, want %v", i, got, want)
```

**Print got before want, and label the order in the message.** The usual format
is `YourFunc(%v) = %v, want %v`. Existing Go code is inconsistent about which
value comes first, so the message has to say which is which. A trailing `want
%v` and a `(-want +got)` diff key both do that.

**Print a diff when the output is large.** Finding the difference between two
large printed values by eye is slow. Print the diff, add text giving its
direction, and start it on a new line because it spans several lines.

```go
// BAD
t.Errorf("Parse(%q) = %+v, want %+v", in, got, want)

// GOOD
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("Parse(%q) mismatch (-want +got):\n%s", in, diff)
}
```

With `cmp.Diff(want, got)`, the key `-want +got` matches the `-` and `+` that
begin the diff lines.

**Choose subtest names that stay readable after escaping.** The test runner
replaces spaces with underscores and escapes non-printing characters, so a name
built from raw input data becomes unreadable in the log.

```go
// BAD
t.Run(fmt.Sprintf("%v", tc.in), func(t *testing.T) { /* ... */ })

// GOOD
t.Run("trailing newline", func(t *testing.T) {
    t.Logf("input: %q", tc.in)
    // ...
})
```

Identify the inputs with `t.Log` inside the subtest body, or in the failure
messages, where the runner does not escape them.

## Comparing values

**Compare the whole structure in one shot.** When a function returns a struct,
build the struct you expect and compare it once with a diff or a deep
comparison. The same applies to arrays and maps.

```go
// BAD
if got.Name != want.Name {
    t.Errorf("NewUser(%q).Name = %q, want %q", in, got.Name, want.Name)
}
if got.Age != want.Age {
    t.Errorf("NewUser(%q).Age = %d, want %d", in, got.Age, want.Age)
}

// GOOD
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("NewUser(%q) mismatch (-want +got):\n%s", in, diff)
}
```

**Compare multiple return values individually.** Several return values do not
need wrapping in a struct before comparison. Compare each and print it.

**Use the cmp package.** Use `cmp.Equal` for equality and `cmp.Diff` for a
human-readable diff. It is maintained by the Go team, produces stable results
across Go releases, and is user-configurable.

**Prefer cmp to reflect.DeepEqual in new code.** `reflect.DeepEqual` is
sensitive to changes in unexported fields and other implementation details.
Update older code to `cmp` where practical.

**Configure cmp with cmpopts when exact equality does not apply.** For
approximate equality, other semantic equality, or fields that cannot be compared
at all, pass options such as `cmpopts.EquateApprox` for a float tolerance and
`cmpopts.IgnoreInterfaces` for incomparable fields (an `io.Reader` field, for
example). If no configuration fits, do whatever works.

**Compare protocol buffer messages with the proto.Equal comparer.**

```go
if diff := cmp.Diff(want, got, cmp.Comparer(proto.Equal)); diff != "" {
    t.Errorf("Build() mismatch (-want +got):\n%s", diff)
}
```

**Do not assert on output whose stability you do not control.** Compare
semantically relevant information that survives changes in your dependencies.
For a formatted string or serialized bytes, assume the exact output can change.
`json.Marshal` makes no guarantee about the exact bytes it emits, and its output
has changed in the past.

```go
// BAD
if string(b) != `{"id":1,"name":"gopher"}` {
    t.Errorf("Marshal() = %s, want %s", b, `{"id":1,"name":"gopher"}`)
}

// GOOD
var got Record
if err := json.Unmarshal(b, &got); err != nil {
    t.Fatalf("Unmarshal(%s) failed: %v", b, err)
}
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("Marshal/Unmarshal round trip mismatch (-want +got):\n%s", diff)
}
```

**Know what `==` covers.** The operator uses the language-defined comparisons:
numeric, string, and pointer values, and structs whose fields are such values.
Two pointers are equal only when they point to the same variable.

## Keeping the test running

**Prefer t.Error to t.Fatal.** A test run should report every failed check, so
whoever fixes it sees the whole picture in one run. When comparing several
properties of one output, use `t.Error` for each comparison.

```go
// BAD
if got.Name != want.Name {
    t.Fatalf("Load().Name = %q, want %q", got.Name, want.Name)
}

// GOOD
if got.Name != want.Name {
    t.Errorf("Load().Name = %q, want %q", got.Name, want.Name)
}
if got.Size != want.Size {
    t.Errorf("Load().Size = %d, want %d", got.Size, want.Size)
}
```

**Reserve t.Fatal for setup that the test cannot run without.** In a
table-driven test, that means setup performed before the loop.

**In a loop without subtests, use t.Error then continue.** The failure ends work
on that table entry and the next entry still runs.

```go
for _, tc := range tests {
    got, err := Parse(tc.in)
    if err != nil {
        t.Errorf("Parse(%q) failed: %v", tc.in, err)
        continue
    }
    // ... checks on got
}
```

**Inside a t.Run subtest, use t.Fatal for a case that cannot continue.**
`t.Fatal` ends only the current subtest, so the remaining cases still run.

```go
for _, tc := range tests {
    t.Run(tc.name, func(t *testing.T) {
        got, err := Parse(tc.in)
        if err != nil {
            t.Fatalf("Parse(%q) failed: %v", tc.in, err)
        }
        // ... checks on got
    })
}
```

## Test helpers

**Call `t.Helper` in a helper that takes a `*testing.T`.** A test helper performs
setup or teardown, such as building an input message, and does not depend on the
code under test. `t.Helper` attributes its failures to the line that called it.

```go
func TestSomeFunction(t *testing.T) {
    golden := readFile(t, "testdata/golden.txt")
    // ...
}

func readFile(t *testing.T, filename string) string {
    t.Helper()

    contents, err := os.ReadFile(filename)
    if err != nil {
        t.Fatal(err)
    }
    return string(contents)
}
```

**Skip t.Helper where it hides the cause of a failure.** The attribution is
wrong when the conditions that led to the failure live inside the helper. In
particular, `t.Helper` is not a tool for implementing assert libraries.

## Test structure

**Use a table-driven test when many cases share the same checking logic.** Good
fits are checking that actual output equals expected output, and checking that
outputs always satisfy the same invariants.

**Write separate test functions when cases need different checking logic.** Test
code is hard to follow when each table entry passes through several layers of
conditional logic to pick the right check for the right input.

**Use a sequence of subtests in one function for cases with different logic and
identical setup.**

**Split success cases and error cases into two table-driven functions.** One
function checks that non-error output matches exactly, the other checks that
invalid input produces a non-nil error.

## Error semantics

**Do not use string comparison to check which type of error was returned.**
Comparing error strings, or using `reflect.DeepEqual` on errors, makes the test
fail whenever a message is reworded, which turns it into a change-detector test.

```go
// BAD
if err.Error() != "user 42 not found" {
    t.Errorf("Lookup(42) error = %v, want user 42 not found", err)
}

// GOOD
if !errors.Is(err, ErrNotFound) {
    t.Errorf("Lookup(42) error = %v, want %v", err, ErrNotFound)
}
```

**String matching is fine for checking a property of a message.** Checking that
an error from the package under test mentions the offending parameter name is a
legitimate use.

**Separate the human-readable message from the programmatic structure when the
error type matters to callers.** Expose the structure callers check, and avoid
`fmt.Errorf`, which tends to destroy semantic error information.

**Test only for a non-nil error when the API does not define error kinds.** If
the API makes no promise about which error comes back for which input, build the
messages with `fmt.Errorf` and assert that an error was returned when one was
expected.

## Assert libraries

**Write checks in Go with `if` and `t.Errorf`.** An assert library either stops
the test early (when the assertion calls `t.Fatalf` or panics) or drops the
information about what the test got right. It also builds a sub-language on top
of Go, duplicating expression evaluation and comparison, and makes imprecise
tests easy to write.

```go
// BAD
assert.IsNotNil(t, "obj", obj)
assert.StringEq(t, "obj.Type", obj.Type, "blogPost")
assert.IntEq(t, "obj.Comments", obj.Comments, 2)
assert.StringNotEq(t, "obj.Body", obj.Body, "")

// GOOD
if obj == nil || obj.Type != "blogPost" || obj.Comments != 2 || obj.Body == "" {
    t.Errorf("AddPost() = %+v", obj)
}
```

Go prints structures well, so a single `t.Errorf` with `%+v` says what happened.

## Outside this source

The wiki page does not cover test doubles (fakes, stubs, mocks), `t.Cleanup`,
test-only exported API, control flow in test bodies, or goroutines in tests.

Go Code Review Comments has its own two-rule summary of test failures under
"Useful Test Failures", which writes the message with a semicolon,
`Foo(%q) = %d; want %d`. Both separators are in use; the rest of that page
covers non-test code. It also asks a new package to ship a runnable `Example`
function or a test demonstrating a complete call sequence, which this page does
not mention. See the go-code-review-comments skill.

## Review checklist

- Does every failure message name the function under test?
- Does it print the input, or a case name when the input is large or opaque?
- Is the got value printed before the want value, with the order labeled?
- Is any case identified only by its table index?
- Do large comparisons print a `cmp.Diff` with a direction key and a leading
  newline?
- Are subtest names readable after spaces and non-printing characters are
  escaped?
- Are structs, arrays, and maps compared whole?
- Are comparisons done with `cmp`?
- Does any assertion depend on the exact bytes of `json.Marshal` or another
  package's formatting?
- Is `t.Fatal` limited to setup and to subtest bodies, with `t.Error` plus
  `continue` in loops without subtests?
- Do helpers taking `*testing.T` call `t.Helper`?
- Does the table hold cases that need different checking logic?
- Are error checks free of error-string comparison?
- Are there assert-library calls that should be plain `if` statements?
