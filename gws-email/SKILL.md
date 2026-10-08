---
name: gws-email
description: |
  Send email through the `gws` (Google Workspace) CLI, including
  well-formatted HTML mail. Use when asked to email something, mail a report,
  send a summary or link by email, or save a draft. Covers the send command
  shape, the auth check and its handoff to the user, why the body must be an
  inlined-style HTML fragment, and a script that inlines a tested stylesheet
  so you do not hand-write style attributes.
---

# Sending email with the gws CLI

## What the request authorizes

The request authorizes exactly what is sent and to whom. Asking for an email
does not authorize publishing an Artifact or uploading anything to get a link
to send. A Gmail draft also leaves the machine, so `--draft` needs the same
request as a send. Use `--dry-run` while revising the body.

```
BAD   Publish the report as an Artifact and email the link.
GOOD  Send the report body inline, as HTML, to the address the request
      named.
```

## Check auth first

`gws` fails at send time with an unhelpful 401, so check before building
anything:

```
gws auth status | grep -E 'token_valid|token_error'
```

If `"token_valid": false`, the fix is an interactive browser login that you
cannot perform. Stop and hand it to the user as a copy-pasteable line:

> Run this in the session: `! gws auth login`

A present `has_refresh_token` does not mean the token works. Only
`token_valid` does.

## The command

```
gws gmail +send --to <recipient> --subject 'Subject line' \
  --body "$(cat body.html)" --html
```

"Email me" means the user's own address as the session context reports it.
If the session reports none, ask. Never write a real address into a skill,
script, or committed file.

Useful flags: `--cc` / `--bcc` (comma-separated), `--from` (a configured
send-as alias), `-a PATH` (repeatable attachment, 25MB total), `--draft`
(save instead of send), `--dry-run`. Success prints a JSON object with
`"labelIds": ["SENT"]`.

Always build the body in a file and pass it with `"$(cat file)"`. Inlining a
long HTML string into the shell command invites quoting bugs and makes the
body impossible to revise without retyping it.

## The body must be an HTML fragment with inline styles

Two constraints that are easy to get wrong:

- **Markdown does not render.** `--body` is either plain text or HTML.
  Sending markdown produces a wall of asterisks and backticks. Converting a
  markdown report to email means writing the HTML.
- **`<style>` blocks and external CSS are unreliable.** Mail clients strip
  them. Every rule has to live in a `style=""` attribute on the element
  itself. Same for images and fonts: no external references.

Write fragment tags only. No `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>`;
the helper wraps the content itself.

Escape `<`, `>`, and `&` inside `<pre>` and `<code>`. Shell snippets and
anything showing placeholder syntax like `<id>` will silently vanish
otherwise.

## Do not hand-write the style attributes

Write clean semantic HTML, then inline a tested stylesheet with
`scripts/inline_styles.py` in this skill's directory:

```
python3 <skill-dir>/scripts/inline_styles.py body.html > body.inlined.html
gws gmail +send --to ... --subject '...' \
  --body "$(cat body.inlined.html)" --html
```

The script styles `h1` `h2` `h3` `p` `ul` `ol` `li` `a` `code` `pre` `table`
`th` `td` `hr`, wraps everything in a max-width readable container, and
leaves any element that already has a `style` attribute alone so you can
override one thing inline. `<code>` inside `<pre>` is skipped. Add
`class="callout"` to a `<p>` for a highlighted box, which suits caveats,
assumptions, and warnings.

Adjust the `STYLES` dict in the script rather than sprinkling one-off
overrides through the document.

## Formatting that reads well

- A summary or lede paragraph up top, then `<h2>` sections. Headed sections
  survive skimming on a phone; a single long body does not.
- `<table>` for anything with repeated structure (log lines with their
  source and trigger, options with tradeoffs). It renders far better than a
  nested list.
- `<pre>` for commands and code. It scrolls horizontally rather than
  wrapping into nonsense.
- `class="callout"` for the two or three statements the reader must not
  miss.

For the wording of the body, run the writing-review skill. This skill covers
the HTML.
