# Isogeny-based Cryptography Wiki

Welcome to the source repository for the [isogeny-crypto.github.io](https://isogeny-crypto.github.io) wiki. This repository contains the markdown source files, mathematical configurations, and build scripts used to generate our collaborative reference for isogeny-based cryptographic protocols.

## Tech Stack & Architecture

This website is statically generated using Quarto. It leverages MathJax for fully accessible mathematical rendering, TikZJax for client-side diagrams rendered from pure TikZ, and a custom Python pre-render hook to dynamically query the GitHub API for contributor attribution.

### Dependencies

To build or preview this site locally, you must install the following:

1. **Quarto CLI**: The core HTML rendering engine.
2. **Python 3**: Required to execute the `fetch_contributors.py` pre-render script.
3. **Git**: For version control and repository syncing.

Recommended Editor: Visual Studio Code with the official Quarto Extension for live previewing and integrated LaTeX support.

---

## Accessibility & Mathematics Mandate

To meet strict accessibility standards, this wiki exclusively uses the latest version of MathJax for all mathematical rendering.

Unlike lightweight alternatives, MathJax provides native screen-reader compatibility and an Assistive Explorer. This is a hard requirement for our repository, as it allows visually impaired researchers to interactively step through complex supersingular elliptic curve parameters, matrices, and commutative diagrams without losing semantic context.

- Use standard `$` for inline math and `$$` for display equations.
- The repository is configured to use `html-math-method: mathjax` globally. Do not override this setting in individual files.
- For diagrams, use fenced code blocks with the `.tikz` class (see below). TikZJax renders them client-side. Diagrams automatically centre and invert correctly in dark mode.
- TikZJax supports only a subset of LaTeX fonts and math commands. In particular, `\mathfrak` can be unreliable; prefer `\mathrm` as a fallback.

### Writing TikZ Diagrams

Use a fenced code block with the `.tikz` class. The `tikz.lua` Pandoc filter converts it to the correct HTML at build time; no raw HTML needed in your source files.

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

A larger example: the CSIDH key exchange diagram:

````markdown
```{.tikz}
\usetikzlibrary{arrows.meta}
\begin{tikzpicture}

  \node (E0)  at (3, 4) {$E_0$};
  \node (EA)  at (0, 2) {$E_A = [\mathfrak{a}] * E_0$};
  \node (EB)  at (6, 2) {$E_B = [\mathfrak{b}] * E_0$};
  \node (EAB) at (3, 0) {$E_{AB} = E_{BA}$};

  \draw[-{Stealth}, thick] (E0)  -- node[left,  midway] {$[\mathfrak{a}]$} (EA);
  \draw[-{Stealth}, thick] (E0)  -- node[right, midway] {$[\mathfrak{b}]$} (EB);
  \draw[-{Stealth}, thick] (EA)  -- node[right, midway] {$[\mathfrak{b}]$} (EAB);
  \draw[-{Stealth}, thick] (EB)  -- node[left,  midway] {$[\mathfrak{a}]$} (EAB);

\end{tikzpicture}
```
````

To adjust diagram size, change the coordinate spacing directly, spread nodes further apart to enlarge, closer to compress. You can also add `[scale=1.5]` to the `\begin{tikzpicture}` options.

---

## Local Development Workflow

### 1. Clone the Repository

```bash
git clone https://github.com/isogeny-crypto/isogeny-crypto.github.io.git
cd isogeny-crypto.github.io
```

### 2. Live Preview (Writing Mode)

To spin up a local development server with hot-reloading:

```bash
python3 fetch_contributors.py
quarto preview
```

Note: This utilises a fast local cache and does not generate final production files.

### 3. Build for Production

Before committing your changes to GitHub, generate the contributor snippets and compile the final site into the `docs` folder.

```bash
python3 fetch_contributors.py
quarto render --clean
```

This repository also wires the generator into Quarto's `pre-render` step, but running it explicitly keeps local builds and fresh checkouts predictable.

---

## Key Configurations

### Citations & Cross-References

We use a classic alphanumeric cryptographic citation style (e.g., [Cas18]).

```bash
curl -L -o alpha.csl https://raw.githubusercontent.com/citation-style-language/styles/master/din-1505-2-alphanumeric.csl
```

- Add all BibTeX entries to `references.bib`.
- Cite inline using Citeproc syntax: `[@citation_key]`.
- Due to Quarto's file-isolation in website projects, cross-references between different `.qmd` files must use relative path anchors, not the native `@sec-` tags.

### Automated Contributor Tags

At build time, `fetch_contributors.py` dynamically queries the GitHub API to find the commit history of every `.qmd` file and generates a markdown snippet. To prevent API rate limit errors (HTTP 403), the script authenticates using a GitHub Personal Access Token.

**Local Setup & Token Expiration:**

- **Usage:** Before building the site locally, expose your token as an environment variable:
  - Mac/Linux: `export GITHUB_TOKEN="your_token_here"`
  - Windows: `$env:GITHUB_TOKEN="your_token_here"`
- **Handling Expiration:** If builds start failing with `HTTP Error 403: rate limit exceeded`, your token has likely expired. To fix this:
  1. Go to your [GitHub Developer Settings](https://github.com/settings/tokens).
  2. Generate a new "Personal access token (classic)" (no specific scopes required for public repositories).
  3. Update your local `GITHUB_TOKEN` environment variable.

**Usage Notes:**

- Do not edit the hidden `.contributors/` folder manually.
- Ensure the bottom of your article includes the shortcode: `{{< include ../../.contributors/filename.md >}}`.
- The script parses the remote GitHub repository. If you create a brand new file locally, the script will output "Pending GitHub sync" until your first push.

---

## Deployment

Deployment is handled entirely by GitHub Pages. The repository serves the site from the `/docs` directory on the `main` branch. We commit before running `quarto render --clean` so that the latest text modification dates are available via git.

```bash
git add .
git commit -m "<descriptive commit message>"
quarto render --clean
git add docs/
git commit --amend --no-edit
git push origin main
```
