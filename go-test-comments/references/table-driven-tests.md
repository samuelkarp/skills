# Table-driven tests

Sources: https://go.dev/wiki/TestComments, sections "Table-Driven Tests vs
Multiple Test Functions", "Keep Going", and "Choose Human-Readable Subtest
Names"; and the page it links to, https://go.dev/wiki/TableDrivenTests.

## What a table-driven test is

Each table entry is a complete test case with inputs and expected results, and
sometimes extra information such as a test name that makes the output readable.
The test iterates the entries and performs the necessary checks for each one.
The test code is written once and amortized over every entry, so it is worth
writing careful checks with good error messages. Table-driven testing is not a
tool or a package, it is a way of writing tests.

Copy and paste in a test is the signal to consider a table, or to pull the
copied code into a helper function.

## When a table fits

Use a table whenever many different cases can be tested with similar testing
logic. Two common shapes:

- Checking that the actual output of a function equals the expected output.
- Checking that the outputs of a function always conform to the same set of
  invariants.

## When separate test functions fit better

When some cases need different checking logic from others, write multiple test
functions. Test code becomes hard to understand when every entry in a table has
to pass through several kinds of conditional logic so the right check runs for
the right input.

When the cases need different logic but identical setup, a sequence of subtests
inside a single test function can work.

The two approaches combine. For a function where you check that the non-error
output matches exactly and also check that invalid input returns a non-nil
error, the clearest result is two table-driven test functions: one for the
normal outputs, one for the error outputs.

## Slice of structs

From the `fmt` package's own tests:

```go
var flagtests = []struct {
    in  string
    out string
}{
    {"%a", "[%a]"},
    {"%-a", "[%-a]"},
    {"%+a", "[%+a]"},
    {"%#a", "[%#a]"},
    {"% a", "[% a]"},
    {"%0a", "[%0a]"},
    {"%1.2a", "[%1.2a]"},
    {"%-1.2a", "[%-1.2a]"},
    {"%+1.2a", "[%+1.2a]"},
    {"%-+1.2a", "[%+-1.2a]"},
    {"%-+1.2abc", "[%+-1.2a]bc"},
    {"%-1.2abc", "[%-1.2a]bc"},
}

func TestFlagParser(t *testing.T) {
    var flagprinter flagPrinter
    for _, tt := range flagtests {
        t.Run(tt.in, func(t *testing.T) {
            s := Sprintf(tt.in, &flagprinter)
            if s != tt.out {
                t.Errorf("got %q, want %q", s, tt.out)
            }
        })
    }
}
```

Here the input is the subtest name and the failure message carries the result
and the expected result, so a failure says which case failed and why without
reading the test code. Go Test Comments asks for more than this example gives:
name the function in the message as well, `Sprintf(%q) = %q, want %q`.

A `t.Errorf` call is not an assertion. The test continues after an error is
logged. When testing something with integer input, it is worth knowing whether
the function fails for all inputs, only for odd inputs, or for powers of two.

## Map of cases

Cases can also be stored in a map.

```go
tests := map[string]struct {
  input  string
  result string
}{
  "empty string": {
    input:  "",
    result: "",
  },
  "one character": {
    input:  "x",
    result: "x",
  },
  "one multi byte glyph": {
    input:  "🎉",
    result: "🎉",
  },
  "string with multiple multi-byte glyphs": {
    input:  "🥳🎉🐶",
    result: "🐶🎉🥳",
  },
}

for name, test := range tests {
  // test := test // NOTE: uncomment for Go < 1.22, see /doc/faq#closures_and_goroutines
  t.Run(name, func(t *testing.T) {
    t.Parallel()
    if got, expected := reverse(test.input), test.result; got != expected {
      t.Fatalf("reverse(%q) returned %q; expected %q", test.input, got, expected)
    }
  })
}
```

One advantage of a map is that the name of each case is simply the map key. More
importantly, map iteration order is not specified and is not guaranteed to be
the same from one iteration to the next, which keeps each case independent of
the others and keeps ordering from affecting results.

## Parallel subtests

Parallelizing a table test is simple but needs precision. Note the three
changes, especially the re-declaration of `test` for Go versions before 1.22.

```go
package main

import (
    "testing"
)

func TestTLog(t *testing.T) {
    t.Parallel() // marks TLog as capable of running in parallel with other tests
    tests := []struct {
        name string
    }{
        {"test 1"},
        {"test 2"},
        {"test 3"},
        {"test 4"},
    }
    for _, test := range tests {
    // test := test // NOTE: uncomment for Go < 1.22, see /doc/faq#closures_and_goroutines
        t.Run(test.name, func(t *testing.T) {
            t.Parallel() // marks each test case as capable of running in parallel with each other
            t.Log(test.name)
        })
    }
}
```

## Failing a single entry

Failures that set up the whole test function, before the loop, are `t.Fatal`
material. Failures affecting one entry are handled by where the check sits:

```go
// Without subtests: t.Error then continue.
for _, tc := range tests {
    got, err := Parse(tc.in)
    if err != nil {
        t.Errorf("Parse(%q) failed: %v", tc.in, err)
        continue
    }
    if got != tc.want {
        t.Errorf("Parse(%q) = %v, want %v", tc.in, got, tc.want)
    }
}

// Inside t.Run: t.Fatal ends this subtest and lets the next one run.
for _, tc := range tests {
    t.Run(tc.name, func(t *testing.T) {
        got, err := Parse(tc.in)
        if err != nil {
            t.Fatalf("Parse(%q) failed: %v", tc.in, err)
        }
        if got != tc.want {
            t.Errorf("Parse(%q) = %v, want %v", tc.in, got, tc.want)
        }
    })
}
```

## Naming the cases

The name passed to `t.Run` is escaped by the test runner: spaces become
underscores and non-printing characters are escaped. Pick case names that read
well after that. Print the inputs with `t.Log` inside the subtest, or in the
failure messages, where they are not escaped. Do not identify a case by its
index in the table.
