---
title: 'How this site is built'
description: 'A quick tour of the stack: Astro 7, static HTML, and GitHub Pages.'
pubDate: 2026-07-06
tags: ['astro', 'meta']
---

This site is deliberately boring, in the good way. Here's the short version of
how it's put together.

## The stack

- **[Astro 7](https://astro.build)** builds everything to static HTML at build
  time. There's almost no JavaScript shipped to the browser — just a tiny bit
  for the mobile menu and the typewriter effect on the home page.
- **IBM Plex Mono**, self-hosted, for that fixed-width teletype look. No
  render-blocking trip to a font CDN.
- **GitHub Pages** hosts the output, deployed automatically by GitHub Actions on
  every push to `main`.

## Content collections

Blog posts are Markdown files validated by a schema, so a missing `title` or a
malformed date fails the build instead of shipping broken. That means I can
write in plain text and trust the tooling to keep me honest.

## Quality gates

Every pull request runs a small suite of Playwright checks: broken-link
crawling, an accessibility scan, and a layout-stability budget. If a change
would ship a janky or inaccessible page, CI catches it first.

That's it. Simple enough to forget about, which is exactly the point.
