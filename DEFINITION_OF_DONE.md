# Definition of Done for Reports

> A report in WCAG Spine is done when it is accurate, accessible, reviewable, and useful to the audience it was written for.

---

## Core outcome

The report is complete when a reviewer can read it end to end and answer:

- What the report is about
- Why it matters
- What evidence supports the findings
- What action, if any, should happen next

---

## Required completion criteria

### 1. Purpose and scope are clear

- The report states its goal in plain language
- The intended audience is clear
- The scope is explicit, including any exclusions or assumptions

### 2. Findings are evidence-based

- Statements about WCAG, ACT Rules, ARRM, Trusted Tester, or project behaviour are backed by current repository data or cited external sources
- Facts, interpretation, and recommendations are clearly separated
- Any uncertainty, gaps, or limitations are called out directly

### 3. The report is accessible

- Headings are descriptive and ordered logically
- Links use meaningful text
- Tables and lists are understandable without relying on colour alone
- Language is plain, respectful, and consistent with the project's accessibility commitments
- If diagrams are included, they follow this repository's documented accessibility requirements

### 4. It matches the current project state

- File names, commands, views, and data structures referenced in the report match the repository
- The report does not contradict the current dashboard behaviour or documented workflow
- Any metrics or examples are current, reproducible, and dated when appropriate

### 5. It is actionable

- Conclusions are specific enough to support a decision, follow-up task, or review
- Recommended next steps are clear when further work is needed
- Outstanding risks or blockers are listed instead of being implied

### 6. It is review-ready

- Another contributor can verify the main claims from the cited sources
- Spelling, grammar, and terminology have been checked
- Related documentation links or cross-references have been updated where needed
- AI-assisted authorship has been disclosed in `README.md` when applicable

---

## Repo-specific validation

If the report is paired with code, data, or workflow changes, it is not done until the relevant project validation has been completed and the outcome is recorded:

- `python3 -m pytest`
- `npm run test:a11y`
- `python scripts/sync_data.py` when data-pipeline behaviour or generated data is affected

If there are pre-existing failures unrelated to the report, they should be noted rather than silently ignored.

---

## Ready-to-close checklist

- [ ] Purpose, audience, and scope are clear
- [ ] Findings are supported by evidence
- [ ] Accessibility and plain-language review are complete
- [ ] References match the current repository state
- [ ] Actions, decisions, or next steps are clear
- [ ] Related documentation has been updated
- [ ] Required validation has been run or exceptions have been documented

