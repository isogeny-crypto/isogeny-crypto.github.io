# Contributing

This wiki is a reference for isogeny-based cryptography researchers. **Accuracy comes first.** These rules apply to every contributor, human or AI.

See also: [README.md](README.md) (build), [MAINTAINING.md](MAINTAINING.md) (maintainers), [Code of Conduct](CODE_OF_CONDUCT.md).

1. [Ways to contribute](#1-ways-to-contribute)
2. [Scope](#2-scope)
3. [Setup](#3-setup)
4. [Workflow](#4-workflow)
5. [Adding a scheme page](#5-adding-a-scheme-page)
6. [Rules](#6-rules)
7. [Commits and pull requests](#7-commits-and-pull-requests)
8. [Checklist](#8-checklist)

## 1. Ways to contribute

| Goal | How |
|---|---|
| Report an error | **Report an issue** link on the page, or [open an issue](https://github.com/isogeny-crypto/isogeny-crypto.github.io/issues/new/choose) |
| Fix a typo | **Edit this page** link on the page (GitHub creates the PR) |
| Suggest a missing scheme | *Propose a scheme* issue |
| Write a page or a *Progress* section | Claim it with a *Work on a page* issue, then follow [§4](#4-workflow)–[§5](#5-adding-a-scheme-page) |

Check [open issues](https://github.com/isogeny-crypto/isogeny-crypto.github.io/issues) and [PRs](https://github.com/isogeny-crypto/isogeny-crypto.github.io/pulls) first so work isn't duplicated.

## 2. Scope

The wiki covers isogeny-based **key establishment** (key exchange, PKE, KEM, updatable encryption, PAKE, …) and **signature** schemes (including identification protocols and ring, threshold, blind, adaptor, and designated-verifier signatures). A scheme qualifies if it is:

1. **Peer-reviewed:** published at a conference or in a journal. An ePrint alone doesn't qualify.
2. **Named** by its paper.
3. **New or modified:** named variants count (e.g. AprèsSQI). Attacks, implementations and fixes don't; they go in the scheme's [*Progress*](#66-progress-sections) section.

Each scheme gets one page. When one paper introduces several schemes, each gets its own page, and they share one BibTeX entry. For other primitives (hash functions, VDFs, …), open an issue first.

## 3. Setup

Prerequisites: [README → Prerequisites](README.md#prerequisites).

```bash
gh repo fork isogeny-crypto/isogeny-crypto.github.io --clone=false   # or "Fork" on GitHub
git clone https://github.com/<you>/isogeny-crypto.github.io.git
cd isogeny-crypto.github.io
git remote add upstream https://github.com/isogeny-crypto/isogeny-crypto.github.io.git
npm ci
```

## 4. Workflow

One branch per contribution. Never commit to `main`.

```bash
git switch main && git pull upstream main        # start up to date
git switch -c add-sidh-um                        # branch: add-…, fix-…, progress-…
npm run preview                                  # live preview (shows drafts)
npm run lint                                     # rule check; must show 0 errors
git add <files>                                  # by name, not `git add .`
git commit -m "Add SIDH UM key-establishment page"
git push -u origin add-sidh-um                   # then open the PR from the printed link
```

- **The PR:** fill in the template, and add `Closes #<issue>` if you claimed the work. CI lints, builds, and checks links. Download the **site-preview** artifact from the *Checks* tab to see the exact result.
- **Review changes:** commit and push to the same branch.
- **Conflicts:** `git fetch upstream && git rebase upstream/main`, fix the conflicts, then `git push --force-with-lease`.
- **After merging:** `git switch main && git pull upstream main && git branch -d <branch>`.

## 5. Adding a scheme page

Running example: **Foo-SIDH**.

1. **Paper:** work from the paper that introduces the scheme (the proceedings version, or the latest ePrint revision).
2. **BibTeX:** check that `references.bib` has its entry. Add one if needed, following [§6.5](#65-bibliography).
3. **Page:**
   ```bash
   cp templates/key-establishment.qmd schemes/key-establishment/foosidh.qmd
   # signatures: templates/digital-signature.qmd → schemes/digital-signature/
   ```
   The filename is the scheme name in lowercase letters and digits (`POKÉ` → `poke.qmd`, `$k$-SIDH` → `ksidh.qmd`). Write it following [§6](#6-rules), and delete the template comments.
4. **Home page:** link the name in `index.qmd`: `[Foo-SIDH](/schemes/key-establishment/foosidh.qmd)`. A new line must follow [§6.7](#67-home-page-lists).
5. **Publish:** delete `draft: true` once Overview, Scheme Design and Security Assumptions are complete. Until then the page is hidden from the site, and links to it show as plain text.

## 6. Rules

### 6.1 Page structure

These `##` sections, in this order:

| Section | Content |
|---|---|
| **Overview** | **One paragraph**, plain English: the problem, what the scheme builds on, and its key idea. Cites the introducing paper. |
| **Scheme Design** | The algorithms in the paper's order and with its names, as `###` subsections. Key establishment: parameters → keygen → encrypt/encapsulate → decrypt/decapsulate. Signatures: parameters → keygen → identification protocol → sign → verify, naming the transform used (Fiat–Shamir, …). |
| **Security Assumptions** | Theory only: the security notion proved (e.g. IND-CPA, sEUF-CMA in the QROM), then one bullet per hardness assumption with its **name**, a precise statement, and whether it is **new** or **borrowed**. A borrowed assumption links to the wiki page of the scheme that introduced it (`…/<scheme>.qmd#security-assumptions`). If that scheme has no page yet, create a draft for it ([§5](#5-adding-a-scheme-page), step 3) and link that. No attack costs, parameter conditions, or implementation remarks: attacks belong in *Progress*, and parameter conditions in *Scheme Design*. |
| **Progress** | As in [§6.6](#66-progress-sections). `TODO` is acceptable. |

- **Frontmatter:** `title` is the name exactly as the paper writes it. `subtitle` is the expanded name. `date` is the date the page was created (`YYYY-MM-DD`).
- **Broken schemes:** a one-line blockquote above the Overview linking `#progress`.
- **Don't add** `#` headings, hand-numbered headings, or a *References* section; all three are generated.

### 6.2 Writing

- Write for researchers. Every claim must be **traceable to a cited paper**. Never guess; leave the point out or write `TODO`.
- **Define every symbol before first use.** Keep the paper's notation.
- Use a neutral tone. No *novel*, *groundbreaking*, *elegant*. Quote comparisons as the paper states them.
- Spell out each acronym on first use: *indistinguishability under chosen-ciphertext attack (IND-CCA)*.
- Parties: Alice/Bob for key establishment, prover/verifier for identification, signer/verifier for signatures.
- **No emoji** anywhere: pages, docs, code, comments, commit messages, issues, PRs.

### 6.3 Maths and diagrams

- MathJax only, for screen-reader accessibility: `$…$` inline, `$$…$$` display. No images of equations, and don't override `html-math-method`.
- Diagrams are optional. Add one only when the paper has a figure illustrating the protocol and it helps the reader.
- Diagrams are ` ```{.tikz fig-alt="…"} ` blocks (syntax in [README](README.md#tikz)). `fig-alt` is required: a one- or two-sentence description for screen readers.
- In TikZ, use `\mathrm`, not `\mathfrak`, and put every library in a single `\usetikzlibrary{…}` line.
- Redraw the paper's figure faithfully. Don't rely on colour alone, because dark mode inverts it.

### 6.4 Links and citations

- Cite with `[@key]` or `[@key1; @key2]`.
- Link wiki pages by absolute path: `[FESTA](/schemes/key-establishment/festa.qmd)`. To link a section, add its anchor (the heading in lowercase, spaces → hyphens): `…/csidh.qmd#security-assumptions`.
- Couveignes and Rostovtsev–Stolbunov have no wiki pages, so always link their ePrints: `[Couveignes](https://eprint.iacr.org/2006/291)`, `[Rostovtsev–Stolbunov](https://eprint.iacr.org/2006/145)`.

### 6.5 Bibliography

`references.bib` has two parts. Run `npm run format` to apply the layout; `npm run lint` checks everything else.

| | Scheme papers (top) | Follow-up work (below `% Follow-up work`) |
|---|---|---|
| **Holds** | Papers that introduce a listed scheme | Papers cited in *Progress* |
| **Key** | Scheme name in lowercase letters and digits (`poke`, `ksidh`); joint papers: `msidh-mdsidh` | Google Scholar style: `<surname><year><first title word>` (`castryck2023efficient`); add `b`, `c` for clashes |
| **Order** | By year | By key |

- **Types:** `@inproceedings` needs `booktitle`; `@article` needs `journal`. Both need `author`, `title`, `year`, and `url`.
- **Venues:** short names (`CRYPTO`, `EUROCRYPT`, `PKC`, …). Put volume and number in their own fields.
- **Year:** the conference year, even if the proceedings appeared later. For journals, the publication year.
- **Authors:** in "First Last" order, with accented letters as Unicode (`Péter`, not `P{\'e}ter`). Protect capitals with braces: `{SIDH}`.
- **URL:** the IACR ePrint page if there is one, otherwise the DOI or publisher's page. Search the file for it before adding an entry; the lint flags duplicate URLs.

### 6.6 Progress sections

What happened after publication: attacks, security analyses, fixes, parameter changes, and performance improvements. Leave out papers that merely cite the scheme, and surveys.

```markdown
- **2022**: Polynomial-time key recovery for all SIDH parameter sets [@castryck2023efficient].
```

- One bullet per paper, oldest first. The year is when the result was first made public (usually its ePrint year); within a year, order by ePrint number.
- One neutral sentence per bullet. Link the result's wiki page if it has one.
- A breaking attack **must** be listed.
- Until the section is written: `TODO`, optionally followed by ePrint IDs to cover.

### 6.7 Home-page lists

`index.qmd` lists **every** in-scope scheme, with or without a page:

```markdown
- []{r=100} [Name](/schemes/<section>/<name>.qmd) (YEAR)    ← has a page
- []{g=100} Name (YEAR)                                      ← no page yet
- []{r=100} Name (YEAR--YEAR)                                ← broken
```

- **List:** *Key Establishment* for key exchange, PKE, KEM, etc.; *Digital Signature* for signatures and identification protocols.
- **Name:** exactly as the paper writes it (`POKÉ`, `$\Pi$-CSIDH`).
- **Year:** the conference year, or the publication year for a journal. It must match the BibTeX `year`.
- **Broken (`YEAR--YEAR`):** an attack that no parameter change can fix. The range ends in the year the attack became public. Attacks that are fixable go in *Progress*, not here.
- **Order:** by year. A new line goes after the existing lines with the same year.
- **Disc:** each technique's share of the scheme, as percentages summing to 100 (so far always 100, 50/50, or 34/33/33):
  - `r` **torsion points:** publishes or relies on images of torsion points under secret isogenies (SIDH-style, higher-dimensional/Kani).
  - `b` **quaternion algebra:** computes with quaternion orders and ideals via the Deuring correspondence (KLPT, ideal-to-isogeny).
  - `g` **group action:** built on a commutative class-group action (CSIDH, CSURF, SCALLOP).

  If you're unsure which techniques apply, ask in the PR; maintainers decide.
- Add the BibTeX entry in the same PR.

### 6.8 Other home-page links

*Getting Started* and community links must be **freely accessible** (books, theses, school recordings or materials, open recurring events), listed chronologically. Maintainers decide what to include.

### 6.9 Don't edit

- Generated: `docs/`, `.contributors/`, `.tikz-cache/`.
- Infrastructure (`_quarto.yml`, `scripts/`, `.github/`): open an issue first.

### 6.10 AI tools

Allowed, but **you are the author**: verify every statement against the paper. Don't commit prompts, agent configuration, or downloaded papers.

## 7. Commits and pull requests

- One scheme or fix per PR.
- Imperative commit messages: `Add PIKE key-establishment page`, `Fix degree of phi in QFESTA keygen`. Not `update` or `typos`.
- A PR is merged after maintainer approval and green CI, usually squashed.

## 8. Checklist

`npm run lint` checks the mechanical rules. You check the rest:

- [ ] `npm run lint`: 0 errors, and no warnings for your files.
- [ ] Every claim is traceable to a cited paper, and every symbol is defined before use.
- [ ] Assumptions are theory only, marked new or borrowed, and borrowed ones link to their wiki page.
- [ ] Every diagram has meaningful `fig-alt` text and matches the paper.
- [ ] Any new home-page line has the right list, year and disc.
- [ ] The preview looks right in light and dark mode.
- [ ] Only this scheme's files are changed: the page, `references.bib`, and `index.qmd`.

---

Contributions are licensed under [CC BY 4.0](LICENSE). Contributors are credited automatically on each page they edit.
