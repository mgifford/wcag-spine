#!/usr/bin/env python3
from __future__ import annotations
"""
WCAG Spine - Data Orchestrator
Synchronizes data from W3C ARRM, ACT Rules, Axe-core, and Alfa
to produce a consolidated master_spine.json covering all WCAG 2.2 SCs.

Data sources
------------
- W3C ACT Rules JSON (rules.json)         — ACT rule IDs and their WCAG SC mappings
- W3C ACT testcases JSON (testcases.json) — richer SC mappings, including secondary SCs
- Alfa rule index (TypeScript source)     — Alfa rule IDs and their WCAG Criterion mappings
- axe-core rules directory (JSON)         — axe rule IDs and their WCAG tag mappings
- W3C ARRM CSV files                      — responsible roles and task ownership per SC
- DHS Trusted Tester v5 HTML             — step-by-step federal test procedures per SC
"""

import csv
import json
import re
import sys
import urllib.request
import urllib.error
from io import StringIO
from pathlib import Path
from datetime import date

# ---------------------------------------------------------------------------
# Source URLs
# ---------------------------------------------------------------------------
ARRM_ALL_TASKS_URL = (
    "https://raw.githubusercontent.com/w3c/wai-arrm/draft/_data/arrm/arrm-all-tasks.csv"
)
ARRM_WCAG_SC_URL = (
    "https://raw.githubusercontent.com/w3c/wai-arrm/draft/_data/arrm/arrm-wcag-sc.csv"
)
# Machine-readable WCAG-to-ACT mapping published by W3C in the wcag-act-rules GitHub repo.
# This replaced the former rules.json endpoint at
#   https://www.w3.org/WAI/standards-guidelines/act/rules/data/rules.json
# which is no longer available.  Each entry includes an "accessibility_requirements" dict
# with keys like "wcag20:1.3.1" / "wcag21:1.3.5" (primary and secondary SCs).
ACT_RULES_URL = (
    "https://raw.githubusercontent.com/w3c/wcag-act-rules/main/wcag-mapping.json"
)
# W3C ACT testcases JSON — supplemental secondary-SC coverage.  The wcag-mapping.json
# already includes secondary requirements via accessibility_requirements, so this source
# is now a secondary enrichment only.  Fetch failures are handled gracefully.
ACT_TESTCASES_URL = (
    "https://www.w3.org/WAI/content-assets/wcag-act-rules/testcases.json"
)
# Alfa rules TypeScript index — exports every Alfa rule with its WCAG Criterion mapping.
# Parsing Criterion.of("X.Y.Z") calls gives us a direct SC→Alfa-rule-ID map.
ALFA_RULES_INDEX_URL = (
    "https://raw.githubusercontent.com/Siteimprove/alfa/main/packages/alfa-rules/src/index.ts"
)
# Alfa EARL implementation report — maps Alfa rules to ACT rules (all consistency
# levels, including partial/semi-automated implementations).
ALFA_ACT_EARL_URL = (
    "https://raw.githubusercontent.com/Siteimprove/alfa-act-r/main/reports/alfa-automated-report.json"
)
# axe-core GitHub raw rules directory listing (GitHub API JSON).
# Each entry names a JSON rule file; fetching select files gives us WCAG tags.
AXE_RULES_API_URL = (
    "https://api.github.com/repos/dequelabs/axe-core/contents/lib/rules"
)
# Fallback: fetch the compiled axe.js and regex-parse rule metadata when the API
# listing + individual file strategy is blocked or rate-limited.
AXE_CORE_JS_URL = (
    "https://raw.githubusercontent.com/dequelabs/axe-core/develop/axe.js"
)
TT_IMPLEMENTATIONS_URL = (
    "https://section508coordinators.github.io/TrustedTester/index.html"
)
# Section 508 Coordinator resources: https://github.com/Section508Coordinators

TT_BASE_URL = "https://section508coordinators.github.io/TrustedTester/"

# Section 508 Functional Performance Criteria (FPC) mapping from CivicActions.
# Maps each WCAG 2.0 SC to the disability groups it affects.
FPC_MAPPING_URL = (
    "https://raw.githubusercontent.com/CivicActions/accessibility-data-reference/main/mapping-wcag-to-fpc.csv"
)

# Maps CSV column headers to short FPC codes.
# Source: https://www.section508.gov/develop/mapping-wcag-to-fpc/
FPC_COLUMN_NAMES: dict[str, str] = {
    "Without Vision (WV)": "WV",
    "Limited Vision (LV)": "LV",
    "Without Perception of Color (WPC)": "WPC",
    "Without Hearing (WH)": "WH",
    "Limited Hearing (LH)": "LH",
    "Without Speech (WS)": "WS",
    "Limited Manipulation (LM)": "LM",
    "Limited Reach and Strength (LRS)": "LRS",
    "Limited Language, Cognitive, and Learning Abilities (LLCLA)": "LLCLA",
}

# Maps each WCAG SC number to the most relevant TrustedTester section page.
# SCs not covered by TT v5 (WCAG 2.1/2.2 or AAA) are mapped to the closest
# equivalent section.  Source: appendixa.html cross-reference table.
TT_SC_PAGE: dict[str, str] = {
    # 1.1 – Text Alternatives
    "1.1.1": "images.html",
    # 1.2 – Time-based Media
    "1.2.1": "audiovideo.html",
    "1.2.2": "media.html",
    "1.2.3": "media.html",
    "1.2.4": "media.html",
    "1.2.5": "media.html",
    "1.2.6": "media.html",
    "1.2.7": "media.html",
    "1.2.8": "media.html",
    "1.2.9": "audiovideo.html",
    # 1.3 – Adaptable
    "1.3.1": "structure.html",
    "1.3.2": "css-content-position.html",
    "1.3.3": "sensory.html",
    "1.3.4": "keyboard.html",
    "1.3.5": "forms.html",
    "1.3.6": "structure.html",
    # 1.4 – Distinguishable
    "1.4.1": "sensory.html",
    "1.4.2": "auto.html",
    "1.4.3": "sensory.html",
    "1.4.4": "resize.html",
    "1.4.5": "images.html",
    "1.4.6": "sensory.html",
    "1.4.7": "sensory.html",
    "1.4.8": "sensory.html",
    "1.4.9": "images.html",
    "1.4.10": "resize.html",
    "1.4.11": "sensory.html",
    "1.4.12": "resize.html",
    "1.4.13": "keyboard.html",
    # 2.1 – Keyboard Accessible
    "2.1.1": "keyboard.html",
    "2.1.2": "keyboard.html",
    "2.1.3": "keyboard.html",
    "2.1.4": "keyboard.html",
    # 2.2 – Enough Time
    "2.2.1": "timelimits.html",
    "2.2.2": "auto.html",
    "2.2.3": "timelimits.html",
    "2.2.4": "timelimits.html",
    "2.2.5": "timelimits.html",
    "2.2.6": "timelimits.html",
    # 2.3 – Seizures and Physical Reactions
    "2.3.1": "flashing.html",
    "2.3.2": "flashing.html",
    "2.3.3": "flashing.html",
    # 2.4 – Navigable
    "2.4.1": "repetitive.html",
    "2.4.2": "titles.html",
    "2.4.3": "keyboard.html",
    "2.4.4": "links.html",
    "2.4.5": "multiple.html",
    "2.4.6": "structure.html",
    "2.4.7": "keyboard.html",
    "2.4.8": "repetitive.html",
    "2.4.9": "links.html",
    "2.4.10": "structure.html",
    "2.4.11": "keyboard.html",
    "2.4.12": "keyboard.html",
    "2.4.13": "keyboard.html",
    # 2.5 – Input Modalities
    "2.5.1": "keyboard.html",
    "2.5.2": "keyboard.html",
    "2.5.3": "forms.html",
    "2.5.4": "keyboard.html",
    "2.5.5": "keyboard.html",
    "2.5.6": "keyboard.html",
    "2.5.7": "keyboard.html",
    "2.5.8": "keyboard.html",
    # 3.1 – Readable
    "3.1.1": "language.html",
    "3.1.2": "language.html",
    "3.1.3": "language.html",
    "3.1.4": "language.html",
    "3.1.5": "language.html",
    "3.1.6": "language.html",
    # 3.2 – Predictable
    "3.2.1": "keyboard.html",
    "3.2.2": "forms.html",
    "3.2.3": "repetitive.html",
    "3.2.4": "repetitive.html",
    "3.2.5": "repetitive.html",
    "3.2.6": "repetitive.html",
    # 3.3 – Input Assistance
    "3.3.1": "forms.html",
    "3.3.2": "forms.html",
    "3.3.3": "forms.html",
    "3.3.4": "forms.html",
    "3.3.5": "forms.html",
    "3.3.6": "forms.html",
    "3.3.7": "forms.html",
    "3.3.8": "forms.html",
    "3.3.9": "forms.html",
    # 4.1 – Compatible
    "4.1.1": "parsing.html",
    "4.1.2": "forms.html",
    "4.1.3": "forms.html",
}


def _tt_sc_url(sc_num: str) -> str:
    """Return the full TrustedTester URL for a WCAG SC number (e.g. '1.4.2').

    Falls back to appendixa.html for any SC not present in TT_SC_PAGE.

    Note: Mermaid diagram TT nodes represent all test steps for an SC at once,
    so only SC-level URLs are needed here.  Step-level overrides (e.g. 1.3.1.B
    → tables.html) are handled by ttStepUrl() in assets/js/app.js for the
    Cards and Table views.
    """
    return TT_BASE_URL + TT_SC_PAGE.get(sc_num, "appendixa.html")

# npm registry endpoint to resolve the latest published axe-core version
AXE_NPM_DIST_TAGS_URL = "https://registry.npmjs.org/-/package/axe-core/dist-tags"

# Fallback axe-core version used when the npm registry is unreachable
AXE_VERSION_FALLBACK = "4.11"

# npm registry endpoint to resolve the latest published Alfa version
ALFA_NPM_DIST_TAGS_URL = (
    "https://registry.npmjs.org/-/package/@siteimprove/alfa-rules/dist-tags"
)

# ---------------------------------------------------------------------------
# ARRM URL mappings
# ---------------------------------------------------------------------------
ARRM_BASE_URL = "https://www.w3.org/WAI/planning/arrm"

# Maps the task ID prefix (e.g. "IMG") to the anchor on the ARRM tasks page.
# Headings come from https://www.w3.org/WAI/planning/arrm/tasks/
ARRM_TASK_CATEGORY_URLS: dict[str, str] = {
    "IMG": f"{ARRM_BASE_URL}/tasks/#images-and-graphs",
    "SEM": f"{ARRM_BASE_URL}/tasks/#semantic-structure",
    "INP": f"{ARRM_BASE_URL}/tasks/#input-modalities",
    "FRM": f"{ARRM_BASE_URL}/tasks/#form-interactions",
    "CSS": f"{ARRM_BASE_URL}/tasks/#css-and-presentation",
    "NAV": f"{ARRM_BASE_URL}/tasks/#navigation",
    "TAB": f"{ARRM_BASE_URL}/tasks/#data-tables",
    "ANM": f"{ARRM_BASE_URL}/tasks/#animation-and-movement",
    "SCT": f"{ARRM_BASE_URL}/tasks/#static-content",
    "DYN": f"{ARRM_BASE_URL}/tasks/#dynamic-interactions",
}

# Maps the Primary Ownership role name to the ARRM role-specific page.
ARRM_ROLE_URLS: dict[str, str] = {
    "Content Authoring":          f"{ARRM_BASE_URL}/content-author/",
    "Front-End Development":      f"{ARRM_BASE_URL}/front-end/",
    "User Experience (UX) Design": f"{ARRM_BASE_URL}/user-experience/",
    "Visual Design":              f"{ARRM_BASE_URL}/visual-designer/",
}

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
SEED_FILE = DATA_DIR / "master_spine.json"
OUTPUT_FILE = DATA_DIR / "master_spine.json"

# Ordered list of the tool engines tracked in ``act_implementations``.  Used
# as the canonical key order for all per-engine dicts in this module.
IMPL_ENGINES: tuple[str, ...] = ("axe", "alfa", "equal_access", "qualweb")


def _empty_impl() -> dict:
    """Return a fresh empty implementation dict for one ACT rule.

    The ``consistency`` key holds a mapping of individual engine rule IDs to
    their best-known ACT consistency level (``"consistent"``, ``"partial"``,
    or ``"incorrect"``).  It is distinct from the per-engine list keys so that
    callers can still iterate ``IMPL_ENGINES`` for rule-ID lists without
    special-casing this key.
    """
    d: dict = {engine: [] for engine in IMPL_ENGINES}
    d["consistency"] = {}
    return d


# Canonical ranking for ACT consistency levels — higher is better.
_CONSISTENCY_RANK: dict[str, int] = {
    "consistent": 2,
    "partial":    1,
    "incorrect":  0,
}


def _consistency_rank(level: str) -> int:
    """Return a numeric rank for a consistency level string (higher = better).

    Unknown levels (empty string, ``"not-checked"``, etc.) return ``-1`` so
    that any known level will replace them during a best-wins merge.
    """
    return _CONSISTENCY_RANK.get(level.lower() if level else "", -1)


def _earl_outcome_to_consistency(outcome_val: object) -> str:
    """Convert an EARL outcome value to a consistency level string.

    EARL implementation reports use:
      * ``earl:passed``   → ``"consistent"``
      * ``earl:failed``   → ``"incorrect"``
      * ``earl:cantTell`` → ``"partial"``

    The value may arrive as a plain string or a JSON-LD ``{"@id": "..."}``
    dict.  Returns an empty string when the outcome cannot be mapped.
    """
    if isinstance(outcome_val, dict):
        raw = outcome_val.get("@id") or outcome_val.get("id") or ""
    else:
        raw = str(outcome_val) if outcome_val else ""
    raw = raw.lower()
    if "passed" in raw:
        return "consistent"
    if "canttell" in raw or "cant_tell" in raw:
        return "partial"
    if "failed" in raw:
        return "incorrect"
    return ""


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def fetch_text(url: str, timeout: int = 30) -> str | None:
    """Fetch URL content as text; return None on failure."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "wcag-spine-sync/1.0 (https://github.com/mgifford/wcag-spine)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
        print(f"  WARNING: Could not fetch {url}: {exc}", file=sys.stderr)
        return None


def fetch_axe_version() -> str:
    """
    Return the latest published axe-core major.minor version string (e.g. "4.10").

    Resolves the version from the npm registry dist-tags endpoint.  If the
    registry is unreachable the hard-coded ``AXE_VERSION_FALLBACK`` is used so
    that the sync can still complete offline.
    """
    raw = fetch_text(AXE_NPM_DIST_TAGS_URL)
    if raw is not None:
        try:
            tags = json.loads(raw)
            full_version = tags.get("latest", "")
            # Keep only major.minor (e.g. "4.10.2" → "4.10")
            parts = full_version.split(".")
            if len(parts) >= 2:
                return f"{parts[0]}.{parts[1]}"
            print(
                f"  WARNING: Unexpected axe-core version format '{full_version}'; "
                f"using fallback {AXE_VERSION_FALLBACK}",
                file=sys.stderr,
            )
        except (json.JSONDecodeError, AttributeError) as exc:
            print(f"  WARNING: Could not parse axe-core version: {exc}", file=sys.stderr)
    print(f"  WARNING: Using axe-core fallback version {AXE_VERSION_FALLBACK}", file=sys.stderr)
    return AXE_VERSION_FALLBACK


def fetch_alfa_version() -> str | None:
    """
    Return the latest published @siteimprove/alfa-rules full version string
    (e.g. "0.112.0"), or None when the npm registry is unreachable.
    """
    raw = fetch_text(ALFA_NPM_DIST_TAGS_URL)
    if raw is not None:
        try:
            tags = json.loads(raw)
            version = tags.get("latest", "")
            if version:
                return version
        except (json.JSONDecodeError, AttributeError) as exc:
            print(f"  WARNING: Could not parse Alfa version: {exc}", file=sys.stderr)
    print("  WARNING: Could not determine Alfa version from npm.", file=sys.stderr)
    return None


def normalise_sc(raw: str) -> str | None:
    """Return a canonical 'X.Y.Z' SC number or None if unparseable."""
    # Accept forms like 1.1.1, SC 1.1.1, success-criterion-1-1-1
    match = re.search(r"(\d+)[\.\-](\d+)[\.\-](\d+)", raw)
    if match:
        return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
    return None


def fetch_tt_steps() -> dict[str, list[str]]:
    """
    Scrape Trusted Tester v5 test identifiers and titles from the HTML pages.
    Returns mapping of SC -> ["Test ID: Title", ...].
    """
    sc_to_steps: dict[str, list[str]] = {}
    base_url = "https://section508coordinators.github.io/TrustedTester/"
    
    # We only fetch each unique page once
    unique_pages = sorted(set(TT_SC_PAGE.values()))
    page_to_content: dict[str, str] = {}
    
    print(f"  → Scraping {len(unique_pages)} Trusted Tester pages …")
    for page in unique_pages:
        url = base_url + page
        content = fetch_text(url)
        if content:
            page_to_content[page] = content

    for sc, page in TT_SC_PAGE.items():
        content = page_to_content.get(page)
        if not content:
            continue
            
        # Extract checks for this specific SC. 
        # Pattern in HTML: <td>1.1.1-some-slug</td> \s* <td>7.A</td>
        sc_pattern = sc.replace(".", r"\.")
        pattern = r'<td>(' + sc_pattern + r'-[a-zA-Z0-9\-]+)</td>\s*<td>([0-9A-Z\.]+)</td>'
        matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
        
        steps = []
        for m in matches:
            # Derive a clean title from the slug (e.g. "meaningful-image-name" -> "Meaningful Image Name")
            slug = m.group(1).replace(sc + "-", "").replace("-", " ").title()
            test_id = m.group(2)
            steps.append(f"{test_id} - {slug}")
        
        if steps:
            sc_to_steps[sc] = sorted(list(set(steps)))
            
    return sc_to_steps


def load_seed() -> dict:
    """Load the pre-seeded master_spine.json from disk."""
    with SEED_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def fetch_fpc_map() -> dict[str, list[str]]:
    """Fetch the Section 508 Functional Performance Criteria (FPC) CSV and parse it.

    Returns a dict mapping each WCAG 2.0 SC number to the list of FPC codes that
    apply to it, e.g. ``{"1.1.1": ["WV", "LV", "WH", "LH", "LLCLA"], ...}``.

    The source CSV (CivicActions accessibility-data-reference) covers WCAG 2.0 SCs
    only; WCAG 2.1 / 2.2 additions are not present and will receive an empty list.
    SCs that appear in the CSV but have no FPC codes checked (e.g. 2.3.1) are also
    stored with an empty list so the field is consistently present for every SC.

    Returns an empty dict on fetch/parse failure so the caller can fall back to
    the existing seed data gracefully.
    """
    raw = fetch_text(FPC_MAPPING_URL)
    if raw is None:
        print("  WARNING: FPC mapping unavailable; using seed fpc data", file=sys.stderr)
        return {}
    fpc_map: dict[str, list[str]] = {}
    try:
        reader = csv.DictReader(StringIO(raw))
        for row in reader:
            sc_raw = row.get("WCAG 2.0 SC", "").strip()
            sc_num = normalise_sc(sc_raw)
            if not sc_num:
                continue
            # Values in the CSV are the FPC code itself (e.g. "WV") when the SC
            # is affected, or an empty string when it is not.  We validate that
            # the cell value matches the expected code to avoid false positives.
            fpc_codes = [
                code
                for col, code in FPC_COLUMN_NAMES.items()
                if row.get(col, "").strip() == code
            ]
            fpc_map[sc_num] = fpc_codes
    except (csv.Error, KeyError) as exc:
        print(f"  WARNING: Could not parse FPC CSV: {exc}", file=sys.stderr)
        return {}
    return fpc_map


# ---------------------------------------------------------------------------
# ACT Rules
# ---------------------------------------------------------------------------

def _extract_rule_ids(items: object) -> list[str]:
    """Extract rule ID strings from a value that may be a list of strings or dicts.

    For dict entries the first non-empty string among the keys ``id``,
    ``ruleId``, and ``rule`` is used.  The ``or`` chain intentionally treats
    empty strings as "missing" — rule IDs should never be empty strings.
    """
    result: list[str] = []
    if not isinstance(items, list):
        return result
    for item in items:
        if isinstance(item, str) and item:
            result.append(item)
        elif isinstance(item, dict):
            rule_id = item.get("id") or item.get("ruleId") or item.get("rule") or ""
            if rule_id:
                result.append(rule_id)
    return result


def _extract_implementations(rule: dict) -> dict:
    """
    Extract per-engine implementation rule IDs from an ACT rule dict.

    Handles two known formats from W3C rules.json:
      1. ``implementations`` is a dict keyed by consistency level whose values
         are dicts keyed by tool name:
         ``{"consistent": {"axe-core": [...], "Alfa": [...]}, ...}``
      2. ``implementations`` is a flat list of dicts each with ``technology``
         (or ``tool``) and ``rule`` (or ``id`` / ``ruleId``) fields:
         ``[{"technology": "axe-core", "rule": "image-alt"}, ...]``

    Returns a dict with keys ``axe``, ``alfa``, ``equal_access``, ``qualweb``
    mapping to sorted, deduplicated lists of rule ID strings, plus a
    ``consistency`` key that maps each engine rule ID to its best-known ACT
    consistency level (``"consistent"``, ``"partial"``, or ``"incorrect"``).
    """
    axe_rules: list[str] = []
    alfa_rules: list[str] = []
    equal_access_rules: list[str] = []
    qualweb_rules: list[str] = []
    consistency_map: dict[str, str] = {}

    def _record(rule_id: str, level: str) -> None:
        """Keep the best (highest-ranked) consistency level per rule ID."""
        if not rule_id or not level:
            return
        level_lo = str(level).lower()
        current = consistency_map.get(rule_id)
        if current is None or _consistency_rank(level_lo) > _consistency_rank(current):
            consistency_map[rule_id] = level_lo

    implementations = rule.get("implementations", {})

    if isinstance(implementations, dict):
        # Format 1: keyed by consistency level
        for level, tools in implementations.items():
            if not isinstance(tools, dict):
                continue
            for rid in _extract_rule_ids(tools.get("axe-core") or tools.get("axe") or []):
                axe_rules.append(rid)
                _record(rid, level)
            for rid in _extract_rule_ids(tools.get("Alfa") or tools.get("alfa") or []):
                alfa_rules.append(rid)
                _record(rid, level)
            for rid in _extract_rule_ids(
                tools.get("Equal Access") or tools.get("equal_access") or []
            ):
                equal_access_rules.append(rid)
                _record(rid, level)
            for rid in _extract_rule_ids(tools.get("QualWeb") or tools.get("qualweb") or []):
                qualweb_rules.append(rid)
                _record(rid, level)
    elif isinstance(implementations, list):
        # Format 2: flat list of tool entries
        for impl in implementations:
            if not isinstance(impl, dict):
                continue
            tech = (impl.get("technology") or impl.get("tool") or "").lower()
            # Empty strings treated as missing — rule IDs should never be empty.
            rule_id = (
                impl.get("rule") or impl.get("id") or impl.get("ruleId") or ""
            )
            if not rule_id:
                continue
            consistency = (impl.get("consistency") or "").lower()
            rule_id = str(rule_id)
            if "axe" in tech:
                axe_rules.append(rule_id)
                _record(rule_id, consistency)
            elif "alfa" in tech:
                alfa_rules.append(rule_id)
                _record(rule_id, consistency)
            elif "equal" in tech or "ibm" in tech:
                equal_access_rules.append(rule_id)
                _record(rule_id, consistency)
            elif "qualweb" in tech:
                qualweb_rules.append(rule_id)
                _record(rule_id, consistency)

    return {
        "axe": sorted(set(axe_rules)),
        "alfa": sorted(set(alfa_rules)),
        "equal_access": sorted(set(equal_access_rules)),
        "qualweb": sorted(set(qualweb_rules)),
        "consistency": consistency_map,
    }


def fetch_act_rules() -> tuple[dict[str, list[str]], dict[str, dict]]:
    """
    Download the W3C ACT rules mapping JSON and return:
      1. SC-to-ACT mapping: ``{ "X.Y.Z": ["rule_id", ...], ... }``
      2. ACT-rule-to-implementations mapping:
         ``{ "rule_id": {"axe": [...], "alfa": [...], "equal_access": [...], "qualweb": [...]}, ... }``

    Supports two JSON formats:

    **wcag-mapping.json** (current, hosted on GitHub):
    ``{"act-rules": [{"frontmatter": {"id": "...", "accessibility_requirements":
    {"wcag20:1.3.1": {...}, ...}}, ...}]}``

    SC numbers are extracted from ``accessibility_requirements`` keys with a
    ``wcag20:``, ``wcag21:``, or ``wcag22:`` prefix; both primary (``forConformance``)
    and secondary associations are included.

    **Legacy rules.json** (no longer available at the original W3C URL):
    list or ``{"rules": [...]}`` with ``id`` and ``successCriteria`` fields.

    The second dict is populated only when the source JSON includes
    ``implementations`` data for each rule; it will be empty otherwise.
    """
    sc_to_act: dict[str, list[str]] = {}
    act_implementations: dict[str, dict] = {}
    raw = fetch_text(ACT_RULES_URL)
    if raw is None:
        return sc_to_act, act_implementations
    try:
        rules = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"  WARNING: ACT rules JSON decode error: {exc}", file=sys.stderr)
        return sc_to_act, act_implementations

    if isinstance(rules, dict) and "act-rules" in rules:
        # wcag-mapping.json format: {"act-rules": [{...}, ...]}
        rule_list = rules["act-rules"]
        for rule in rule_list:
            # Skip deprecated rules — they are no longer active ACT rules.
            if rule.get("deprecated", False):
                continue
            fm = rule.get("frontmatter", {})
            rule_id = fm.get("id", "") or rule.get("id", "")
            # SC numbers live in accessibility_requirements keys like "wcag20:1.3.1".
            reqs = fm.get("accessibility_requirements") or {}
            for req_key in reqs:
                if req_key.startswith(("wcag20:", "wcag21:", "wcag22:")):
                    sc_raw = req_key.split(":", 1)[1]
                    sc = normalise_sc(sc_raw)
                    if sc and rule_id:
                        sc_to_act.setdefault(sc, [])
                        if rule_id not in sc_to_act[sc]:
                            sc_to_act[sc].append(rule_id)
            if rule_id:
                impl = _extract_implementations(rule)
                if any(impl.values()):
                    act_implementations[rule_id] = impl
    else:
        # Legacy rules.json format: list or {"rules": [...]}
        rule_list = rules if isinstance(rules, list) else rules.get("rules", [])
        for rule in rule_list:
            rule_id = rule.get("id", "")
            sc_nums = rule.get("successCriteria", []) or rule.get("sc", []) or []
            for sc_raw in sc_nums:
                sc = normalise_sc(str(sc_raw))
                if sc:
                    sc_to_act.setdefault(sc, [])
                    if rule_id and rule_id not in sc_to_act[sc]:
                        sc_to_act[sc].append(rule_id)
            if rule_id:
                impl = _extract_implementations(rule)
                if any(impl.values()):
                    act_implementations[rule_id] = impl

    return sc_to_act, act_implementations


# ---------------------------------------------------------------------------
# EARL Implementation Report (Alfa)
# ---------------------------------------------------------------------------

def _extract_act_id_from_url(url_or_id: str) -> str | None:
    """Extract a 6-character ACT rule ID from a URL or plain ID string.

    Handles URLs like:
      https://act-rules.github.io/rules/09o5cg
      https://www.w3.org/WAI/standards-guidelines/act/rules/09o5cg/
    as well as plain 6-character IDs (e.g. ``"09o5cg"``).
    """
    match = re.search(r"/rules/([a-z0-9]{6})(?:/|$)", url_or_id)
    if match:
        return match.group(1)
    if re.fullmatch(r"[a-z0-9]{6}", url_or_id):
        return url_or_id
    return None


def _extract_alfa_id_from_url(url_or_id: str) -> str | None:
    """Extract an Alfa rule ID (``SIA-RXX``) from a URL or plain ID string.

    Handles URLs like:
      https://alfa.siteimprove.com/rules/sia-r66
    as well as plain IDs in ``SIA-RXX`` form (case-insensitive on input,
    upper-case on output).
    """
    match = re.search(r"/rules/(sia-r\d+)", url_or_id, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    if re.match(r"^SIA-R\d+$", url_or_id, re.IGNORECASE):
        return url_or_id.upper()
    return None


def _parse_earl_assertions(data: object) -> list[dict]:
    """Return a flat list of assertion dicts from various EARL JSON structures.

    Handles:
      * A JSON-LD ``@graph`` array at the top level (or nested under a key).
      * A plain list of assertion dicts.
      * A dict with an ``"assertions"`` key.

    An empty list under any key is treated the same as a missing key (falsy
    ``or`` chain).  For EARL implementation reports an empty ``@graph`` means
    no assertions, so this fall-through behaviour is intentional.
    """
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    # Use or-chaining: empty lists (no assertions) are equivalent to missing keys.
    return (
        data.get("@graph")
        or data.get("assertions")
        or data.get("results")
        or []
    )


def fetch_earl_alfa_mappings(
    sc_to_act: dict[str, list[str]],
) -> tuple[dict[str, list[str]], dict[str, dict]]:
    """Fetch the Alfa ACT-R EARL implementation report and extract mappings.

    Uses ``sc_to_act`` (from :func:`fetch_act_rules`) to resolve the WCAG SCs
    for each ACT rule found in the report, then returns:

    1. ``sc_to_alfa`` — ``{"X.Y.Z": ["SIA-R66", ...]}``
       Alfa rules keyed by WCAG SC number, derived from the EARL assertions.
    2. ``act_impl_updates`` — ``{"09o5cg": {"alfa": ["SIA-R66"]}}``
       Updates to merge into ``meta.act_implementations`` so the ACT Rules
       view can show which Alfa rule backs each ACT rule.

    The function processes *all* consistency levels (consistent, partial, etc.)
    so that semi-automated implementations are included alongside full ones.
    Network or parse failures are handled gracefully: both dicts are empty.
    """
    sc_to_alfa: dict[str, list[str]] = {}
    act_impl_updates: dict[str, dict] = {}

    # Build a reverse map: ACT rule ID → list of SC numbers.
    act_to_scs: dict[str, list[str]] = {}
    for sc, rule_ids in sc_to_act.items():
        for rid in rule_ids:
            act_to_scs.setdefault(rid, []).append(sc)

    raw = fetch_text(ALFA_ACT_EARL_URL)
    if raw is None:
        return sc_to_alfa, act_impl_updates

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"  WARNING: Alfa EARL report JSON decode error: {exc}", file=sys.stderr)
        return sc_to_alfa, act_impl_updates

    assertions = _parse_earl_assertions(data)
    processed = 0
    for assertion in assertions:
        if not isinstance(assertion, dict):
            continue

        # --- Extract the ACT rule ID from the "test" field ---
        test_val = (
            assertion.get("earl:test")
            or assertion.get("test")
            or {}
        )
        if isinstance(test_val, str):
            act_id = _extract_act_id_from_url(test_val)
        elif isinstance(test_val, dict):
            raw_id = (
                test_val.get("@id")
                or test_val.get("id")
                or test_val.get("url")
                or ""
            )
            act_id = _extract_act_id_from_url(str(raw_id))
        else:
            continue

        if not act_id:
            continue

        # --- Extract the Alfa rule ID from the "subject" field ---
        subj_val = (
            assertion.get("earl:subject")
            or assertion.get("subject")
            or {}
        )
        if isinstance(subj_val, str):
            alfa_id = _extract_alfa_id_from_url(subj_val)
        elif isinstance(subj_val, dict):
            raw_id = (
                subj_val.get("@id")
                or subj_val.get("id")
                or subj_val.get("url")
                or ""
            )
            alfa_id = _extract_alfa_id_from_url(str(raw_id))
            if not alfa_id:
                title = (
                    subj_val.get("dct:title")
                    or subj_val.get("title")
                    or ""
                )
                alfa_id = _extract_alfa_id_from_url(str(title))
        else:
            continue

        if not alfa_id:
            continue

        # --- Extract consistency from the EARL result outcome ---
        result_val = (
            assertion.get("earl:result")
            or assertion.get("result")
            or {}
        )
        if isinstance(result_val, dict):
            outcome_val = result_val.get("earl:outcome") or result_val.get("outcome") or ""
        else:
            outcome_val = str(result_val)
        consistency = _earl_outcome_to_consistency(outcome_val)

        # --- Map Alfa rule to each WCAG SC covered by this ACT rule ---
        scs_for_act = act_to_scs.get(act_id, [])
        for sc in scs_for_act:
            lst = sc_to_alfa.setdefault(sc, [])
            if alfa_id not in lst:
                lst.append(alfa_id)

        # --- Record the Alfa rule and its consistency in act_impl_updates ---
        entry = act_impl_updates.setdefault(act_id, _empty_impl())
        if alfa_id not in entry["alfa"]:
            entry["alfa"].append(alfa_id)
        if consistency:
            old = entry["consistency"].get(alfa_id, "")
            if not old or _consistency_rank(consistency) > _consistency_rank(old):
                entry["consistency"][alfa_id] = consistency

        processed += 1

    print(f"  → Processed {processed} EARL assertions from Alfa report")
    return sc_to_alfa, act_impl_updates


def fetch_act_testcases_sc_map() -> dict[str, list[str]]:
    """
    Download the W3C ACT testcases JSON and build a supplemental SC-to-ACT mapping.

    The testcases.json is richer than rules.json for secondary-SC coverage: a rule
    like ``09o5cg`` ("Text has minimum contrast") has test cases tagged for both
    1.4.3 and 1.4.6, so fetching testcases gives us those secondary associations
    that rules.json may omit.

    Returns ``{ "X.Y.Z": ["rule_id", ...], ... }`` — same shape as ``fetch_act_rules()``.
    """
    sc_to_act: dict[str, list[str]] = {}
    raw = fetch_text(ACT_TESTCASES_URL)
    if raw is None:
        return sc_to_act
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"  WARNING: ACT testcases JSON decode error: {exc}", file=sys.stderr)
        return sc_to_act

    # The testcases.json is a list of test-case objects.  Each has at least
    # "ruleId" (string) and "successCriteria" (list of strings like "1.4.3").
    testcases = data if isinstance(data, list) else data.get("testcases", [])
    for tc in testcases:
        if not isinstance(tc, dict):
            continue
        rule_id = (tc.get("ruleId") or tc.get("rule_id") or tc.get("rule") or "").strip()
        if not rule_id:
            continue
        # successCriteria may be a list of strings like ["1.4.3"] or ["1.4.3", "1.4.6"]
        sc_list = tc.get("successCriteria") or tc.get("sc") or []
        if isinstance(sc_list, str):
            sc_list = [sc_list]
        for sc_raw in sc_list:
            sc = normalise_sc(str(sc_raw))
            if sc:
                sc_to_act.setdefault(sc, [])
                if rule_id not in sc_to_act[sc]:
                    sc_to_act[sc].append(rule_id)

    total = sum(len(v) for v in sc_to_act.values())
    print(f"  → ACT testcases: {total} rule/SC pairs from testcases.json")
    return sc_to_act


def fetch_alfa_sc_map() -> dict[str, list[str]]:
    """
    Fetch Alfa rule→WCAG SC mappings from the Alfa rules TypeScript index.

    The Alfa source file exports every rule with ``Criterion.of("X.Y.Z")`` calls
    inside each rule's ``requirements`` array.  A simple regex extracts both the
    rule IDs (``"SIA-RNNN"``) and the criteria they reference.

    Returns ``{ "X.Y.Z": ["SIA-RNNN", ...], ... }``.
    """
    sc_to_alfa: dict[str, list[str]] = {}
    raw = fetch_text(ALFA_RULES_INDEX_URL)
    if raw is None:
        return sc_to_alfa

    # Match rule blocks: export { default as SIA_R66 } from "./rules/sia-r66"; followed
    # by the rule definition containing Criterion.of("1.4.6").
    # Strategy: split by rule identifier lines and parse each chunk.
    #
    # The Alfa index TypeScript lists re-exports like:
    #   export { default as SIA_R66 } from "./rules/sia-r66";
    # We collect rule IDs from these lines and then scan the file for
    # Criterion references near each rule to build the map.
    #
    # Simpler regex approach: find every occurrence of
    #   SIA-Rnn ... Criterion.of("X.Y.Z")   (within reason)
    # by scanning for blocks that contain both.

    # Pattern 1: in-line export with criterion, e.g. from generated metadata files.
    # Pattern 2: parse the TypeScript source which lists rules as re-exports and
    # individual rule files that contain Criterion.of("X.Y.Z").
    #
    # Since the index file is a re-export only, we parse it to get rule IDs, then
    # attempt to fetch each rule file.  However, to avoid ~130 HTTP requests we
    # use a bulk regex over the entire index for any embedded criterion references.

    # Build the list of Alfa rule IDs from export lines.
    # Lines look like: export { default as SIA_R3 } from "./rules/sia-r3";
    rule_id_re = re.compile(r'\bSIA[_-]R(\d+)\b', re.IGNORECASE)
    alfa_ids = sorted(set(
        f"SIA-R{m.group(1)}" for m in rule_id_re.finditer(raw)
    ), key=lambda x: int(x.split("-R", 1)[1]) if "-R" in x else 0)

    # If the index already embeds Criterion.of("X.Y.Z") mappings, extract them.
    # Build a coarse mapping: for each criterion found adjacent to each rule mention.
    # This works when the rule source is inlined or concatenated into the index.
    crit_re = re.compile(r'Criterion\.of\(["\'](\d+\.\d+\.\d+)["\']', re.IGNORECASE)
    sc_mentions = [m.group(1) for m in crit_re.finditer(raw)]
    if sc_mentions:
        # There are inlined criteria; pair them with the nearest preceding rule ID.
        for m_crit in crit_re.finditer(raw):
            sc = m_crit.group(1)
            pos = m_crit.start()
            # Find the closest SIA-Rnn mention before this position (within 4 KB).
            window = raw[max(0, pos - 4096):pos]
            matches = list(rule_id_re.finditer(window))
            if matches:
                rid = f"SIA-R{matches[-1].group(1)}"
                sc_to_alfa.setdefault(sc, [])
                if rid not in sc_to_alfa[sc]:
                    sc_to_alfa[sc].append(rid)

    if sc_to_alfa:
        total = sum(len(v) for v in sc_to_alfa.values())
        print(f"  → Alfa index: {total} rule/SC pairs from inline criteria")
        return sc_to_alfa

    # Fallback: the index is a thin re-export file without inlined criteria.
    # Fetch individual rule files; limit to a batch to avoid excess HTTP calls.
    # Rule files are at: .../packages/alfa-rules/src/rules/sia-rNNN.ts
    base_rule_url = ALFA_RULES_INDEX_URL.rsplit("/", 1)[0] + "/rules/"
    fetched = 0
    for rid in alfa_ids:
        rule_file_url = base_rule_url + rid.lower() + ".ts"
        rule_src = fetch_text(rule_file_url)
        if rule_src is None:
            continue
        fetched += 1
        for m_crit in crit_re.finditer(rule_src):
            sc = m_crit.group(1)
            sc_to_alfa.setdefault(sc, [])
            if rid not in sc_to_alfa[sc]:
                sc_to_alfa[sc].append(rid)

    total = sum(len(v) for v in sc_to_alfa.values())
    print(f"  → Alfa rules: {total} rule/SC pairs from {fetched} individual rule files")
    return sc_to_alfa


def _parse_axe_rule_tags(tags: list) -> list[str]:
    """
    Convert axe-core rule ``tags`` to a list of canonical WCAG SC numbers.

    axe tags use the form ``"wcag143"`` for 1.4.3, ``"wcag1411"`` for 1.4.11,
    or ``"wcag2a"`` / ``"wcag21aa"`` (level tags, which are ignored).

    Format: ``wcag`` + [principle 1-4] + [guideline 1-5] + [SC number 1-99+]
    """
    sc_list: list[str] = []
    for tag in tags:
        tag_str = str(tag)
        # SC-specific tags: wcag + single principle digit + single guideline digit
        # + one-or-more digits for the SC number (e.g. wcag143 → 1.4.3,
        # wcag1411 → 1.4.11, wcag2410 → 2.4.10).
        # Level tags like "wcag2a", "wcag21aa" do NOT end with \d+ so are excluded.
        # Using [1-4] for principle and \d for guideline (single digit, future-proof
        # beyond guideline 5 while still capturing only meaningful single-digit guidelines).
        m = re.fullmatch(r'wcag([1-4])(\d)(\d+)', tag_str, re.IGNORECASE)
        if m:
            sc_list.append(f"{m.group(1)}.{m.group(2)}.{m.group(3)}")
    return sc_list


def fetch_axe_sc_map() -> dict[str, list[str]]:
    """
    Fetch axe-core rule→WCAG SC mappings from the axe-core GitHub source.

    Strategy
    --------
    1. Fetch the GitHub API directory listing for ``lib/rules``.
    2. For each ``*.json`` rule file, fetch its content and read the ``tags`` array.
    3. Convert tags like ``"wcag143"`` → ``"1.4.3"`` and build the SC→rule map.

    Falls back to regex-parsing the compiled ``axe.js`` when the API listing is
    unavailable (e.g. rate-limited).

    Returns ``{ "X.Y.Z": ["rule-id", ...], ... }``.
    """
    sc_to_axe: dict[str, list[str]] = {}

    # --- Strategy 1: GitHub API listing + individual rule JSON files ---
    listing_raw = fetch_text(AXE_RULES_API_URL)
    if listing_raw is not None:
        try:
            listing = json.loads(listing_raw)
        except json.JSONDecodeError:
            listing = []

        if isinstance(listing, list):
            rule_files = [
                entry for entry in listing
                if isinstance(entry, dict)
                and entry.get("name", "").endswith(".json")
                and entry.get("type") == "file"
            ]
            fetched = 0
            for rf in rule_files:
                raw_url = rf.get("download_url", "")
                if not raw_url:
                    continue
                rule_raw = fetch_text(raw_url)
                if rule_raw is None:
                    continue
                try:
                    rule_obj = json.loads(rule_raw)
                except json.JSONDecodeError:
                    continue
                # Rule ID is the file name without extension, or the "id" field.
                rule_id = (
                    rule_obj.get("id")
                    or rf.get("name", "").removesuffix(".json")
                )
                if not rule_id:
                    continue
                tags = rule_obj.get("tags", [])
                for sc in _parse_axe_rule_tags(tags):
                    sc_to_axe.setdefault(sc, [])
                    if rule_id not in sc_to_axe[sc]:
                        sc_to_axe[sc].append(rule_id)
                fetched += 1

            if sc_to_axe:
                total = sum(len(v) for v in sc_to_axe.values())
                print(f"  → axe-core: {total} rule/SC pairs from {fetched} rule JSON files")
                return sc_to_axe

    # --- Strategy 2: Regex over compiled axe.js ---
    print("  → axe-core: falling back to axe.js regex parsing", file=sys.stderr)
    axe_js = fetch_text(AXE_CORE_JS_URL)
    if axe_js is None:
        print("  WARNING: Could not fetch axe.js for rule metadata", file=sys.stderr)
        return sc_to_axe

    # Match rule-metadata blocks: id:"some-rule", ... tags:["wcag2a","wcag143",...]
    # This is a heuristic over minified/bundled JS.
    block_re = re.compile(
        r'"id"\s*:\s*"([^"]+)"[^}]{0,500}?"tags"\s*:\s*\[([^\]]+)\]',
        re.DOTALL,
    )
    tag_str_re = re.compile(r'"(wcag\d[^"]*)"', re.IGNORECASE)
    for m in block_re.finditer(axe_js):
        rule_id = m.group(1)
        tags_blob = m.group(2)
        tags = tag_str_re.findall(tags_blob)
        for sc in _parse_axe_rule_tags(tags):
            sc_to_axe.setdefault(sc, [])
            if rule_id not in sc_to_axe[sc]:
                sc_to_axe[sc].append(rule_id)

    total = sum(len(v) for v in sc_to_axe.values())
    print(f"  → axe-core: {total} rule/SC pairs from axe.js (regex fallback)")
    return sc_to_axe


# ---------------------------------------------------------------------------
# W3C ARRM
# ---------------------------------------------------------------------------

def fetch_arrm_roles() -> dict[str, list[str]]:
    """
    Download arrm-wcag-sc.csv and return:
      { "X.Y.Z": ["Role A", "Role B"], ... }
    """
    sc_to_roles: dict[str, list[str]] = {}
    raw = fetch_text(ARRM_WCAG_SC_URL)
    if raw is None:
        return sc_to_roles
    reader = csv.DictReader(StringIO(raw))
    for row in reader:
        # Common column names for the SC number
        sc_raw = (
            row.get("sc_num")
            or row.get("scNum")
            or row.get("sc-num")
            or row.get("sc")
            or row.get("successCriterion")
            or ""
        )
        sc = normalise_sc(sc_raw)
        if not sc:
            continue
        role = (
            row.get("role")
            or row.get("Role")
            or row.get("responsibility")
            or ""
        ).strip()
        if role:
            sc_to_roles.setdefault(sc, [])
            if role not in sc_to_roles[sc]:
                sc_to_roles[sc].append(role)
    return sc_to_roles


def fetch_arrm_tasks() -> dict[str, list[dict]]:
    """
    Download arrm-all-tasks.csv and return a mapping of SC number to a list of
    structured task objects:
      {
        "X.Y.Z": [
          {
            "id":                  "IMG-001",
            "task":                "Informative alternate text …",
            "primary_ownership":   "Content Authoring",
            "secondary_ownership": "User Experience (UX) Design",
            "category_url":        "https://…/tasks/#images-and-graphs",
            "role_url":            "https://…/content-author/"
          },
          ...
        ],
        ...
      }
    """
    sc_to_tasks: dict[str, list[dict]] = {}
    raw = fetch_text(ARRM_ALL_TASKS_URL)
    if raw is None:
        return sc_to_tasks
    reader = csv.DictReader(StringIO(raw))
    for row in reader:
        sc_raw = (
            row.get("WCAG SC")
            or row.get("sc_num")
            or row.get("scNum")
            or row.get("sc-num")
            or row.get("sc")
            or row.get("successCriterion")
            or ""
        )
        sc = normalise_sc(sc_raw)
        if not sc:
            continue

        task_id = (row.get("ID") or "").strip()
        task_desc = (row.get("Task") or row.get("task") or row.get("description") or "").strip()
        if not task_id or not task_desc:
            continue

        primary = (row.get("Primary Ownership") or row.get("primary_ownership") or "").strip()
        secondary = (row.get("Secondary Ownership") or row.get("secondary_ownership") or "").strip()
        if secondary.lower() == "none":
            secondary = ""

        # Derive URLs from the prefix (e.g. "IMG" from "IMG-001")
        prefix = task_id.split("-")[0] if "-" in task_id else ""
        category_url = ARRM_TASK_CATEGORY_URLS.get(prefix, f"{ARRM_BASE_URL}/tasks/")
        role_url = ARRM_ROLE_URLS.get(primary, "")

        task_obj = {
            "id":                  task_id,
            "task":                task_desc,
            "primary_ownership":   primary,
            "secondary_ownership": secondary,
            "category_url":        category_url,
            "role_url":            role_url,
        }

        existing_ids = {t["id"] for t in sc_to_tasks.get(sc, [])}
        if task_id not in existing_ids:
            sc_to_tasks.setdefault(sc, []).append(task_obj)

    return sc_to_tasks


# ---------------------------------------------------------------------------
# Merge logic
# ---------------------------------------------------------------------------

def merge_into_spine(
    spine: dict,
    act_map: dict,
    roles_map: dict,
    tasks_map: dict,
    act_implementations: dict | None = None,
    axe_map: dict | None = None,
    alfa_map: dict | None = None,
    fpc_map: dict | None = None,
    tt_map: dict | None = None,
) -> None:
    """Merge fetched data into the in-memory spine (mutates in place).

    Parameters
    ----------
    spine:               The in-memory spine (loaded from master_spine.json).
    act_map:             SC → list of ACT rule IDs.
    roles_map:           SC → list of ARRM role names.
    tasks_map:           SC → list of ARRM task dicts.
    act_implementations: ACT rule ID → engine implementation dict (freshly fetched).
    axe_map:             SC → list of axe-core rule IDs (directly fetched).
    alfa_map:            SC → list of Alfa rule IDs (directly fetched).
    fpc_map:             SC → list of Section 508 FPC codes (e.g. ["WV", "LV"]).
    tt_map:              SC → list of Trusted Tester step strings (e.g. ["7.A - Image Name"]).

    Automation propagation
    ----------------------
    After merging per-SC ACT, axe, and Alfa rule IDs, the function also
    *derives* additional axe/Alfa rules from the combined implementation data
    (seed data already stored in ``meta.act_implementations`` **plus** any
    freshly fetched ``act_implementations``).  For every ACT rule mapped to an
    SC the engine rules in that implementation entry are added to the SC's
    ``automation.axe`` / ``automation.alfa`` arrays.

    This means:
    * If ACT rule ``09o5cg`` maps to SC 1.4.6 (via the seed or a live fetch),
      and its implementation data shows Alfa uses ``SIA-R66``, then 1.4.6 also
      gets ``SIA-R66`` — without requiring a manual seed-data edit.
    * The propagation works even offline, because seed data in
      ``meta.act_implementations`` is always available as the baseline.
    """
    sc_dict = spine.get("success_criteria", {})

    # Build the combined implementation map: start from what is already stored
    # in the spine (seed + any prior syncs) and layer fresh data on top.
    # This ensures propagation works even when network fetches return nothing.
    combined_impl: dict[str, dict] = {}
    seed_impl = spine.get("meta", {}).get("act_implementations", {})
    for act_id, impl in seed_impl.items():
        # Copy engine-rule lists; copy the consistency dict separately so that
        # the generic `list(v)` loop doesn't corrupt the dict-valued key.
        combined_impl[act_id] = {k: list(v) for k, v in impl.items() if k != "consistency"}
        combined_impl[act_id]["consistency"] = dict(impl.get("consistency", {}))
    for act_id, impl in (act_implementations or {}).items():
        if act_id not in combined_impl:
            combined_impl[act_id] = {k: list(v) for k, v in impl.items() if k != "consistency"}
            combined_impl[act_id]["consistency"] = dict(impl.get("consistency", {}))
        else:
            for engine in ("axe", "alfa", "equal_access", "qualweb"):
                merged = list(dict.fromkeys(
                    combined_impl[act_id].get(engine, []) + impl.get(engine, [])
                ))
                combined_impl[act_id][engine] = merged
            # Merge consistency maps: keep the best (highest-ranked) level per rule ID.
            old_cons = combined_impl[act_id].setdefault("consistency", {})
            for rid, level in impl.get("consistency", {}).items():
                if rid not in old_cons or _consistency_rank(level) > _consistency_rank(old_cons[rid]):
                    old_cons[rid] = level

    for sc_num, entry in sc_dict.items():
        # --- ACT ---
        live_act = act_map.get(sc_num, [])
        if live_act:
            merged_act = sorted(set(entry["automation"]["act"]) | set(live_act))
            entry["automation"]["act"] = merged_act

        # --- axe-core (directly fetched) ---
        if axe_map:
            live_axe = axe_map.get(sc_num, [])
            if live_axe:
                merged_axe = sorted(set(entry["automation"]["axe"]) | set(live_axe))
                entry["automation"]["axe"] = merged_axe

        # --- Alfa (directly fetched) ---
        if alfa_map:
            live_alfa = alfa_map.get(sc_num, [])
            if live_alfa:
                merged_alfa = sorted(set(entry["automation"]["alfa"]) | set(live_alfa))
                entry["automation"]["alfa"] = merged_alfa

        # --- Propagate ACT implementation data to per-SC engine arrays ---
        # For every ACT rule that applies to this SC, add the engine rules
        # listed in combined_impl to the SC's axe / alfa arrays.
        if combined_impl:
            current_act = entry["automation"]["act"]
            derived_axe  = set(entry["automation"]["axe"])
            derived_alfa = set(entry["automation"]["alfa"])
            for act_id in current_act:
                impl = combined_impl.get(act_id, {})
                derived_axe.update(impl.get("axe", []))
                derived_alfa.update(impl.get("alfa", []))
            entry["automation"]["axe"]  = sorted(derived_axe)
            entry["automation"]["alfa"] = sorted(derived_alfa)

        # --- ARRM roles ---
        live_roles = roles_map.get(sc_num, [])
        if live_roles:
            merged_roles = list(dict.fromkeys(entry["manual"]["roles"] + live_roles))
            entry["manual"]["roles"] = merged_roles

        # --- ARRM structured tasks ---
        # Stored separately from tt_steps (Trusted Tester procedures).
        live_tasks = tasks_map.get(sc_num, [])
        if live_tasks:
            existing = entry["manual"].setdefault("arrm_tasks", [])
            existing_ids = {t["id"] for t in existing}
            for t in live_tasks:
                if t["id"] not in existing_ids:
                    existing.append(t)
                    existing_ids.add(t["id"])

        # --- Section 508 Functional Performance Criteria (FPC) ---
        # Only overwrite when fresh FPC data was fetched; fall back to seed.
        if fpc_map and sc_num in fpc_map:
            entry["fpc"] = fpc_map[sc_num]
        elif "fpc" not in entry:
            entry["fpc"] = []

        # --- Trusted Tester steps ---
        # Overwrite if we fetched live steps; otherwise keep seed/AI summary.
        if tt_map and sc_num in tt_map:
            entry["manual"]["tt_steps"] = tt_map[sc_num]
            # Flag that these steps are sourced from DHS
            entry["manual"]["tt_source"] = "DHS Trusted Tester v5"
        else:
            if "tt_source" not in entry["manual"]:
                entry["manual"]["tt_source"] = "Summarized by AI"

    # --- Store updated ACT implementation data in meta ---
    # Write back the combined (seed + fresh) implementation map so future syncs
    # can use accumulated data as their baseline.
    existing_meta_impl = spine.setdefault("meta", {}).setdefault("act_implementations", {})
    for act_id, impl in combined_impl.items():
        existing_meta_impl[act_id] = impl


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading seed data …")
    spine = load_seed()

    print("Fetching axe-core version …")
    axe_version = fetch_axe_version()
    print(f"  → axe-core version: {axe_version}")

    print("Fetching Alfa version …")
    alfa_version = fetch_alfa_version()
    print(f"  → Alfa version: {alfa_version or '(unavailable)'}")

    print("Fetching ACT rules (wcag-mapping.json) …")
    act_map, act_implementations = fetch_act_rules()
    print(f"  → {sum(len(v) for v in act_map.values())} ACT rule/SC mappings found")
    if act_implementations:
        print(f"  → Implementation data found for {len(act_implementations)} ACT rules")

    print("Fetching ACT rules (testcases.json — secondary SC coverage) …")
    act_testcases_map = fetch_act_testcases_sc_map()
    if act_testcases_map:
        # Merge testcases SC map into act_map (testcases may have secondary SCs).
        for sc, rule_ids in act_testcases_map.items():
            existing = act_map.setdefault(sc, [])
            for rid in rule_ids:
                if rid not in existing:
                    existing.append(rid)
        print(f"  → After merging testcases: {sum(len(v) for v in act_map.values())} total ACT rule/SC pairs")
    else:
        print("  → Testcases source unavailable; using rules.json only")

    print("Fetching Alfa rules (SC mapping) …")
    alfa_map = fetch_alfa_sc_map()
    if alfa_map:
        print(f"  → {sum(len(v) for v in alfa_map.values())} Alfa rule/SC pairs found")
    else:
        print("  → Alfa SC map unavailable; engine propagation will rely on ACT implementations")

    print("Fetching axe-core rules (SC mapping) …")
    axe_map = fetch_axe_sc_map()
    if axe_map:
        print(f"  → {sum(len(v) for v in axe_map.values())} axe-core rule/SC pairs found")
    else:
        print("  → axe-core SC map unavailable; engine propagation will rely on ACT implementations")

    print("Fetching ARRM roles …")
    roles_map = fetch_arrm_roles()
    print(f"  → {sum(len(v) for v in roles_map.values())} role/SC mappings found")

    print("Fetching ARRM tasks …")
    tasks_map = fetch_arrm_tasks()
    print(f"  → {sum(len(v) for v in tasks_map.values())} task/SC mappings found")

    print("Fetching Section 508 Functional Performance Criteria (FPC) mapping …")
    fpc_map = fetch_fpc_map()
    if fpc_map:
        print(f"  → {len(fpc_map)} SC/FPC mappings found")
    else:
        print("  → FPC mapping unavailable; using seed data")

    print("Fetching Trusted Tester v5 steps …")
    tt_map = fetch_tt_steps()
    if tt_map:
        print(f"  → {sum(len(v) for v in tt_map.values())} TT steps found across {len(tt_map)} SCs")
    else:
        print("  → Trusted Tester scrape unavailable; using seed data")

    print("Fetching Alfa EARL implementation report …")
    earl_alfa_map, earl_act_impl = fetch_earl_alfa_mappings(act_map)
    if earl_alfa_map:
        print(
            f"  → Alfa EARL: {sum(len(v) for v in earl_alfa_map.values())} "
            f"Alfa rule/SC mappings across {len(earl_alfa_map)} SCs"
        )
        # Merge EARL-derived Alfa rules into alfa_map so merge_into_spine picks them up.
        for sc, rule_ids in earl_alfa_map.items():
            existing = alfa_map.setdefault(sc, [])
            for rid in rule_ids:
                if rid not in existing:
                    existing.append(rid)
    # Merge EARL-derived ACT implementation updates so the propagation logic in
    # merge_into_spine can derive axe/alfa engine rules from combined_impl.
    for act_id, impl in earl_act_impl.items():
        if act_id not in act_implementations:
            act_implementations[act_id] = impl
        else:
            for engine in IMPL_ENGINES:
                merged = list(dict.fromkeys(
                    act_implementations[act_id].get(engine, [])
                    + impl.get(engine, [])
                ))
                act_implementations[act_id][engine] = merged

    print("Merging data …")
    merge_into_spine(
        spine,
        act_map,
        roles_map,
        tasks_map,
        act_implementations=act_implementations,
        axe_map=axe_map or {},
        alfa_map=alfa_map or {},
        fpc_map=fpc_map or {},
        tt_map=tt_map or {},
    )

    spine["meta"]["generated"] = date.today().isoformat()
    spine["meta"]["axe_version"] = axe_version
    if alfa_version:
        spine["meta"]["alfa_version"] = alfa_version
    spine["meta"].setdefault("sources", {})["trusted_tester"] = TT_IMPLEMENTATIONS_URL
    spine["meta"]["sources"]["section508_coordinators"] = "https://github.com/Section508Coordinators"
    spine["meta"]["sources"]["fpc_mapping"] = FPC_MAPPING_URL
    spine["meta"]["sources"]["act_rules"] = ACT_RULES_URL
    spine["meta"]["sources"]["act_testcases"] = ACT_TESTCASES_URL
    spine["meta"]["sources"]["alfa_rules_index"] = ALFA_RULES_INDEX_URL
    spine["meta"]["sources"]["alfa_earl"] = ALFA_ACT_EARL_URL
    spine["meta"]["sources"]["axe_rules_api"] = AXE_RULES_API_URL

    # Preserve data_quality metadata (AI-generated field declarations and the
    # manually-curated corrections log).  The sync never overwrites this block
    # — corrections added by humans remain intact across automated runs.
    spine["meta"].setdefault("data_quality", {
        "ai_generated_fields": [
            "manual.tt_steps",
            "manual.arrm_tasks",
            "manual.roles",
        ],
        "ai_generated_note": (
            "Manual testing procedures (Trusted Tester steps, ARRM tasks, and role "
            "assignments) were initially generated with AI assistance. This project is "
            "actively transitioning to live-synced data; check the 'source' attribute "
            "on individual components for verification."
        ),
        "upstream_sourced_fields": [
            "automation.act",
            "automation.axe",
            "automation.alfa",
        ],
        "upstream_sourced_note": (
            "Automation rule mappings (ACT, Axe-core, Alfa) are sourced directly from "
            "upstream repositories and are updated by the daily sync workflow."
        ),
        "known_corrections": [],
    })

    print(f"Writing {OUTPUT_FILE} …")
    with OUTPUT_FILE.open("w", encoding="utf-8") as fh:
        json.dump(spine, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    total_sc = len(spine.get("success_criteria", {}))
    print(f"Done — {total_sc} Success Criteria written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
