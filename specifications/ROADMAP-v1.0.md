# Engineering Roadmap — Version 1.0

**Project:** AI Engineering Toolkit  
**Current Version:** 0.1.0  
**Target Version:** 1.0.0  
**Date:** 2026-06-30  

---

## Baseline — What v0.1 Delivers

- Work item creation (bug / feature / refactor)
- Sequential numbering per type (BUG-001, FEAT-001, REF-001)
- Filesystem folder creation
- `metadata.yaml` generation (9 fields)
- Interactive CLI
- `src/templates/` folder with 6 placeholder markdown files

---

## Known Issues Entering v1.0 Planning

From code review (2026-06-30):

| ID | Severity | Issue |
|---|---|---|
| C-01 | Critical | `TEMPLATES_DIR` points to wrong path |
| C-02 | Critical | `TemplateService` is an empty stub |
| C-03 | Critical | No tests exist |
| M-01 | Medium | `NumberingService` reads `OUTPUT_DIR` from config directly |
| M-02 | Medium | `WorkItem.prefix` / `number` leak construction detail |
| M-03 | Medium | No single source of truth for valid work types |
| M-04 | Medium | `cli.py` catches bare `Exception` |
| M-05 | Medium | `SRC_DIR`, `TESTS_DIR` unused in config |
| M-06 | Medium | `FileSystemService` reads `OUTPUT_DIR` from config directly |
| m-01 | Minor | `WorkItem.folder_name` is a filesystem concern in a domain model |
| m-03 | Minor | `MetadataService.write()` return value discarded |
| m-04 | Minor | `utils/` is empty with no defined purpose |
| m-06 | Minor | Generated artifact (`output/BUG-003`) committed to git |
| m-08 | Minor | `README.md` is empty |

Planned feature not yet implemented:

| ID | Feature |
|---|---|
| FEAT-002 | Template Engine — renders `spec.md` per work type from template files |

---

## Milestones

```
M1 — Architecture Repair       (foundation, must be first)
M2 — Work Type Registry        (enables M3 and M4)
M3 — Template Engine           (FEAT-002 implementation)
M4 — Test Suite                (validates M1–M3)
M5 — CLI Hardening             (user-facing quality)
M6 — Documentation             (release readiness)
M7 — Release                   (v1.0 tag)
```

---

## M1 — Architecture Repair

**Goal:** Fix all critical and medium structural issues so the foundation is correct before adding features.

**Complexity:** Low–Medium overall

| Task | Fixes | Complexity | Depends On |
|---|---|---|---|
| Fix `TEMPLATES_DIR` in `config.py` to point at `SRC_DIR / "templates"` | C-01 | Low | — |
| Remove `SRC_DIR` and `TESTS_DIR` from `config.py` if unused, or use them | M-05 | Low | — |
| Decouple `NumberingService` — accept directory as parameter, not from config | M-01 | Medium | — |
| Decouple `FileSystemService` — accept output path as parameter, not from config | M-06 | Medium | — |
| Update `WorkItemFactory` to pass `OUTPUT_DIR` when calling `NumberingService` | M-01 | Low | Decouple NumberingService |
| Update `WorkItemService` to pass `OUTPUT_DIR` when calling `FileSystemService` | M-06 | Low | Decouple FileSystemService |
| Remove `output/BUG-003-investor-page` from git history | m-06 | Low | — |

**Exit criteria:**  
- All services accept paths as parameters  
- Config exports only what is actively used  
- `TEMPLATES_DIR` resolves to the correct directory  
- No generated files tracked in git  

---

## M2 — Work Type Registry

**Goal:** Create a single source of truth for valid work types so the CLI, factory, and template engine all derive from one definition.

**Complexity:** Low

| Task | Fixes | Complexity | Depends On |
|---|---|---|---|
| Define `WorkType` enum or constant registry in `models/` or `config/` | M-03 | Low | M1 |
| Update `WorkItemFactory.PREFIXES` to derive from the registry | M-03 | Low | Registry defined |
| Update CLI prompt to derive valid types from the registry | M-03 | Low | Registry defined |
| Update future `TemplateFactory` to derive template filenames from the registry | M-03 | Low | Registry defined |

**Exit criteria:**  
- Adding a new work type requires editing exactly one location  
- CLI, factory, and template lookup are all derived from that definition  

---

## M3 — Template Engine (FEAT-002)

**Goal:** Implement `TemplateService` and `TemplateFactory` so that `spec.md` is written into every new work item folder.

**Complexity:** Medium

| Task | Fixes | Complexity | Depends On |
|---|---|---|---|
| Implement `TemplateFactory` — map work type → template path | FEAT-002 | Low | M2 (registry), C-01 (TEMPLATES_DIR) |
| Define `RenderedTemplate` model | FEAT-002 | Low | M1 |
| Implement `TemplateService.load()` — read raw template from disk | FEAT-002 | Low | C-01 |
| Implement `TemplateService.render()` — substitute `{{placeholders}}` | FEAT-002 | Low | — |
| Implement `TemplateService.write()` — orchestrate load → render → write | FEAT-002 | Medium | load, render, TemplateFactory |
| Define `TemplateNotFoundError` custom exception | FEAT-002 | Low | — |
| Update `WorkItemService.create()` to call `TemplateService.write()` as step 3 | FEAT-002, C-02 | Low | TemplateService complete |
| Populate `src/templates/bug.md` with bug-specific section headings | FEAT-002 | Low | — |
| Populate `src/templates/feature.md` with feature-specific section headings | FEAT-002 | Low | — |
| Populate `src/templates/refactor.md` with refactor-specific section headings | FEAT-002 | Low | — |

**Exit criteria (from FEAT-002 spec):**  
- AC-01 through AC-10 all pass  
- `spec.md` written for every work item  
- No unreplaced `{{` tokens in output  
- Unknown work type raises `TemplateNotFoundError` with clear message  

---

## M4 — Test Suite

**Goal:** Cover all critical paths with automated tests. 20 test cases are pre-defined in FEAT-002 spec; extend to cover M1 and M2 changes.

**Complexity:** Medium

| Task | Covers | Complexity | Depends On |
|---|---|---|---|
| Set up test runner (`pytest` or stdlib `unittest`) in `tests/` | C-03 | Low | requirements.txt updated |
| Add `pytest` (or equivalent) to `requirements.txt` | C-03 | Low | — |
| Test `WorkItem` — id formatting, folder_name sanitisation, defaults | C-03 | Low | M1 |
| Test `WorkItemFactory` — valid types, invalid type raises `ValueError` | C-03 | Low | M2 |
| Test `NumberingService` — empty dir returns 1, existing folders return next | C-03 | Medium | M1 (decoupled) |
| Test `FileSystemService` — folder created at correct path | C-03 | Low | M1 (decoupled) |
| Test `MetadataService` — YAML written with all 9 fields | C-03 | Low | M1 |
| Test `TemplateFactory` — T01–T05 from FEAT-002 spec | FEAT-002, C-03 | Low | M3 |
| Test `TemplateService.load()` — T11–T12 | FEAT-002, C-03 | Low | M3 |
| Test `TemplateService.render()` — T06–T10 | FEAT-002, C-03 | Low | M3 |
| Integration test: `WorkItemService.create()` — both files written | C-03 | Medium | M3 |
| Integration test: full CLI simulation — T16–T20 | C-03 | Medium | M3, M5 |

**Exit criteria:**  
- All 20 FEAT-002 test cases pass  
- All unit tests pass  
- Tests run with a single command (`pytest` or `python -m pytest`)  
- No tests depend on the real `output/` directory (use `tmp_path` fixture)  

---

## M5 — CLI Hardening

**Goal:** Make the CLI robust, user-friendly, and correct in its error handling.

**Complexity:** Low

| Task | Fixes | Complexity | Depends On |
|---|---|---|---|
| Replace bare `except Exception` with specific exception types | M-04 | Low | M3 (TemplateNotFoundError defined) |
| Handle empty title input — validate before calling factory | — | Low | — |
| Handle empty work type input — re-prompt or exit cleanly | — | Low | — |
| Print full output path as relative, not absolute | — | Low | — |
| Handle `KeyboardInterrupt` (Ctrl+C) gracefully | M-04 | Low | — |

**Exit criteria:**  
- No bare `except Exception` in CLI  
- Empty inputs produce a clear message, not a traceback  
- Ctrl+C exits cleanly with no stack trace  

---

## M6 — Documentation

**Goal:** Make the repository usable by anyone without prior context.

**Complexity:** Low

| Task | Fixes | Complexity | Depends On |
|---|---|---|---|
| Write `README.md` — purpose, installation, usage, examples | m-08 | Low | M5 |
| Add inline comments to `WorkItem.folder_name` explaining the sanitisation logic | m-01 | Low | — |
| Add `CHANGELOG.md` — v0.1.0 release notes | — | Low | — |
| Delete `src.zip` from working tree | m-07 | Low | — |

**Exit criteria:**  
- A new developer can clone, install, and run from `README.md` alone  
- `CHANGELOG.md` documents what v0.1 delivered  

---

## M7 — Release

**Goal:** Tag v1.0.0 with all milestones complete and verified.

**Complexity:** Low

| Task | Complexity | Depends On |
|---|---|---|
| Final full test run — all tests green | Low | M4 |
| Final CLI smoke test — create one of each work type | Low | M5 |
| Confirm `output/` is gitignored and clean | Low | M1 |
| Confirm no `__pycache__` in commit | Low | .gitignore |
| Merge any open branches | Low | All milestones |
| Tag `v1.0.0` | Low | All above |
| Push tag | Low | Tag created |

---

## Dependency Graph

```
M1 (Architecture Repair)
  │
  ├── M2 (Work Type Registry)
  │     │
  │     └── M3 (Template Engine)
  │               │
  │               └── M4 (Test Suite) ──── M5 (CLI Hardening)
  │                                                │
  │                                                └── M6 (Documentation)
  │                                                          │
  │                                                          └── M7 (Release)
  │
  └── (M4 also depends directly on M1 for decoupled services)
```

M1 is the prerequisite for everything. M2 and M3 must complete before M4 is meaningful. M5 can partially proceed in parallel with M4 but requires `TemplateNotFoundError` from M3.

---

## Complexity Summary

| Milestone | Tasks | Low | Medium | High | Total Effort |
|---|---|---|---|---|---|
| M1 — Architecture Repair | 7 | 5 | 2 | 0 | Low |
| M2 — Work Type Registry | 4 | 4 | 0 | 0 | Low |
| M3 — Template Engine | 10 | 8 | 2 | 0 | Medium |
| M4 — Test Suite | 12 | 9 | 3 | 0 | Medium |
| M5 — CLI Hardening | 5 | 5 | 0 | 0 | Low |
| M6 — Documentation | 4 | 4 | 0 | 0 | Low |
| M7 — Release | 7 | 7 | 0 | 0 | Low |
| **Total** | **49** | **42** | **7** | **0** | **Medium** |

No high-complexity tasks. The project is structurally sound — the work is completions and corrections, not redesigns.

---

## Recommended Implementation Order

```
1. M1 — Fix TEMPLATES_DIR                           (unblock everything)
2. M1 — Remove dead config constants
3. M1 — Decouple NumberingService
4. M1 — Decouple FileSystemService
5. M1 — Update callers (Factory + WorkItemService)
6. M1 — Clean git history (remove output artifact)
─────────────────────────────────────────────────────
7. M2 — Define WorkType registry
8. M2 — Update Factory, CLI, and template lookup
─────────────────────────────────────────────────────
9.  M3 — Define TemplateNotFoundError
10. M3 — Implement TemplateFactory
11. M3 — Define RenderedTemplate model
12. M3 — Implement TemplateService.load()
13. M3 — Implement TemplateService.render()
14. M3 — Implement TemplateService.write()
15. M3 — Populate bug.md, feature.md, refactor.md
16. M3 — Wire TemplateService into WorkItemService
─────────────────────────────────────────────────────
17. M4 — Add pytest to requirements.txt
18. M4 — WorkItem unit tests
19. M4 — WorkItemFactory unit tests
20. M4 — NumberingService unit tests
21. M4 — FileSystemService unit tests
22. M4 — MetadataService unit tests
23. M4 — TemplateFactory unit tests (T01–T05)
24. M4 — TemplateService unit tests (T06–T12)
25. M4 — WorkItemService integration test (T13–T15)
26. M4 — Full CLI integration test (T16–T20)
─────────────────────────────────────────────────────
27. M5 — Replace bare except Exception
28. M5 — Validate empty inputs
29. M5 — Handle KeyboardInterrupt
30. M5 — Relative path in output
─────────────────────────────────────────────────────
31. M6 — Write README.md
32. M6 — Write CHANGELOG.md
33. M6 — Delete src.zip
─────────────────────────────────────────────────────
34. M7 — Full test run
35. M7 — Smoke test all 3 work types
36. M7 — Tag v1.0.0 and push
```

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Decoupling services (M1) breaks CLI flow | Low | High | Integration test in M4 catches regressions |
| `WorkType` registry (M2) doesn't match existing `PREFIXES` dict | Low | Medium | Registry replaces dict — update together |
| Template rendering produces empty or malformed `spec.md` | Medium | Medium | T06–T10 unit tests catch this before integration |
| Test suite depends on real filesystem state | Medium | High | Use `pytest` `tmp_path` fixture — never write to real `output/` |
| v1.0 scope expands (new features added mid-flight) | Medium | High | Defer all new features to v1.1; v1.0 is completions only |

---

## What v1.0 Does NOT Include

These are explicitly deferred to v1.1 or later:

- `list` command (show all work items)
- `update` command (change status or assignee)
- Multiple output files per work type
- YAML front-matter in templates
- Custom template directories
- Jinja2 or external template engine
- Rollback on partial creation failure
- Web interface
- Database storage
