# Fabrica: the core

> Draft. What has to be in place for a way of working to be Fabrica. The how is in the [patterns](patterns/README.md). ai-mem is one implementation of it for Claude Code.

A *fabrica* was the workshop that built a cathedral and kept it standing, across more generations than any single builder lived. What it kept was not stone but knowledge: practices, handoffs, a lodge book of sketches and reasons, apprentices and masters learning from each other.

## Values

We are humans and agents working together. Through this work we have come to value:

- **Practices** over tools
- **Judgment** over scores
- **Knowledge at the right moment** over knowledge at every moment
- **Reasons** over rules
- **Mutual learning** over silent automation
- **Superseding** over forgetting

The items on the right have value. We value the items on the left more.

## Definition

Fabrica is a practice that lets humans and agents learn from their own work: experience is captured at the boundaries of the work, kept with its reasons, and brought back when a situation calls for it.

Fabrica is not a work process. It has no cadence, no timebox and no pipeline of its own. It runs alongside whatever method a team uses to do the work: Scrum, a delivery method such as BMAD, a film production, a research project. That method produces the work and its planning artifacts. Fabrica keeps what the team learns while doing it.

## The premise

An agent does not know where it is. It does not know on its own whether it orchestrates, assists or reviews, what came before, or what was decided and why. Within a session, what is in its context acts at once; across sessions, nothing carries over unless something carries it. A human recognises a situation ("I have been here before") without effort. An agent has no such signal.

So Fabrica gives the work structure at the points where knowledge can move: the boundaries. Its conventions are not workflow polish. They are how an agent learns its role, its scope and its history.

## Three kinds of knowledge

Knowledge ages in three different ways, and Fabrica keeps the three apart.

| Kind | Examples | How it changes |
|---|---|---|
| **State** | the current focus, a handoff | Overwritten. Only the latest counts; version control keeps the history. |
| **Decisions and learnings** | a decision with its reason, an observation, an open task | Added to and superseded. Never silently changed while they carry a reason. |
| **Evidence** | a measurement, a source, a past design | Never changes. Claims are traced back to it. |

Mixing them does damage: state overwrites reasons, or inference creeps into evidence.

## Roles

| Role | Who | Responsibility |
|---|---|---|
| **Navigator** | a human | Sets direction, states the charter, owns the decisions. |
| **Orchestrator** | a human or an agent | Keeps the overview across a body of work; runs the Taskly and the handoffs. |
| **Librarian** | an agent | Answers from the record by judgment. Reads only. "Not documented" is a valid answer. |
| **Archivist** | an agent | Writes the record: integrates what is new with what is there, decides between new, update, supersede and confirm, sets the links. Reports what it put where; the Navigator can correct any placement. |
| **Team members** | humans or agents | Do the work and report what they learned. Any team counts. |

Only the Navigator and the Archivist write records. Everyone else delivers record candidates as plain text.

## Rituals

Each ritual happens at a boundary of the work, not on a schedule.

| Ritual | When | What happens | Read / write |
|---|---|---|---|
| **Charter** | a conversation begins | Scope, terms and mode are stated. The charter is the question to the record. | read |
| **Taskly** | a task ends | Agents report what they learned, what blocked them and what comes next; the human adds what they saw. Record candidates come out of it. | write |
| **Handoff** | a boundary is crossed | Only conclusions, reasons and open points are carried over, never the history. | both |
| **Review against the record** | work is checked | The work is checked against the decisions and learnings that concern it, not only against general practice. | read |
| **Consolidation** | now and then | Records are linked, superseded, cleaned of dead weight and given better cues. | write |

Every boundary has a read side and a write side. Between boundaries, nothing is pushed into the work.

## Artifacts

- **The record.** One file per decision, learning or open task, kept in version control in the area of its topic (the nearest folder that holds the work it is about). Each record states its reason, whose view it holds, and a cue: the situation in which someone would need it without knowing to ask.
- **Links between records.** A record that is overtaken is marked `supersedes` by its successor and stays readable. A later record can `confirm` or `contradict` an earlier one, or be `derived_from` it. Trust in a record comes from these links, not from a score.
- **Focus.** One short text per area: what is being worked on now and what comes next. State, overwritten.
- **Handoff.** Charter, conclusions, open points. State, overwritten.
- **Sources.** Dated evidence that never changes: measurements, talks, past designs.

## Minimum

A team practises Fabrica when:

1. every conversation states its charter;
2. every task ends with a Taskly whose candidates reach the Archivist;
3. decisions are kept with their reasons and superseded, not deleted;
4. the Librarian is asked at the boundaries before a decision is made, not guessed around.

Everything else is a [pattern](patterns/README.md): useful, named, and optional.

## Fabrica and Kaizen

Fabrica has the shape of Kaizen, the continuous improvement of the Toyota Production System. Like Kaizen, it is not a production process: it runs alongside the work and is carried by those who do it.

| Kaizen | Fabrica |
|---|---|
| **Hansei:** structured reflection after a piece of work, including what went wrong | **Taskly:** what was learned, what blocked, what comes next |
| **Yokoten:** a lesson is passed sideways to other teams | **Librarian and areas:** a record kept in one place is brought to the place that needs it |
| **Standard work:** the current best way is written down and replaced when a better one is found | **Decisions with their reasons,** superseded instead of deleted; work is reviewed against them |
| **5 Whys:** to the cause, not the symptom | **The why travels with the work:** a record names the cause and the reason |
| **A3 report:** problem, cause and countermeasure on one page | **The record:** Decision / Why / Scope, Rule / When / Why |
| **PDCA** | Charter (plan), the work (do), review against the record (check), Taskly and consolidation (act) |

The difference is where experience lives. In a Toyota team it lives in people's heads, and the standard writes down the part that must be shared. Agents start every session without that memory; sideways spreading and reflection do not happen by themselves. So in Fabrica, seniority comes from the record itself. Like the lodge book of a cathedral workshop, carried from one generation of builders to the next, the record is carried from session to session, and keeps explicitly, with its reasons, what a human team carries implicitly.

## What Fabrica is not

- Not a tool. Tools can support it, and any of them can be replaced.
- Not a work process. It brings no cadence of its own and runs alongside the method that does the work.
- Not fine-tuning. No model weights change.
- Not retrieval over a corpus. The record holds judged experience, not documents to search.
- Not a rule engine. Rules emerge from reflection, and they carry their reasons.
- Not a simulation of a person's memory. It is closer to the memory of a workshop: rituals, roles and a shared record.

## Status

Fabrica is young. Some of its practices are shown to work in use, some are on probation, some are only convention. Each pattern says which. The record of how Fabrica itself was built is its own proof: it is public, together with the reasons and the dead ends.

## Lineage

Kaizen and the Toyota Production System (hansei, yokoten, standard work, PDCA). The form of the Agile Manifesto. Christopher Alexander's pattern language. Architecture Decision Records (Nygard). Chelsea Troy's *The Curse of Unbounded Contexts* (DDD Europe 2026): charter, one conversation one domain, carry-only-conclusions handoffs, the third-time rule. Domain-Driven Design's bounded contexts and context maps. Team Topologies. The cathedral workshops, the *fabricae* and *Bauhütten*.
