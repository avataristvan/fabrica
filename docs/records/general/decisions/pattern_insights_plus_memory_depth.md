id: pattern_insights_plus_memory_depth
type: pattern
area: general
perspective: agent
created: 1779134945.990008
---

Rule: /insights gives behavioral patterns from the outside; ai-mem gives architectural depth from the inside. Neither is sufficient alone.

When: Planning sessions, retrospectives, or any session where a fresh agent analyzes past behavior and proposes next steps.

Why: A fresh subsession agent working only from /insights sees frequencies and friction patterns, but not the deliberate decisions behind them. It proposes 'just do X' without knowing X was already tried, already rejected, or already superseded by a more nuanced solution. The depth of ai-mem is what separates 'OK with limits' from genuinely expert-level recommendations.

How to apply: For any planning or retrospective session, run mem_query first, then /insights (or vice versa), then synthesize both. The inside view corrects the outside view's shallowness; the outside view surfaces behavioral patterns the inside view can't see because it's too close to the work.

Without ai-mem: CLAUDE.md + MEMORY.md would still provide structure, but the system degrades to surface-level pattern matching. The expertise layer disappears.