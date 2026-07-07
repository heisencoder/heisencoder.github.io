# heisencoder.net

The source for my personal site, live at [heisencoder.net](https://heisencoder.net) —
a home base for my writing, my projects, and links to where I am elsewhere on
the web.

Built with [Astro](https://astro.build) (plain static HTML/CSS, minimal JS) and
deployed automatically to **GitHub Pages** on every push to `main`. Design: a
fixed-width "teletype" aesthetic — mint green primary, burnt orange secondary,
IBM Plex Mono — adapted from the
[Greenbriar Technology Group](https://github.com/greenbriartechnology/greenbriartechnology.github.io)
site.

## Local development

Requires **Node.js 24+**.

```sh
npm install      # install dependencies (also enables the git hooks)
npm run dev      # dev server at http://localhost:4321
npm run build    # build to ./dist
npm run preview  # preview the production build
npm run lint     # astro check (well-formed pages + types) + eslint
npm test         # Playwright tests (first run: npx playwright install --with-deps chromium)
npm run check:links  # fetch every external link, report OK/WARN/FAIL (ad hoc)
```

## Writing a blog post

Posts are Markdown files in `src/content/blog/`. Add a new `.md` file with
frontmatter and it shows up automatically — newest first — on `/blog/` and in
the "Latest posts" teaser on the home page.

```markdown
---
title: 'My post title'
description: 'A one-line summary used in previews and search results.'
pubDate: 2026-07-08
tags: ['optional', 'tags']
# updatedDate: 2026-07-10   # optional
# draft: true               # optional — hidden from the build until removed
---

Body text goes here. Start section headings at `##` — the post title above is
already the page's single `<h1>`.
```

The frontmatter is validated by a schema (`src/content.config.ts`), so a missing
field or a malformed date fails the build instead of shipping a broken page.

## Editing content

- **Site-wide info** (name, tagline, email, social links, nav): `src/consts.ts`.
- **Home page copy**: `src/pages/index.astro`.
- **Colors / fonts / spacing**: the CSS custom properties at the top of
  `src/styles/global.css` (`--mint`, `--orange`, `--paper`, `--mono`, ...).

## Fonts

IBM Plex Mono is **self-hosted** in `public/fonts/` (woff2, weights 400/500/700,
latin + latin-ext) and declared via `@font-face` in `src/styles/global.css` — so
the site makes no render-blocking request to Google's font servers. The rules use
`font-display: optional`, so the font never swaps mid-view and contributes no
layout shift (CLS).

## Quality checks

`npm run lint` and `npm test` run in CI on every pull request
(`.github/workflows/ci.yml`) and gate merges into `main`:

- **`tests/links.spec.ts`** — crawls every page: 200 status, well-formed
  `<head>`, no broken links or images, no uncaught JS errors, valid in-page
  anchors, nav reachability, every image reserves its space (width+height or
  `aspect-ratio`), and no CSS/fonts loaded from third-party origins.
- **`tests/cls.spec.ts`** — measures Cumulative Layout Shift on every page and
  fails if it exceeds a tight budget.
- **`tests/site.spec.ts`** — behavior: the 404 page and the mobile nav toggle.
- **`tests/a11y.spec.ts`** — an [axe-core](https://github.com/dequelabs/axe-core)
  WCAG 2.1 A/AA scan on every page.

A `pre-commit` hook (`.githooks/pre-commit`, enabled by `npm install`) blocks
direct commits to the protected `main` branch — work on a feature branch and
open a PR. External links aren't checked in CI (some hosts block bots), so run
`npm run check:links` by hand when you change them.

## Deploying

Automatic: every push to `main` builds and publishes via
`.github/workflows/deploy.yml`. The custom domain lives in `public/CNAME`.

> **One-time setup:** in the repo's **Settings → Pages**, set the build source to
> **GitHub Actions** (not "Deploy from a branch") so the workflow above is what
> publishes the site.

## Project structure

```text
public/                  # copied verbatim into the build (CNAME, favicon, fonts, images)
src/
├── components/           # Nav, Footer, PageHeader
├── content/blog/         # Markdown blog posts
├── content.config.ts     # blog collection schema (Content Layer API)
├── layouts/Layout.astro  # base HTML shell, <head>, fonts, nav + footer
├── pages/                # routes (index, blog/index, blog/[...slug], 404)
├── styles/global.css     # theme + all shared styles
└── consts.ts             # site info, social links, nav
tests/                    # Playwright tests (structure, behavior, a11y, CLS)
scripts/                  # ad-hoc external link checker
.github/workflows/        # ci.yml (lint + tests), deploy.yml (build + deploy)
```

## License

© Matt Ball. All rights reserved.
