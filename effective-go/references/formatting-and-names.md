# Formatting, commentary, and names

Depth for the "Formatting", "Commentary", and "Names" sections of Effective Go
(https://go.dev/doc/effective_go).

## Formatting

Formatting arguments are the most contentious and the least consequential part of a style
discussion. Go removes the argument by handing the job to a program. `gofmt` reads a Go source file
and emits it in a standard style of indentation and vertical alignment, keeping comments and
reflowing them where needed. `go fmt` is the same transformation applied at package level.

The working rule: when a new layout situation comes up, run `gofmt` and take its answer. If the
answer looks wrong, rearrange the program or file a bug against `gofmt`. Do not hand-format around
it. Every file in the standard library is `gofmt` output.

Alignment is the clearest case. Given

```go
type T struct {
    name string // name of the object
    value int // its value
}
```

`gofmt` produces aligned columns:

```go
type T struct {
    name    string // name of the object
    value   int    // its value
}
```

Details that `gofmt` fixes and you should not think about:

- **Indentation.** Tabs, emitted by default. Spaces appear only where you have no choice.
- **Line length.** There is no limit. A long line that feels long gets wrapped with one extra tab
  of indentation on the continuation.
- **Parentheses.** `if`, `for`, and `switch` have no parentheses in their syntax. Go's operator
  precedence hierarchy is short, so spacing can carry the grouping: `x<<8 + y<<16` groups as the
  spacing suggests.

## Commentary

Go has C-style `/* */` block comments and C++-style `//` line comments. Line comments are the norm.
Block comments show up as package comments, inside an expression, and to disable a large region of
code during debugging.

A comment placed immediately before a top-level declaration, with no blank line between the comment
and the declaration, documents that declaration. These doc comments are the primary documentation
for a package or command and are what `go doc` and pkg.go.dev display. The full conventions live in
the separate "Go Doc Comments" document.

```go
// Package ring implements operations on circular lists.
package ring

// New creates a ring of n elements.
func New(n int) *Ring {
	// ...
}
```

## Names

A name's first character decides whether it is visible outside its package, so naming carries
semantics in Go, not only style.

### Package names

A package name becomes the accessor for its contents at every use site. After `import "bytes"`, the
importer writes `bytes.Buffer`. Give the package a short, concise, evocative name: lower case, a
single word, no underscores, no mixedCaps. Err toward brevity, because everyone using the package
types that name.

Collisions are not worth pre-empting. The package name is only the default for imports; an importer
that hits a conflict renames locally, and the import path in the file settles which package is in
use. (The `import .` form can simplify a test that must live outside the package it tests, and is
avoided elsewhere.)

The package name is the base name of its source directory. `src/encoding/base64` is imported as
`"encoding/base64"` and is named `base64`.

Because the qualifier is always present at the use site, exported names do not repeat it:

| Package | Exported name | Read as |
| --- | --- | --- |
| `bufio` | `Reader` | `bufio.Reader` |
| `ring` | `New` | `ring.New` |
| `sync` | `Once.Do` | `once.Do(setup)` |

`bufio.Reader` does not collide with `io.Reader`, since imported names always carry their package.
A constructor in a package that exports one type is `New`, so `ring.New` returns a `*ring.Ring`. A
constructor for another type in the same package is `NewT`.

Long names do not automatically read better. `once.Do(setup)` says what it does; `DoOrWaitUntilDone`
adds length. A good doc comment is often worth more than extra words in the identifier.

### Getters

Go has no automatic getters and setters. Writing them yourself is fine and often right. Do not put
`Get` in the name. For an unexported field `owner`, the getter is `Owner` and the setter, if there
is one, is `SetOwner`. Case already distinguishes the exported method from the unexported field.

```go
owner := obj.Owner()
if owner != user {
    obj.SetOwner(user)
}
```

### Interface names

A one-method interface takes the method name plus `-er`, or a similar agent noun: `Reader`,
`Writer`, `Formatter`, `CloseNotifier`.

`Read`, `Write`, `Close`, `Flush`, `String` and their peers have canonical signatures and meanings.
Two directions follow. Do not give a method one of those names unless it has that signature and
meaning. When your type has a method whose meaning matches a well-known one, use the well-known
name and signature: the string converter is `String`, and `ToString` is the wrong name.

### MixedCaps

Multiword names are written `MixedCaps` or `mixedCaps`. Underscores do not appear in Go names.
