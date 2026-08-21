---
name: effective-go
description: |
  Idiomatic Go style and design rules from the Go project's "Effective Go".
  Use when writing or reviewing Go code, naming packages, types, and methods,
  choosing between new and make, working with slices, maps, and composite literals,
  designing interfaces and choosing pointer or value receivers, using embedding and
  the blank identifier, writing goroutine and channel code, or handling errors, panic,
  and recover. Covers gofmt, doc comments, control structures, defer, String, and init.
---

# Effective Go

"Effective Go" (https://go.dev/doc/effective_go) is the Go project's guide to writing clear, idiomatic Go. The document was written for Go's 2009 release and is not actively updated: it describes the core language before modules, generics, and error wrapping, and it says so at the top. Its guidance on formatting, naming, program construction, interfaces, and concurrency is still the baseline for Go code. Use this file for the rules that apply while writing or reviewing code. Open a reference file when you need the reasoning or a full worked example. Lines marked **Later Go:** record where the language moved on; the source's rule is stated first.

## References

- [references/formatting-and-names.md](references/formatting-and-names.md): open for gofmt behavior, doc comment conventions, and the full naming rules for packages, getters, interfaces, and multiword names.
- [references/control-flow-and-functions.md](references/control-flow-and-functions.md): open for semicolon insertion, `if`/`for`/`switch`/type switch forms, labeled break, multiple and named results, and defer semantics.
- [references/data-and-allocation.md](references/data-and-allocation.md): open for `new` vs `make`, composite literals, arrays, slices, two-dimensional slices, maps, `append`, the `fmt` verbs, constants with `iota`, and `init`.
- [references/methods-and-interfaces.md](references/methods-and-interfaces.md): open for pointer vs value receivers, the addressability rule, type conversions to borrow methods, type assertions, and returning interfaces from constructors.
- [references/embedding-and-blank-identifier.md](references/embedding-and-blank-identifier.md): open for struct and interface embedding, method promotion, name conflict rules, and every use of `_`.
- [references/concurrency.md](references/concurrency.md): open for goroutines, unbuffered and buffered channels, channels of channels, the semaphore and leaky buffer patterns, and parallelization.
- [references/errors-and-panic.md](references/errors-and-panic.md): open for the `error` interface, structured error types, error string conventions, and the panic/recover pattern at a package boundary.

## Formatting and comments

**Run gofmt and accept its output.** `gofmt` (or `go fmt`, which works on a package) sets indentation, alignment, and comment layout. If its output looks wrong, rearrange the program or file a bug against `gofmt`. All standard library code is formatted with it.

**Indent with tabs, and let lines run long.** `gofmt` emits tabs. Go has no line length limit; if a line feels too long, wrap it and indent the continuation with an extra tab.

**Leave out parentheses in control structures.** `if`, `for`, and `switch` take no parentheses. Operator precedence is short enough that spacing carries meaning: `x<<8 + y<<16` groups the way it reads.

**Use `//` line comments; keep `/* */` for package comments.** Block comments also serve inside an expression or to disable a large block of code.

**Write a doc comment directly above each top-level declaration, with no blank line between.** Those comments are the package's primary documentation. Details are in "Go Doc Comments".

## Names

**Give a package a short, lower-case, single-word name.** No underscores, no mixedCaps. The package name is the base name of its source directory: `src/encoding/base64` is imported as `"encoding/base64"` and named `base64`.

**Name exported identifiers assuming the package qualifier is present.** The buffered reader in `bufio` is `bufio.Reader`. A package's sole constructor for its sole type is `New`, so `ring.New` returns a `*ring.Ring`.

```go
// good: bufio.Reader, ring.New, once.Do
// bad:  bufio.BufReader, ring.NewRing, once.DoOrWaitUntilDone
```

**Name a getter after the field, with no `Get` prefix.** A field `owner` gets a method `Owner`, and the setter, if there is one, is `SetOwner`.

**Name a one-method interface after the method plus `-er`.** `Reader`, `Writer`, `Formatter`, `CloseNotifier`. `Read`, `Write`, `Close`, `Flush`, and `String` have canonical signatures and meanings: use those names only with those signatures, and use them when your method has that meaning. A string converter is `String`.

**Write multiword names as `MixedCaps` or `mixedCaps`.** Underscores do not appear in Go names.

## Semicolons and brace placement

**Put the opening brace on the same line as the statement.** The lexer inserts a semicolon after a line ending in an identifier, a literal, or one of `break continue fallthrough return ++ -- ) }`. A brace on its own line therefore terminates the statement above it.

```go
if i < f() {
    g()
}
```

## Control structures

**Use `if` with an initializer to scope the value to the test, and drop the `else` when the body ends in `break`, `continue`, `goto`, or `return`.** Error handling then reads as a straight line of guarded returns.

```go
if err := file.Chmod(0664); err != nil {
    log.Print(err)
    return err
}
f, err := os.Open(name)
if err != nil {
    return err
}
codeUsing(f)
```

**Reuse `err` with `:=` when at least one new variable is on the left.** In the same scope, `:=` assigns to an existing variable and declares the new ones. A `:=` in an inner scope declares a new variable that shadows the outer one.

**Use the single `for` keyword for all loops.** The three-clause form `for init; cond; post {}`, the condition-only form `for cond {}`, and the infinite form `for {}` are all spelled `for`; there is no `while`.

**Use `range` to walk a slice, array, string, map, or channel.** Drop the second variable if you only need the index, and use `_` for an index you do not need. Ranging over a string decodes UTF-8 one rune at a time, and the index is the byte position of each rune.

```go
for key, value := range oldMap {
    newMap[key] = value
}
for pos, char := range "日本語" { // char is a rune, pos its byte offset
    fmt.Printf("%#U at byte %d\n", char, pos)
}
```

**Swap and step with parallel assignment.** Go has no comma operator, and `++`/`--` are statements, so a reversing loop reads `for i, j := 0, len(a)-1; i < j; i, j = i+1, j-1`.

**Use `switch` for if-else chains.** Cases need not be constants or integers, they are evaluated top to bottom, there is no automatic fallthrough, and a `switch` with no expression switches on `true`. Cases may list several values separated by commas. To break out of a loop from inside a `switch`, label the loop and use `break Label`.

```go
switch {
case '0' <= c && c <= '9':
    return c - '0'
case 'a' <= c && c <= 'f':
    return c - 'a' + 10
}
```

**Use a type switch to discover an interface's dynamic type.** Declaring the variable inside the switch gives it the case's type in each clause.

```go
switch t := t.(type) {
case bool:
    fmt.Printf("boolean %t\n", t) // t is a bool here
case *int:
    fmt.Printf("pointer to integer %d\n", *t) // t is a *int here
default:
    fmt.Printf("unexpected type %T\n", t)
}
```

## Functions

**Return an error as a second result.** Multiple return values remove the C habit of overloading an in-band value or writing through a pointer argument.

```go
func (file *File) Write(b []byte) (n int, err error)
```

**Name result parameters when the names document the signature or when a deferred function must set them.** Named results are initialized to their zero values, and a bare `return` returns their current values.

```go
func nextInt(b []byte, pos int) (value, nextPos int) {
    // ...
    return // returns value and nextPos
}
```

**Defer cleanup on the line after you acquire the resource.** The deferred call runs when the enclosing function returns, on every path. Deferred calls run in LIFO order, and their arguments are evaluated when the `defer` executes, not when the call runs.

```go
f, err := os.Open(filename)
if err != nil {
    return "", err
}
defer f.Close() // runs on every return path
```

## Data and allocation

**Use `new(T)` for zeroed storage and `make` for slices, maps, and channels.** `new(T)` returns `*T` pointing at a zeroed `T`. `make(T, args)` initializes the internal data structure of a slice, map, or channel and returns a `T`.

```go
var p *[]int = new([]int) // *p is nil; rarely what you want
v := make([]int, 100)     // v refers to a new array of 100 ints
```

**Later Go:** since Go 1.26 `new` also takes a value expression, as in `new(int64(300))`.

**Design types so the zero value is useful.** `sync.Mutex` has no explicit constructor because its zero value is an unlocked mutex; `bytes.Buffer`'s zero value is an empty buffer. The property is transitive, so a struct of such fields is ready to use after `var v T`.

**Build values with composite literals.** `&File{fd: fd, name: name}` replaces a constructor that assigns field by field. Labeled fields may appear in any order, and omitted fields take their zero values. `&File{}` and `new(File)` are equivalent. Arrays, slices, and maps take literals too, with indices or keys as labels.

**Prefer slices to arrays.** An array is a value: assigning it or passing it to a function copies every element, and its length is part of its type. A slice holds a reference to an underlying array, so a function that modifies slice elements modifies the caller's data. `len` and `cap` are legal on a nil slice and return 0.

**Assign the result of `append`.** `append` may allocate a new underlying array, so the returned slice is the only valid one. Use `...` to append one slice to another.

```go
x := []int{1, 2, 3}
x = append(x, 4, 5, 6)
x = append(x, y...)
```

**Build a two-dimensional slice as a slice of slices.** Allocate each row separately when rows change size independently, or slice one flat array when the shape is fixed.

```go
picture := make([][]uint8, YSize)
pixels := make([]uint8, XSize*YSize)
for i := range picture {
    picture[i], pixels = pixels[:XSize], pixels[XSize:]
}
```

**Use the comma ok form to tell a missing map entry from a zero value.** Indexing a map with an absent key yields the element type's zero value. `delete(m, k)` is safe when the key is absent.

```go
if seconds, ok := timeZone[tz]; ok {
    return seconds
}
log.Println("unknown time zone:", tz)
```

**Print with `%v` and give types a `String() string` method.** `%+v` adds field names, `%#v` prints Go syntax, `%T` prints the type, `%q` quotes a string. Maps print with sorted keys. Inside a `String` method, convert the receiver before printing it, or `Sprintf` recurses forever.

```go
func (m MyString) String() string {
    return fmt.Sprintf("MyString=%s", string(m)) // the conversion is required
}
```

## Initialization

**Use `iota` for enumerated constants.** Constants are created at compile time from constant expressions and may only be numbers, runes, strings, or booleans.

```go
const (
    _           = iota // skip the first value
    KB ByteSize = 1 << (10 * iota)
    MB
    GB
)
```

**Use `init` for setup that expressions cannot express.** Each file may define `init` functions. They run after all imported packages are initialized and after every package-level variable's initializer has been evaluated. Typical work: validate state and register flags.

## Methods and interfaces

**Define methods on any named type, and choose the receiver by whether the method mutates.** A pointer method may modify the receiver; a value method operates on a copy. Value methods can be called on values and pointers; pointer methods require an addressable value, and the compiler inserts `&` when the value is addressable. An interface is satisfied by `*T` alone when the method set uses pointer receivers.

```go
type ByteSlice []byte

func (p *ByteSlice) Write(data []byte) (n int, err error) {
    *p = append(*p, data...)
    return len(data), nil
}

var b ByteSlice
fmt.Fprintf(&b, "%d days\n", 7) // &b, because *ByteSlice is the io.Writer
```

**Keep interfaces to one or two methods and name what a type can do.** A type may satisfy several interfaces, and any type can satisfy one: a struct, an integer, a channel, or a function. The `http.HandlerFunc` adapter turns a plain function into a `Handler` by giving the function type a `ServeHTTP` method.

**Convert a type to borrow another type's methods.** When two types share an underlying type, the conversion is free and creates no new value.

```go
func (s Sequence) String() string {
    s = s.Copy()
    sort.IntSlice(s).Sort()
    return fmt.Sprint([]int(s))
}
```

**Guard a type assertion with the comma ok form.** A bare `value.(string)` panics when the dynamic type is wrong. A type switch handles several possibilities at once.

```go
str, ok := value.(string) // ok is false and str is "" when the type differs
```

**Export the interface when the concrete type exists only to implement it.** `crc32.NewIEEE` returns a `hash.Hash32`, so swapping in `adler32.New` changes one line at the call site.

## The blank identifier

**Assign to `_` for a result you do not need.** Never use it to swallow an error you should check.

```go
if _, err := os.Stat(path); os.IsNotExist(err) {
    fmt.Printf("%s does not exist\n", path)
}
```

**Import for side effect with `_`.** `import _ "net/http/pprof"` states that the package is present for what its `init` registers.

**Assert interface satisfaction at compile time with a blank variable.** Use this when no static conversion in the package already proves it.

```go
var _ json.Marshaler = (*RawMessage)(nil)
```

## Embedding

**Embed a type to promote its methods.** An embedded field has no name, and the outer type gains the embedded type's methods. Only interfaces may be embedded in interfaces.

```go
type ReadWriter interface {
    Reader
    Writer
}

type Job struct {
    Command string
    *log.Logger // Job now has Print, Printf, Println
}
```

**Remember that a promoted method's receiver is the inner type.** Embedding is delegation, so an embedded `Logger` method knows nothing about the outer `Job`. To wrap a promoted method, name the embedded field by its type: `job.Logger.Printf(...)`.

**Expect the outer name to win.** A field or method at an outer level hides the same name nested deeper. Two identical names at the same depth are an error only when the name is used.

## Concurrency

**Share memory by communicating.** Pass values on channels so that one goroutine at a time holds a given value, and data races cannot arise. Locks and atomic operations remain available in `sync` for small pieces of bookkeeping.

**Start a goroutine with `go` and know that it needs a way to report completion.** Goroutines are multiplexed onto OS threads, cost about a stack allocation, and grow their stacks on demand. A function literal launched with `go` is a closure over the variables it names.

```go
go func() {
    time.Sleep(delay)
    fmt.Println(message)
}() // the trailing parentheses call the literal
```

**Use an unbuffered channel to synchronize.** The receive blocks until a value arrives, and the send blocks until the receiver takes it, so the exchange is also a rendezvous.

```go
c := make(chan int)
go func() {
    list.Sort()
    c <- 1 // signal; the value does not matter
}()
doSomethingForAWhile()
<-c // wait for the sort
```

**Use a buffered channel as a counting semaphore.** Its capacity is the limit on work in flight. Acquire before the work and release after it.

```go
var sem = make(chan int, MaxOutstanding)

func handle(r *Request) {
    sem <- 1
    process(r)
    <-sem
}
```

**Gate goroutine creation, not only the work inside it.** Launching a goroutine per request lets an unbounded number of them pile up on the semaphore. Either acquire before `go`, or start a fixed pool of handlers ranging over the request channel.

```go
func handle(queue chan *Request) {
    for r := range queue { // one goroutine per handler, MaxOutstanding of them
        process(r)
    }
}
```

**Put a reply channel in the request to demultiplex answers.** Channels are first class values, which gives a rate-limited parallel RPC with no mutexes.

```go
type Request struct {
    args       []int
    f          func([]int) int
    resultChan chan int
}
```

**Split a calculation across `runtime.NumCPU()` goroutines and count the pieces back.** Each piece signals on a shared channel and the caller drains one value per piece. `runtime.GOMAXPROCS(0)` reports the user's setting.

**Recycle buffers through a buffered channel with `select` and `default`.** A `select` with a `default` clause never blocks: take a free buffer when one exists, allocate when none does, return it when there is room, and drop it for the collector when the free list is full.

```go
select {
case b = <-freeList: // got one
default:
    b = new(Buffer) // none free
}
```

**Later Go:** since Go 1.22 a `for` loop variable is a fresh variable each iteration, so `for req := range queue { go func() { process(req) }() }` is correct. Before 1.22 the goroutines shared one variable and had to take it as a parameter.

## Errors, panic, and recover

**Return an `error` as the last result and let the caller decide.** The interface is one method.

```go
type error interface {
    Error() string
}
```

**Define an error type when callers need the details.** `os.PathError` carries the operation, the path, and the underlying error, so the printed message names its origin.

**Prefix error strings with the operation or package.** `"image: unknown format"`.

**Type-assert on an error to test a specific failure.**

```go
if e, ok := err.(*os.PathError); ok && e.Err == syscall.ENOSPC {
    deleteTempFiles()
}
```

**Later Go:** since Go 1.13, wrap with `fmt.Errorf("...: %w", err)` and inspect with `errors.Is` and `errors.As`, which see through wrapping. The source predates all three.

**Panic only when the program truly cannot continue.** A library that cannot initialize itself may panic; a computation that fails to converge may panic. Ordinary failures return errors.

**Recover only in a deferred function, and only for panics you raised.** `recover` stops the unwinding and returns the value passed to `panic`. Re-panic on any value your package did not create, so an unrelated runtime error is not silently converted to an error return.

```go
func safelyDo(work *Work) {
    defer func() {
        if err := recover(); err != nil {
            log.Println("work failed:", err)
        }
    }()
    do(work)
}
```

**Convert an internal panic to an error at the package boundary.** A recursive parser can panic with a private error type on bad input; the exported `Compile` recovers and returns an `error`, while `MustCompile` panics for callers who supply constant input.

## Not covered by the source

The document predates modules, generics, and error wrapping and states this itself. Take package layout, `go.mod`, type parameters, `context`, `errors.Is`/`errors.As`, and `sync.WaitGroup`-based fan-in from current Go documentation.

## Review checklist

- `gofmt` clean, opening brace on the statement line.
- Doc comment on every exported declaration, starting with the declared name.
- Package name short and lower case; exported names read well with the qualifier.
- Getter `Owner`, setter `SetOwner`, one-method interface `Fooer`, `MixedCaps` throughout.
- `if err := ...; err != nil` and early return; no `else` after a terminating body.
- `defer` on the line after acquiring a file, lock, or connection.
- `make` for slices, maps, and channels; `new` or a composite literal for everything else.
- Zero value of every exported struct is usable, or the type documents its constructor.
- `append` result assigned back.
- Comma ok on map lookups and type assertions.
- `String() string` on types that get printed, with the receiver converted inside it.
- Receiver is a pointer when the method mutates, and consistent across the type's methods.
- Interfaces small; concrete types unexported when they only implement one.
- No `_` hiding an error; interface checks written as `var _ I = (*T)(nil)`.
- Goroutine creation bounded; every goroutine has a way to finish.
- Errors returned, not panicked; `recover` only in a deferred function.
