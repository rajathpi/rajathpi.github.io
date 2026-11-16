# rajathpi.github.io

Personal site, served by GitHub Pages from `main`. Plain HTML, one stylesheet, no build step.

```
index.html          home
blogs.html          list of all writing
blogs/<slug>.html   one file per post (start from blogs/_template.html)
styles/site.css     the only stylesheet (light + automatic dark mode), incl. the figure kit
scripts/figs.js     animates figures once when they scroll into view
blogs/_figures.html figure kit: flow, bars, vs, stats, timeline — copy-paste markup
tools/check_pages.py  layout check: 375 + 1280 px, light + dark (overlap, overflow, contrast)
assets/             images
```

New post: copy `blogs/_template.html`, fill the `{{...}}` slots, use figures from `blogs/_figures.html`,
then add a line to `blogs.html` (and to the Writing list in `index.html` if it's a highlight).
Before pushing: `python tools/check_pages.py . blogs/<post>.html` must print "OK, no issues".

The previous card-style design lives on the `classic-design` branch (tag `classic-design-2026-11`).
