# Semicolons, control structures, and functions

Depth for the "Semicolons", "Control structures", and "Functions" sections of Effective Go
(https://go.dev/doc/effective_go).

## Semicolons

The grammar uses semicolons as statement terminators, and the lexer inserts them automatically, so
source rarely contains one. The rule: if the last token on a line is an identifier (including
keywords such as `break`, `continue`, `fallthrough`, `return`), a basic literal, `++`, `--`, `)`,
`]`, or `}`, the lexer inserts a semicolon after it. A semicolon may also be omitted before a
closing brace.

The visible consequence is brace placement. An opening brace must sit on the line that begins the
statement.

```go
if i < f() {
    g()
}
```

```go
if i < f()  // a semicolon is inserted here
{           // so this brace starts a new statement: compile error
    g()
}
```

Semicolons still appear where they are written by hand: the clauses of a three-clause `for` loop,
and multiple short statements placed on one line.

## Control structures

Go has `if`, `for`, `switch`, `select`, and `goto`. There is no `do` and no `while`. The condition
never takes parentheses, and the body always takes braces.

### If

Mandatory braces push simple conditions onto multiple lines, which suits a language where the body
usually ends in `return` or `log`.

`if` accepts an initialization statement, like `for`. Use it to bind a value to the scope of the
test:

```go
if err := file.Chmod(0664); err != nil {
    log.Print(err)
    return err
}
```

When an `if` body ends in `break`, `continue`, `goto`, or `return`, drop the `else`. Error cases
then peel off one at a time and the successful path runs down the page with no indentation:

```go
f, err := os.Open(name)
if err != nil {
    return err
}
d, err := f.Stat()
if err != nil {
    f.Close()
    return err
}
codeUsing(f, d)
```

### Redeclaration and reassignment

In the snippet above, `err` is declared by the first `:=` and assigned by the second. A `:=` may
name a variable `v` that already exists when three conditions hold:

1. The existing declaration is in the same scope. (A `:=` in an inner scope declares a new variable
   that shadows the outer one.)
2. The value is assignable to `v`.
3. At least one other variable on the left is new.

This is why the repeated `f, err := ...` / `d, err := ...` shape compiles with a single `err`.

### For

One keyword covers three forms:

```go
for init; cond; post { }  // three-clause
for cond { }              // condition only
for { }                   // forever
```

Short declarations make the loop variable local:

```go
sum := 0
for i := 0; i < 10; i++ {
    sum += i
}
```

To iterate a slice, array, string, map, or channel, use `range`. Drop the second variable when only
the index or key is wanted, and use `_` for an index that is not:

```go
for key, value := range oldMap {
    newMap[key] = value
}

sum := 0
for _, value := range array {
    sum += value
}
```

`range` over a string decodes UTF-8. Each iteration yields one rune and the byte index where that
rune starts. Bytes that are not valid UTF-8 yield `U+FFFD` and advance one byte.

```go
for pos, char := range "日本語" {
    fmt.Printf("character %#U starts at byte position %d\n", char, pos)
}
```

Go has no comma operator, and `++` and `--` are statements, not expressions. Use parallel
assignment when a loop advances more than one variable:

```go
for i, j := 0, len(a)-1; i < j; i, j = i+1, j-1 {
    a[i], a[j] = a[j], a[i]
}
```

### Switch

Go's `switch` is more general than C's. The expression need not be constant or even an integer;
cases are evaluated top to bottom until one matches; there is no automatic fallthrough (the
`fallthrough` keyword is explicit); and a case may list several values separated by commas. A
`switch` with no expression switches on `true`, which makes it the natural shape for an if-else
chain:

```go
func unhex(c byte) byte {
    switch {
    case '0' <= c && c <= '9':
        return c - '0'
    case 'a' <= c && c <= 'f':
        return c - 'a' + 10
    case 'A' <= c && c <= 'F':
        return c - 'A' + 10
    }
    return 0
}
```

```go
func shouldEscape(c byte) bool {
    switch c {
    case ' ', '?', '&', '=', '#', '+', '%':
        return true
    }
    return false
}
```

A `break` inside a `switch` leaves the `switch`. To leave an enclosing loop, label the loop:

```go
Loop:
    for n := 0; n < len(src); n += size {
        switch {
        case src[n] < sizeOne:
            if validateOnly {
                break // leaves the switch, continues the loop
            }
            size = 1
            update(src[n])
        case src[n] < sizeTwo:
            if n+1 >= len(src) {
                err = errShortInput
                break Loop // leaves the loop
            }
            size = 2
            update(src[n] + src[n+1]<<shift)
        }
    }
```

`continue` also accepts a label, and applies only to loops.

### Type switch

A type switch discovers the dynamic type of an interface value. The syntax is a type assertion with
the keyword `type` in place of a type name. Declaring a variable in the switch header gives it the
case's type inside each clause.

```go
var t any
t = functionOfSomeType()
switch t := t.(type) {
default:
    fmt.Printf("unexpected type %T\n", t) // t has the interface type
case bool:
    fmt.Printf("boolean %t\n", t) // t is a bool
case int:
    fmt.Printf("integer %d\n", t) // t is an int
case *bool:
    fmt.Printf("pointer to boolean %t\n", *t) // t is a *bool
case *int:
    fmt.Printf("pointer to integer %d\n", *t) // t is a *int
}
```

**Later Go:** the source writes this as `var t interface{}`. Since Go 1.18, `any` is an alias for
`interface{}` and is the usual spelling.

## Functions

### Multiple return values

A Go function returns any number of values. The pattern that shapes the standard library is a
result plus an error:

```go
func (file *File) Write(b []byte) (n int, err error)
```

This removes the C conventions of encoding an error in an in-band value (a negative count) and of
passing a pointer for the function to write through. `File.Write` reports both how many bytes it
wrote and why it stopped.

A function that consumes part of its input returns the new position along with the value:

```go
func nextInt(b []byte, i int) (int, int) {
    for ; i < len(b) && !isDigit(b[i]); i++ {
    }
    x := 0
    for ; i < len(b) && isDigit(b[i]); i++ {
        x = x*10 + int(b[i]) - '0'
    }
    return x, i
}

for i := 0; i < len(b); {
    x, i = nextInt(b, i)
    fmt.Println(x)
}
```

### Named result parameters

Results may be named. A named result is an ordinary variable, initialized to its zero value at
function entry. A bare `return` returns the current values of all of them.

Two reasons to name them. The names document the signature: `func nextInt(b []byte, pos int)
(value, nextPos int)` says which returned `int` is which. And the names let a deferred function
observe or modify the results before the caller sees them.

```go
func ReadFull(r Reader, buf []byte) (n int, err error) {
    for len(buf) > 0 && err == nil {
        var nr int
        nr, err = r.Read(buf)
        n += nr
        buf = buf[nr:]
    }
    return
}
```

### Defer

`defer` schedules a function call to run immediately before the surrounding function returns. It
runs on every exit path, including a panic, which makes it the tool for releasing whatever you have
just acquired: closing a file, unlocking a mutex, returning a resource.

```go
func Contents(filename string) (string, error) {
    f, err := os.Open(filename)
    if err != nil {
        return "", err
    }
    defer f.Close() // f.Close runs when Contents returns

    var result []byte
    buf := make([]byte, 100)
    for {
        n, err := f.Read(buf[0:])
        result = append(result, buf[0:n]...)
        if err != nil {
            if err == io.EOF {
                break
            }
            return "", err // f is closed on this path too
        }
    }
    return string(result), nil // and on this one
}
```

Two properties matter:

**Arguments are evaluated when the `defer` statement executes**, not when the call runs. A deferred
`f.Close()` closes the `f` that was current at the `defer`. A deferred `fmt.Println(i)` prints the
`i` from that moment.

**Deferred calls run last-in, first-out.**

```go
for i := 0; i < 5; i++ {
    defer fmt.Printf("%d ", i)
}
// prints: 4 3 2 1 0
```

Both properties together support a tracing pair, where the entry message is produced by the
argument expression and the exit message by the deferred call:

```go
func trace(s string) string {
    fmt.Println("entering:", s)
    return s
}

func un(s string) {
    fmt.Println("leaving:", s)
}

func a() {
    defer un(trace("a"))
    fmt.Println("in a")
}
```

`trace("a")` runs at the `defer`, printing "entering: a"; `un("a")` runs at return, printing
"leaving: a".
