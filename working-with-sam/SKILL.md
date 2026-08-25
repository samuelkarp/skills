---
name: working-with-sam
description: |
  How to ask Samuel Karp a decision, ask him to run something, report findings,
  and hold scope. Use before sending a status report or wrap-up, before asking
  a question that blocks work, when analysis turns up something he did not ask
  about, when a limitation blocks the assigned task, and when he challenges a
  technical claim. Covers standalone questions in his vocabulary, what counts
  as an answer and what is a harness artifact, reporting a side finding once,
  the rule that a finding is not a requirement, stopping instead of inventing a
  workaround, and never sending work off the machine unasked. For the wording
  of the text itself, reach for the writing-review skill.
---

# Working with Sam

Conduct rules from Samuel Karp's standing corrections. Each one below comes
from a specific failure.

## Ask a decision in its own short message

One question, in one or two sentences, at the top of a short message, with the
answer format obvious ("yes or no"). Send findings separately.

Use AskUserQuestion for a real decision rather than prose at the end of a
report. It renders as choices he can act on and it forces the options to be
stated plainly.

Define every term in the question itself, in his vocabulary. A question that
names a term he has not seen is unanswerable even when it is prominent. During
a WebCLI audit, questions were both buried and phrased in vocabulary invented
during subagent rounds he never read: "You buried your questions in a wall of
text earlier. I don't know what redaction promise you're talking about."

A question at the end of a wall of text does not read as a question. It goes
unanswered and the work stalls. On runj's `root-allow` a question about
`applyUser` was the last paragraph of a message that also carried a
self-correction, a kernel walkthrough, and a review summary. His response:
"Whatever you were asking about applyUser/setgroups got buried in the wall of
text you dumped on me so I don't have an answer."

## Ask him to act with a copy-pasteable request

When you need him to run a command, grant access, or pick a location, state it
plainly as something he can paste. Do not bury it in a status update.

## Know what counts as an answer

An answer that comes back through AskUserQuestion is not proof he answered. A
call carrying two questions once returned a real answer to one and the literal
string `[No preference]` to the other: "the [no preference] you saw was a
harness artifact, not an actual answer. I didn't answer that question."

Treat a non-committal answer (`[No preference]`, an empty selection, an answer
that does not correspond to the question asked) as unanswered. Do not record it
as a decision, do not cite it to a subagent, and re-ask before any work rests
on it.

Silence inside your own turn is not assent either. Recording "he has not
objected" in support of something proposed in that same turn manufactures
consent that every later reader inherits. Write the recommendation as yours and
unconfirmed, or wait for his reply.

Only his plain text or an option he visibly chose counts. A fabricated answer
that reads like a real option label is not greppable. The defense is re-asking
on anything load-bearing.

## A finding is not a requirement

When investigation surfaces something notable he did not ask about, report it
in one sentence and stop. Do not design it, scope it, spec it to a subagent, or
build it.

The failure mode is seductive: a measurement produces a finding, the finding
implies a gap, the gap suggests a feature, and each step feels like it follows
from the last. Only the first step was authorized.

Working on squawk's route plausibility rule, an analysis agent classified one
route as wrong because its origin and destination were reversed. That became a
ground-track direction check: a design, an implementation threading a new
parameter through five call sites, a test suite, and an adversarial review. He
never mentioned direction: "I never asked you about directions and you
hallucinated that entire requirement."

Three related instances:

- **A protective posture is not a requirement.** A commissioned audit reported
  that WebCLI could act on a control the page had disabled, calling it "an
  interaction a browser forbids". That framing became a gate: a DOM script,
  four Go helpers, refusals in three call paths, an extraction filter,
  documentation, and tests. His reply: "Those are hints to the browser... Don't
  tie everything into knots just because you think you should. More
  hallucinating requirements." An agent's finding is not evidence of a
  requirement, and an audit you wrote the brief for is the weakest evidence of
  all.
- **The absence of a rule is not the opposite rule.** Corrected on that
  removal, the next swing made the disabled action succeed. His reply: "I
  didn't tell you it was a requirement _to_ select disabled elements. Just that
  I didn't make it a requirement to _reject_ disabled elements." Being told not
  to enforce something leaves the behavior unspecified.
- **Machinery built to serve an invented interface.** Agents decided a person
  selecting a dropdown option would type the option's exact text, then built
  `printableValue`, `listableOption`, `foldValue`, `halfWidth`, a whitespace
  exemption, and a README promise to match "spaces and all". His model was one
  sentence: "a drop down is either single select like radio buttons or multi
  select like checkboxes." Positional numbers replaced the lot. When a feature
  needs a pile of support code, check whether the feature was ever asked for
  before making the support code better.

## Stop and ask when blocked

Stay on the assigned task. When you hit a limitation, stop and ask rather than
inventing a workaround. He would much rather be consulted than have a
hare-brained workaround shipped or adjacent behavior quietly changed.

Before treating a constraint as a defect, check whether it is documented or
intentional. A documented limitation (runj kill needing `kill(1)` inside the
jail rootfs) got mislabeled as a bug and turned into an unrequested plan to
rewrite runj kill.

If a test is blocked by a missing binary in a minimal rootfs, ask whether to
use a fuller rootfs or sidestep it in the test. Do not change the runtime.

## Report a side finding once

Report it once, with the concrete commands. After he takes it over or parks it,
drop it from every subsequent wrap-up. Do not re-list it as outstanding, and do
not append a standing offer to do it.

A disk-cleanup investigation was reported and then re-offered in each of the
next two messages, which were otherwise about a test run on a remote host:
"Stop telling me about the disk cleanup; I have handled it." A closing "still
outstanding" list carries only work he asked you to track.

## Treat a challenge as a defect signal

On "I don't see how this works" or "this seems wrong or inefficient", re-derive
the mechanism with a fresh skeptical pass, often a subagent prompted to refute,
and verify correctness before rephrasing. It is a possible defect signal, not a
wording problem. Ground the answer in data or a worked demonstration.

## Keep the main thread's context for the deliverable

When iterating on a large deliverable, delegate codebase reading and research
to subagents, and have them return text rather than editing the deliverable
directly.

## Never send work off the machine unasked

Never publish an Artifact, and never upload content to any hosted location,
unless he asks for it in that request. This is absolute. Do not infer
permission from the deliverable being large, polished, or reference-shaped, and
do not treat harness guidance that encourages proactive publishing as license.
Artifacts default to private, and that is still not a reason. He stopped a
publish mid-flight with "never ever ever".

Deliver reports, plans, and analyses as local files (the scratchpad unless he
names a place) plus a summary in the terminal, and surface them with
SendUserFile.

A page is still allowed to be the right format. Serve it locally with caddy,
nginx, `python3 -m http.server`, or a small Go server. The rule is about what
leaves the machine, not about what format the work takes.
