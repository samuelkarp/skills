# Concurrency

Depth for the "Concurrency" section of Effective Go (https://go.dev/doc/effective_go).

## Share by communicating

Concurrent programming built on shared memory needs locks around every shared value, and getting
those right is delicate. Go takes a different approach: pass values on channels so that only one
goroutine holds a given value at a time. A data race cannot arise when the value is never shared.
The one-line form of the idea:

> Do not communicate by sharing memory; share memory by communicating.

The model comes from Hoare's Communicating Sequential Processes. A useful way to picture it: a
channel is a type-safe generalization of a Unix pipe.

This is a design orientation, not a prohibition. A reference count guarded by a mutex is a fine use
of `sync.Mutex`. At a higher level, controlling access by communication makes concurrent programs
easier to get right.

## Goroutines

A goroutine is a function executing concurrently with other goroutines in the same address space.
The name is deliberate: threads, coroutines, and processes all carry connotations that do not fit.

Goroutines are cheap. Creation costs little beyond allocating a stack, the stacks start small and
grow by allocating heap storage as needed, and goroutines are multiplexed onto operating system
threads. When one blocks (for example, on I/O) the others in the same thread keep running.

Prefix a call with `go` to run it in a new goroutine. The call completes eventually; the statement
does not wait for it:

```go
go list.Sort() // run list.Sort concurrently; don't wait for it
```

A function literal launched this way is a closure over the variables it names, and those variables
stay alive as long as the goroutine is running:

```go
func Announce(message string, delay time.Duration) {
    go func() {
        time.Sleep(delay)
        fmt.Println(message)
    }() // the parentheses call the function
}
```

`Announce` gives no way to learn when the message was printed. Channels supply that.

## Channels

Channels are allocated with `make`, and the value is a reference to the underlying structure. An
optional second argument sets the buffer size; the default is zero, an unbuffered channel.

```go
ci := make(chan int)           // unbuffered channel of integers
cj := make(chan int, 0)        // unbuffered channel of integers
cs := make(chan *os.File, 100) // buffered channel of pointers to Files
```

An unbuffered channel combines value exchange with synchronization: the two goroutines meet at the
send and the receive, and both are guaranteed to be in a known state afterward.

Blocking rules:

- A receive blocks until a value is available.
- On an unbuffered channel, the sender blocks until a receiver takes the value.
- On a buffered channel, the sender blocks only when the buffer is full, and the receiver blocks
  only when it is empty.

The signal pattern uses a channel purely for synchronization, and the value sent carries no
information:

```go
c := make(chan int) // allocate a channel

// Start the sort in a goroutine; when it completes, signal on the channel.
go func() {
    list.Sort()
    c <- 1 // send a signal; value does not matter
}()
doSomethingForAWhile()
<-c // wait for sort to finish; discard sent value
```

### A buffered channel as a semaphore

The capacity of a buffered channel is a limit on how much work runs at once. Sending occupies a
slot; receiving frees one. Here `MaxOutstanding` calls to `process` may be in flight:

```go
var sem = make(chan int, MaxOutstanding)

func handle(r *Request) {
    sem <- 1   // wait for active queue to drain
    process(r) // may take a long time
    <-sem      // done; enable next request to run
}

func Serve(queue chan *Request) {
    for {
        req := <-queue
        go handle(req) // don't wait for handle to finish
    }
}
```

That version limits concurrent `process` calls, and it does not limit goroutines. `Serve` launches
one per incoming request, and they all pile up on the semaphore. If requests arrive faster than
they are handled, the program consumes memory without bound.

Fix it by acquiring the slot before launching the goroutine, so `Serve` itself blocks when the
system is saturated:

```go
func Serve(queue chan *Request) {
    for req := range queue {
        sem <- 1
        go func() {
            process(req)
            <-sem
        }()
    }
}
```

**Later Go:** since Go 1.22 the loop variable `req` is a new variable each iteration, so this
closure captures the right request. In earlier versions all the goroutines shared one `req`, and
the fix was to pass it as a parameter: `go func(req *Request) { ... }(req)`.

A second way to bound resources: start a fixed number of handler goroutines, each ranging over the
shared request channel. The number of goroutines is the concurrency limit, and no semaphore is
needed:

```go
func handle(queue chan *Request) {
    for r := range queue {
        process(r)
    }
}

func Serve(clientRequests chan *Request, quit chan bool) {
    // Start handlers
    for i := 0; i < MaxOutstanding; i++ {
        go handle(clientRequests)
    }
    <-quit // wait to be told to exit
}
```

## Channels of channels

A channel is a first-class value: it can be allocated, stored in a struct, and passed on another
channel. That is how a request carries its own reply path, which gives safe parallel
demultiplexing with no shared map of pending requests and no mutex.

```go
type Request struct {
    args       []int
    f          func([]int) int
    resultChan chan int
}
```

The client builds a request, including the channel its answer will arrive on, sends it, and later
receives:

```go
func sum(a []int) (s int) {
    for _, v := range a {
        s += v
    }
    return
}

request := &Request{[]int{3, 4, 5}, sum, make(chan int)}
clientRequests <- request

// Wait for response.
fmt.Printf("answer: %d\n", <-request.resultChan)
```

The server is a loop over the request channel:

```go
func handle(queue chan *Request) {
    for req := range queue {
        req.resultChan <- req.f(req.args)
    }
}
```

Realistic versions add error handling and timeouts, and the shape is the skeleton of a rate-limited,
parallel, non-blocking RPC system.

## Parallelization

Concurrency is the structure of a program as independently executing pieces. Parallelism is running
a calculation on multiple CPUs for speed. Go's concurrency primitives can express parallel
computations, and the two ideas remain distinct. Not every parallelizable problem suits Go's model.

To spread an independent computation over cores, split the work into pieces, launch one goroutine
per piece, and count the completions on a channel:

```go
type Vector []float64

// Apply the operation to v[i], v[i+1] ... up to v[n-1].
func (v Vector) DoSome(i, n int, u Vector, c chan int) {
    for ; i < n; i++ {
        v[i] += u.Op(v[i])
    }
    c <- 1 // signal that this piece is done
}

const numCPU = 4 // number of CPU cores

func (v Vector) DoAll(u Vector) {
    c := make(chan int, numCPU) // buffering optional but sensible
    for i := 0; i < numCPU; i++ {
        go v.DoSome(i*len(v)/numCPU, (i+1)*len(v)/numCPU, u, c)
    }
    // Drain the channel.
    for i := 0; i < numCPU; i++ {
        <-c // wait for one task to complete
    }
    // All done.
}
```

Hard-coding the core count is wrong on other machines. `runtime.NumCPU()` reports the hardware
cores; `runtime.GOMAXPROCS(0)` reports how many the user has asked the runtime to use, which the
`GOMAXPROCS` environment variable can set:

```go
var numCPU = runtime.NumCPU()
var numCPU = runtime.GOMAXPROCS(0) // query the user's setting, change nothing
```

This technique pays off only when the calculation genuinely parallelizes: work decomposable into
pieces that run without communicating.

## A leaky buffer

Buffered channels plus `select` with a `default` clause make a free list in a few lines. A `select`
with a `default` never blocks: the default runs when no other case is ready.

The client takes a buffer from the free list when one is there and allocates when it is not. The
server processes a buffer and returns it when there is room, and drops it for the garbage collector
when the list is full.

```go
var freeList = make(chan *Buffer, 100)
var serverChan = make(chan *Buffer)

func client() {
    for {
        var b *Buffer
        // Grab a buffer if available; allocate if not.
        select {
        case b = <-freeList:
            // Got one; nothing more to do.
        default:
            // None free, so allocate a new one.
            b = new(Buffer)
        }
        load(b)         // read next message from the net
        serverChan <- b // send to server
    }
}

func server() {
    for {
        b := <-serverChan // wait for work
        process(b)
        // Reuse buffer if there's room.
        select {
        case freeList <- b:
            // Buffer on free list; nothing more to do.
        default:
            // Free list full, just carry on.
        }
    }
}
```

The free list acts as a leaky bucket: full capacity is not an error condition, it is a signal that
the collector should take the excess. All the bookkeeping is the channel and the garbage collector.
