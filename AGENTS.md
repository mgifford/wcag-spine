# AI Agent Instructions (AGENTS.md)

> **System instructions for AI coding assistants contributing to this project.**
>
> This file follows the [agents.md](https://agents.md) convention — a machine-readable manifest
> that tells AI agents how to work within this repository's standards and constraints.

This file provides guidance for AI agents (GitHub Copilot, Cursor, Claude, Antigravity, etc.) working on the **WCAG Spine** project — an interactive dashboard visualising WCAG 2.2 Success Criteria with accessible HTML/CSS components.

## Primary References

Before proposing or writing any changes, read these project files:

1. **[ACCESSIBILITY.md](./ACCESSIBILITY.md)** — Accessibility commitment and requirements (WCAG 2.2 AA)
2. **[README.md](./README.md)** — Project overview, data schema, and architecture

## Project Overview

This project is a **WCAG data visualisation dashboard** with three key components:

| File | Purpose |
|------|---------|
| `index.html` | GitHub Pages dashboard — filtering, cards, spine view, table views |
| `assets/js/app.js` | Frontend logic — HTML node generation, filters, routing |
| `assets/css/style.css` | Dashboard styles — must maintain WCAG contrast ratios |
| `data/master_spine.json` | Merged WCAG 2.2 data (auto-updated daily) |
| `scripts/sync_data.py` | Python data orchestrator — fetches from W3C, Axe, Alfa, Trusted Tester |
| `.github/workflows/sync_accessibility.yml` | Daily sync + GitHub Pages deploy |

## Core Requirements

### Accessibility

- All dashboard features must comply with **WCAG 2.2 Level AA**
- The `index.html` must remain keyboard-navigable and screen reader compatible
- All visualisations must use semantic HTML and SVG-like accessibility patterns
- Ensure all custom components (Spine View, Flow Diagram) have `aria-label` or `aria-labelledby`
- Color combinations must pass WCAG contrast ratios (4.5:1 min) in both light and dark modes
- Use semantic HTML, proper ARIA attributes, and keyboard focus management


### Data Integrity

The `master_spine.json` schema must remain:

```json
{
  "meta": { "generated": "...", "wcag_version": "2.2", "sources": {} },
  "success_criteria": {
    "X.Y.Z": {
      "title": "...", "level": "A|AA|AAA", "principle": "...", "url": "...",
      "automation": { "act": [], "axe": [], "alfa": [] },
      "manual": {
        "roles": [],
        "tt_steps": [],
        "arrm_tasks": [{ "id": "...", "task": "...", "primary_ownership": "...",
                         "secondary_ownership": "...", "category_url": "...", "role_url": "..." }]
      }
    }
  }
}
```

- **Never** remove or rename top-level schema keys — `app.js` depends on this structure
- `_TT_IDS_IN_NODE=4` in `sync_data.py` and `TT_IDS_IN_NODE=4` in `app.js` must stay in sync
- SC keys must always be in format `"X.Y.Z"` (e.g., `"2.4.11"`)

### Code Quality

- Keep changes **minimal and request-scoped** — do not refactor unrelated code
- Maintain existing patterns in `app.js` (filter logic, HTML rendering, URL routing)
- Python code in `sync_data.py` uses only the standard library — do not add third-party dependencies
- All JavaScript in `app.js` runs in the browser — no Node.js-specific APIs
- Prefer `const`/`let` over `var`; use semantic variable names

### Documentation

- Keep all documentation links valid
- Update cross-references when adding new pages
- Follow the project's plain-language style

### AI Disclosure

Transparency about AI use is a core commitment of this project. When contributing as an AI agent, you **must** update the **AI Disclosure** section in `README.md`:

- Add your LLM name (and version or variant if known) to the table if it is not already listed.
- Describe the task(s) you performed (e.g., code generation, documentation, data mapping, PR automation).
- Be specific: note whether your contribution affected the project *build*, *data pipeline*, or *runtime* behaviour.
- **Never** add an LLM or tool that you cannot confirm was actually used in this project.


## Testing and Validation

- **Data sync:** Run `python scripts/sync_data.py` locally to validate data changes
- **Dashboard:** Open `index.html` in a browser; verify all views (Cards, Spine, Table)
- **Keyboard:** Tab through all interactive elements; confirm no keyboard traps
- **Screen reader:** Test with NVDA (Windows) or VoiceOver (macOS) on at least one view
- **Contrast:** Use browser DevTools or a contrast checker for any CSS color changes

## Priority Taxonomy

When identifying or reporting issues:

- **Critical:** Dashboard feature prevents users from completing core tasks (blocked navigation, keyboard trap)
- **High:** Significant accessibility barrier or WCAG data error
- **Medium:** Documentation clarity or incomplete examples
- **Low:** Minor improvements, typos, enhancements

Never introduce Critical or High severity accessibility issues.

## Quick Decision Framework

If uncertain about an approach:

1. Consult **[ACCESSIBILITY.md](./ACCESSIBILITY.md)** for project-level commitments
2. Check existing patterns in `app.js` and `index.html`
3. When in doubt, choose the more accessible option

## Machine-Readable Standards Reference

This project's data is grounded in [wai-yaml-ld](https://github.com/mgifford/wai-yaml-ld) machine-readable standards:

- [WCAG 2.2 (YAML)](https://github.com/mgifford/wai-yaml-ld/blob/main/kitty-specs/001-wai-standards-yaml-ld-ingestion/research/wcag-2.2-normative.yaml)
- [ARIA Informative (YAML)](https://github.com/mgifford/wai-yaml-ld/blob/main/kitty-specs/001-wai-standards-yaml-ld-ingestion/research/wai-aria-informative.yaml)
- [Standards Link Graph (YAML)](https://github.com/mgifford/wai-yaml-ld/blob/main/kitty-specs/001-wai-standards-yaml-ld-ingestion/research/standards-link-graph.yaml)

## Continuous Improvement

Help maintain quality by:

- Suggesting accessibility improvements when reviewing code
- Documenting new patterns in `examples/` for reuse
- Sharing reasoning in PR descriptions
- Flagging outdated WCAG guidance or broken data source links

---

**Remember:** This project exists to make WCAG data more accessible. The tool must itself be a demonstration of good accessibility practice.
