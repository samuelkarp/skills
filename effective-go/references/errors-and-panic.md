# Errors, panic, and recover

Depth for the "Errors" section of Effective Go (https://go.dev/doc/effective_go), including its
"Panic" and "Recover" subsections.

## Return errors

Multiple return values let a library routine report a detailed error alongside its result, and
callers see enough to act. A failed `os.Open` reports which file and which system-level reason,
not only that something went wrong.

The `error` interface is one method:

```go
type error interface {
    Error() string
}
```

A library is free to implement anything it likes under that interface, so a caller can both print
the error and inspect it.

## Error types carry detail

`os.PathError` is the standard shape: a struct holding the operation, the subject, and the
underlying cause.

```go
// PathError records an error and the operation and
// file path that caused it.
type PathError struct {
    Op   string // "open", "unlink", etc.
    Path string // The associated file.
    Err  error  // Returned by the system call.
}

func (e *PathError) Error() string {
    return e.Op + " " + e.Path + ": " + e.Err.Error()
}
```

Its message names everything a reader needs, even when the message is printed far from where the
failure happened:

```
open /etc/passwx: no such file or directory
```

## Error strings name their origin

When it is feasible, give an error string a prefix identifying the operation or the package that
produced it. The `image` package reports `image: unknown format`. The prefix is what makes a
message useful in a log line that has no other context.

The Errors section stops there. The companion rule, that error strings stay lower case and carry no
trailing punctuation so they compose inside a larger message, comes from Go Code Review Comments;
see the go-code-review-comments skill.

## Callers inspect errors by type

A caller that wants to react to one specific failure uses a type switch or a type assertion on the
error, then examines the fields. If the assertion fails, `ok` is false and the value is nil, so a
wrong guess is not a crash:

```go
for try := 0; try < 2; try++ {
    file, err = os.Create(filename)
    if err == nil {
        return
    }
    if e, ok := err.(*os.PathError); ok && e.Err == syscall.ENOSPC {
        deleteTempFiles() // recover some space
        continue
    }
    return
}
```

**Later Go:** since Go 1.13, an error can wrap another with `fmt.Errorf("...: %w", err)`, and
callers test with `errors.Is(err, syscall.ENOSPC)` or extract with
`var e *os.PathError; errors.As(err, &e)`. Those functions unwrap chains, which a direct type
assertion does not. The source predates all of this, and its structural advice, define a type,
carry the cause, prefix the message, is unchanged.

## Panic

`panic` creates a run-time error that stops the program. It takes a value of any type, usually a
string, that is printed as the program dies. It is for situations where there is nothing sensible
to do and no caller who could fix it.

Library code normally does not panic. A library that cannot initialize itself is the accepted
exception, since nothing downstream can proceed:

```go
var user = os.Getenv("USER")

func init() {
    if user == "" {
        panic("no value for $USER")
    }
}
```

An impossible internal state is another. This cube root fails to converge only if the algorithm or
the machine is broken, so there is no error worth returning:

```go
// A toy implementation of cube root using Newton's method.
func CubeRoot(x float64) float64 {
    z := x / 3 // arbitrary initial value
    for i := 0; i < 1e6; i++ {
        prevz := z
        z -= (z*z*z - x) / (3 * z * z)
        if veryClose(z, prevz) {
            return z
        }
    }
    // A million iterations has not converged; something is wrong.
    panic(fmt.Sprintf("CubeRoot(%g) did not converge", x))
}
```

This is example code. A real library returns an error and lets the caller decide.

## Recover

When `panic` is called, the goroutine stops its current function, unwinds its stack running every
deferred function on the way, and, if the unwinding reaches the top of the stack, kills the program.

`recover` stops that unwinding and returns the value passed to `panic`. Because deferred functions
are the only code that runs during unwinding, `recover` is useful only inside one. It returns nil
when the goroutine is not panicking, and it returns nil unless it is called directly by a deferred
function. That second rule means deferred code can call library routines that themselves use panic
and recover internally without disturbing the outer recovery.

A server that must survive a bad unit of work isolates each one:

```go
func server(workChan <-chan *Work) {
    for work := range workChan {
        go safelyDo(work)
    }
}

func safelyDo(work *Work) {
    defer func() {
        if err := recover(); err != nil {
            log.Println("work failed:", err)
        }
    }()
    do(work)
}
```

If `do(work)` panics, the failure is logged and that goroutine exits cleanly; the other goroutines
are unaffected. Calling `recover` is the whole recovery: the deferred closure needs nothing else.

One caution the pattern hides: after an arbitrary panic there is no guarantee that shared data
structures the failed work touched are in a consistent state.

## Panic across a package boundary, converted to an error

Deep recursive code can report failures by panicking with a private type, and the package's
exported entry point converts that panic back into an ordinary error return. Callers never see the
panic.

An idealized regular expression compiler does this. The parser signals a bad pattern by panicking
with a local `Error`:

```go
// Error is the type of a parse error; it satisfies the error interface.
type Error string

func (e Error) Error() string {
    return string(e)
}

// error is a method of *Regexp that reports parsing errors by panicking.
func (regexp *Regexp) error(err string) {
    panic(Error(err))
}
```

The exported entry point runs the parser under a deferred recovery that turns the panic into a
return value. `Compile` names its results, so the deferred closure can set them:

```go
// Compile returns a parsed representation of the regular expression.
func Compile(str string) (regexp *Regexp, err error) {
    regexp = new(Regexp)
    // doParse will panic if there is a parse error.
    defer func() {
        if e := recover(); e != nil {
            regexp = nil    // Clear return value.
            err = e.(Error) // Will re-panic if not a parse error.
        }
    }()
    return regexp.doParse(str), nil
}
```

The type assertion `e.(Error)` carries the whole safety argument. If the recovered value is not the
package's own error type, the assertion panics, so an unrelated run-time failure such as an index
out of range keeps unwinding and is reported as the run-time error it is.

With that in place, the parser calls `regexp.error(...)` from any depth without unwinding by hand:

```go
if pos == 0 {
    re.error("'*' illegal at start of expression")
}
```

The re-panic replaces the panic value, and both the original and the new failure appear in the crash
report, so the root cause stays visible. Filtering unexpected values and re-panicking with the
original takes more code.

The rule this illustrates: do not let a panic escape the package. Recover at the boundary and
present an `error`, and re-panic on anything you did not raise yourself.
