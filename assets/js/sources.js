/**
 * sources.js — Data Sources & Provenance page logic for WCAG Spine.
 *
 * Loads master_spine.json to populate:
 *  - Meta generation info (date, versions)
 *  - Live upstream source URLs from meta.sources
 *  - Known data corrections from meta.data_quality.known_corrections
 *  - An interconnection diagram (Mermaid) showing the data flow
 */

"use strict";

(async function initSources() {
  const loadingEl = document.getElementById("sources-loading");
  const contentEl = document.getElementById("sources-content");

  /** Safely set text content of an element by id. */
  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text || "—";
  }

  /** Escape HTML special characters. */
  function escHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // ---------------------------------------------------------------------------
  // Fetch spine data
  // ---------------------------------------------------------------------------
  let meta = {};
  try {
    const resp = await fetch("data/master_spine.json");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    meta = data.meta || {};
  } catch (err) {
    loadingEl.textContent = `Failed to load data: ${err.message}. Some sections may be unavailable.`;
    loadingEl.setAttribute("role", "alert");
    // Still show the static content
    if (contentEl) {
      loadingEl.hidden = true;
      contentEl.hidden = false;
    }
    return;
  }

  // ---------------------------------------------------------------------------
  // Populate meta info
  // ---------------------------------------------------------------------------
  setText("meta-generated", meta.generated);
  setText("meta-wcag", meta.wcag_version ? `WCAG ${meta.wcag_version}` : null);
  setText("meta-axe", meta.axe_version ? `axe-core ${meta.axe_version}` : null);
  setText("meta-alfa", meta.alfa_version ? `@siteimprove/alfa-rules ${meta.alfa_version}` : null);

  // ---------------------------------------------------------------------------
  // Render live upstream source URLs
  // ---------------------------------------------------------------------------
  const liveSourcesEl = document.getElementById("live-sources-content");
  if (liveSourcesEl && meta.sources) {
    const SOURCE_LABELS = {
      act_rules:             "ACT Rules — WCAG mapping (W3C GitHub)",
      arrm:                  "ARRM all tasks CSV (W3C WAI)",
      axe_core:              "Axe-core rule descriptions (Deque)",
      alfa:                  "Alfa rules README (Siteimprove)",
      trusted_tester:        "Trusted Tester v5 (Section508Coordinators)",
      section508_coordinators: "Section 508 Coordinators (GitHub org)",
      act_testcases:         "ACT testcases JSON (W3C)",
      alfa_rules_index:      "Alfa rules TypeScript index (Siteimprove)",
      axe_rules_api:         "Axe-core rules GitHub API",
      alfa_earl:             "Alfa EARL implementation report (alfa-act-r)",
      fpc_mapping:           "Section 508 FPC mapping (CivicActions)",
    };

    const rows = Object.entries(meta.sources).map(([key, url]) => {
      const label = SOURCE_LABELS[key] || key;
      return `<tr>
        <td><code>${escHtml(key)}</code></td>
        <td>${escHtml(label)}</td>
        <td class="source-url-cell"><a href="${escHtml(url)}" target="_blank" rel="noopener noreferrer">${escHtml(url)}</a></td>
      </tr>`;
    }).join("\n");

    liveSourcesEl.innerHTML = `
      <div class="table-wrapper" role="region" aria-label="Upstream source URLs" tabindex="0">
        <table class="sources-table">
          <caption>Upstream source URLs from the last data sync</caption>
          <thead>
            <tr>
              <th scope="col">Key</th>
              <th scope="col">Description</th>
              <th scope="col">URL</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
  } else if (liveSourcesEl) {
    liveSourcesEl.innerHTML = "<p>Source URL data not available.</p>";
  }

  // ---------------------------------------------------------------------------
  // Render known corrections
  // ---------------------------------------------------------------------------
  const correctionsEl = document.getElementById("corrections-content");
  if (correctionsEl) {
    const corrections = meta.data_quality && meta.data_quality.known_corrections;
    if (corrections && corrections.length > 0) {
      const rows = corrections.map(c => `<tr>
        <td><a href="index.html#checklist/${escHtml(c.sc)}">${escHtml(c.sc)}</a></td>
        <td><code>${escHtml(c.field)}</code></td>
        <td>${escHtml(c.correction)}</td>
        <td>${escHtml(c.reported_by || "—")}</td>
        <td>${escHtml(c.date || "—")}</td>
      </tr>`).join("\n");

      correctionsEl.innerHTML = `
        <div class="table-wrapper" role="region" aria-label="Known data corrections" tabindex="0">
          <table class="sources-table">
            <caption>Known corrections applied to master_spine.json data</caption>
            <thead>
              <tr>
                <th scope="col">SC</th>
                <th scope="col">Field</th>
                <th scope="col">Correction</th>
                <th scope="col">Reported by</th>
                <th scope="col">Date</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>`;
    } else {
      correctionsEl.innerHTML = "<p>No corrections have been logged yet.</p>";
    }
  }

  // ---------------------------------------------------------------------------
  // Render HTML interconnection data flow
  // ---------------------------------------------------------------------------
  const diagramEl = document.getElementById("sources-diagram");
  if (diagramEl) {
    diagramEl.innerHTML = `
      <div class="flow-container" aria-label="Data flow from upstream sources to dashboard">
        <div class="flow-step">
          <div class="flow-step-title">Upstream Sources</div>
          <div class="flow-step-items">
            <span class="badge badge-upstream">W3C ACT</span>
            <span class="badge badge-upstream">axe-core</span>
            <span class="badge badge-upstream">Alfa</span>
            <span class="badge badge-upstream">ARRM</span>
            <span class="badge badge-ai">Trusted Tester</span>
          </div>
        </div>
        <div class="flow-arrow">➡</div>
        <div class="flow-step">
          <div class="flow-step-title">Sync Pipeline</div>
          <div class="flow-step-items">
            <span class="badge badge-sync">sync_data.py</span>
          </div>
        </div>
        <div class="flow-arrow">➡</div>
        <div class="flow-step">
          <div class="flow-step-title">Central Data</div>
          <div class="flow-step-items">
            <span class="badge badge-data">master_spine.json</span>
          </div>
        </div>
        <div class="flow-arrow">➡</div>
        <div class="flow-step">
          <div class="flow-step-title">Dashboard Views</div>
          <div class="flow-step-items">
            <span class="badge badge-view">Cards</span>
            <span class="badge badge-view">Spine</span>
            <span class="badge badge-view">Table</span>
          </div>
        </div>
      </div>`;
  }

  // ---------------------------------------------------------------------------
  // Show content, hide loading
  // ---------------------------------------------------------------------------
  if (loadingEl) loadingEl.hidden = true;
  if (contentEl) contentEl.hidden = false;
})();
