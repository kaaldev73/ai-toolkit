# Engineering Roadmap — Version 1.0

**Project:** AI Engineering Toolkit  
**Previous Version:** 0.1.0 (post-cleanup)  
**Target Version:** 1.0.0  
**Revised:** 2026-06-30 (incorporates findings from Review 1 and Review 2)  

---

## Baseline — What v0.1.0 Delivers

| Capability | Status |
|---|---|
| Work item creation (bug / feature / refactor) | ✅ Done |
| Sequential numbering per type (BUG-001, FEAT-001) | ✅ Done |
| Filesystem folder creation | ✅ Done |
| `metadata.yaml` — 9 fields | ✅ Done |
| Interactive CLI | ✅ Done |
| `src/templates/` — 6 placeholder markdown files | ✅ Done |
| Template engine (`TemplateService`) | ❌ Stub only |
| Test suite | ❌ None |
| README / documentation | ❌ Empty |

---

## Open Issues Entering v1.0

### Critical

| ID | Issue | Resolved by |
|---|---|---|
| C-01 | `TemplateService` is an empty stub in production | M4 |
| C-02 | No tests exist | M5 |
| C-03 | `NumberingService` hardwired to `OUTPUT_DIR` — untestable | M1 |
| C-04 | `FileSystemService` hardwired to `OUTPUT_DIR` — untestable | M1 |

### Medium

| ID | Issue | Resolved by |
|---|---|---|
| M-01 | No single source of truth for valid work types | M3 |
| M-02 | `WorkItem.prefix` / `number` exposed as public mutable fields | M2 |
| M-03 | `WorkItem.folder_name` encodes filesystem concern in domain model | M2 |
| M-04 | `MetadataService.write()` return value discarded by caller | M6 |
| M-05 | Bare `except Exception` in CLI swallows all errors | M6 |
| M-06 | `WorkItemService` docstring claims "management" — has only `create` | M7 |
| M-07 | `PROJECT_ROOT` fragile to `config.py` being moved | M7 |

### Minor

| ID | Issue | Resolved by |
|---|---|---|
| m-01 | `utils/` has no defined scope | M7 |
| m-02 | `PREFIXES` is an untyped dict — no enforcement or type safety | M3 |
| m-03 | Folder name parsing in `NumberingService` fragile to non-standard names | M1 |
| m-04 | `created` / `updated` typed as `str` rather than `date` | M2 |
| m-05 | Input normalisation duplicated in both CLI and factory | M6 |
| m-06 | `MetadataService` named "Service" — is a serialiser | M7 |
| m-07 | `README.md` is empty | M8 |

### Planned Feature Not Yet Implemented

| ID | Feature |
|---|---|
| FEAT-002 | Template Engine — renders `spec.md` per work type | M4 |

---

## Milestones

```
M1 — Service Decoupling        (testability foundation — must be first)
M2 — Model Integrity           (domain model correctness)
M3 — Work Type Registry        (single source of truth)
M4 — Template Engine           (FEAT-002 implementation)
M5 — Test Suite                (validates M1 through M4)
M6 — CLI Hardening             (user-facing correctness)
M7 — Code Quality              (minor items and naming)
M8 — Documentation             (release readiness)
M9 — Release                   (v1.0.0 tag)
```

---

## M1 — Service Decoupling

**Goal:** Make `NumberingService` and `FileSystemService` receive their working directory as a parameter rather than importing it from global config. This is the prerequisite for any meaningful test suite — services that depend on a hardwired global path cannot be tested in isolation.

**Complexity:** Medium  
**Blocks:** M5 (tests require decoupled services)

| # | Task | Issue | Complexity | Depends On |
|---|---|---|---|---|
| 1.1 | Remove `OUTPUT_DIR` import from `NumberingService` | C-03 | Low | — |
| 1.2 | Add `directory: Path` parameter to `NumberingService.get_next_number()` | C-03 | Low | 1.1 |
| 1.3 | Harden the folder name parsing — use regex `^PREFIX-(\d+)-` instead of `split("-")[1]` | m-03 | Low | — |
| 1.4 | Remove `OUTPUT_DIR` import from `FileSystemService` | C-04 | Low | — |
| 1.5 | Add `output_dir: Path` parameter to `FileSystemService.create_work_item_folder()` | C-04 | Low | 1.4 |
| 1.6 | Update `WorkItemFactory.create()` to pass `OUTPUT_DIR` to `NumberingService` | C-03 | Low | 1.2 |
| 1.7 | Update `WorkItemService.create()` to pass `OUTPUT_DIR` to `FileSystemService` | C-04 | Low | 1.5 |

**Exit criteria:**
- Neither `NumberingService` nor `FileSystemService` imports from `config`
- Both accept path as a parameter
- `OUTPUT_DIR` is passed only from `WorkItemFactory` and `WorkItemService`
- CLI still runs end-to-end without regression

---

## M2 — Model Integrity

**Goal:** Correct `WorkItem` so it is a pure domain model — its fields represent identity and attributes, not construction inputs or filesystem concerns. Fix date field types so invalid values cannot be assigned.

**Complexity:** Medium  
**Blocks:** M5 (model tests are straightforward only after these corrections)

| # | Task | Issue | Complexity | Depends On |
|---|---|---|---|---|
| 2.1 | Move character-stripping and slug logic out of `WorkItem.folder_name` into `FileSystemService` | M-03 | Medium | M1 complete |
| 2.2 | Remove `folder_name` property from `WorkItem` | M-03 | Low | 2.1 |
| 2.3 | Update `FileSystemService` to compute the folder name from `work_item.id` and `work_item.title` | M-03 | Low | 2.1 |
| 2.4 | Change `WorkItem.created` and `WorkItem.updated` from `str` to `datetime.date` | m-04 | Low | — |
| 2.5 | Update `MetadataService.write()` to call `.isoformat()` on date fields at serialisation time | m-04 | Low | 2.4 |
| 2.6 | Evaluate whether `prefix` and `number` should be hidden — if `id` is the only external accessor, make them private (`_prefix`, `_number`) | M-02 | Medium | — |

**Exit criteria:**
- `WorkItem` contains no filesystem logic
- `created` and `updated` are `date` objects — not strings
- Assigning `"not-a-date"` to `created` is rejected by the type system
- `metadata.yaml` still serialises dates as ISO strings
- CLI still runs end-to-end without regression

---

## M3 — Work Type Registry

**Goal:** Create a single authoritative definition of valid work types. Every component that needs to know the valid types — the CLI, the factory, the template engine — derives from it. Adding a new type becomes a one-location edit.

**Complexity:** Low  
**Blocks:** M4 (template engine derives filenames from the registry)

| # | Task | Issue | Complexity | Depends On |
|---|---|---|---|---|
| 3.1 | Define a `WorkType` enum (or `TypedDict` registry) in `models/` with `key`, `prefix`, `template_file`, `display_label` fields | M-01, m-02 | Low | M2 complete |
| 3.2 | Replace `WorkItemFactory.PREFIXES` dict with a lookup against `WorkType` | M-01, m-02 | Low | 3.1 |
| 3.3 | Update CLI prompt to generate the type list from `WorkType` rather than a hard-coded string | M-01 | Low | 3.1 |
| 3.4 | Validate that `src/templates/` files match the `template_file` values in the registry | M-01 | Low | 3.1 |

**Exit criteria:**
- `WorkType` is the single location that defines all valid types
- Adding `"task"` to `WorkType` automatically makes it available in the CLI and factory
- CLI prompt string is derived, not hard-coded
- No stranded references to `{"bug": "BUG", ...}` elsewhere

---

## M4 — Template Engine (FEAT-002)

**Goal:** Implement `TemplateService` and `TemplateFactory` so that every new work item folder contains both `metadata.yaml` and `spec.md`. Full specification in `specifications/FEAT-002-template-engine.md`.

**Complexity:** Medium  
**Blocks:** M5 (template tests), M6 (CLI needs `TemplateNotFoundError`)

| # | Task | Issue | Complexity | Depends On |
|---|---|---|---|---|
| 4.1 | Define `TemplateNotFoundError` custom exception in `utils/` | FEAT-002 | Low | — |
| 4.2 | Define `RenderedTemplate` dataclass in `models/` (`content: str`, `output_path: Path`, `work_item_id: str`) | FEAT-002 | Low | M2 complete |
| 4.3 | Implement `TemplateFactory.get_path(work_type)` — derives filename from `WorkType` registry, verifies file exists | FEAT-002 | Low | M3 complete, 4.1 |
| 4.4 | Implement `TemplateService.load(path)` — reads raw template from disk, raises `TemplateNotFoundError` if missing | FEAT-002 | Low | 4.1 |
| 4.5 | Implement `TemplateService.render(raw, work_item)` — substitutes all `{{placeholders}}` via `str.replace`, longest-key-first | FEAT-002 | Low | — |
| 4.6 | Implement `TemplateService.write(folder, work_item)` — orchestrates `get_path` → `load` → `render` → write `spec.md`, returns `RenderedTemplate` | FEAT-002 | Medium | 4.2, 4.3, 4.4, 4.5 |
| 4.7 | Wire `TemplateService.write()` into `WorkItemService.create()` as step 3 | FEAT-002, C-01 | Low | 4.6 |
| 4.8 | Write `src/templates/bug.md` — Steps to Reproduce, Expected Behaviour, Actual Behaviour, Root Cause | FEAT-002 | Low | — |
| 4.9 | Write `src/templates/feature.md` — Problem Statement, Proposed Solution, Acceptance Criteria, Dependencies | FEAT-002 | Low | — |
| 4.10 | Write `src/templates/refactor.md` — Current State, Target State, Motivation, Risk Assessment | FEAT-002 | Low | — |

**Exit criteria (AC-01 through AC-10 from FEAT-002 spec):**
- Every work item produces both `metadata.yaml` and `spec.md`
- No unreplaced `{{` tokens in `spec.md`
- Each work type produces the correct section shape
- Unknown work type raises `TemplateNotFoundError` before any file is created
- Missing template file raises `TemplateNotFoundError` with expected path in message
- No new external dependencies introduced

---

## M5 — Test Suite

**Goal:** Achieve test coverage across all services, the factory, and the model. All 20 FEAT-002 test cases pass. No test touches the real `output/` directory.

**Complexity:** Medium  
**Blocks:** M9 (cannot release without a passing test suite)

| # | Task | Covers | Complexity | Depends On |
|---|---|---|---|---|
| 5.1 | Add `pytest` to `requirements.txt` | C-02 | Low | — |
| 5.2 | Create `tests/conftest.py` with `tmp_path`-based output and templates fixtures | C-02 | Low | 5.1 |
| 5.3 | `test_work_item.py` — id formatting, `__str__`, default fields, date types | M2, C-02 | Low | M2 complete |
| 5.4 | `test_work_item_factory.py` — valid types, invalid type raises `ValueError`, normalisation | M3, C-02 | Low | M3 complete |
| 5.5 | `test_numbering_service.py` — empty dir returns 1, sequential increment, non-matching folders ignored, fragile name rejected | M1, C-02 | Medium | M1 complete |
| 5.6 | `test_filesystem_service.py` — folder created at correct path, slug computed correctly, special characters stripped | M2, C-02 | Low | M1, M2 complete |
| 5.7 | `test_metadata_service.py` — all 9 fields present in YAML, dates serialised as ISO strings, file written at correct path | M2, C-02 | Low | M2 complete |
| 5.8 | `test_template_factory.py` — T01–T05 from FEAT-002 spec (bug, feature, refactor resolve; unknown raises; uppercase raises) | M4, C-02 | Low | M4 complete |
| 5.9 | `test_template_service_load.py` — T11–T12 (valid path returns content; missing path raises `TemplateNotFoundError`) | M4, C-02 | Low | M4 complete |
| 5.10 | `test_template_service_render.py` — T06–T10 (all 8 placeholders replaced; unknown left untouched; empty input; repeated placeholders) | M4, C-02 | Low | M4 complete |
| 5.11 | `test_work_item_service.py` — T13–T15 (both files written; missing folder raises; unknown type raises before write) | M4, C-02 | Medium | M1, M4 complete |
| 5.12 | `test_cli_integration.py` — T16–T20 (both files created; no unreplaced tokens; work type sections present) | M4, M6, C-02 | Medium | M4, M6 complete |

**Exit criteria:**
- `pytest` runs with a single command from project root
- All tests pass
- No test reads from or writes to the real `output/` directory
- Test run is repeatable with no dependency on prior state

---

## M6 — CLI Hardening

**Goal:** Make the CLI correct in its error handling, clear to the user on bad input, and clean on exit under all conditions.

**Complexity:** Low  
**Blocks:** M5 (integration tests verify CLI behaviour)

| # | Task | Issue | Complexity | Depends On |
|---|---|---|---|---|
| 6.1 | Remove duplicate `.lower().strip()` from CLI — factory is the normalisation point | m-05 | Low | — |
| 6.2 | Replace bare `except Exception` with `ValueError`, `TemplateNotFoundError`, `IOError` | M-05 | Low | M4 complete (TemplateNotFoundError defined) |
| 6.3 | Add explicit `except KeyboardInterrupt` to exit cleanly on Ctrl+C | M-05 | Low | — |
| 6.4 | Validate that `title` is not empty before calling factory — print clear message, re-prompt or exit | — | Low | — |
| 6.5 | Print folder path as relative to project root, not absolute | — | Low | — |
| 6.6 | Resolve the discarded return value from `MetadataService.write()` — either use it in output or change the method to return `None` | M-04 | Low | — |

**Exit criteria:**
- `ValueError` from bad work type prints a specific actionable message
- `TemplateNotFoundError` prints the missing path
- `IOError` prints the failing operation
- Empty title produces a clear message, not a traceback
- Ctrl+C exits with return code 130, no stack trace
- No bare `except Exception` anywhere in the CLI

---

## M7 — Code Quality

**Goal:** Resolve all minor and naming issues that do not affect functionality but reduce maintainability and clarity.

**Complexity:** Low  
**Blocks:** Nothing — can run partially in parallel with M5 and M6

| # | Task | Issue | Complexity | Depends On |
|---|---|---|---|---|
| 7.1 | Correct `WorkItemService` class docstring — remove "management" | M-06 | Low | — |
| 7.2 | Add a structural assertion to `config.py` that `PROJECT_ROOT` contains `src/` — fail fast on wrong path | M-07 | Low | — |
| 7.3 | Define the scope of `utils/` — add a one-line comment or move `TemplateNotFoundError` there | m-01 | Low | M4 complete |
| 7.4 | Consider renaming `MetadataService` to `MetadataWriter` — more precise, less misleading | m-06 | Low | — |
| 7.5 | Review `WorkItem.prefix` and `number` visibility — rename to `_prefix`, `_number` if only `id` is needed externally | M-02 | Low | M2 complete |

**Exit criteria:**
- All docstrings accurately describe current behaviour
- `config.py` fails fast with a clear message if the path is wrong
- `utils/` has a defined and documented scope

---

## M8 — Documentation

**Goal:** Make the repository usable by a new developer without prior context.

**Complexity:** Low  
**Blocks:** M9

| # | Task | Issue | Complexity | Depends On |
|---|---|---|---|---|
| 8.1 | Write `README.md` — purpose, requirements, installation, usage with examples for all 3 work types | m-07 | Low | M6 complete |
| 8.2 | Write `CHANGELOG.md` — v0.1.0 section listing what was delivered and known issues at launch | — | Low | — |
| 8.3 | Update `specifications/FEAT-002-template-engine.md` status from Draft to Implemented | — | Low | M4 complete |

**Exit criteria:**
- A developer with Python 3.10+ can clone, run `pip install -r requirements.txt`, and create a work item using only `README.md`
- `CHANGELOG.md` exists and covers v0.1.0

---

## M9 — Release

**Goal:** Tag v1.0.0 with all milestones verified.

**Complexity:** Low  
**Blocks:** Nothing

| # | Task | Complexity | Depends On |
|---|---|---|---|
| 9.1 | Full test run — all tests green | Low | M5 |
| 9.2 | Smoke test — create one of each work type, verify folder + both files | Low | M4, M6 |
| 9.3 | Confirm `output/` is absent from git and gitignored | Low | — |
| 9.4 | Confirm no `__pycache__` in commit | Low | `.gitignore` |
| 9.5 | Add v1.0.0 entry to `CHANGELOG.md` | Low | M8 |
| 9.6 | Tag `v1.0.0` | Low | All above |
| 9.7 | Push tag | Low | 9.6 |

---

## Dependency Graph

```
M1 (Service Decoupling)
  │
  ├── M2 (Model Integrity)
  │     │
  │     └── M3 (Work Type Registry)
  │               │
  │               └── M4 (Template Engine)
  │                         │
  │                         ├── M5 (Test Suite) ────────┐
  │                         │                           │
  │                         └── M6 (CLI Hardening) ────►│
  │                                                     │
  │                                         M7 (Code Quality) ──┐
  │                                                             │
  │                                         M8 (Documentation) ─┤
  │                                                             │
  │                                                        M9 (Release)
  │
  └── M5 also depends on M1 directly (decoupled services enable isolation)
```

**Parallel opportunities:**
- M7 (Code Quality) tasks 7.1 and 7.2 can run during any milestone
- M8.2 (`CHANGELOG.md`) can be written at any time
- M4.8–4.10 (template file content) can be written before M4.1–4.7 (implementation)

---

## Complexity Summary

| Milestone | Tasks | Low | Medium | High | Relative Effort |
|---|---|---|---|---|---|
| M1 — Service Decoupling | 7 | 5 | 2 | 0 | Medium |
| M2 — Model Integrity | 6 | 4 | 2 | 0 | Medium |
| M3 — Work Type Registry | 4 | 4 | 0 | 0 | Low |
| M4 — Template Engine | 10 | 9 | 1 | 0 | Medium |
| M5 — Test Suite | 12 | 10 | 2 | 0 | Medium |
| M6 — CLI Hardening | 6 | 6 | 0 | 0 | Low |
| M7 — Code Quality | 5 | 5 | 0 | 0 | Low |
| M8 — Documentation | 3 | 3 | 0 | 0 | Low |
| M9 — Release | 7 | 7 | 0 | 0 | Low |
| **Total** | **60** | **53** | **7** | **0** | **Medium** |

No high-complexity tasks. All work is corrections, completions, and structured additions within the existing design.

---

## Recommended Implementation Order

```
─── M1: Service Decoupling ──────────────────────────────────
 1.  Remove OUTPUT_DIR import from NumberingService
 2.  Add directory parameter to NumberingService.get_next_number()
 3.  Harden folder name parsing with regex (prefix-number pattern)
 4.  Remove OUTPUT_DIR import from FileSystemService
 5.  Add output_dir parameter to FileSystemService.create_work_item_folder()
 6.  Update WorkItemFactory to pass OUTPUT_DIR to NumberingService
 7.  Update WorkItemService to pass OUTPUT_DIR to FileSystemService

─── M2: Model Integrity ─────────────────────────────────────
 8.  Move folder name slug logic into FileSystemService
 9.  Remove WorkItem.folder_name property
10.  Change WorkItem.created / updated to datetime.date
11.  Update MetadataService to serialise dates with .isoformat()
12.  Evaluate prefix / number visibility — privatise if appropriate

─── M3: Work Type Registry ──────────────────────────────────
13.  Define WorkType enum/registry in models/
14.  Replace WorkItemFactory.PREFIXES with registry lookup
15.  Derive CLI prompt from registry
16.  Validate template filenames match registry entries

─── M4: Template Engine ─────────────────────────────────────
17.  Define TemplateNotFoundError in utils/
18.  Define RenderedTemplate dataclass in models/
19.  Implement TemplateFactory.get_path()
20.  Implement TemplateService.load()
21.  Implement TemplateService.render()
22.  Implement TemplateService.write()
23.  Wire TemplateService into WorkItemService.create() as step 3
24.  Write src/templates/bug.md with bug-specific sections
25.  Write src/templates/feature.md with feature-specific sections
26.  Write src/templates/refactor.md with refactor-specific sections

─── M6: CLI Hardening ───────────────────────────────────────
27.  Remove duplicate .lower().strip() from CLI
28.  Replace bare except Exception with specific exception types
29.  Add except KeyboardInterrupt
30.  Validate empty title input
31.  Print relative folder path
32.  Resolve MetadataService.write() return value

─── M5: Test Suite ──────────────────────────────────────────
33.  Add pytest to requirements.txt
34.  Create tests/conftest.py with fixtures
35.  test_work_item.py
36.  test_work_item_factory.py
37.  test_numbering_service.py
38.  test_filesystem_service.py
39.  test_metadata_service.py
40.  test_template_factory.py (T01–T05)
41.  test_template_service_load.py (T11–T12)
42.  test_template_service_render.py (T06–T10)
43.  test_work_item_service.py (T13–T15)
44.  test_cli_integration.py (T16–T20)

─── M7: Code Quality ────────────────────────────────────────
45.  Correct WorkItemService class docstring
46.  Add structural assertion to config.py
47.  Define scope of utils/ package
48.  Evaluate MetadataService rename
49.  Privatise WorkItem.prefix / number if appropriate

─── M8: Documentation ───────────────────────────────────────
50.  Write README.md
51.  Write CHANGELOG.md (v0.1.0 + v1.0.0)
52.  Update FEAT-002 status to Implemented

─── M9: Release ─────────────────────────────────────────────
53.  Full test run
54.  Smoke test — all 3 work types
55.  Verify output/ is gitignored and absent
56.  Add v1.0.0 CHANGELOG entry
57.  Tag v1.0.0 and push
```

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Moving `folder_name` from `WorkItem` to `FileSystemService` (M2) breaks existing folder lookup in `NumberingService` | Medium | High | Fix `NumberingService` parsing first (M1.3) so it no longer depends on the folder name format being produced by `WorkItem` |
| Privatising `prefix`/`number` on `WorkItem` (M2, M7) breaks test introspection | Low | Low | Tests should assert `work_item.id == "BUG-001"`, not `work_item.prefix` |
| `WorkType` enum (M3) introduces import circularity if placed in wrong package | Low | Medium | Place in `models/work_type.py` — no service or factory imports are needed there |
| Template rendering produces malformed output on titles with `{{` in them | Low | Medium | T06–T10 tests surface this; render replaces only known keys |
| Test isolation failure — tests write to real `output/` | Medium | High | `conftest.py` fixtures must use `tmp_path` and monkeypatch `OUTPUT_DIR` before any test runs |
| v1.0 scope expands mid-flight | Medium | High | Gate strictly: list, update, search, database, web UI are all v1.1+ |

---

## Explicitly Deferred to v1.1+

| Feature | Reason |
|---|---|
| `list` command | Requires index or filesystem scan — separate design |
| `update` command (status, assignee) | Requires reading and rewriting `metadata.yaml` |
| Multiple output files per work type | Template engine v2 — beyond current spec |
| Jinja2 or external template engine | Dependency addition — needs justification |
| Custom / per-project template directories | Config extension — not needed for single-project v1.0 |
| Rollback on partial creation failure | Transactional filesystem — complex, low value at this scale |
| Database-backed storage | Architectural shift — separate roadmap |
| Web interface | Separate product surface |
| Numbering index file for performance | Not needed below ~10,000 items |
