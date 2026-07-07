---
title: 'Hello, world'
description: "A first post — what this site is, and what I plan to do with it."
pubDate: 2026-07-07
tags: ['meta']
---

Welcome, and thanks for stopping by. This is the first post on the new
heisencoder.net — a small, fast, statically generated home for my writing and
projects.

## Why a new site?

I wanted one place I actually control that links out to everywhere else I live
online, and that gives me somewhere to write when I have something worth saying.
No tracking, no clutter — just a fast page and some words.

## What to expect

I'll write about the things I build and the problems I run into along the way:

- Notes on software and the occasional deep dive
- Write-ups of small side projects
- Whatever else I'm tinkering with

## How this gets published

Posts are plain Markdown files in `src/content/blog/`. To add one, I drop a new
`.md` file in that folder with a bit of frontmatter:

```markdown
---
title: 'My next post'
description: 'A one-line summary for previews and search.'
pubDate: 2026-07-08
tags: ['example']
---

Body text goes here.
```

Push to `main`, and GitHub Actions builds the site and deploys it. That's the
whole workflow.

More soon.
