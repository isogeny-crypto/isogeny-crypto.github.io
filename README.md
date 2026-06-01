# Isogeny-based Cryptography Wiki

Welcome to the source repository for the [isogeny-crypto.github.io](https://isogeny-crypto.github.io) wiki. This repository contains the markdown source files, mathematical configurations, and build scripts used to generate our collaborative reference for isogeny-based cryptographic protocols.

## Tech Stack & Architecture

This website is statically generated using Quarto. It leverages MathJax for fully accessible mathematical rendering and a custom Python pre-render hook to dynamically query the GitHub API for contributor attribution.

### Dependencies
To build or preview this site locally, you must install the following:

1. Quarto CLI: The core HTML rendering engine.
2. Python 3: Required to execute the fetch_contributors.py pre-render script.
3. Git: For version control and repository syncing.

Recommended Editor: Visual Studio Code with the official Quarto Extension for live previewing and integrated LaTeX support.

---

## Accessibility & Mathematics Mandate

To meet strict accessibility standards, this wiki exclusively uses the latest version of MathJax for all mathematical rendering. 

Unlike lightweight alternatives, MathJax provides native screen-reader compatibility and an Assistive Explorer. This is a hard requirement for our repository, as it allows visually impaired researchers to interactively step through complex supersingular elliptic curve parameters, matrices, and commutative diagrams without losing semantic context.

* Use standard `$` for inline math and `$$` for display equations.
* The repository is configured to use `html-math-method: mathjax` globally. Do not override this setting in individual files.

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
quarto preview
```
Note: This utilizes a fast local cache and does not generate final production files.

### 3. Build for Production

Before committing your changes to GitHub, you must compile the final site into the docs folder and trigger the Python script to fetch the latest contributors.

Run a clean render to ensure no stale cache remains:
```bash
quarto render --clean
```

## Key Configurations

### Citations & Cross-References

We utilize a classic alphanumeric cryptographic citation style (e.g., [Cas18]).

```bash
curl -L -o alpha.csl https://raw.githubusercontent.com/citation-style-language/styles/master/din-1505-2-alphanumeric.csl
```

- Add all BibTeX entries to references.bib.
- Cite inline using the exact Citeproc syntax: `[@citation_key]`.
- Due to Quarto's file-isolation in website projects, cross-references between different .qmd files must be done via relative path anchors, not the native @sec- tags.

### Automated Contributor Tags

At build time, fetch_contributors.py dynamically queries the GitHub API to find the commit history of every `.qmd` file and generates a markdown snippet.

- Do not edit the hidden .contributors/ folder manually.
- Ensure the bottom of your article includes the shortcode: `{{< include ../../.contributors/filename.md >}}`.
- Note: The script parses the remote GitHub repository. If you create a brand new file locally, the script will output "Pending GitHub sync" until your first push.

## Deployment

Deployment is handled entirely by GitHub Pages.

The repository is configured to serve the site from the `/docs` directory on the main branch. Once you run `quarto render --clean`, simply commit and push your changes. GitHub Actions will automatically detect the updated docs folder and deploy the live site.

```bash
git add .
git commit -m "<descriptive commit message>"
git push origin main
```