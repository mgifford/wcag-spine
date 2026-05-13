# Definition of Done for Reports

> A report in WCAG Spine is done when it is accurate, accessible, reviewable, and useful to the audience it was written for.

---

## What "done" means in this repository

For this project, a report is considered done when a maintainer can read it end to end and clearly understand:

- What the report is about
- Why it matters
- What evidence supports the findings
- What action, if any, should happen next

---

## Default audience and scope

Unless a report explicitly says otherwise, it should be written for:

- Project maintainers reviewing content for publication or follow-up work
- Contributors updating documentation, data, or dashboard behaviour
- Accessibility practitioners using the repository to understand WCAG coverage, automation limits, and manual testing responsibilities

The default scope for a finished report in this repository is:

- The current dashboard and its documented views: Cards, Spine, Table, ACT Rules, and Coverage
- The current filters: Level, Role, Automation, and Search
- The current documentation and accessibility commitments in `README.md` and `ACCESSIBILITY.md`
- The current validation workflow used in this repository

---

## What a completed report already contains

### 1. Clear purpose and boundaries

A done report states its purpose in plain language, names its intended audience, and says what is inside and outside scope. It does not assume the reader already knows whether the report is about documentation quality, dashboard accessibility, automation coverage, data integrity, or workflow health.

### 2. Evidence that can be verified

A done report is grounded in sources that another contributor can verify. In this repository that usually means:

- Current repository files such as `README.md`, `ACCESSIBILITY.md`, `testing-methods.md`, `data/master_spine.json`, and relevant scripts
- Current project behaviour described in the repo, especially the five documented views and their filters
- External standards or source documents when the report discusses WCAG, ACT Rules, ARRM, or Trusted Tester
- Clear separation between observed facts, interpretation, and recommendations

If something is uncertain, incomplete, or inferred, the report says so directly.

### 3. Accessibility and plain language

A done report follows the same accessibility expectations as the rest of the project:

- Headings are descriptive and in a logical order
- Links use meaningful text
- Tables and lists make sense without relying on colour alone
- Language is plain, respectful, and consistent with the repository's accessibility commitments
- Any diagrams or visualisations follow the repository's documented accessibility requirements

### 4. Alignment with the current repository

A done report matches the repo as it exists now. File names, commands, views, terminology, and workflow references are current. The report does not describe outdated navigation, missing views, or commands that are not part of the documented workflow.

When the report includes counts, metrics, or examples, they are either current and reproducible or explicitly dated.

### 5. Actionable conclusions

A done report does more than describe a problem. It leaves the maintainer with a usable outcome:

- A clear decision to make
- A concrete follow-up task
- A documented risk to track
- Or confirmation that no further action is required

If more work is needed, the next step is stated directly instead of being implied.

### 6. Review-ready presentation

A done report has already had its wording, terminology, and structure cleaned up enough for another contributor to review it without first rewriting it. Cross-references are updated where needed, and AI-assisted authorship is disclosed in `README.md` when applicable.

---

## Repo-specific validation

If the report is paired with code, data, or workflow changes, it is not done until the relevant project validation has been run and the outcome has been recorded.

For this repository, that normally means:

- `python3 -m pytest`
- `npm run test:a11y`
- `python scripts/sync_data.py` when data-pipeline behaviour or generated data is affected

If there are pre-existing failures unrelated to the report, they should be noted instead of silently ignored. At the time this document was introduced, the repository already had unrelated Python test failures in `tests/test_sync_data.py`, and local accessibility tests could also fail in environments where the Playwright Chromium executable was not installed.

---

## Practical definition of done

For WCAG Spine, a report is done when it is already in a publishable, reviewable state: the purpose is clear, the claims are supported, the writing is accessible, the details match the current repo, and the reader knows what should happen next. It should read like a finished project document, not like a worksheet that still needs to be completed by someone else.

---

## Closure statement

A maintainer should be able to merge or publish a done report with only normal editorial review. If the document still depends on placeholders, unanswered questions, or unstated evidence, it is not done yet.
