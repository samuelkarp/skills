# Comparing values in tests

Source: https://go.dev/wiki/TestComments, sections "Compare Full Structures",
"Equality Comparison and Diffs", and "Compare Stable Results".

## What `==` compares

The `==` operator uses the language-defined comparisons
(https://go.dev/ref/spec#Comparison_operators). It applies to numeric, string,
and pointer values, and to structs whose fields are values of those kinds. Two
pointers are equal only when they point to the same variable, so `==` on
pointers does not compare what they point to.

## Compare full structures

When a function returns a struct, construct the struct you expect and compare it
in one shot with a diff or a deep comparison. Field-by-field comparisons produce
more code, more failure messages, and no better information. The same rule
applies to arrays and maps.

```go
// BAD
got := NewUser("gopher")
if got.Name != "gopher" {
    t.Errorf("NewUser(%q).Name = %q, want %q", "gopher", got.Name, "gopher")
}
if got.Admin {
    t.Errorf("NewUser(%q).Admin = true, want false", "gopher")
}
if got.Quota != 100 {
    t.Errorf("NewUser(%q).Quota = %d, want %d", "gopher", got.Quota, 100)
}

// GOOD
want := User{Name: "gopher", Admin: false, Quota: 100}
if diff := cmp.Diff(want, NewUser("gopher")); diff != "" {
    t.Errorf("NewUser(%q) mismatch (-want +got):\n%s", "gopher", diff)
}
```

Multiple return values do not need wrapping in a struct first. Compare each
return value on its own and print it.

## Use the cmp package

Use `cmp.Equal` (https://pkg.go.dev/github.com/google/go-cmp/cmp#Equal) for
equality comparison and `cmp.Diff`
(https://pkg.go.dev/github.com/google/go-cmp/cmp#Diff) for a human-readable diff
between objects.

`cmp` is not part of the standard library, but it is maintained by the Go team,
produces stable results across Go version updates, and is user-configurable, so
it serves most comparison needs.

Older code uses `reflect.DeepEqual` for complex structures. Prefer `cmp` in new
code and update older code where practical: `reflect.DeepEqual` is sensitive to
changes in unexported fields and other implementation details.

## Configuring cmp

Approximate equality, other kinds of semantic equality, and fields that cannot
be compared for equality at all (a field holding an `io.Reader`, for example)
are handled by tweaking `cmp.Diff` or `cmp.Equal` with `cmpopts`
(https://pkg.go.dev/github.com/google/go-cmp/cmp/cmpopts) options.

```go
opts := []cmp.Option{
    cmpopts.IgnoreInterfaces(struct{ io.Reader }{}),
    cmpopts.EquateApprox(0, 1e-9),
}
if diff := cmp.Diff(want, got, opts...); diff != "" {
    t.Errorf("Build(%s) mismatch (-want +got):\n%s", tc.name, diff)
}
```

A worked example of `cmpopts.IgnoreInterfaces` is at
https://go.dev/play/p/vrCUNVfxsvF.

When no configuration meets the need, this technique does not work for that
type, so do whatever works.

## Protocol buffers

`cmp` works on protocol buffer messages when the comparison includes the
`cmp.Comparer(proto.Equal)` option.

```go
if diff := cmp.Diff(want, got, cmp.Comparer(proto.Equal)); diff != "" {
    t.Errorf("Convert(%s) mismatch (-want +got):\n%s", tc.name, diff)
}
```

## Compare stable results

Avoid comparing results that depend on the output stability of an external
package you do not control. Compare semantically relevant information that is
stable and resistant to changes in your dependencies. For a function that
returns a formatted string or serialized bytes, it is generally not safe to
assume the output is stable.

`json.Marshal` (https://pkg.go.dev/encoding/json/#Marshal) makes no guarantee
about the exact bytes it emits. It is free to change the output, and has done so
in the past. A test that compares the exact JSON string breaks when the `json`
package changes how it serializes. Parse the JSON and check that it is
semantically equivalent to the expected data structure.

```go
// BAD
b, err := json.Marshal(rec)
if err != nil {
    t.Fatalf("Marshal(%+v) failed: %v", rec, err)
}
if string(b) != `{"id":1,"name":"gopher"}` {
    t.Errorf("Marshal(%+v) = %s, want %s", rec, b, `{"id":1,"name":"gopher"}`)
}

// GOOD
b, err := json.Marshal(rec)
if err != nil {
    t.Fatalf("Marshal(%+v) failed: %v", rec, err)
}
var got map[string]any
if err := json.Unmarshal(b, &got); err != nil {
    t.Fatalf("Unmarshal(%s) failed: %v", b, err)
}
want := map[string]any{"id": float64(1), "name": "gopher"}
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("Marshal(%+v) mismatch (-want +got):\n%s", rec, diff)
}
```

The same reasoning covers `fmt` verbs on types you do not own, error strings
from other packages, and any text produced by a formatter that is free to change
its layout.
