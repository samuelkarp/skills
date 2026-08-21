# Methods, interfaces, and type assertions

Depth for the "Methods" and "Interfaces and other types" sections of Effective Go
(https://go.dev/doc/effective_go).

## Methods on any named type

A method may be defined on any named type whose definition lives in the same package, with two
exceptions: pointer types and interface types. The receiver does not have to be a struct. A named
slice type, a named integer, a named function type, and a named channel type can all carry methods.

## Pointers vs. values

The receiver form decides what the method can do and what can call it.

- A pointer receiver can modify the value the caller holds.
- A value receiver operates on a copy, so changes are discarded when the method returns.

The call rules follow from that:

- **Value methods can be invoked on values and on pointers.** The compiler dereferences the pointer.
- **Pointer methods can be invoked only on pointers, or on addressable values.** For an addressable
  value the compiler inserts the address operator, so `b.Write(...)` becomes `(&b).Write(...)`.

A value that is not addressable (a map element, the result of a function call, a value stored in an
interface) cannot have a pointer method called on it.

```go
type ByteSlice []byte

// Pointer receiver: this method must replace the slice header the caller holds.
func (p *ByteSlice) Append(data []byte) {
    slice := *p
    // ... grow slice and copy data in ...
    *p = slice
}
```

Give the method the canonical `Write` signature and the type satisfies `io.Writer`:

```go
func (p *ByteSlice) Write(data []byte) (n int, err error) {
    slice := *p
    // ... as above ...
    *p = slice
    return len(data), nil
}

var b ByteSlice
fmt.Fprintf(&b, "This hour has %d days\n", 7)
```

`&b` is required at that call, because `*ByteSlice` implements `io.Writer` and `ByteSlice` does not.
Interface satisfaction uses the method set, and the automatic address-of applies only to a direct
method call on an addressable value.

The practical rule: pick one receiver form per type. Mixing value and pointer receivers on the same
type makes the method set depend on which form the caller holds.

## Interfaces

An interface specifies behavior: a type that has these methods can be used here. Interfaces of one
or two methods are the norm, and are named for the method, such as `io.Writer` for a type with
`Write`.

A type can satisfy several interfaces at once. A named slice of ints can be sorted and printed:

```go
type Sequence []int

// Methods required by sort.Interface.
func (s Sequence) Len() int           { return len(s) }
func (s Sequence) Less(i, j int) bool { return s[i] < s[j] }
func (s Sequence) Swap(i, j int)      { s[i], s[j] = s[j], s[i] }

func (s Sequence) Copy() Sequence {
    copy := make(Sequence, 0, len(s))
    return append(copy, s...)
}

// Method for printing: sorts a copy before printing.
func (s Sequence) String() string {
    s = s.Copy()
    sort.Sort(s)
    str := "["
    for i, elem := range s {
        if i > 0 {
            str += " "
        }
        str += fmt.Sprint(elem)
    }
    return str + "]"
}
```

## Conversions

Two types with the same underlying type convert into each other freely. The conversion produces no
new value; it presents the existing value under a different type, and therefore a different method
set. That is a way to borrow behavior.

The `String` method above rebuilds the formatting that `fmt` already has for `[]int`. Converting
gets it back:

```go
func (s Sequence) String() string {
    s = s.Copy()
    sort.Sort(s)
    return fmt.Sprint([]int(s)) // fmt already knows how to print []int
}
```

The same technique reaches `sort.IntSlice`, which carries the three sorting methods, so `Sequence`
does not need to define them at all:

```go
func (s Sequence) String() string {
    s = s.Copy()
    sort.IntSlice(s).Sort()
    return fmt.Sprint([]int(s))
}
```

**Later Go:** `sort.Sort` and `sort.IntSlice` still work. Current code sorts a `[]int` with
`slices.Sort` and a slice by a comparison function with `slices.SortFunc`.

## Interface conversions and type assertions

A type switch is a conversion driven by the dynamic type. Each case names a type, and the declared
variable takes that type inside the case:

```go
type Stringer interface {
    String() string
}

var value any // value provided by the caller
switch str := value.(type) {
case string:
    return str
case Stringer:
    return str.String()
}
```

When only one type is in question, a type assertion names it directly. `value.(string)` yields a
`string` and panics when the dynamic type is not `string`. The comma ok form reports the outcome in
a second result; on failure the value is the zero value of the asserted type and `ok` is false:

```go
str, ok := value.(string)
if ok {
    fmt.Printf("string value is: %q\n", str)
} else {
    fmt.Printf("value is not a string\n")
}
```

The two-case type switch above is equivalent to a chain of comma ok assertions:

```go
if str, ok := value.(string); ok {
    return str
} else if str, ok := value.(Stringer); ok {
    return str.String()
}
```

## Generality

When a type exists only to implement an interface and has no exported methods beyond it, do not
export the type. Export the interface, and have the constructor return the interface type. This
says that the value has no behavior of interest beyond the interface, and it avoids repeating the
documentation of the common methods on each implementation.

The hash packages follow this. `crc32.NewIEEE` and `adler32.New` both return `hash.Hash32`, so
switching checksum algorithms is a change to the constructor call and nothing else.

The `crypto/cipher` interfaces are built the same way:

```go
type Block interface {
    BlockSize() int
    Encrypt(dst, src []byte)
    Decrypt(dst, src []byte)
}

type Stream interface {
    XORKeyStream(dst, src []byte)
}

// NewCTR returns a Stream that encrypts/decrypts using the given Block in
// counter mode. The length of iv must be the same as the Block's block size.
func NewCTR(block Block, iv []byte) Stream
```

`NewCTR` applies to any block cipher and any counter mode source, because it names interfaces at
its boundary.

## Interfaces and methods

Since an interface is only a set of methods, nearly any type can satisfy one. The `net/http`
package makes this concrete:

```go
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}
```

A struct can serve:

```go
type Counter struct {
    n int
}

func (ctr *Counter) ServeHTTP(w http.ResponseWriter, req *http.Request) {
    ctr.n++
    fmt.Fprintf(w, "counter = %d\n", ctr.n)
}

http.Handle("/counter", ctr)
```

An integer can serve:

```go
type Counter int

func (ctr *Counter) ServeHTTP(w http.ResponseWriter, req *http.Request) {
    *ctr++
    fmt.Fprintf(w, "counter = %d\n", *ctr)
}
```

A channel can serve, notifying another part of the program that a request arrived:

```go
type Chan chan *http.Request

func (ch Chan) ServeHTTP(w http.ResponseWriter, req *http.Request) {
    ch <- req
    fmt.Fprint(w, "notification sent")
}
```

And a function can serve, through an adapter type that gives the function type the method:

```go
// The HandlerFunc type is an adapter to allow the use of ordinary functions as
// HTTP handlers.
type HandlerFunc func(ResponseWriter, *Request)

// ServeHTTP calls f(w, req).
func (f HandlerFunc) ServeHTTP(w ResponseWriter, req *Request) {
    f(w, req)
}
```

`HandlerFunc` is a type with a method, and its receiver happens to be a function. That is what makes
this legal:

```go
func ArgServer(w http.ResponseWriter, req *http.Request) {
    fmt.Fprintln(w, os.Args)
}

http.Handle("/args", http.HandlerFunc(ArgServer))
```

The conversion `http.HandlerFunc(ArgServer)` creates no new value; it gives the function the method
set of `HandlerFunc`, which satisfies `Handler`. `http.HandleFunc` wraps that conversion.
