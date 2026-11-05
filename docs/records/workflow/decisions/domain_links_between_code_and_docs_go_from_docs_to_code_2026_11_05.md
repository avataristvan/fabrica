type: domain
topic: workflow
perspective: user
created: 1793905525.711953
cue: I am writing a code comment, build file or package source and want to point at a doc, or I am moving a doc that code mentions.
---

Decision: Links between code and docs go one way, from the docs to the code. Code, build files and package sources do not link docs (no docs/... paths in comments); a comment carries its own why. The bridge from code to knowledge is the commit that changed the code: its message names the experiment or record, and `git show <sha>:<path>` resolves it at that commit even after the doc moved. From the doc side, an experiment or record names the code path it is about. A docs path still found in code is removed the next time that file is touched, not with a change of its own (checksum, pkgrel).
Why: Code leaves the repository (to a device, into a package, as an upstream patch), where a repo path means nothing. No lint reads code, so a code -> doc link rots silently, while doc -> code paths are checkable (mem doctor reports backticked paths that no longer exist). Docs stay free to move, which /fabrica:tidy needs. Same rule as for handoffs: what changes more often or leaves the context does not point at what may move. It replaces the first version ("code links only stable docs; a linked doc keeps its path"), written into the documentation map earlier the same day and turned around after the galaxy pilot (user decided, with the galaxy-tab-a-2016 session).
Scope: reference/documentation_map.md ("Links between code and docs go from the docs to the code only"), /fabrica:tidy, every area.
Evidence: galaxy-tab-a-2016 pmos/device-samsung-gtaxllte/bootmac-after-bluetoothd.conf (under sha512sums in the APKBUILD) ended with "(docs/bt-bdaddr-hog-plan-2026-11-02.md, A4)"; /fabrica:tidy moved that doc to docs/experiments/bt-bdaddr-hog/README.md, and fixing the comment would force a checksum change and a pkgrel bump.

## Edges

- related: [domain_handoffs_point_to_records_never_back_closed_and_deleted_2026_11_05](domain_handoffs_point_to_records_never_back_closed_and_deleted_2026_11_05.md)
- related: [domain_handoff_points_instead_of_copying_2026_10_19](domain_handoff_points_instead_of_copying_2026_10_19.md)
