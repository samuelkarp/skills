# The blank identifier and embedding

Depth for the "The blank identifier" and "Embedding" sections of Effective Go
(https://go.dev/doc/effective_go).

## The blank identifier

`_` can be assigned or declared with a value of any type, and the value is discarded. It is a
write-only placeholder for a spot where the syntax requires a name and the value is not wanted.

### In multiple assignment

When a call returns more than one value and only some are needed, name the rest `_`. This avoids
dummy variables and states that the value is deliberately dropped:

```go
if _, err := os.Stat(path); os.IsNotExist(err) {
    fmt.Printf("%s does not exist\n", path)
}
```

Dropping an *error* is a different matter, and is a bug waiting to happen:

```go
// Bad! This code will crash if path does not exist.
fi, _ := os.Stat(path)
if fi.IsDir() {
    fmt.Printf("%s is a directory\n", path)
}
```

An error result is discarded only when you have decided the operation cannot meaningfully fail, and
the reason belongs in a comment.

### Unused imports and variables

Importing a package or declaring a local variable without using it is a compile error. During
development, half-written code trips this constantly. Package-level blank assignments silence it:

```go
package main

import (
    "fmt"
    "io"
    "log"
    "os"
)

var _ = fmt.Printf // For debugging; delete when done.
var _ io.Reader    // For debugging; delete when done.

func main() {
    fd, err := os.Open("test.go")
    if err != nil {
        log.Fatal(err)
    }
    // TODO: use fd.
    _ = fd
}
```

Put those declarations right after the imports and comment them, so they are easy to find and
delete when the code is finished.

### Import for side effect

Some packages exist to register something in their `init` functions: a database driver, a codec, an
HTTP profiling handler. Importing such a package under `_` states that intent and satisfies the
unused-import rule:

```go
import _ "net/http/pprof"
```

The import causes the package's `init` to run, which registers the profiling handlers, and the
importing file never names the package.

### Interface checks

Most interface satisfaction is checked statically at the point of assignment. When a type is only
ever used through a concrete type inside its own package, nothing forces that check, and a change
to the interface will not be noticed until some distant caller breaks.

A dynamic check with comma ok answers the question at run time:

```go
if _, ok := val.(json.Marshaler); ok {
    fmt.Printf("value %v of type %T implements json.Marshaler\n", val, val)
}
```

A package-level blank declaration makes the compiler answer it instead:

```go
var _ json.Marshaler = (*RawMessage)(nil)
```

The declaration allocates nothing: it converts a typed nil pointer to the interface type, which
compiles only if `*RawMessage` has the methods. If `json.Marshaler` changes, the package stops
compiling and the failure is local.

Use such a declaration only when no static conversion already exists in the package, which is rare.
Its presence tells a reader that the satisfaction is intentional.

## Embedding

Go has no type-driven subclassing. It has embedding, which borrows an implementation by including
one type inside another without a field name.

### Interface embedding

Embedding one interface in another forms the union of their method sets:

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// ReadWriter is the interface that combines the Reader and Writer interfaces.
type ReadWriter interface {
    Reader
    Writer
}
```

A `ReadWriter` does what a `Reader` does and what a `Writer` does. Only interfaces can be embedded
in interfaces.

### Struct embedding

A struct field written as a type with no name is embedded, and the outer struct gains the embedded
type's methods:

```go
// ReadWriter stores pointers to a Reader and a Writer.
// It implements io.ReadWriter.
type ReadWriter struct {
    *Reader // *bufio.Reader
    *Writer // *bufio.Writer
}
```

`bufio.ReadWriter` satisfies `io.Reader`, `io.Writer`, and `io.ReadWriter` with no forwarding
methods written by hand. Embedded pointers must be set to valid values before use.

The alternative shape, named fields, requires the forwarding to be written out:

```go
type ReadWriter struct {
    reader *Reader
    writer *Writer
}

func (rw *ReadWriter) Read(p []byte) (n int, err error) {
    return rw.reader.Read(p)
}
```

An embedded field's name for selector purposes is its unqualified type name, so the embedded
`*bufio.Reader` is reached as `rw.Reader`.

### Where embedding differs from subclassing

When a promoted method runs, its receiver is the inner type, not the outer one. An embedded
`bufio.Reader` method knows about the `bufio.Reader` and nothing about the `ReadWriter` containing
it. Embedding is delegation with automatic forwarding.

### Embedding alongside ordinary fields

Embedded and named fields mix freely:

```go
type Job struct {
    Command string
    *log.Logger
}
```

`Job` now has `Print`, `Printf`, `Println`, and the rest of the logger's methods, so `job.Println("starting now...")`
works. Construct it like any struct:

```go
func NewJob(command string, logger *log.Logger) *Job {
    return &Job{command, logger}
}

job := &Job{command, log.New(os.Stderr, "Job: ", log.Ldate)}
```

To override a promoted method while still using it, define a method on the outer type and call
through the embedded field by its type name:

```go
func (job *Job) Printf(format string, args ...any) {
    job.Logger.Printf("%q: %s", job.Command, fmt.Sprintf(format, args...))
}
```

Embedding a non-pointer works too, and is what `log.Logger` itself would allow: `type Job struct {
Command string; log.Logger }`. Field access then reaches the embedded value directly, as in
`job.Logger`.

### Name conflicts

Two rules govern collisions.

**Depth wins.** A field or method `X` at one level hides any `X` nested more deeply. If `Job` has a
field named `Command` and its embedded `Logger` also had one, `job.Command` refers to the outer one.
This is what lets an outer type specialize a promoted method.

**Same depth is an error only when used.** Two identical names at the same nesting level are a
problem only if the program mentions the name. If neither is referenced outside the type
definition, the type is fine. That property protects a struct against a field being added to a type
it embeds from another package.
