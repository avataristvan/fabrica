# How to develop ai-mem

Tasks for working on ai-mem's own code. Layout and module roles: [architecture](../reference/architecture.md).

## Set up and run the tests

```bash
pip install -e ".[dev]"             # editable install with test dependencies
python -m pytest tests/ -q          # all tests
python -m pytest tests/test_doctor.py -q   # one file
```

Fixtures are in `tests/conftest.py`: it points `AI_MEM_PATH` at a temp dir, and unsets `AI_MEM_WORKSPACE_ROOT`. Infrastructure tests use `FileMemoryRepository` on temp dirs (`tests/infrastructure/test_file_repository.py`); use-case tests use the in-memory repository in `conftest.py`. `tests/test_stdlib_only.py` imports every `ai_mem` module with `python -I -S`, the check for `dependencies = []`. Run the count yourself rather than trusting a number in a doc: `python -m pytest tests/ -q | tail -1`.

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
- A delete without ids is refused.
- No ranking step exists: reading is by the librarian's judgment, so do not add scores.
