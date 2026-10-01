# Isogeny-based Cryptography Wiki

[![Build and deploy](https://github.com/isogeny-crypto/isogeny-crypto.github.io/actions/workflows/deploy.yml/badge.svg)](https://github.com/isogeny-crypto/isogeny-crypto.github.io/actions/workflows/deploy.yml)

Source for **[isogeny-crypto.github.io](https://isogeny-crypto.github.io)**. It is a [Quarto](https://quarto.org) website with MathJax for maths and TikZ diagrams rendered to SVG at build time.

**Adding content:** [CONTRIBUTING.md](CONTRIBUTING.md). **Maintaining:** [MAINTAINING.md](MAINTAINING.md). This file covers the build.

## Quick start

```bash
git clone https://github.com/isogeny-crypto/isogeny-crypto.github.io.git
cd isogeny-crypto.github.io
npm ci && npm run preview
```

## Prerequisites

| Tool | Version | For |
|---|---|---|
| [Quarto](https://quarto.org/docs/get-started/) | 1.9.38 (pinned in CI) | rendering |
| [Node.js](https://nodejs.org) | 20+ | TikZ → SVG (`node-tikzjax`) |
| Python | 3.8+, stdlib only | lint, link check, contributor fetch |
| Git | any | page modification dates |

Windows: use WSL (`scripts/tikz.lua` calls `mkdir -p`).

## Commands

| Command | Does |
|---|---|
| `npm ci` | Install Node dependencies from the lockfile |
| `npm run preview` | Live preview, including draft pages. Skips the contributor fetch, except on the first run in a fresh clone, which does a full render. |
| `npm run lint` | Check sources against the CONTRIBUTING.md rules. No build needed. |
| `npm run format` | Rewrite `references.bib` in the canonical layout |
| `npm run build` | Full render to `docs/`, as in CI. Leaves out drafts. |
| `npm run check` | Check internal links and anchors in `docs/` (run after `build`) |

## Layout

```
index.qmd                 home page: intro, scheme lists, legend
schemes/<section>/*.qmd   one page per scheme (key-exchange, digital-signature)
references.bib            scheme papers (by year), then follow-up work (by key)
templates/                page templates (not rendered); tikzjax-header.html (diagram CSS)
assets/                   fonts for TikZ SVGs; disc colours (scheme-list.css)
scripts/
  lint.py                 source checks (CI, before render)
  format_bib.py           canonical references.bib layout
  fetch_contributors.py   pre-render: contributor snippets, mtime sync
  tikz.lua, tikz2svg.mjs  {.tikz} blocks → cached SVG
  contributors.lua        appends References + contributors to each page
  discs.lua               []{r=50 b=50} → coloured disc
  check_links.py          post-build link and anchor check
.github/                  CI workflow, issue forms, PR template
```

Only `index.qmd` and `schemes/**/*.qmd` are published (`project.render` in `_quarto.yml`). Pages with `draft: true` are left out of the build: they're dropped from the sidebar and search, and links to them become plain text. They do appear in preview.

Generated (gitignored): `docs/`, `.contributors/`, `.tikz-cache/`, `.quarto/`.

## Build pipeline

```
quarto render
├─ pre-render  fetch_contributors.py   (full renders only)
│    ├─ mtime of each page := its last commit            → "Modified" date
│    └─ GitHub API → .contributors/<page path>.md        → contributor list
├─ filters     tikz.lua → contributors.lua → discs.lua
└─ output      docs/
```

### TikZ

````markdown
```{.tikz fig-alt="CSIDH: E_0 maps to E_A and E_B, which both map to E_AB."}
\usetikzlibrary{arrows.meta}
\begin{tikzpicture}
  \node (E0) at (3,4) {$E_0$};  \node (EA) at (0,2) {$E_A$};
  \node (EB) at (6,2) {$E_B$};  \node (EAB) at (3,0) {$E_{AB}$};
  \draw[-{Stealth}] (E0) -- node[left] {$[\mathrm{a}]$} (EA);
  \draw[-{Stealth}] (E0) -- node[right] {$[\mathrm{b}]$} (EB);
  \draw[-{Stealth}] (EA) -- node[right] {$[\mathrm{b}]$} (EAB);
  \draw[-{Stealth}] (EB) -- node[left] {$[\mathrm{a}]$} (EAB);
\end{tikzpicture}
```
````

- `fig-alt` becomes the diagram's accessible name (`role="img"`, `aria-label`).
- Only the **first** `\usetikzlibrary{…}` line is used, so list every library in it. `\mathfrak` is unreliable; use `\mathrm`.
- To resize, change coordinates or use `[scale=…]`. Diagrams are centred and inverted in dark mode.
- SVGs are cached in `.tikz-cache/` by a hash of the source. CI keeps the cache between runs.

### Citations

- Style: `alpha.csl` (labels like [Cas18]). A missing key is only a Pandoc warning; `npm run lint` is what catches it.
- Cross-page links use paths (`/schemes/…/x.qmd#anchor`), not `@sec-` references.
- To refresh the style: `curl -L -o alpha.csl https://raw.githubusercontent.com/citation-style-language/styles/master/din-1505-2-alphanumeric.csl`

### Discs

`[]{r=50 b=50}` becomes a conic-gradient disc, filled clockwise from 12 o'clock in r, b, g order. The colours are defined in `assets/scheme-list.css`, and their meaning is in [CONTRIBUTING.md §6.7](CONTRIBUTING.md#67-home-page-lists).

### Contributors

Snippets are matched to pages by **file path**. New pages show *Pending GitHub sync…* until they are pushed. If the API fails, the previous snippet is kept.

Unauthenticated calls are limited to 60 per hour, and a full build makes one per page. For repeated local builds:

```bash
export GITHUB_TOKEN="$(gh auth token)"
```

## CI and deployment

`.github/workflows/deploy.yml` runs on every PR, on pushes to `main`, and on manual dispatch:

1. Lint (fails fast)
2. Restore the TikZ cache
3. `quarto render`
4. Link check
5. **PR:** upload `docs/` as the `site-preview` artifact. **`main`:** publish `docs/` to `gh-pages` as a single orphan commit.

GitHub settings: [MAINTAINING.md](MAINTAINING.md#repository-settings).

**Upgrades:**
- **Quarto:** bump `version:` in `deploy.yml` and the Prerequisites table together.
- **node-tikzjax:** `npm update node-tikzjax`, then `rm -rf .tikz-cache` and rebuild.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `HTTP Error 403` during build | Rate limit or expired token: set `GITHUB_TOKEN`. The build still succeeds. |
| Lint error | The message names the file, line and rule. `references.bib` layout errors: `npm run format`. |
| Link check fails | The log names the page and `href`. Usually a heading was renamed. |
| Page missing from the build | It has `draft: true`. |
| Deleted pages still appear locally | `rm -rf docs && npm run build` |
| Diagram fails to render | Check for unsupported fonts/packages or several `\usetikzlibrary` lines. Test with `echo '<tikz>' \| node scripts/tikz2svg.mjs` |
| `npm ci` lockfile mismatch | `npm install`, then commit `package-lock.json` |

## License and citation

Everything here is licensed under **[CC BY 4.0](LICENSE)**. You may reuse or fork it with credit, for example:

> Based on the [Isogeny-based Cryptography Wiki](https://isogeny-crypto.github.io), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Changes were made.

To cite it, use [CITATION.cff](CITATION.cff) (GitHub's *Cite this repository* button).
