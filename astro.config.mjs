// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Canonical site URL. Used for sitemap, canonical tags, and absolute links.
  site: 'https://heisencoder.net',
  // Served from the domain root on GitHub Pages (custom domain), so no base path.
  base: '/',
  // Lenient, matching how GitHub Pages actually serves the site: both /blog and
  // /blog/ resolve (the former via a 301 to the latter). Our own internal links
  // all use the trailing-slash form to skip that redirect — the links test
  // enforces this — but a stray slash-less URL still works rather than 404ing.
  trailingSlash: 'ignore',
  integrations: [sitemap()],
  markdown: {
    // Emit both a light and a dark syntax theme as CSS custom properties
    // (--shiki-light / --shiki-dark and their -bg variants) rather than a
    // single hard-coded color set. global.css then selects the set that
    // matches the active theme, so fenced code blocks follow light/dark mode.
    shikiConfig: {
      themes: { light: 'github-light', dark: 'github-dark' },
      defaultColor: false,
    },
  },
});
