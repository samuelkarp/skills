# Keeping claims true

A wording pass is where accurate text becomes inaccurate. Two mechanisms do it.

## A sweep drops the scope

A scoped claim and a general one read as stylistic variants, so the edit feels
lossless while removing the qualifier that made it true.

On runj's `root-allow` branch, a sweep across dozens of sites removed
"grants/denies" framing. It turned "require privilege that a jail denying
`allow.suser` grants to no one" into "no process has privilege in a jail with
`allow.suser` false". The original claim covered a specific set of operations;
the replacement covers every privilege and is false three ways over: FreeBSD's
`priv_check_cred` grants `PRIV_VM_MLOCK`, `PRIV_KMEM_READ`, and
`PRIV_DEBUG_UNPRIV` on paths that never reach the `suser_enabled` check. The
counterexample was already documented. The false sentence landed at seven sites
before an adversarial reviewer caught it.

The scoped form names the operations the claim covers. The commit body on the
same branch states it that way:

> setgroups(2), setgid(2), and raising a hard limit are privileged operations.
> A jail with allow.suser disabled does not have a super-user.

When a sweep touches a sentence carrying a technical claim:

- Re-derive the claim against the source before writing the replacement.
- Keep the scope explicit by naming the operations it covers.
- Grep for the old phrasing allowing for line breaks. The one instance that
  survived this sweep spanned a newline.

## A constant absorbs the review

A checkable token (a constant, an identifier, a path) is the part a reviewer
can act on, so it draws the check, and the quantifier around it reads as
context.

A commit body said a library's index request "uses the client the library
builds, which gives up after 10 seconds." A review found
`Timeout: 10 * time.Second` in `defaultClient` and passed the sentence. The
sentence also asserted that the index request always uses that client. That
holds only where `NewCatalog` builds the client; with a caller-supplied client
the request uses the caller's client, which may set no timeout.

The source does not record how the commit body was corrected. BAD is the
original claim; GOOD is an illustrative rewrite that carries the scope:

```
BAD   The index request uses the client the library builds, which gives
      up after 10 seconds.
GOOD  When NewCatalog builds the client, the index request uses
      defaultClient, which gives up after 10 seconds. A client supplied
      by the caller has the caller's timeouts.
```

The same pattern took seven correction rounds on a reference doc for the same
library, each round's claim true of one request shape and written without the
qualifier.

- When dispatching a review of technical claims, make scope its own named
  item: which caller, which construction path, which request shape each
  sentence holds for.
- Any sentence saying every, always, or never gets checked against the code
  before it ships. This applies to commit bodies and code comments as much as
  docs.
