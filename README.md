# Isogeny-based Cryptography Wiki

Welcome to the source repository for the [isogeny-crypto.github.io](https://isogeny-crypto.github.io) wiki. This repository contains the markdown source files, mathematical configurations, and build scripts used to generate our collaborative reference for isogeny-based cryptographic schemes.

## Tech Stack & Architecture

This website is statically generated using Quarto. It leverages MathJax for fully accessible mathematical rendering, `node-tikzjax` to compile TikZ diagrams to SVG at build time, and a Python pre-render hook to dynamically query the GitHub API for contributor attribution.

**Deployment is fully automated.** Pushing to `main` triggers a GitHub Actions workflow that installs dependencies, renders the site, and publishes it to GitHub Pages — no manual build step required.

### Dependencies

To preview the site locally, install the following:

1. **Quarto CLI** — the core HTML rendering engine. [Download here](https://quarto.org/docs/get-started/).
2. **Python 3** — runs `fetch_contributors.py` as a pre-render hook.
3. **Node.js (v20+)** — runs `tikz2svg.mjs` to convert TikZ diagrams to SVG at build time.
4. **Git** — required by `fetch_contributors.py` to sync file modification dates from commit history.

Recommended editor: Visual Studio Code with the official [Quarto extension](https://marketplace.visualstudio.com/items?itemName=quarto.quarto) for live previewing and integrated LaTeX support.

---

## Accessibility & Mathematics Mandate

To meet strict accessibility standards, this wiki exclusively uses MathJax for all mathematical rendering.

Unlike lightweight alternatives, MathJax provides native screen-reader compatibility and an Assistive Explorer. This is a hard requirement for our repository, as it allows visually impaired researchers to interactively step through complex supersingular elliptic curve parameters, matrices, and commutative diagrams without losing semantic context.

- Use standard `$` for inline math and `$$` for display equations.
- The repository is configured to use `html-math-method: mathjax` globally. Do not override this setting in individual files.
- For diagrams, use fenced code blocks with the `.tikz` class (see below). Diagrams automatically centre and invert correctly in dark mode.

### Writing TikZ Diagrams

Use a fenced code block with the `.tikz` class. The `tikz.lua` Pandoc filter converts it to SVG at build time; no raw HTML is needed in your source files. Rendered SVGs are cached in `.tikz-cache/` by content hash, so unchanged diagrams are never re-rendered.

````markdown
```{.tikz}
\usetikzlibrary{arrows.meta}
\begin{tikzpicture}

  \node (A) at (0, 1) {$A$};
  \node (B) at (2, 1) {$B$};
  \node (C) at (0, 0) {$C$};
  \node (D) at (2, 0) {$D$};

  \draw[-{Stealth}, thick] (A) -- node[above] {$\phi$} (B);
  \draw[-{Stealth}, thick] (A) -- (C);
  \draw[-{Stealth}, thick] (B) -- (D);
  \draw[-{Stealth}, thick] (C) -- (D);

\end{tikzpicture}
```
````

A larger example — the CSIDH key exchange diagram:

````markdown
```{.tikz}
\usetikzlibrary{arrows.meta}
\begin{tikzpicture}

  \node (E0)  at (3, 4) {$E_0$};
  \node (EA)  at (0, 2) {$E_A = [\mathrm{a}] * E_0$};
  \node (EB)  at (6, 2) {$E_B = [\mathrm{b}] * E_0$};
  \node (EAB) at (3, 0) {$E_{AB} = E_{BA}$};

  \draw[-{Stealth}, thick] (E0)  -- node[left,  midway] {$[\mathrm{a}]$} (EA);
  \draw[-{Stealth}, thick] (E0)  -- node[right, midway] {$[\mathrm{b}]$} (EB);
  \draw[-{Stealth}, thick] (EA)  -- node[right, midway] {$[\mathrm{b}]$} (EAB);
  \draw[-{Stealth}, thick] (EB)  -- node[left,  midway] {$[\mathrm{a}]$} (EAB);

\end{tikzpicture}
```
````

Note that TikZJax supports only a subset of LaTeX fonts and math commands. In particular, `\mathfrak` can be unreliable; prefer `\mathrm` as a fallback.

To adjust diagram size, change the coordinate spacing directly — spread nodes further apart to enlarge, closer to compress. You can also add `[scale=1.5]` to the `\begin{tikzpicture}` options.

---

## Local Development Workflow

### 1. Clone the repository

```bash
git clone https://github.com/isogeny-crypto/isogeny-crypto.github.io.git
cd isogeny-crypto.github.io
```

### 2. Install Node dependencies

```bash
npm ci
```

Run this once after cloning, and again whenever `package-lock.json` changes. Using `npm ci` (instead of `npm install`) ensures you get exactly the versions recorded in the lockfile.

### 3. Set up your GitHub token (optional but recommended)

`fetch_contributors.py` queries the GitHub API to attribute contributors to each page. Without a token, the API allows 60 requests per hour — enough for small builds. For frequent local builds, authenticate to raise this limit:

**Mac/Linux** — add to your `~/.zshrc` or `~/.bashrc`:
```bash
export GITHUB_TOKEN="your_token_here"
```

**Windows (PowerShell)**:
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

To get a token: go to [GitHub Developer Settings](https://github.com/settings/tokens) → generate a new "Personal access token (classic)" with no scopes (public repo access requires none). If you skip this step, the script will fall back to "Pending GitHub sync..." for contributor fields.

> **Token expiry:** if builds start failing with `HTTP Error 403`, your token has expired. Generate a new one and update the environment variable.

### 4. Live preview (writing mode)

```bash
npm run preview
```

This spins up a local development server with hot-reloading. The contributor fetch is skipped in preview mode for speed — contributor snippets from your last full build are reused.

### 5. Verify a full local build (optional)

You only need this if you want to check the final rendered output before pushing. CI will do this automatically on every push.

```bash
npm run build
```

---

## Deployment

**Deployment is automatic.** Simply push your changes to `main`:

```bash
git add .
git commit -m "your descriptive message"
git push
```

The GitHub Actions workflow (`.github/workflows/deploy.yml`) will then:

1. Check out the repository with full Git history (needed for contributor date syncing).
2. Install Python, Node.js, and Quarto.
3. Run `npm ci` to install dependencies.
4. Run `quarto render`, which triggers `fetch_contributors.py` automatically as a pre-render hook.
5. Push the rendered `docs/` folder to the `gh-pages` branch, which GitHub Pages serves.

You can monitor the progress of any deployment under the **Actions** tab of the repository on GitHub. A green checkmark means the site is live; a red cross means something failed and you can click through to read the logs.

> **First-time setup:** after merging the Actions workflow, go to your repo on GitHub → **Settings** → **Pages** → set the source branch to `gh-pages` and the folder to `/ (root)`.

---

## Key Configurations

### Citations & cross-references

We use a classic alphanumeric cryptographic citation style (e.g., [Cas18]).

- Add all BibTeX entries to `references.bib`.
- Cite inline using Citeproc syntax: `[@citation_key]`.
- Due to Quarto's file-isolation in website projects, cross-references between different `.qmd` files must use relative path anchors, not the native `@sec-` tags.

To refresh `alpha.csl` from upstream:
```bash
curl -L -o alpha.csl https://raw.githubusercontent.com/citation-style-language/styles/master/din-1505-2-alphanumeric.csl
```

### Automated contributor attribution

At build time, `fetch_contributors.py` queries the GitHub API for the commit history of every `.qmd` file in `schemes/` and writes a small markdown snippet into the `.contributors/` directory, named after the page's title (e.g. `sidh.md`, `csi-fish.md`). The `contributors.lua` Pandoc filter then automatically appends the relevant snippet to the bottom of each rendered page, preceded by a horizontal rule.

**This is fully automatic — no changes are needed to your `.qmd` files.** When you create a new scheme page, simply write your content and push; the contributor block will appear at the bottom after the first CI build.

**Important notes:**

- Do not edit `.contributors/` manually — it is regenerated on every full build and is gitignored.
- New files will show "Pending GitHub sync..." until your first push, because the script queries the remote repository's commit history.
- Contributor snippets are matched to pages by the `title:` field in each `.qmd`'s YAML frontmatter. Make sure every scheme page has a unique, stable title.

### scheme list legend (colored discs)

The homepage's Key Establishment / Digital Signature lists (`index.qmd`) mark each scheme with a small colored disc indicating which underlying technique it relies on, per the legend: red = torsion points, blue = Deuring correspondence, green = group action.

Discs are written with a shorthand span, expanded at build time by the `discs.lua` Pandoc filter:

```markdown
- []{r=100} SIDH (2011--2022)
- []{b=100} SQISign (2020)
- []{r=50 b=50} pSIDH (2022--2023)
```

`r`, `g`, `b` are percentages (0–100) for red/green/blue. Give one color for a solid disc, or two/three for a split disc rendered as a CSS `conic-gradient` in that ratio — useful for schemes that draw on more than one technique. Percentages need not sum to 100. Styling for the resulting disc lives in `assets/scheme-list.css`.

## Template 

Upload the paper to an LLM model (eg. Google Gemini Pro) with the following prompt:

```
Study the attached file and generate a detailed, concrete description of the newly introduced scheme [NAME] in Quarto Markdown (.qmd) format. The target audience is researchers working in isogeny-based cryptography. Organize the information under the following headings:
1. Overview (one paragraph summarizing the scheme motivation in plain english without sounding like a sales pitch) 
2. Scheme Design (walk through the scheme while defining each symbol before usage)
3. Security Assumptions (what problems are assumed hard, whether assumptions are new or borrowed from previous schemes) 
```

Iterate until you get a good initial draft. Then proof read and make necessary edits like adding references, hyperlinks, and `tikz` diagram of the scheme (generated from screenshot using LLM, eg. Anthropic Claude Sonnet or Mistral Vibe/Le Chat).