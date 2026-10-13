id: the-coder_trust_domain_contract
type: pattern
area: general
perspective: the-coder
created: 1781305453.940226
---

Rule: Trust the domain contract — do not filter again what the repository layer already guarantees.
When: Use case implementation that builds on repository methods.
Why: Double filtering is noise and implies false distrust of one's own abstraction. If the contract is unclear, clarify it in the interface — not through defensive checks in the caller.
