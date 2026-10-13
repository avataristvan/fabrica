id: the-coder_mcp_tool_description_contract
type: pattern
area: general
perspective: the-coder
created: 1779142854.871379
---

Rule: When authoring MCP tools or AI-facing APIs, include explicit routing instructions in the tool description — not just parameter docs.
When: Writing MCP server `list_tools()` or any tool schema exposed to an LLM.
Why: The tool description IS part of the behavioral contract. LLMs use it to decide which tool to call and how. Implicit conventions ('use the active collection') create silent bugs when the user's intent targets a different scope. Explicit instructions ('when the user asks to store for a different project, pass collection=repo.X explicitly') prevent misrouting without code changes.
How to apply: Add one 'When X, do Y' clause per non-obvious routing decision. Keep it under 2 sentences — verbosity dilutes attention.