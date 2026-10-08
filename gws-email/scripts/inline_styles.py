#!/usr/bin/env python3
"""Inline a fixed stylesheet into a semantic HTML fragment for email.

Email clients strip <style> blocks unpredictably, so every rule has to live in a
style="" attribute. Writing those by hand is expensive and error prone. Write
clean semantic HTML instead and run it through this script.

    python3 inline_styles.py body.html > body.inlined.html

Tags that already carry a style attribute are left alone, so you can override any
single element inline. <code> inside <pre> is skipped (the pre already styles it).

Add a class to opt into the callout box:

    <p class="callout">Assumption: ...</p>
"""

import re
import sys

MONO = "font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

STYLES = {
    "h1": "font-size:23px;line-height:1.3;margin:0 0 6px;color:#1f2328;",
    "h2": "font-size:18px;margin:28px 0 10px;padding-bottom:6px;"
          "border-bottom:1px solid #d1d9e0;color:#1f2328;",
    "h3": "font-size:15px;margin:22px 0 8px;color:#1f2328;",
    "p": "margin:0 0 12px;",
    "ul": "margin:0 0 12px;padding-left:22px;",
    "ol": "margin:0 0 12px;padding-left:22px;",
    "li": "margin-bottom:6px;",
    "a": "color:#0969da;",
    "code": f"{MONO};font-size:12px;background:#f0f1f3;padding:1px 4px;border-radius:3px;",
    "pre": f"background:#f6f8fa;border:1px solid #d1d9e0;border-radius:6px;"
           f"padding:12px 14px;overflow-x:auto;{MONO};font-size:12.5px;"
           f"line-height:1.5;margin:0 0 14px;",
    "table": "border-collapse:collapse;width:100%;font-size:13px;margin:0 0 14px;",
    "th": "text-align:left;padding:8px 10px;border:1px solid #d1d9e0;font-weight:600;"
          "background:#f6f8fa;",
    "td": "padding:8px 10px;border:1px solid #d1d9e0;vertical-align:top;",
    "hr": "border:0;border-top:1px solid #d1d9e0;margin:24px 0;",
}

CALLOUT = ("margin:0 0 12px;padding:10px 14px;background:#fff8e6;"
           "border-left:3px solid #d4a72c;border-radius:0 4px 4px 0;")

WRAPPER = ('<div style="max-width:760px;margin:0 auto;padding:8px 4px;'
           'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Helvetica,'
           'Arial,sans-serif;font-size:15px;line-height:1.6;color:#1f2328;">')


def style_tag(match, css):
    tag, attrs = match.group(1), match.group(2)
    if re.search(r'\bstyle\s*=', attrs):
        return match.group(0)
    if 'class="callout"' in attrs or "class='callout'" in attrs:
        css = CALLOUT
    attrs = re.sub(r'\s*class\s*=\s*"[^"]*"', "", attrs)
    return f'<{tag}{attrs} style="{css}">'


def inline(html):
    # Hold <pre> blocks aside so their contents are not rewritten.
    blocks = []

    def stash(m):
        blocks.append(m.group(0))
        return f"\x00PRE{len(blocks) - 1}\x00"

    html = re.sub(r"<pre\b.*?</pre>", stash, html, flags=re.S | re.I)

    for tag, css in STYLES.items():
        if tag == "pre":
            continue
        pattern = re.compile(rf"<({tag})((?:\s[^>]*)?)>", re.I)
        html = pattern.sub(lambda m: style_tag(m, css), html)

    def restore(m):
        block = blocks[int(m.group(1))]
        return re.sub(r"<(pre)((?:\s[^>]*)?)>",
                      lambda t: style_tag(t, STYLES["pre"]), block, count=1,
                      flags=re.I)

    html = re.sub(r"\x00PRE(\d+)\x00", restore, html)
    return f"{WRAPPER}\n{html.strip()}\n</div>\n"


if __name__ == "__main__":
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    sys.stdout.write(inline(src))
