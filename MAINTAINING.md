# Maintaining

Everything not covered by [README.md](README.md) (build) or [CONTRIBUTING.md](CONTRIBUTING.md) (rules).

## Maintainers

| GitHub | Role | Contact (Code of Conduct reports) |
|---|---|---|
| [@gkorpal](https://github.com/gkorpal) | Lead | gkorpal@zohomail.in |

To add a maintainer: grant write access, add a row here, and add them to `CITATION.cff` if appropriate.

## Roadmap

Status, October 2026:

| List | Listed | Published | Notes |
|---|---|---|---|
| Key Establishment | 33 | 25 | |
| Digital Signature | 42 | 1 | SQISign and SQIsignHD are drafts |

All *Progress* sections are `TODO`.

- **Until December 2026:** the lead maintainer writes every scheme page (Progress may stay `TODO`) and commits directly to `main`.
- **December 2026 launch:** open to the public for *Progress* sections and corrections. From then on, every change goes through a PR.

### Launch checklist

- [ ] Every listed scheme has a published page.
- [x] Every diagram has `fig-alt`.
- [x] Lint shows 0 warnings.
- [ ] Branch protection on `main` enabled ([settings](#repository-settings)).
- [x] Labels created: `error`, `new scheme`, `claimed`, `good first issue`.
- [ ] `good first issue`s opened for well-known *Progress* sections (SIDH, CSIDH).
- [ ] `CITATION.cff` authorship policy decided.
- [ ] Announced (Isogeny Club, Leuven Isogeny Days, …).

## Repository settings

These live in GitHub's settings, not in the repo. Re-check them after any transfer.

| Setting | Value |
|---|---|
| Pages → Source | branch `gh-pages`, `/ (root)` |
| Actions → Workflow permissions | Read (default). The workflow requests `contents: write` itself. |
| General → Pull Requests | Squash merging only (PR title and description); auto-delete head branches |
| Branch rule for `main` *(from launch)* | Require a PR with 1 approval and the status check `build`; block force pushes |

The workflow needs no secrets.

## Reviewing a PR

1. CI is green, and the lint shows no warnings for the changed files.
2. Scope: one scheme or fix, touching only the page, `references.bib`, and `index.qmd`.
3. Accuracy: against the paper, spot-check the parameters, one step per algorithm, and each assumption (including new or borrowed). Ask for section references where you can't verify something.
4. Style: [CONTRIBUTING.md §6](CONTRIBUTING.md#6-rules).
5. Home-page line: list, year and disc follow [§6.7](CONTRIBUTING.md#67-home-page-lists). You decide disputed discs.
6. `site-preview` artifact: check the page in light and dark mode, and that the diagram matches the paper.
7. **Squash and merge** with an imperative title. Make sure the claim issue closes.

Stale claims: ping after 30 days of inactivity, and unassign after 2 more weeks.

## Common tasks

**Mark a scheme broken.**
1. In `index.qmd`, change `(YEAR)` to `(YEAR--BREAKYEAR)`.
2. Add the blockquote to the page.
3. Add the attack to *Progress*, with a bib entry.
4. Add the attack to the *Progress* of dependent schemes too.

**Rename a page.** Update the filename, the `index.qmd` link, and cross-links (`grep -rn old.qmd schemes index.qmd`); lint and the link check catch any you miss. GitHub Pages has no redirects. For a widely shared URL, add Quarto `aliases:` to the page.

**Add a category.** Agree on it in an issue first (it changes the scope). Then add:
- `schemes/<cat>/` and `templates/<cat>.qmd`
- a sidebar section in `_quarto.yml`
- a `### <Cat>` list in `index.qmd`
- an entry in `LISTS` in `scripts/lint.py`
- updates to CONTRIBUTING.md §2, §5 and §6.7, and to the issue form dropdowns

**Promote a lint warning to an error.** Remove `warn=True` from the check in `scripts/lint.py` once the existing pages comply.

## Citation metadata

`CITATION.cff` lists only the founder. Decide on a policy before launch (e.g. maintainers only, or maintainers plus anyone who wrote a complete page). Every contributor is already credited on each page. Update `date-released` for each citable snapshot.

## Licence

CC BY 4.0 covers everything. Contributions come in under the same licence. Diagrams are redrawn in TikZ, never copied as images, and cite their source paper.

## Known issues

| Issue | Notes |
|---|---|
| Windows builds untested | `tikz.lua` uses `mkdir -p`; use WSL |
| One GitHub API call per page | Fine for CI. Locally, set `GITHUB_TOKEN`. |
| Quarto doesn't clean `docs/` | `rm -rf docs` before a full local build |

Personal tooling (AI prompts, downloaded papers) belongs in the gitignored `papers/` directory.
