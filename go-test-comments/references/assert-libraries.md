# Assert libraries

Source: https://go.dev/wiki/TestComments, sections "Assert Libraries" and "Mark
Test Helpers".

## The rule

Avoid the use of "assert" libraries to help your tests.

## The pattern being avoided

Go developers arriving from xUnit frameworks often want to write code like:

```go
assert.IsNotNil(t, "obj", obj)
assert.StringEq(t, "obj.Type", obj.Type, "blogPost")
assert.IntEq(t, "obj.Comments", obj.Comments, 2)
assert.StringNotEq(t, "obj.Body", obj.Body, "")
```

Three problems with it:

- It stops the test early, if the assert calls `t.Fatalf` or panics, or it omits
  interesting information about what the test got right.
- It forces the assert package to create a whole new sub-language, duplicating
  features already in Go: expression evaluation, comparisons, sometimes more.
- It makes imprecise tests easy to write.

## The Go form

Go has good support for printing structures, so the same check reads:

```go
if obj == nil || obj.Type != "blogPost" || obj.Comments != 2 || obj.Body == "" {
    t.Errorf("AddPost() = %+v", obj)
}
```

Strive to write tests that are precise both about what went wrong and about what
went right, using Go itself.

## Rewriting assertion-style checks

| Assertion call | Go form |
| --- | --- |
| `assert.Nil(t, err)` | `if err != nil { t.Fatalf("Load(%q) failed: %v", path, err) }` |
| `assert.Equal(t, want, got)` | `if got != want { t.Errorf("Load(%q) = %v, want %v", path, got, want) }` |
| `assert.Equal(t, wantStruct, gotStruct)` | `if diff := cmp.Diff(want, got); diff != "" { t.Errorf("Load(%q) mismatch (-want +got):\n%s", path, diff) }` |
| `assert.Contains(t, s, "region")` | `if !strings.Contains(s, "region") { t.Errorf("Describe() = %q, want it to contain %q", s, "region") }` |
| `assert.Len(t, got, 3)` | `if len(got) != 3 { t.Errorf("Split(%q) returned %d parts, want %d", in, len(got), 3) }` |

Each Go form names the function, prints the input, and prints got before want,
which the assertion call cannot do on its own.

## Grouped checks

Checking several properties of one value in a single `if` reports the whole
value once, which shows what was right along with what was wrong:

```go
if obj == nil || obj.Type != "blogPost" || obj.Comments != 2 || obj.Body == "" {
    t.Errorf("AddPost() = %+v", obj)
}
```

Checking them separately reports each property that failed, and the run
continues through all of them:

```go
if obj.Type != "blogPost" {
    t.Errorf("AddPost().Type = %q, want %q", obj.Type, "blogPost")
}
if obj.Comments != 2 {
    t.Errorf("AddPost().Comments = %d, want %d", obj.Comments, 2)
}
```

Both are precise. Pick the one that makes the failure easier to diagnose for the
value in question.

## t.Helper and assertions

`t.Helper` attributes a failure inside a helper to the line that called the
helper. That is right for setup and teardown code, and wrong when it obscures
the connection between a test failure and the conditions that led to it.
`t.Helper` is not to be used to implement assert libraries.
