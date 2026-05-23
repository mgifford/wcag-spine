# SBOM

This software bill of materials is a repository-scoped inventory generated from the manifests committed in this repository on 2026-05-23. It covers the first-party project metadata, CI runtimes and GitHub Actions pinned in `.github/workflows/sync_accessibility.yml`, Python tooling declared in `pyproject.toml` / `requirements.txt`, and the exact npm dependency tree locked in `package-lock.json`.

## Scope notes

- Exact versions are listed where the repository pins or locks them.
- Python development tooling is not lockfile-pinned in this repository; where needed, this file records both the declared constraint and the locally validated installed version.
- Licenses are taken from the repository `LICENSE` file, package metadata in `package-lock.json`, Python package metadata, or the upstream `LICENSE` file for each GitHub Action pinned in the workflow.

## First-party project metadata

| Component | Version / reference | License | Evidence / notes |
|---|---|---|---|
| Repository source (`wcag-spine`) | N/A | GNU AFFERO GENERAL PUBLIC LICENSE | Root `LICENSE` file in this repository |
| Python project metadata (`pyproject.toml`) | 0.1.0 | No package license declared in `pyproject.toml` | Project metadata for sync/validation tooling |
| npm package metadata (`package.json`) | 1.0.0 | ISC | `package.json` / root entry in `package-lock.json`; differs from the repository `LICENSE` file |

## Toolchains and CI runtimes

| Component | Version / reference | License | Evidence / notes |
|---|---|---|---|
| Python runtime | 3.12 | PSF | `.github/workflows/sync_accessibility.yml` uses `actions/setup-python@v5` with `python-version: "3.12"`; `pyproject.toml` requires `>=3.12` |
| Node.js runtime | 20 | Node.js license | `.github/workflows/sync_accessibility.yml` uses `actions/setup-node@v4` with `node-version: "20"` |
| npm CLI | Bundled with Node.js 20 | npm CLI license | Implicit via the Node.js runtime used for `npm ci` and audit commands |
| uv | Contributor-managed install | Apache-2.0 | Documented in `README.md` for local Python workflow; not pinned in repo manifests |

## GitHub Actions used by CI

| Component | Version / reference | License | Evidence / notes |
|---|---|---|---|
| `actions/checkout` | `v4` | MIT | Referenced in `.github/workflows/sync_accessibility.yml` |
| `actions/setup-python` | `v5` | MIT | Referenced in `.github/workflows/sync_accessibility.yml` |
| `stefanzweifel/git-auto-commit-action` | `v5` | MIT | Referenced in `.github/workflows/sync_accessibility.yml` |
| `actions/setup-node` | `v4` | MIT | Referenced in `.github/workflows/sync_accessibility.yml` |
| `actions/configure-pages` | `v5` | MIT | Referenced in `.github/workflows/sync_accessibility.yml` |
| `actions/upload-pages-artifact` | `v3` | MIT | Referenced in `.github/workflows/sync_accessibility.yml` |
| `actions/deploy-pages` | `v4` | MIT | Referenced in `.github/workflows/sync_accessibility.yml` |

## Python development dependencies

| Component | Declared version / constraint | Observed local version | License | Evidence / notes |
|---|---|---|---|---|
| `pytest` | `pytest>=8.0` | `9.0.3` | MIT | Declared in `requirements.txt` and `[dependency-groups].dev` in `pyproject.toml`; local package metadata exposes `License-Expression: MIT` |

## Node.js dependencies locked in `package-lock.json` (351 packages)

| Package | Exact version | License |
|---|---|---|
| `@axe-core/playwright` | `4.11.1` | MPL-2.0 |
| `@formatjs/ecma402-abstract` | `2.3.6` | MIT |
| `@formatjs/fast-memoize` | `2.2.7` | MIT |
| `@formatjs/icu-messageformat-parser` | `2.11.4` | MIT |
| `@formatjs/icu-skeleton-parser` | `1.8.16` | MIT |
| `@formatjs/intl-localematcher` | `0.6.2` | MIT |
| `@lhci/cli` | `0.15.1` | Apache-2.0 |
| `@lhci/utils` | `0.15.1` | Apache-2.0 |
| `@paulirish/trace_engine` | `0.0.53` | BSD-3-Clause |
| `@playwright/test` | `1.59.1` | Apache-2.0 |
| `@puppeteer/browsers` | `2.13.0` | Apache-2.0 |
| `@sentry-internal/tracing` | `7.120.4` | MIT |
| `@sentry/core` | `7.120.4` | MIT |
| `@sentry/integrations` | `7.120.4` | MIT |
| `@sentry/node` | `7.120.4` | MIT |
| `@sentry/types` | `7.120.4` | MIT |
| `@sentry/utils` | `7.120.4` | MIT |
| `@tootallnate/quickjs-emscripten` | `0.23.0` | MIT |
| `@types/node` | `25.6.0` | MIT |
| `@types/yauzl` | `2.10.3` | MIT |
| `accepts` | `1.3.8` | MIT |
| `agent-base` | `7.1.4` | MIT |
| `ansi-colors` | `4.1.3` | MIT |
| `ansi-escapes` | `3.2.0` | MIT |
| `ansi-regex` | `5.0.1` | MIT |
| `ansi-regex` | `4.1.1` | MIT |
| `ansi-regex` | `5.0.1` | MIT |
| `ansi-regex` | `5.0.1` | MIT |
| `ansi-regex` | `5.0.1` | MIT |
| `ansi-regex` | `3.0.1` | MIT |
| `ansi-regex` | `5.0.1` | MIT |
| `ansi-regex` | `5.0.1` | MIT |
| `ansi-styles` | `4.3.0` | MIT |
| `ansi-styles` | `3.2.1` | MIT |
| `argparse` | `1.0.10` | MIT |
| `array-flatten` | `1.1.1` | MIT |
| `ast-types` | `0.13.4` | MIT |
| `async` | `3.2.6` | MIT |
| `axe-core` | `4.11.2` | MPL-2.0 |
| `b4a` | `1.8.0` | Apache-2.0 |
| `balanced-match` | `1.0.2` | MIT |
| `bare-events` | `2.8.2` | Apache-2.0 |
| `bare-fs` | `4.7.0` | Apache-2.0 |
| `bare-os` | `3.8.7` | Apache-2.0 |
| `bare-path` | `3.0.0` | Apache-2.0 |
| `bare-stream` | `2.13.0` | Apache-2.0 |
| `bare-url` | `2.4.0` | Apache-2.0 |
| `basic-auth` | `2.0.1` | MIT |
| `basic-ftp` | `5.2.2` | MIT |
| `body-parser` | `1.20.4` | MIT |
| `brace-expansion` | `1.1.14` | MIT |
| `buffer-crc32` | `0.2.13` | MIT |
| `bytes` | `3.1.2` | MIT |
| `call-bind-apply-helpers` | `1.0.2` | MIT |
| `call-bound` | `1.0.4` | MIT |
| `camelcase` | `5.3.1` | MIT |
| `chalk` | `4.1.2` | MIT |
| `chalk` | `2.4.2` | MIT |
| `chardet` | `0.7.0` | MIT |
| `chrome-launcher` | `0.13.4` | Apache-2.0 |
| `chrome-launcher` | `1.2.1` | Apache-2.0 |
| `chromium-bidi` | `14.0.0` | Apache-2.0 |
| `cli-cursor` | `2.1.0` | MIT |
| `cli-width` | `2.2.1` | ISC |
| `cliui` | `8.0.1` | ISC |
| `cliui` | `6.0.0` | ISC |
| `cliui` | `8.0.1` | ISC |
| `color-convert` | `2.0.1` | MIT |
| `color-convert` | `1.9.3` | MIT |
| `color-name` | `1.1.4` | MIT |
| `color-name` | `1.1.3` | MIT |
| `compressible` | `2.0.18` | MIT |
| `compression` | `1.8.1` | MIT |
| `concat-map` | `0.0.1` | MIT |
| `configstore` | `5.0.1` | BSD-2-Clause |
| `content-disposition` | `0.5.4` | MIT |
| `content-type` | `1.0.5` | MIT |
| `cookie` | `0.7.2` | MIT |
| `cookie-signature` | `1.0.7` | MIT |
| `corser` | `2.0.1` | MIT |
| `crypto-random-string` | `2.0.0` | MIT |
| `csp_evaluator` | `1.1.5` | Apache-2.0 |
| `data-uri-to-buffer` | `6.0.2` | MIT |
| `debug` | `2.6.9` | MIT |
| `debug` | `2.6.9` | MIT |
| `debug` | `4.4.3` | MIT |
| `debug` | `2.6.9` | MIT |
| `debug` | `2.6.9` | MIT |
| `debug` | `2.6.9` | MIT |
| `debug` | `2.6.9` | MIT |
| `decamelize` | `1.2.0` | MIT |
| `decimal.js` | `10.6.0` | MIT |
| `define-lazy-prop` | `2.0.0` | MIT |
| `degenerator` | `5.0.1` | MIT |
| `depd` | `2.0.0` | MIT |
| `destroy` | `1.2.0` | MIT |
| `devtools-protocol` | `0.0.1467305` | BSD-3-Clause |
| `devtools-protocol` | `0.0.1581282` | BSD-3-Clause |
| `dot-prop` | `5.3.0` | MIT |
| `dunder-proto` | `1.0.1` | MIT |
| `ee-first` | `1.1.1` | MIT |
| `emoji-regex` | `8.0.0` | MIT |
| `encodeurl` | `2.0.0` | MIT |
| `end-of-stream` | `1.4.5` | MIT |
| `enquirer` | `2.4.1` | MIT |
| `es-define-property` | `1.0.1` | MIT |
| `es-errors` | `1.3.0` | MIT |
| `es-object-atoms` | `1.1.1` | MIT |
| `escalade` | `3.2.0` | MIT |
| `escape-html` | `1.0.3` | MIT |
| `escape-string-regexp` | `1.0.5` | MIT |
| `escape-string-regexp` | `4.0.0` | MIT |
| `escodegen` | `2.1.0` | BSD-2-Clause |
| `esprima` | `4.0.1` | BSD-2-Clause |
| `estraverse` | `5.3.0` | BSD-2-Clause |
| `esutils` | `2.0.3` | BSD-2-Clause |
| `etag` | `1.8.1` | MIT |
| `eventemitter3` | `4.0.7` | MIT |
| `events-universal` | `1.0.1` | Apache-2.0 |
| `express` | `4.22.1` | MIT |
| `external-editor` | `3.1.0` | MIT |
| `extract-zip` | `2.0.1` | BSD-2-Clause |
| `fast-fifo` | `1.3.2` | MIT |
| `fd-slicer` | `1.1.0` | MIT |
| `figures` | `2.0.0` | MIT |
| `finalhandler` | `1.3.2` | MIT |
| `find-up` | `4.1.0` | MIT |
| `follow-redirects` | `1.16.0` | MIT |
| `forwarded` | `0.2.0` | MIT |
| `fresh` | `0.5.2` | MIT |
| `fs.realpath` | `1.0.0` | ISC |
| `fsevents` | `2.3.2` | MIT |
| `function-bind` | `1.1.2` | MIT |
| `get-caller-file` | `2.0.5` | ISC |
| `get-intrinsic` | `1.3.0` | MIT |
| `get-proto` | `1.0.1` | MIT |
| `get-stream` | `5.2.0` | MIT |
| `get-uri` | `6.0.5` | MIT |
| `glob` | `7.2.3` | ISC |
| `gopd` | `1.2.0` | MIT |
| `graceful-fs` | `4.2.11` | ISC |
| `has-flag` | `4.0.0` | MIT |
| `has-flag` | `3.0.0` | MIT |
| `has-symbols` | `1.1.0` | MIT |
| `hasown` | `2.0.2` | MIT |
| `he` | `1.2.0` | MIT |
| `html-encoding-sniffer` | `3.0.0` | MIT |
| `http-errors` | `2.0.1` | MIT |
| `http-link-header` | `1.1.3` | MIT |
| `http-proxy` | `1.18.1` | MIT |
| `http-proxy-agent` | `7.0.2` | MIT |
| `http-server` | `14.1.1` | MIT |
| `https-proxy-agent` | `7.0.6` | MIT |
| `iconv-lite` | `0.4.24` | MIT |
| `iconv-lite` | `0.6.3` | MIT |
| `image-ssim` | `0.2.0` | MIT |
| `immediate` | `3.0.6` | MIT |
| `imurmurhash` | `0.1.4` | MIT |
| `inflight` | `1.0.6` | ISC |
| `inherits` | `2.0.4` | ISC |
| `inquirer` | `6.5.2` | MIT |
| `intl-messageformat` | `10.7.18` | BSD-3-Clause |
| `ip-address` | `10.2.0` | MIT |
| `ipaddr.js` | `1.9.1` | MIT |
| `is-docker` | `2.2.1` | MIT |
| `is-fullwidth-code-point` | `3.0.0` | MIT |
| `is-fullwidth-code-point` | `3.0.0` | MIT |
| `is-fullwidth-code-point` | `2.0.0` | MIT |
| `is-fullwidth-code-point` | `3.0.0` | MIT |
| `is-fullwidth-code-point` | `3.0.0` | MIT |
| `is-fullwidth-code-point` | `3.0.0` | MIT |
| `is-obj` | `2.0.0` | MIT |
| `is-typedarray` | `1.0.0` | MIT |
| `is-wsl` | `2.2.0` | MIT |
| `isomorphic-fetch` | `3.0.0` | MIT |
| `jpeg-js` | `0.4.4` | BSD-3-Clause |
| `js-library-detector` | `6.7.0` | MIT |
| `js-yaml` | `3.14.2` | MIT |
| `legacy-javascript` | `0.0.1` | Apache-2.0 |
| `lie` | `3.1.1` | MIT |
| `lighthouse` | `12.6.1` | Apache-2.0 |
| `lighthouse-logger` | `1.2.0` | Apache-2.0 |
| `lighthouse-logger` | `2.0.2` | Apache-2.0 |
| `lighthouse-stack-packs` | `1.12.2` | Apache-2.0 |
| `localforage` | `1.10.0` | Apache-2.0 |
| `locate-path` | `5.0.0` | MIT |
| `lodash` | `4.18.1` | MIT |
| `lodash-es` | `4.18.1` | MIT |
| `lookup-closest-locale` | `6.2.0` | MIT |
| `lru-cache` | `7.18.3` | ISC |
| `make-dir` | `3.1.0` | MIT |
| `marky` | `1.3.0` | Apache-2.0 |
| `math-intrinsics` | `1.1.0` | MIT |
| `media-typer` | `0.3.0` | MIT |
| `merge-descriptors` | `1.0.3` | MIT |
| `metaviewport-parser` | `0.3.0` | MIT |
| `methods` | `1.1.2` | MIT |
| `mime` | `1.6.0` | MIT |
| `mime-db` | `1.54.0` | MIT |
| `mime-db` | `1.52.0` | MIT |
| `mime-types` | `2.1.35` | MIT |
| `mimic-fn` | `1.2.0` | MIT |
| `minimatch` | `3.1.5` | ISC |
| `minimist` | `1.2.8` | MIT |
| `mitt` | `3.0.1` | MIT |
| `mkdirp` | `0.5.6` | MIT |
| `ms` | `2.0.0` | MIT |
| `ms` | `2.0.0` | MIT |
| `ms` | `2.0.0` | MIT |
| `ms` | `2.0.0` | MIT |
| `ms` | `2.0.0` | MIT |
| `ms` | `2.1.3` | MIT |
| `ms` | `2.0.0` | MIT |
| `mute-stream` | `0.0.7` | ISC |
| `negotiator` | `0.6.3` | MIT |
| `negotiator` | `0.6.4` | MIT |
| `netmask` | `2.1.1` | MIT |
| `node-fetch` | `2.7.0` | MIT |
| `object-inspect` | `1.13.4` | MIT |
| `on-finished` | `2.4.1` | MIT |
| `on-headers` | `1.1.0` | MIT |
| `once` | `1.4.0` | ISC |
| `onetime` | `2.0.1` | MIT |
| `open` | `8.4.2` | MIT |
| `open` | `7.4.2` | MIT |
| `opener` | `1.5.2` | (WTFPL OR MIT) |
| `os-tmpdir` | `1.0.2` | MIT |
| `p-limit` | `2.3.0` | MIT |
| `p-locate` | `4.1.0` | MIT |
| `p-try` | `2.2.0` | MIT |
| `pac-proxy-agent` | `7.2.0` | MIT |
| `pac-resolver` | `7.0.1` | MIT |
| `parse-cache-control` | `1.0.1` | UNKNOWN |
| `parseurl` | `1.3.3` | MIT |
| `path-exists` | `4.0.0` | MIT |
| `path-is-absolute` | `1.0.1` | MIT |
| `path-to-regexp` | `0.1.13` | MIT |
| `pend` | `1.2.0` | MIT |
| `playwright` | `1.59.1` | Apache-2.0 |
| `playwright-core` | `1.59.1` | Apache-2.0 |
| `portfinder` | `1.0.38` | MIT |
| `progress` | `2.0.3` | MIT |
| `proxy-addr` | `2.0.7` | MIT |
| `proxy-agent` | `6.5.0` | MIT |
| `proxy-from-env` | `1.1.0` | MIT |
| `pump` | `3.0.4` | MIT |
| `puppeteer-core` | `24.40.0` | Apache-2.0 |
| `qs` | `6.14.2` | BSD-3-Clause |
| `range-parser` | `1.2.1` | MIT |
| `raw-body` | `2.5.3` | MIT |
| `require-directory` | `2.1.1` | MIT |
| `require-main-filename` | `2.0.0` | ISC |
| `requires-port` | `1.0.0` | MIT |
| `restore-cursor` | `2.0.0` | MIT |
| `rimraf` | `3.0.2` | ISC |
| `rimraf` | `2.7.1` | ISC |
| `robots-parser` | `3.0.1` | MIT |
| `run-async` | `2.4.1` | MIT |
| `rxjs` | `6.6.7` | Apache-2.0 |
| `safe-buffer` | `5.1.2` | MIT |
| `safe-buffer` | `5.2.1` | MIT |
| `safer-buffer` | `2.1.2` | MIT |
| `secure-compare` | `3.0.1` | MIT |
| `semver` | `7.7.4` | ISC |
| `semver` | `6.3.1` | ISC |
| `semver` | `5.7.2` | ISC |
| `send` | `0.19.2` | MIT |
| `serve-static` | `1.16.3` | MIT |
| `set-blocking` | `2.0.0` | ISC |
| `setprototypeof` | `1.2.0` | ISC |
| `side-channel` | `1.1.0` | MIT |
| `side-channel-list` | `1.0.1` | MIT |
| `side-channel-map` | `1.0.1` | MIT |
| `side-channel-weakmap` | `1.0.2` | MIT |
| `signal-exit` | `3.0.7` | ISC |
| `smart-buffer` | `4.2.0` | MIT |
| `socks` | `2.8.7` | MIT |
| `socks-proxy-agent` | `8.0.5` | MIT |
| `source-map` | `0.6.1` | BSD-3-Clause |
| `speedline-core` | `1.4.3` | MIT |
| `sprintf-js` | `1.0.3` | BSD-3-Clause |
| `statuses` | `2.0.2` | MIT |
| `streamx` | `2.25.0` | MIT |
| `string-width` | `4.2.3` | MIT |
| `string-width` | `4.2.3` | MIT |
| `string-width` | `4.2.3` | MIT |
| `string-width` | `2.1.1` | MIT |
| `string-width` | `4.2.3` | MIT |
| `string-width` | `4.2.3` | MIT |
| `strip-ansi` | `6.0.1` | MIT |
| `strip-ansi` | `6.0.1` | MIT |
| `strip-ansi` | `6.0.1` | MIT |
| `strip-ansi` | `6.0.1` | MIT |
| `strip-ansi` | `4.0.0` | MIT |
| `strip-ansi` | `5.2.0` | MIT |
| `strip-ansi` | `6.0.1` | MIT |
| `strip-ansi` | `6.0.1` | MIT |
| `supports-color` | `5.5.0` | MIT |
| `supports-color` | `7.2.0` | MIT |
| `tar-fs` | `3.1.2` | MIT |
| `tar-stream` | `3.1.8` | MIT |
| `teex` | `1.0.1` | MIT |
| `text-decoder` | `1.2.7` | Apache-2.0 |
| `third-party-web` | `0.26.7` | MIT |
| `through` | `2.3.8` | MIT |
| `tldts-core` | `6.1.86` | MIT |
| `tldts-icann` | `6.1.86` | MIT |
| `tmp` | `0.0.33` | MIT |
| `tmp` | `0.1.0` | MIT |
| `toidentifier` | `1.0.1` | MIT |
| `tr46` | `0.0.3` | MIT |
| `tree-kill` | `1.2.2` | MIT |
| `tslib` | `1.14.1` | 0BSD |
| `tslib` | `2.8.1` | 0BSD |
| `type-is` | `1.6.18` | MIT |
| `typed-query-selector` | `2.12.1` | MIT |
| `typedarray-to-buffer` | `3.1.5` | MIT |
| `undici-types` | `7.19.2` | MIT |
| `union` | `0.5.0` | UNKNOWN |
| `unique-string` | `2.0.0` | MIT |
| `unpipe` | `1.0.0` | MIT |
| `url-join` | `4.0.1` | MIT |
| `utils-merge` | `1.0.1` | MIT |
| `uuid` | `8.3.2` | MIT |
| `vary` | `1.1.2` | MIT |
| `webdriver-bidi-protocol` | `0.4.1` | Apache-2.0 |
| `webidl-conversions` | `3.0.1` | BSD-2-Clause |
| `whatwg-encoding` | `2.0.0` | MIT |
| `whatwg-fetch` | `3.6.20` | MIT |
| `whatwg-url` | `5.0.0` | MIT |
| `which-module` | `2.0.1` | ISC |
| `wrap-ansi` | `7.0.0` | MIT |
| `wrap-ansi` | `7.0.0` | MIT |
| `wrap-ansi` | `6.2.0` | MIT |
| `wrappy` | `1.0.2` | ISC |
| `write-file-atomic` | `3.0.3` | ISC |
| `ws` | `8.20.0` | MIT |
| `ws` | `7.5.10` | MIT |
| `xdg-basedir` | `4.0.0` | MIT |
| `y18n` | `5.0.8` | ISC |
| `y18n` | `5.0.8` | ISC |
| `y18n` | `4.0.3` | ISC |
| `yargs` | `17.7.2` | MIT |
| `yargs` | `17.7.2` | MIT |
| `yargs` | `15.4.1` | MIT |
| `yargs-parser` | `21.1.1` | ISC |
| `yargs-parser` | `21.1.1` | ISC |
| `yargs-parser` | `13.1.2` | ISC |
| `yargs-parser` | `18.1.3` | ISC |
| `yauzl` | `2.10.0` | MIT |
| `zod` | `3.25.76` | MIT |

## Source manifests

- `/home/runner/work/wcag-spine/wcag-spine/package-lock.json`
- `/home/runner/work/wcag-spine/wcag-spine/package.json`
- `/home/runner/work/wcag-spine/wcag-spine/pyproject.toml`
- `/home/runner/work/wcag-spine/wcag-spine/requirements.txt`
- `/home/runner/work/wcag-spine/wcag-spine/.github/workflows/sync_accessibility.yml`
- `/home/runner/work/wcag-spine/wcag-spine/LICENSE`
