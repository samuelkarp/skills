# Testing error semantics

Source: https://go.dev/wiki/TestComments, section "Test Error Semantics".

## The problem with error strings

A unit test that performs string comparisons, or uses `reflect.DeepEqual`, to
check that a particular kind of error is returned for a particular input is
fragile: rewording the error message later breaks the test. That turns the unit
test into a change detector
(https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html).

Do not use string comparison to check what type of error your function returns.

```go
// BAD
_, err := Lookup(42)
if err == nil || err.Error() != "user 42 not found" {
    t.Errorf("Lookup(42) error = %v, want %q", err, "user 42 not found")
}
```

## String matching that is acceptable

It is fine to use string comparison to check that an error message coming from
the package under test satisfies some property, for example that it includes the
parameter name.

```go
// GOOD
_, err := Resolve("region", "")
if err == nil {
    t.Fatalf("Resolve(%q, %q) succeeded, want error", "region", "")
}
if !strings.Contains(err.Error(), "region") {
    t.Errorf("Resolve(%q, %q) error = %v, want it to name the parameter %q",
        "region", "", err, "region")
}
```

## When the error type matters

If you care about testing the exact type of error your functions return,
separate the error string intended for human eyes from the structure exposed for
programmatic use. Avoid `fmt.Errorf` there, which tends to destroy semantic
error information.

```go
// Package under test exposes the structure callers check.
var ErrNotFound = errors.New("not found")

type UserError struct {
    ID   int64
    Code Code
}

func (e *UserError) Error() string { return fmt.Sprintf("user %d: %v", e.ID, e.Code) }
func (e *UserError) Is(target error) bool { return target == ErrNotFound && e.Code == CodeMissing }
```

The test checks the structure, not the text:

```go
_, err := Lookup(42)
if !errors.Is(err, ErrNotFound) {
    t.Errorf("Lookup(42) error = %v, want %v", err, ErrNotFound)
}

var uerr *UserError
if !errors.As(err, &uerr) {
    t.Fatalf("Lookup(42) error = %v, want a *UserError", err)
}
if uerr.ID != 42 {
    t.Errorf("Lookup(42) error ID = %d, want %d", uerr.ID, 42)
}
```

## When the error type does not matter

Many people who write APIs do not care exactly which kinds of errors their API
returns for different inputs. For such an API, it is sufficient to create error
messages with `fmt.Errorf` and, in the unit test, check only whether the error
was non-nil when an error was expected.

```go
for _, tc := range tests {
    _, err := Parse(tc.in)
    if gotErr := err != nil; gotErr != tc.wantErr {
        t.Errorf("Parse(%q) error = %v, want error presence %t", tc.in, err, tc.wantErr)
    }
}
```

## Beyond the source page

The wiki page predates the error-wrapping API added in Go 1.13. `fmt.Errorf`
with the `%w` verb wraps an error so that `errors.Is` and `errors.As` still find
it, which preserves the programmatic structure that plain `fmt.Errorf` discards.
The page's rule stands either way: check the structure, not the message text.
