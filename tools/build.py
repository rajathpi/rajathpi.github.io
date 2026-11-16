"""Build the blog from Markdown.

    python tools/build.py

Reads posts/*.md and writes:
  blogs/<slug>.html   one page per post (from templates/post.html)
  blogs.html          the writing list, grouped by topic (from templates/blogs.html)
  feed.xml            RSS feed of all posts
  index.html          only the Writing list between <!-- writing:start --> and <!-- writing:end -->

Post file = a small header, then Markdown. Raw HTML (figures from blogs/_figures.html) is allowed.

    ---
    title: Kaggriculture: How Switching On One Disabled Setting Beat the Public Bots
    description: One sentence for search engines and link previews.
    meta: Kaggriculture (Kaggle) · 6 min read          <- grey line under the title
    date: 2026-10                                     <- sorts the lists; shown as "Oct 2026"
    topic: Game agents                                <- section on the writing page (see TOPICS)
    list: Kaggriculture: how switching on one ...     <- optional shorter title for the lists
    summary: 786 of 10,148. The whole ladder ...      <- one line under the title in the list
    home: The whole ladder ran one shared action tape. <- optional; puts the post on the homepage
    archived: yes                                     <- optional; hides it in a footnote
    ---

Needs: pip install markdown
"""
import datetime, html, pathlib, re, sys

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOPICS = ["Reasoning (ARC Prize)", "Game agents", "Applied ML", "Open source", "Notes"]
SITE = "https://rajathpi.github.io"
HOME_POSTS = 6  # newest posts with a `home:` line shown on the homepage


def read_post(path):
    text = path.read_text(encoding="utf8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text.replace("\r\n", "\n"), re.S)
    if not m:
        sys.exit(f"{path.name}: missing the --- header --- block")
    head = {}
    for line in m.group(1).splitlines():
        if line.strip():
            k, _, v = line.partition(":")
            head[k.strip()] = v.strip()
    for need in ("title", "description", "meta", "date", "topic"):
        if need not in head:
            sys.exit(f"{path.name}: header needs '{need}:'")
    if head["topic"] not in TOPICS and not head.get("archived"):
        sys.exit(f"{path.name}: topic must be one of {TOPICS}")
    head["slug"] = path.stem
    head["body"] = markdown.markdown(m.group(2), extensions=["fenced_code", "tables"])
    return head


def month(d):
    return datetime.date(int(d[:4]), int(d[5:7]), 1).strftime("%b %Y")


def fill(template, **kv):
    for k, v in kv.items():
        template = template.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{\w+\}\}", template)
    if left:
        sys.exit(f"template slot not filled: {left}")
    return template


def main():
    post_t = (ROOT / "templates/post.html").read_text(encoding="utf8")
    posts = sorted((read_post(p) for p in (ROOT / "posts").glob("*.md")), key=lambda p: p["date"], reverse=True)
    esc = html.escape

    for p in posts:
        archived = '<p class="archived">Archived: an early notebook, kept so old links keep working.</p>\n' if p.get("archived") else ""
        robots = '<meta name="robots" content="noindex">\n' if p.get("archived") else ""
        page = fill(post_t, SLUG=p["slug"], TITLE=esc(p["title"]), DESC=esc(p["description"]), ROBOTS=robots, H1=esc(p["title"]),
                    META=esc(p["meta"]), ARCHIVED=archived, BODY=p["body"].strip())
        (ROOT / "blogs" / f"{p['slug']}.html").write_text(page, encoding="utf8", newline="\n")

    def item(p, line, with_date=True):
        d = f'<span class="d">{month(p["date"])}</span> ' if with_date else ""
        s = f'<span class="s">{esc(line)}</span>' if line else ""
        return f'    <li>{d}<a href="blogs/{p["slug"]}.html">{esc(p.get("list") or p["title"])}</a>{s}</li>'

    sections = []
    for topic in TOPICS:
        rows = [item(p, p.get("summary", "")) for p in posts if p["topic"] == topic and not p.get("archived")]
        if rows:
            sections.append(f'  <h2>{esc(topic)}</h2>\n  <ul class="plain">\n' + "\n".join(rows) + "\n  </ul>")
    old = [f'<a href="blogs/{p["slug"]}.html">{esc(p.get("list") or p["title"])}</a>' for p in posts if p.get("archived")]
    if old:
        sections.append(f'  <p class="dim" style="margin-top:36px;font-size:15px">Archived early notebooks: {", ".join(old)}.</p>')
    blogs_t = (ROOT / "templates/blogs.html").read_text(encoding="utf8")
    (ROOT / "blogs.html").write_text(fill(blogs_t, LISTS="\n\n".join(sections)), encoding="utf8", newline="\n")

    home = [p for p in posts if p.get("home") and not p.get("archived")][:HOME_POSTS]
    rows = "\n".join(f'    <li><a href="blogs/{p["slug"]}.html">{esc(p.get("list") or p["title"])}</a>'
                     f'<span class="s">{esc(p["home"])} {p["date"][:4]}</span></li>' for p in home)
    idx = ROOT / "index.html"
    t = idx.read_text(encoding="utf8")
    new = re.sub(r"(<!-- writing:start -->\n).*?(\s*<!-- writing:end -->)",
                 lambda m: m.group(1) + '  <ul class="plain">\n' + rows + "\n  </ul>" + m.group(2), t, flags=re.S)
    if new == t and "<!-- writing:start -->" not in t:
        sys.exit("index.html: add <!-- writing:start --> and <!-- writing:end --> around the Writing list")
    idx.write_text(new, encoding="utf8", newline="\n")
    # RSS feed of every non-archived post
    def rfc822(d):
        return datetime.date(int(d[:4]), int(d[5:7]), 1).strftime("%a, %d %b %Y 00:00:00 +0000")
    items = "".join(
        f"""  <item>
    <title>{esc(p['title'])}</title>
    <link>{SITE}/blogs/{p['slug']}.html</link>
    <guid>{SITE}/blogs/{p['slug']}.html</guid>
    <pubDate>{rfc822(p['date'])}</pubDate>
    <description>{esc(p.get('summary') or p['description'])}</description>
  </item>
""" for p in posts if not p.get("archived"))
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Rajath Pai, writing</title>
  <link>{SITE}/blogs.html</link>
  <description>Short write-ups of ML competitions and notes, each ending with what to reuse.</description>
{items}</channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(feed, encoding="utf8", newline="\n")
    print(f"built {len(posts)} posts, blogs.html, index.html, feed.xml")


if __name__ == "__main__":
    main()
