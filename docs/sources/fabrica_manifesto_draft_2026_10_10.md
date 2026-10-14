---
type: design-doc
date: 2026-10-10
origin: ~/workspace/fabrica/MANIFESTO.md (draft v0.1), briefly docs/fabrica/MANIFESTO.md; folded into docs/fabrica/core.md and the patterns on 2026-10-14
status: processed
---

## What the source says

# The Fabrica Manifesto

*Draft v0.1, 2026-10-10. Written from the user's material (`ai-mem/docs/epistemology-framework.md`, the ai-mem session of 2026-10-10, Chelsea Troy's practices). It is the user's to own and change.*

A *fabrica* was the workshop that built a cathedral and kept it standing, across more generations than any single builder lived. What it kept was not stone but knowledge: practices, handoffs, a lodge book of sketches and reasons, apprentices and masters learning from each other.

Fabrica is a framework for the same thing between humans and AI. It treats their collaboration as an **iterative knowledge mechanism**: experience is gathered at the boundaries of the work, kept with its reasons, and brought back when the situation calls for it. Tools can support it. ai-mem is one, the memory plugin for Fabrica. The framework itself is conventions, roles and rituals.

## Values

We are humans and agents working together. Through this work we have come to value:

- **Practices** over tools
- **Judgment** over scores
- **Knowledge at the right moment** over knowledge at every moment
- **Reasons** over rules
- **Mutual learning** over silent automation
- **Superseding** over forgetting

The items on the right have value. We value the items on the left more.

## Principles

1. **Agents do not know where they are.** An agent does not know on its own whether it orchestrates, assists or reviews, or what came before. Conventions give it role, scope and history. They are structural scaffolding, not workflow polish.

2. **Experience is knowledge in the context one is in.** Humans recognise a situation ("I have been here before") without effort, and recall follows. An agent has no such signal across sessions. Within a session, what is in context acts at once. So recall happens at boundaries, and it loads experience into the working context.

3. **Every boundary has a read side and a write side.** A session start, a handoff, a review and a change of mode are boundaries. At each one, what is known is brought in and what was learned is carried out. Between boundaries, no knowledge is pushed into the work.

4. **Knowledge comes in three kinds that age differently.** State is overwritten. Decisions are added to and superseded, never silently changed. Evidence never changes. Mixing them lets state erase reasons, or lets inference creep into evidence.

5. **Keep apart what a source says and what we infer.** Every claim can be traced to its evidence. Who says something belongs to what is said.

6. **The why travels with the work.** A rule without its reason is applied literally, or dropped when it looks wrong. A reason can be applied to cases no rule foresaw. Handoffs carry conclusions and their reasons, not the history of how we got there.

7. **Knowledge lives where its topic lives.** It does not live in a catch-all level, and it does not live with whoever wrote it. Every record says whose view it holds: the human's, the agent's, a role's. Those views stay side by side, and where they disagree, the disagreement is visible.

8. **Superseded, not deleted.** What has been overtaken stays readable, marked by what replaced it. The path to a decision is part of the decision.

9. **The record is tended.** Data hygiene and data care are part of the work, not cleanup after it.
   - Records stay clean: in format, linked, without duplicates, with sources that are actually used.
   - Records stay respectful: people who are not part of the work appear only generalised or under a pseudonym.
   - Dead weight is cleared, reasons are kept. The question is whether removing something loses a reason or a step on the path to a decision. If it does, the thing is superseded. If it does not, it may go. Version control is the archive underneath, so what is cleared is not lost.
   - Where a rule has to be broken for this, it is broken openly: as a stated exception with its reason, noted in the record, never as silent drift.

10. **Rituals are enforced, judgment is not.** Conventions do not break loudly. They fade. So the occurrence of a ritual is checked, and whether the practice is still alive is diagnosed. The content of a judgment stays with a role.

11. **Both sides learn.** The human sees what the agent noticed. The agent sees what the human values. Automation could give more signals, but convention gives better ones. The human stays an active participant, not a source of labels.

12. **Honest epistemic state.** Not-knowing is information, and "not documented" is a valid answer. Uncertainty is stated, not smoothed over. Corrections happen without apology, in both directions.

13. **Wisdom, not only rules.** When a lesson concerns people, record who was affected and how, not only what failed. The account of why it matters reaches situations no rule anticipated.

14. **One conversation, one domain.** Every conversation states its scope, terms and mode. When the domain or the mode changes, a handoff closes the conversation and a new one begins.

15. **Competence grows from organised experience.** An agent becomes more senior through better-organised knowledge, not a larger model. That means what worked, what failed, in which context, and why.

## Rituals

Like a retro or a daily in Scrum, Fabrica's rituals happen at known moments:

| Ritual | When | What happens |
|---|---|---|
| **Charter** | A conversation begins | Scope, terms and mode are stated. The charter is the question to the record. |
| **Taskly** | A task ends | Agents report what they learned, what blocked them and what comes next. The human adds what they saw. Record candidates come out of it. |
| **Handoff** | A boundary is crossed | Only conclusions, reasons and open points are carried over, never the history. |
| **Review against the record** | Work is checked | The work is checked against the decisions and learnings that concern it, not only against general practice. |
| **Consolidation** | Now and then | Records are linked, superseded and given better cues, so that future recall finds them. |

## Roles

- **Navigator:** the human. Sets direction, states the charter, owns the decisions.
- **Orchestrator:** keeps the overview across a body of work, and runs the Taskly and the handoffs.
- **Librarian:** answers from the record by judgment, and only reads.
- **Archivist:** writes the record and integrates what is new with what is there.
- **Team members:** do the work and report what they learned. Any team counts: coding, writing, film, research, decision-making.

## What Fabrica is not

- Not a tool. Tools can support it, and any of them can be replaced.
- Not fine-tuning. No model weights change.
- Not retrieval over a corpus. The record holds judged experience, not documents to search.
- Not a rule engine. Rules emerge from reflection, and they carry their reasons.
- Not a simulation of a person's memory. It is closer to the memory of a workshop: rituals, roles and a shared record.

## Lineage

The form of the Agile Manifesto. Architecture Decision Records (Nygard). Chelsea Troy's *The Curse of Unbounded Contexts* (DDD Europe 2026): charter, one conversation one domain, carry-only-conclusions handoffs, the third-time rule. Domain-Driven Design's bounded contexts and context maps. Team Topologies. The cathedral workshops, the *fabricae* and *Bauhütten*.
