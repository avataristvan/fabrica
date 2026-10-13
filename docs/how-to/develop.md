# How to develop ai-mem

Tasks for working on ai-mem's own code. Layout and module roles: [architecture](../reference/architecture.md).

## Set up and run the tests

```bash
pip install -e ".[dev]"             # editable install with test dependencies
python -m pytest tests/ -q          # all tests
python -m pytest tests/test_doctor.py -q   # one file
```

Fixtures are in `tests/conftest.py`: it points `AI_MEM_PATH` at a temp dir, sets `AI_MEM_ADR_DISABLED=1` and unsets `AI_MEM_RECORDS_HOME` and `AI_MEM_WORKSPACE_ROOT`. Infrastructure tests for the default backend use `FileMemoryRepository` on temp dirs (`tests/infrastructure/test_file_repository.py`). Run the count yourself rather than trusting a number in a doc: `python -m pytest tests/ -q | tail -1`.

Run `tests/test_daemon.py` alone before suspecting a change when it fails: it fails sporadically (see `CLAUDE.md`, "Known noise").

Install and uninstall tests run `install.py`/`uninstall.py` against a temp `HOME`, never the real `~/.claude`.

## Add a use case

1. Create `ai_mem/application/<name>.py` with a class `<Action>UseCase`.
2. `__init__` accepts only injected dependencies (repositories, other use cases).
3. One public method, `execute(self, ...)`, with no side effects via globals.
4. Wire it in the adapter that needs it (`mem_cli.py`, a hook, or a CLI entry point), at module load or in the command handler, not deeper.

```python
from ai_mem.domain.memory import MemoryRepository

class MyUseCase:
    def __init__(self, repo: MemoryRepository) -> None:
        self._repo = repo

    def execute(self, ...) -> ...:
        ...
```

## Add infrastructure

Add a concrete implementation of a domain Protocol in `ai_mem/infrastructure/`. Never import from `application/` or from other infrastructure modules. Runtime code of the practice (`mem`, hooks, lint, doctor) stays standard-library only.

## Add or change a hook

Enforcing hooks live in `ai_mem/hooks/<name>.py` as `python -m ai_mem.hooks.<name>` entry points. They must check or remind, never raise, never write stderr, and treat every id and path from stdin as untrusted. Behaviour and registration: [hooks](../reference/hooks.md). Test the module by piping a JSON payload on stdin; do not rely on this session's running hooks.

## Run an entry point by hand

```bash
python3 -m ai_mem.hook          # SessionStart hook (pipe a JSON payload on stdin)
mem doctor                      # diagnosis of the practice
mem lint                        # check the current area's records
```

## Change a doc

Documentation is organised by [Diátaxis](https://diataxis.fr/): `docs/tutorial/` (learning), `docs/how-to/` (tasks), `docs/reference/` (facts), `docs/explanation/` (why). Dated evidence is `docs/sources/` and never changes. Before moving or merging a doc, list every record, skill and agent that points at it, then update the live ones; records are changed only by the archivist. After a doc change, run `mem doctor` and read its Sources section.

## Conventions

- Timestamps in records are numbers (`created`, `valid_until`); the format is in the [record format](../reference/record-format.md).
- A delete without ids is refused; whole-collection deletes belong to the rollback stack only.
- No ranking step exists: reading is by the librarian's judgment, so do not add scores.
