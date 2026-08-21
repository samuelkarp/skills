---
name: go-code-review-comments
description: |
  Applies the Go project's "Code Review Comments" style rules to Go code.
  Use when reviewing a Go change, writing or refactoring Go code, or deciding on naming,
  doc comments, error handling and error strings, receivers, interfaces, context.Context
  plumbing, goroutine lifetimes, imports, or test failure messages. Covers gofmt/goimports,
  MixedCaps and initialisms, package and variable names, pointer vs value receivers, in-band
  errors, indenting error flow, named results, naked returns, crypto/rand, and a checklist.
  This is the review-comment list; for the language idioms underneath it reach for the
  effective-go skill, and for test code the go-test-comments skill.
---

# Go Code Review Comments

These rules come from the Go project's wiki page "Go Code Review Comments" (https://go.dev/wiki/CodeReviewComments), a list of the comments most often made during reviews of Go code. It is a list of common style issues, not a complete style guide. Read the section matching the code in front of you, state the rule to the author in the same terms, and run the checklist at the end over a change before approving it.

The page names two companions. It supplements Effective Go, which carries the language idioms these rules assume; see the effective-go skill. Its testing counterpart is Go Test Comments; see the go-test-comments skill for failure message wording, `t.Error` against `t.Fatal`, `cmp` comparisons, table-driven tests, and error-semantics testing. The two rules below are all this page says about tests.

## Formatting, imports, and tooling

**Run gofmt on your code.** It fixes the majority of mechanical style issues automatically, and almost all Go code in the wild is gofmt'd. goimports is a superset that also adds and removes import lines as needed.

**Break lines because of the semantics of what you are writing.** Go has no rigid line length limit. Avoid uncomfortably long lines, and keep lines long where that reads better, such as repetitive ones. Wrapping in the middle of a call or declaration usually signals too many parameters or long variable names, so fix the names or the semantics. Function length works the same way: there is no line count rule, but a function can be too long, and the fix is to move the function boundaries.

**Group imports with the standard library first,** separated by blank lines. goimports does this for you.

```go
import (
	"fmt"
	"os"

	"github.com/foo/bar"
	"rsc.io/goversion/version"
)
```

**Rename an import only to avoid a name collision.** Good package names do not require renaming. On a collision, rename the most local or project-specific import.

**Import for side effects only in package main or in tests.** The blank form `import _ "pkg"` belongs in the main package of a program, or in tests that need it.

**Use `import .` only in a test that cannot join its package.** It hides whether a name like `Quux` is declared in the current package or an imported one. The one accepted use is a test kept out of the package under test by a circular dependency.

```go
package foo_test

import (
	"bar/testutil" // also imports "foo"
	. "foo"
)
```

## Naming

**Use MixedCaps or mixedCaps for multiword names,** even where that breaks conventions from other languages. An unexported constant is `maxLength`, not `MAX_LENGTH`.

**Give initialisms and acronyms a consistent case.** "URL" appears as `URL` or `url` (`urlPony`, `URLPony`), never `Url`, so a method is `ServeHTTP`, not `ServeHttp`. With several initialized words, write `xmlHTTPRequest` or `XMLHTTPRequest`. This covers "ID" when it means identifier, so write `appID`. Protocol buffer generated code is exempt: human-written code is held to a higher standard than machine-written code.

**Omit the package name from the identifiers in it.** Every reference already carries the package name.

```go
package chubby
type ChubbyFile struct{} // BAD:  clients write chubby.ChubbyFile
type File struct{}       // GOOD: clients write chubby.File
```

**Avoid meaningless package names:** `util`, `common`, `misc`, `api`, `types`, and `interfaces` say nothing about what is inside.

**Keep variable names short.** The further from its declaration a name is used, the more descriptive it must be. Prefer `c` to `lineCount` and `i` to `sliceIndex` for locals with limited scope. Loop indices and readers can be a single letter (`i`, `r`). Unusual things and globals need more descriptive names.

**Name a receiver after the identity of its type, and stay consistent.** One or two letters suffice, such as `c` or `cl` for `Client`. The receiver is just another parameter, so `me`, `this`, and `self` do not belong. Its role is obvious and serves no documentary purpose, and it appears on nearly every line of every method of the type. If the receiver is `c` in one method, do not call it `cl` in another.

## Comments and documentation

**Write doc comments on all top-level exported names,** and on non-trivial unexported type and function declarations.

**Make declaration comments full sentences that begin with the name** and end with a period, even where that feels redundant. They then format well in godoc.

```go
// Request represents a request to run a command.
type Request struct{ ... }

// Encode writes the JSON encoding of req to w.
func Encode(w io.Writer, req *Request) { ... }
```

**Put the package comment adjacent to the package clause with no blank line,** which is what godoc presents.

```go
// Package math provides basic constants and mathematical functions.
package math
```

**Start a `package main` comment with a capitalized first word.** After the binary name, several styles work: `// Binary seedgen ...`, `// Command seedgen ...`, `// Program seedgen ...`, `// The seedgen command ...`, `// The seedgen program ...`, or `// Seedgen ...`. These are examples, and sensible variants of them are acceptable. These comments are publicly visible and written in proper English, so the first word is capitalized even when it is the binary name and the capital does not match the command-line spelling. A lower-case first word is not an acceptable option.

## Errors

**Do not discard errors with `_`.** If a function returns an error, check that the function succeeded: handle the error, return it, or, in truly exceptional situations, panic.

**Do not use panic for normal error handling.** Use `error` and multiple return values.

**Keep error strings uncapitalized and free of ending punctuation.** They are usually printed following other context, so a capital lands mid-message. Proper nouns and acronyms keep their capitals. Logging is line-oriented and not combined inside other messages, so this does not apply there.

```go
// BAD:  fmt.Errorf("Something bad")
// GOOD: fmt.Errorf("something bad")
// so log.Printf("Reading %s: %v", filename, err) reads cleanly.
```

**Keep the normal path at minimal indentation and handle the error first,** so a reader can scan the normal path quickly.

```go
// BAD
if err != nil {
	// error handling
} else {
	// normal code
}

// GOOD
if err != nil {
	// error handling
	return // or continue, etc.
}
// normal code
```

When the `if` has an initialization statement, move the short variable declaration to its own line.

```go
// BAD
if x, err := f(); err != nil {
	return
} else {
	// use x
}

// GOOD
x, err := f()
if err != nil {
	return
}
// use x
```

**Signal failure with an additional final return value.** An in-band sentinel such as `""` or `-1` flows into the next call unchecked. The extra value is an `error`, or a `bool` when no explanation is needed. The rule applies to exported functions and is useful for unexported ones.

```go
// BAD: an unchecked "" reaches Parse.
func Lookup(key string) string
Parse(Lookup(key))

// GOOD: Parse(Lookup(key)) is now a compile-time error.
func Lookup(key string) (value string, ok bool)

value, ok := Lookup(key)
if !ok {
	return fmt.Errorf("no value for %q", key)
}
return Parse(value)
```

Values like `nil`, `""`, `0`, and `-1` are fine when they are valid results the caller need not handle differently. Some standard library functions, such as those in `strings`, return in-band error values, which simplifies string-manipulation code at the cost of more diligence from the programmer. In general, Go code returns an additional value for errors.

## Function and API design

**Take `context.Context` as the first parameter.** Contexts carry security credentials, tracing information, deadlines, and cancellation signals across API and process boundaries, and Go programs pass them explicitly along the whole call chain from incoming RPCs and HTTP requests to outgoing requests.

```go
func F(ctx context.Context /* other arguments */) {}
```

A function that is never request-specific may use `context.Background()`, but err on the side of passing a Context even when you think you do not need one. Do not put a Context in a struct field: add a `ctx` parameter to each method that passes it along, the one exception being methods whose signature must match an interface in the standard library or a third party library. Do not create custom Context types or use other interfaces in these signatures. Application data belongs in a parameter, in the receiver, in globals, or, when it truly belongs there, in a Context value. Contexts are immutable, so one `ctx` can go to several calls sharing a deadline, cancellation signal, credentials, and parent trace.

**Pass small values directly.** Do not pass pointers as function arguments to save a few bytes. If a function refers to its argument `x` only as `*x`, the argument should not be a pointer. `*string` and `*io.Reader` are common cases: both values are a fixed size and pass directly. Large structs, and small structs that might grow, are exempt.

**Leave result parameters unnamed when the types are clear on their own,** since named results are repetitive in godoc.

```go
// BAD
func (n *Node) Parent2() (node *Node, err error)
// GOOD
func (n *Node) Parent2() (*Node, error)
```

Names help when a function returns two or three parameters of the same type, or when a result's meaning is unclear from context.

```go
// BAD
func (f *Foo) Location() (float64, float64, error)

// GOOD
// Location returns f's latitude and longitude.
// Negative values mean south and west, respectively.
func (f *Foo) Location() (lat, long float64, err error)
```

Do not name results to avoid declaring a var inside the function: that trades minor implementation brevity for API verbosity. Naming a result so a deferred closure can change it is always OK.

**Keep naked returns to short functions.** A `return` with no arguments returns the named results. It is fine while the function is a handful of lines; once it is medium sized, be explicit. Enabling a naked return is not a reason to name results, because clarity of docs outweighs saving a line or two.

```go
func split(sum int) (x, y int) {
	x = sum * 4 / 9
	y = sum - x
	return
}
```

**Declare an empty slice as `var t []string`.** That is a nil slice; `t := []string{}` is non-nil and zero-length. Their `len` and `cap` are both zero, and the nil slice is the preferred style. A non-nil zero-length slice is preferred in limited circumstances, such as JSON encoding, where a nil slice encodes to `null` and `[]string{}` encodes to `[]`. When designing interfaces, avoid drawing a distinction between the two, since it leads to subtle programming errors.

**Define an interface in the package that consumes it.** The implementing package returns concrete types (usually a pointer or struct), so it can add methods without extensive refactoring. Do not define an interface on the implementor side "for mocking": design the API so it can be tested through the public API of the real implementation. Do not define an interface before it is used, because without a realistic example of usage it is too hard to see whether the interface is necessary or what methods it needs.

```go
package consumer // consumer.go: declare the interface where it is used

type Thinger interface{ Thing() bool }

func Foo(t Thinger) string { ... }
```

```go
package consumer // consumer_test.go: the fake lives with the consumer

type fakeThinger struct{ ... }

func (t fakeThinger) Thing() bool { ... }

// if Foo(fakeThinger{...}) == "x" { ... }
```

BAD, on the producer side:

```go
package producer

type Thinger interface{ Thing() bool }

type defaultThinger struct{ ... }

func (t defaultThinger) Thing() bool { ... }
func NewThinger() Thinger            { return defaultThinger{...} }
```

GOOD, the same producer returning a concrete type:

```go
package producer

type Thinger struct{ ... }

func (t Thinger) Thing() bool { ... }
func NewThinger() Thinger     { return Thinger{...} }
```

Effective Go's "Generality" section points the other way for one case: when a concrete type exists only to implement an interface and will never have exported methods beyond it, that document has the constructor return the interface, as `crc32.NewIEEE` returns a `hash.Hash32`. That applies to a family of interchangeable implementations that already exists. This rule applies to a package with a single implementation. See the effective-go skill.

## Methods, receivers, and copying

**Choose a pointer receiver when in doubt.** A value receiver makes sense for efficiency, usually on small unchanging structs or values of basic type. The guidelines:

- A map, func, or chan receiver is never a pointer. A slice receiver is not a pointer when the method does not reslice or reallocate it.
- A method that mutates the receiver needs a pointer.
- A struct holding a `sync.Mutex` or similar synchronizing field needs a pointer, to avoid copying.
- A large struct or array is more efficient as a pointer. Judge "large" by imagining every element passed as a separate argument: if that feels too large, so is the receiver.
- If other functions or methods may be mutating the receiver, concurrently or through this method, use a pointer. A value receiver copies, so outside updates never reach it.
- If the receiver is a struct, array, or slice with an element that points to something that might be mutating, prefer a pointer receiver: the intention is clearer to the reader.
- A small array or struct that is naturally a value type (like `time.Time`), with no mutable fields and no pointers, or a basic type such as `int` or `string`, makes sense as a value receiver. A value receiver can cut garbage, since a value passed to a value method can use an on-stack copy. The compiler already tries to avoid that allocation, so do not pick a value receiver for this reason without profiling first.
- Do not mix receiver types on one type. Pick pointers or values for all its methods.

**Be careful copying a struct from another package.** `bytes.Buffer` contains a `[]byte`, so the slice in a copy may alias the array in the original and later method calls have surprising effects. In general, do not copy a value of type `T` when its methods are associated with `*T`.

## Concurrency

**Prefer synchronous functions,** which return their results directly or finish any callbacks or channel operations before returning. They keep goroutines localized within a call, which makes lifetimes easy to reason about and avoids leaks and data races, and they are easier to test, since the caller passes an input and checks the output with no polling or synchronization. A caller wanting concurrency calls the function from its own goroutine. Removing unnecessary concurrency at the caller side is difficult and sometimes impossible.

**Make it clear when, or whether, a spawned goroutine exits.** Goroutines leak by blocking on channel sends or receives, and the garbage collector does not terminate a goroutine even when the channels it blocks on are unreachable. Goroutines left in flight past their usefulness cause other problems: sends on closed channels panic, modifying still-in-use inputs after the result is no longer needed still races, and long-lived goroutines make memory usage unpredictable. Keep concurrent code simple enough that lifetimes are obvious; where that is not feasible, document when and why the goroutines exit.

## Security

**Generate keys with `crypto/rand`.** `math/rand` and `math/rand/v2` seeded with `Time.Nanoseconds()` hold just a few bits of entropy, and this applies to throwaway keys too. Use `crypto/rand.Reader`, or `crypto/rand.Text` for text, or encode random bytes with `encoding/hex` or `encoding/base64`.

```go
import "crypto/rand"

func Key() string {
	return rand.Text()
}
```

## Tests and examples

**Ship a new package with examples of intended usage:** a runnable `Example` function, or a simple test demonstrating a complete call sequence.

**Fail a test with the inputs, what you got, and what you wanted.** Assume the person debugging the failure is neither you nor your team. The order is actual then expected, and the message follows that order.

```go
if got != tt.want {
	t.Errorf("Foo(%q) = %d; want %d", tt.in, got, tt.want) // Fatalf if nothing more can be tested
}
```

Assertion helpers are tempting, but each one must still produce a useful message. When the typing adds up, write a table-driven test. To disambiguate failures from a shared helper, wrap each call in its own `TestFoo` so the failure carries that name.

```go
func TestSingleValue(t *testing.T) { testHelper(t, []int{80}) }
func TestNoValues(t *testing.T)    { testHelper(t, []int{}) }
```

Go Test Comments writes the same message with a comma, `YourFunc(%v) = %v, want %v`, and asks the message to name the function under test. Either separator is in use; see the go-test-comments skill for the rest of the test rules.

## Review checklist

- gofmt or goimports has been run.
- Imports are grouped with the standard library first, unrenamed except on collisions, and free of blank or dot imports outside main and tests.
- Names use MixedCaps, consistent initialism case (`URL`, `appID`, `ServeHTTP`), no stutter with the package name, and no `util`-style package names.
- Variable names are short, growing more descriptive with distance from the declaration; receiver names are one or two letters tied to the type and identical across its methods.
- Receiver types are all pointers or all values, with a pointer wherever the method mutates, the struct holds a mutex, or the value is large.
- Every exported top-level name and every non-trivial unexported declaration has a full-sentence doc comment beginning with its name, and the package comment sits adjacent to the package clause, capitalized.
- No error is dropped into `_`, panic is not used for normal errors, and error strings are lowercase with no trailing punctuation.
- Error handling is indented and returns early, the normal path stays flat, and failure is reported by a final `error` or `bool` result.
- `context.Context` is the first parameter, never a struct field, never a custom type.
- Small values pass by value, and empty slices are declared `var t []string`.
- Result parameters are unnamed unless names add clarity, and naked returns appear only in short functions.
- Interfaces are declared by the consumer; producers return concrete types.
- Functions are synchronous, every spawned goroutine has an obvious or documented exit, and keys come from `crypto/rand`, never `math/rand`.
- A new package has a runnable example, and test failures print input, got, and want.
