# FEAT-002 — Template Engine

**Status:** Draft  
**Version:** 0.2.0  
**Type:** Feature  

---

## 1. Technical Design

### Problem

When a work item is created, the system writes `metadata.yaml` only.  
There is no structured document for the engineer to work from.  
Each work type (bug, feature, refactor) requires a different document shape.

### Solution

A template engine that:

1. Selects the correct markdown template for the work type
2. Substitutes `{{placeholders}}` with work item values
3. Writes `spec.md` into the work item folder alongside `metadata.yaml`

### Output Before FEAT-002

```
output/
  BUG-001-Dashboard-crash/
    metadata.yaml
```

### Output After FEAT-002

```
output/
  BUG-001-Dashboard-crash/
    metadata.yaml
    spec.md
```

---

## 2. Folder Structure

```
src/
├── cli.py
├── __init__.py
│
├── config/
│   ├── __init__.py
│   └── config.py                  (add TEMPLATES_DIR constant)
│
├── factories/
│   ├── __init__.py
│   ├── work_item_factory.py
│   └── template_factory.py        (NEW — resolves work_type → Path)
│
├── models/
│   ├── __init__.py
│   ├── work_item.py
│   └── rendered_template.py       (NEW — wraps content + output path)
│
├── services/
│   ├── __init__.py
│   ├── filesystem_service.py
│   ├── metadata_service.py
│   ├── numbering_service.py
│   ├── template_service.py        (IMPLEMENT — load, render, write)
│   └── work_item_service.py       (MODIFY — call TemplateService.write())
│
├── templates/
│   ├── bug.md                     (NEW)
│   ├── feature.md                 (NEW)
│   └── refactor.md                (NEW)
│
└── utils/
    └── __init__.py

specifications/
  FEAT-002-template-engine.md
```

---

## 3. Class Responsibilities

### `RenderedTemplate` (models/rendered_template.py)

Holds the result of a template render operation.

| Field | Type | Description |
|---|---|---|
| `content` | `str` | Fully rendered markdown text |
| `output_path` | `Path` | Where `spec.md` will be written |
| `work_item_id` | `str` | ID of the work item (for tracing) |

Responsibilities:
- Data container only
- No logic
- No IO

---

### `TemplateFactory` (factories/template_factory.py)

Resolves a work type to its template file path.

| Method | Input | Output | Raises |
|---|---|---|---|
| `get_path(work_type)` | `str` | `Path` | `TemplateNotFoundError` |

Responsibilities:
- Map `work_type` → template filename
- Verify the file exists before returning
- Raise `TemplateNotFoundError` if no match or file missing

Template map:

| Work Type | Template File |
|---|---|
| `bug` | `templates/bug.md` |
| `feature` | `templates/feature.md` |
| `refactor` | `templates/refactor.md` |

---

## 4. Service Responsibilities

### `TemplateService` (services/template_service.py)

Three distinct responsibilities, three methods.

| Method | Input | Output | Raises |
|---|---|---|---|
| `load(template_path)` | `Path` | `str` (raw text) | `TemplateNotFoundError` |
| `render(raw, work_item)` | `str`, `WorkItem` | `str` (substituted) | — |
| `write(folder, work_item)` | `Path`, `WorkItem` | `RenderedTemplate` | `TemplateNotFoundError`, `IOError` |

**`load`**
- Reads the template file from disk
- Returns raw text with unreplaced `{{placeholders}}`
- Raises `TemplateNotFoundError` if the file does not exist

**`render`**
- Performs string substitution only — no external dependency
- Replaces every known placeholder
- Unknown placeholders are left untouched (silent pass-through)
- Returns the substituted string

**`write`**
- Orchestrates: `TemplateFactory.get_path()` → `load()` → `render()` → write to `folder/spec.md`
- Returns a `RenderedTemplate` with the content and path
- Called by `WorkItemService.create()` after `MetadataService.write()`

### `WorkItemService` (services/work_item_service.py — modification)

Updated creation sequence:

```
1. FileSystemService.create_work_item_folder(work_item)
2. MetadataService.write(folder, work_item)
3. TemplateService.write(folder, work_item)        ← NEW STEP
4. return folder
```

No other changes to `WorkItemService`.

---

## 5. Placeholder Design

### Syntax

Double curly braces: `{{variable_name}}`

No external library. Pure `str.replace()` in a substitution loop.

### Available Placeholders

| Placeholder | Source | Example |
|---|---|---|
| `{{id}}` | `work_item.id` | `BUG-001` |
| `{{title}}` | `work_item.title` | `Dashboard crash on load` |
| `{{type}}` | `work_item.work_type` | `bug` |
| `{{status}}` | `work_item.status` | `Draft` |
| `{{priority}}` | `work_item.priority` | `Medium` |
| `{{created}}` | `work_item.created` | `2026-06-30` |
| `{{updated}}` | `work_item.updated` | `2026-06-30` |
| `{{assignee}}` | `work_item.assignee` | `` (empty by default) |

### Substitution Context

Built as a plain `dict` from `WorkItem` fields.  
Unknown keys in the template are left as `{{variable_name}}` — no error raised.

### Output Filename

Always `spec.md` regardless of work type.

---

## 6. Error Handling

### `TemplateNotFoundError`

A custom exception in `utils/` or raised directly from services.

Raised when:
- `TemplateFactory.get_path()` is called with an unmapped `work_type`
- `TemplateService.load()` is called with a path that does not exist on disk

Message format:

```
Template not found for work type 'xyz'. Expected: src/templates/xyz.md
```

### Propagation Chain

```
TemplateFactory.get_path()
  → raises TemplateNotFoundError
    → TemplateService.write() does not catch — propagates up
      → WorkItemService.create() does not catch — propagates up
        → cli.py catches all Exception and prints ❌ message
```

No silent swallowing at any layer below `cli.py`.

### `IOError` on Write

If disk write fails, the standard `IOError` propagates unchanged to `cli.py`.

### Partial Creation

If `TemplateService.write()` fails after `MetadataService.write()` succeeded:
- The folder and `metadata.yaml` will exist
- `spec.md` will not exist
- This is acceptable for v0.2 — no rollback required
- Rollback is listed as a future extension

---

## 7. Future Extensibility

These are NOT part of FEAT-002. Listed to ensure the v0.2 design does not block them.

| Extension | How v0.2 Design Allows It |
|---|---|
| Custom template directory per project | `TEMPLATES_DIR` is a config constant — one change point |
| Multiple output files per work type | `TemplateService.write()` could accept a list of template paths |
| YAML front-matter in templates | Stripping front-matter before writing is additive to `load()` |
| Template variable validation (strict mode) | `render()` can add a strict flag that raises on unknown placeholders |
| Jinja2 or other engine | `render()` method is the single substitution point — swap internally |
| Rollback on partial failure | `WorkItemService.create()` can be wrapped in a try/finally cleanup |
| Template versioning | Template filenames can include version suffix: `bug-v2.md` |
| Interactive placeholder prompts | `cli.py` can collect additional inputs before calling `WorkItemFactory` |

---

## 8. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Template file missing at runtime | Medium | Medium | `TemplateNotFoundError` with clear message; ship templates in repo |
| Placeholder typo in template file | High | Low | Unreplaced `{{x}}` visible in output; easy to spot and fix |
| `TEMPLATES_DIR` points to wrong location | Low | High | Integration test verifies path resolves before first run |
| Encoding issue in template file | Low | Low | Always open with `encoding="utf-8"` |
| `spec.md` already exists (re-run) | Low | Low | `open("w")` overwrites silently — acceptable for v0.2 |
| `str.replace()` collision (e.g. `{{id}}` inside `{{assignee_id}}`) | Low | Low | Apply longest-key-first substitution order |

---

## 9. Test Cases

### Unit: `TemplateFactory`

| # | Input | Expected Output |
|---|---|---|
| T01 | `work_type="bug"` | Returns path to `templates/bug.md` |
| T02 | `work_type="feature"` | Returns path to `templates/feature.md` |
| T03 | `work_type="refactor"` | Returns path to `templates/refactor.md` |
| T04 | `work_type="unknown"` | Raises `TemplateNotFoundError` |
| T05 | `work_type="BUG"` (uppercase) | Raises `TemplateNotFoundError` (strict match) |

### Unit: `TemplateService.render()`

| # | Input | Expected Output |
|---|---|---|
| T06 | Template with `{{id}}`, WorkItem id=`BUG-001` | `{{id}}` replaced with `BUG-001` |
| T07 | Template with all 8 placeholders | All replaced, no `{{` remaining |
| T08 | Template with unknown `{{foo}}` | `{{foo}}` left untouched |
| T09 | Empty template string | Returns empty string |
| T10 | Template with repeated `{{title}}` | All occurrences replaced |

### Unit: `TemplateService.load()`

| # | Input | Expected Output |
|---|---|---|
| T11 | Valid path to existing file | Returns raw file contents as `str` |
| T12 | Path to non-existent file | Raises `TemplateNotFoundError` |

### Integration: `TemplateService.write()`

| # | Setup | Expected Output |
|---|---|---|
| T13 | Valid `WorkItem`, valid folder | `spec.md` written, `RenderedTemplate` returned |
| T14 | Valid `WorkItem`, folder does not exist | `IOError` raised (folder must be pre-created by `FileSystemService`) |
| T15 | `work_type` with no template | `TemplateNotFoundError` raised before any write |

### Integration: Full CLI flow

| # | Action | Expected Output |
|---|---|---|
| T16 | Run `python src/cli.py`, enter `bug`, enter title | Both `metadata.yaml` and `spec.md` created |
| T17 | Open `spec.md` | No unreplaced `{{` tokens present |
| T18 | `spec.md` content matches bug template shape | Bug-specific sections visible (e.g., Steps to Reproduce) |
| T19 | Run with `feature` | `spec.md` matches feature template shape |
| T20 | Run with `refactor` | `spec.md` matches refactor template shape |

---

## 10. Acceptance Criteria

**AC-01** — Running `python src/cli.py` creates `spec.md` in the work item folder.

**AC-02** — `spec.md` contains no unreplaced `{{` tokens.

**AC-03** — `spec.md` for `bug` contains bug-specific sections (Steps to Reproduce, Expected Behaviour, Actual Behaviour, Root Cause).

**AC-04** — `spec.md` for `feature` contains feature-specific sections (Problem Statement, Proposed Solution, Acceptance Criteria).

**AC-05** — `spec.md` for `refactor` contains refactor-specific sections (Current State, Target State, Risk Assessment).

**AC-06** — An unknown `work_type` raises `TemplateNotFoundError` with a clear message before any folder or file is created.

**AC-07** — A missing template file raises `TemplateNotFoundError` with the expected file path in the message.

**AC-08** — `metadata.yaml` is unaffected — all existing fields present and correct.

**AC-09** — No new external dependencies introduced — `str.replace()` only, no Jinja2 or similar.

**AC-10** — All 20 test cases pass.
