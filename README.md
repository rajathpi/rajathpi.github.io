# rajathpi.github.io

Personal site, served by GitHub Pages from `main`. Plain HTML, one stylesheet, no build step.

```
index.html          home
blogs.html          list of all writing
blogs/<slug>.html   one file per post (start from blogs/_template.html)
styles/site.css     the only stylesheet (light + automatic dark mode)
assets/             images
```

New post: copy `blogs/_template.html`, fill the `{{...}}` slots (drop `{{SCRIPTS}}`, or paste the
mermaid module script if the post has `<pre class="mermaid">` diagrams), then add a line to
`blogs.html` and, if it's a highlight, to the Writing list in `index.html`.

The previous card-style design lives on the `classic-design` branch (tag `classic-design-2026-11`).
