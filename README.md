# rajathpi.github.io

Personal site, served by GitHub Pages from `main`. Plain HTML, one stylesheet, light only.

## Edit a post
1. Open `posts/<slug>.md` and edit the Markdown (the header at the top holds title, date, topic, list lines).
2. Run `python tools/build.py` (needs `pip install markdown` once).
3. Check: `python tools/check_pages.py . blogs/<slug>.html` must print "OK, no issues".
4. Commit both the `.md` and the generated `.html`.

## New post
Copy any file in `posts/`, rename it (the file name becomes the URL: `blogs/<name>.html`), change the
header, write, build. Set `home:` in the header to also show it on the homepage. Figures: copy blocks from
`blogs/_figures.html` (flow, bars, vs, stats, timeline) straight into the Markdown.

## What is where
```
index.html            home page; edit by hand (its Writing list is filled in by the build)
posts/*.md            every post, in Markdown  <- edit these
blogs/*.html          generated pages (don't edit by hand)
blogs.html            generated writing list (frame in templates/blogs.html)
templates/            page frames for posts and the writing list
styles/site.css       the only stylesheet, incl. the figure kit
scripts/figs.js       animates figures once when they scroll into view
blogs/_figures.html   figure kit reference
tools/build.py        posts/*.md -> blogs/*.html, blogs.html, homepage Writing list
tools/check_pages.py  layout check at 375 + 1280 px (overlap, overflow, contrast, figures appear)
assets/               images
```

The previous card-style design lives on the `classic-design` branch (tag `classic-design-2026-11`).
