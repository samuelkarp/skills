# Data, allocation, printing, and initialization

Depth for the "Data" and "Initialization" sections of Effective Go
(https://go.dev/doc/effective_go).

## Allocation with new

`new(T)` allocates storage for a value of type `T`, zeroes it, and returns its address, a `*T`. It
zeroes; it does not initialize. The value it returns is ready to use only if the zero value of `T`
is ready to use.

The source records one language change of its own: starting with Go 1.26, `new` also accepts a
value expression, so `new(int64(300))` allocates an `int64` holding 300 and returns its address.

Designing a type so that its zero value is useful removes the need for a constructor. `sync.Mutex`
has no `NewMutex`, because a zeroed mutex is an unlocked mutex. `bytes.Buffer` has no constructor,
because a zeroed buffer is an empty buffer ready to be written to.

The property composes. A struct whose fields all have useful zero values has a useful zero value:

```go
type SyncedBuffer struct {
    lock   sync.Mutex
    buffer bytes.Buffer
}

p := new(SyncedBuffer) // *SyncedBuffer, ready to use
var v SyncedBuffer     // SyncedBuffer, ready to use
```

## Constructors and composite literals

A composite literal builds a value from its parts in one expression, so a constructor that assigns
field by field collapses to a single `return`:

```go
func NewFile(fd int, name string) *File {
    if fd < 0 {
        return nil
    }
    return &File{fd: fd, name: name}
}
```

Fields may be given positionally, in which case every field must be present and in order, or with
`field: value` labels. Labeled fields may appear in any order, and omitted fields take their zero
values.

Taking the address of a composite literal allocates a fresh value each time, so `&File{}` is
equivalent to `new(File)`, and a constructor may return the address of a local composite literal.

Arrays, slices, and maps take composite literals too, with the same syntax except that the
labels are indices or keys:

```go
a := [...]string   {Enone: "no error", Eio: "Eio", Einval: "invalid argument"}
s := []string      {Enone: "no error", Eio: "Eio", Einval: "invalid argument"}
m := map[int]string{Enone: "no error", Eio: "Eio", Einval: "invalid argument"}
```

`[...]T{}` sizes the array from its elements.

## Allocation with make

`make(T, args)` applies only to slices, maps, and channels. It returns an initialized value of type
`T`, not a pointer. These three types are references to data structures that must be initialized
before use: a slice is a descriptor holding a pointer, a length, and a capacity, and until that
pointer is set the slice is nil.

For slices, `make([]int, 10, 100)` allocates a backing array of 100 ints and returns a slice of
length 10 and capacity 100 that refers to its first 10 elements. With one size argument, length and
capacity are equal. For maps and channels, `make` initializes the internal structure, with the
argument as a size hint or channel buffer size.

```go
var p *[]int = new([]int) // p is a *[]int; *p is a nil slice
var v []int = make([]int, 100)

var p *[]int = new([]int) // unnecessarily indirect
*p = make([]int, 100, 100)

v := make([]int, 100) // idiomatic
```

## Arrays

Arrays in Go are values, which differs from C in three ways:

- Assigning one array to another copies all the elements.
- Passing an array to a function passes a copy of it.
- The length is part of the type, so `[10]int` and `[20]int` are unrelated types.

A function that must not copy takes a pointer to the array, and `range` over `*a` still works:

```go
func Sum(a *[3]float64) (sum float64) {
    for _, v := range *a {
        sum += v
    }
    return
}

array := [...]float64{7.0, 8.5, 9.1}
x := Sum(&array) // note the explicit &
```

That style is not idiomatic Go. Use slices.

## Slices

A slice wraps an array to give a sized, growable view of a sequence. Except for items with explicit
dimensions such as a transformation matrix, most array programming in Go is done with slices.

A slice holds a reference to an underlying array. Assigning one slice to another makes both refer
to the same array. A function that takes a slice and modifies its elements modifies the caller's
data, which is why `Read` takes a slice and not a pointer plus a count:

```go
func (f *File) Read(buf []byte) (n int, err error)
n, err := f.Read(buf[0:32]) // reads at most 32 bytes
```

A slice's length may change up to its capacity. `len(s)` is the current length, `cap(s)` the
maximum length the slice can take by reslicing. Both are legal on a nil slice and report 0.

Growing a slice requires reallocating when the capacity is exhausted, copying, and returning the
new slice, because the slice header itself is passed by value:

```go
func Append(slice, data []byte) []byte {
    l := len(slice)
    if l+len(data) > cap(slice) { // reallocate
        // Allocate double what is needed, for future growth.
        newSlice := make([]byte, (l+len(data))*2)
        // copy is predeclared and works for any slice type.
        copy(newSlice, slice)
        slice = newSlice
    }
    slice = slice[0 : l+len(data)]
    copy(slice[l:], data)
    return slice
}
```

The built-in `append` does this for you; the hand-written version explains why its result must be
assigned.

## Two-dimensional slices

Go's arrays and slices are one-dimensional. A two-dimensional value is an array of arrays or a
slice of slices, and the rows may have different lengths:

```go
type Transform [3][3]float64 // a 3x3 array, really an array of arrays
type LinesOfText [][]byte    // a slice of byte slices

text := LinesOfText{
    []byte("Now is the time"),
    []byte("for all good gophers"),
    []byte("to bring some fun to the party."),
}
```

Two allocation strategies. Allocate each row on its own when rows grow and shrink independently:

```go
picture := make([][]uint8, YSize)
for i := range picture {
    picture[i] = make([]uint8, XSize)
}
```

Allocate one flat array and slice the rows out of it when the shape is fixed. This costs one
allocation and keeps the pixels contiguous:

```go
picture := make([][]uint8, YSize)
pixels := make([]uint8, XSize*YSize)
for i := range picture {
    picture[i], pixels = pixels[:XSize], pixels[XSize:]
}
```

## Maps

A map associates keys with values. The key type must support equality: integers, floating point and
complex numbers, strings, pointers, interfaces whose dynamic type supports equality, structs, and
arrays. Slices are not valid key types, since equality is not defined on them. Like slices, maps
hold a reference to an underlying structure, so a function that changes a map's contents changes the
caller's map.

```go
var timeZone = map[string]int{
    "UTC": 0 * 60 * 60,
    "EST": -5 * 60 * 60,
    "CST": -6 * 60 * 60,
    "MST": -7 * 60 * 60,
    "PST": -8 * 60 * 60,
}

offset := timeZone["EST"]
```

Fetching an absent key yields the zero value of the element type. That makes `map[string]bool` a
usable set:

```go
attended := map[string]bool{"Ann": true, "Joe": true}
if attended[person] { // false when person is absent
    fmt.Println(person, "was at the meeting")
}
```

When the zero value is a legitimate entry, use the comma ok form to tell absence from a zero value:

```go
seconds, ok := timeZone[tz] // ok reports presence
```

Combined with an `if` initializer, this gives the standard lookup shape:

```go
func offset(tz string) int {
    if seconds, ok := timeZone[tz]; ok {
        return seconds
    }
    log.Println("unknown time zone:", tz)
    return 0
}
```

To test presence without the value, assign the value to the blank identifier:

```go
_, present := timeZone[tz]
```

`delete(timeZone, "PDT")` removes an entry and is safe when the key is absent.

## Printing

Go's formatted printing lives in `fmt`. `Printf`, `Fprintf`, and `Sprintf` take a format string;
`Print` and `Println` format by default rules. The `S` forms return a string, the `F` forms take an
`io.Writer` as their first argument, and the plain forms write to standard output.

```go
fmt.Printf("Hello %d\n", 23)
fmt.Fprint(os.Stdout, "Hello ", 23, "\n")
fmt.Println("Hello", 23)
```

`Println` puts a blank between every pair of operands and appends a newline. `Print` adds a blank
only between two operands when neither is a string.

Numeric verbs do not carry size or signedness flags: the routine reads the argument's type.

```go
var x uint64 = 1<<64 - 1
fmt.Printf("%d %x; %d %x\n", x, x, int64(x), int64(x))
// 18446744073709551615 ffffffffffffffff; -1 -1
```

`%v` is the catchall and formats anything, including arrays, slices, structs, and maps. It is what
`Print` and `Println` use. Maps print with their keys sorted.

```go
fmt.Printf("%v\n", timeZone)
// map[CST:-21600 EST:-18000 MST:-25200 PST:-28800 UTC:0]
```

Struct verbs:

```go
type T struct {
    a int
    b float64
    c string
}
t := &T{7, -2.35, "abc\tdef"}
fmt.Printf("%v\n", t)  // &{7 -2.35 abc	def}
fmt.Printf("%+v\n", t) // &{a:7 b:-2.35 c:abc	def}
fmt.Printf("%#v\n", t) // &main.T{a:7, b:-2.35, c:"abc\tdef"}
```

Other useful verbs: `%q` for a double-quoted string (`%#q` prefers backquotes), `%x` for a hex dump
of a string or byte slice (`% x` spaces the bytes), and `%T` for the type of a value.

To control how your own type prints, give it a `String() string` method. `fmt` calls it for `%v`,
`%s`, `Print`, and friends. Convert the receiver before printing it inside that method, or the
conversion recurses until the stack is exhausted:

```go
type MyString string

func (m MyString) String() string {
    return fmt.Sprintf("MyString=%s", string(m)) // the conversion is required
}
```

`String` methods can call `Sprintf` because the print routines are fully reentrant.

The variadic signature behind all of this is:

```go
func Printf(format string, v ...any) (n int, err error)
```

Inside `Printf`, `v` has type `[]any`. Passing it on to another variadic function requires `...`:
`fmt.Sprintln(v...)` passes the elements; `fmt.Sprintln(v)` passes one slice argument. A variadic
function of a concrete type works the same way:

```go
func Min(a ...int) int {
    min := int(^uint(0) >> 1) // largest int
    for _, i := range a {
        if i < min {
            min = i
        }
    }
    return min
}
```

**Later Go:** the source writes `...interface{}`; `any` is the current spelling.

## Append

The built-in signature, informally:

```go
func append(slice []T, elements ...T) []T
```

`append` cannot be written in Go, because `T` stands for any type. It appends the elements and
returns the result, which must be assigned, since the underlying array may have been replaced:

```go
x := []int{1, 2, 3}
x = append(x, 4, 5, 6) // [1 2 3 4 5 6]

y := []int{4, 5, 6}
x = append(x, y...) // ... is required to append a slice
```

## Initialization

Go's initialization is more capable than C's or C++'s: complex structures can be built during it,
and initialization order across packages is handled correctly.

### Constants

Constants are created at compile time, even inside functions, and may be numbers, runes, strings,
or booleans. Their expressions must be evaluable by the compiler: `1<<3` qualifies,
`math.Sin(math.Pi/4)` does not, because function calls happen at run time.

Enumerated constants use `iota`, which counts within a `const` block and lets the expression repeat
implicitly:

```go
type ByteSize float64

const (
    _           = iota // ignore the first value by assigning to blank
    KB ByteSize = 1 << (10 * iota)
    MB
    GB
    TB
    PB
    EB
    ZB
    YB
)
```

Attaching a `String` method to such a type makes the values print in units. Note that this
particular `String` method uses `%f`, a numeric verb, so it does not call itself recursively:

```go
func (b ByteSize) String() string {
    switch {
    case b >= YB:
        return fmt.Sprintf("%.2fYB", b/YB)
    case b >= ZB:
        return fmt.Sprintf("%.2fZB", b/ZB)
    }
    return fmt.Sprintf("%.2fB", b)
}
```

### Variables

Package-level variables take ordinary expressions, evaluated at run time in dependency order:

```go
var (
    home   = os.Getenv("HOME")
    user   = os.Getenv("USER")
    gopath = os.Getenv("GOPATH")
)
```

### The init function

Each file may define one or more `init` functions, which take no arguments and return nothing. A
package's `init` functions run after every package-level variable in that package has its
initializer evaluated, and those run only after all imported packages are initialized.

Beyond initializations that cannot be expressed as declarations, `init` verifies or repairs program
state before execution proper begins:

```go
func init() {
    if user == "" {
        log.Fatal("$USER not set")
    }
    if home == "" {
        home = "/home/" + user
    }
    if gopath == "" {
        gopath = home + "/go"
    }
    // gopath may be overridden by --gopath flag on command line.
    flag.StringVar(&gopath, "gopath", gopath, "override default GOPATH")
}
```
