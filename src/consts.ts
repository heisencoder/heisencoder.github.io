// Central site metadata — edit these in one place.
export const SITE = {
  name: 'Matt Ball',
  handle: 'heisencoder',
  domain: 'heisencoder.net',
  url: 'https://heisencoder.net',
  tagline: 'Software engineer, tinkerer, and occasional blogger.',
  description:
    "Matt Ball (heisencoder) — software engineer. Home base for my writing, my projects, and links to where I am elsewhere on the web.",
};

// Where to find me elsewhere on the web. Rendered as cards on the home page and
// as links in the footer.
export const SOCIAL = [
  {
    label: 'GitHub',
    handle: '@heisencoder',
    href: 'https://github.com/heisencoder/',
    blurb: 'Code, side projects, and the source for this site.',
  },
  {
    label: 'LinkedIn',
    handle: 'matthewvball',
    href: 'https://www.linkedin.com/in/matthewvball/',
    blurb: 'Work history, and the more professional side of things.',
  },
];

// Internal hrefs keep a trailing slash so they match the files GitHub Pages
// actually serves (e.g. /blog/index.html). Linking to /blog would cost every
// visitor a 301 redirect to /blog/ on each click.
export const NAV = [
  { href: '/', label: 'Home' },
  { href: '/blog/', label: 'Blog' },
];
