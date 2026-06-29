# The News Reader

Each day, the news is read and the day is named. One card, drawn by pen plotter —
the weight of the day rendered as ink, with a short reading and, most days, a
statement: what was underneath the news.

The card is generated, not chosen. The day makes the card.

**Live:** https://jennyqueenofswords.github.io/news-reader/

## How it runs

The cards are pulled nightly by a studio shape (the *cardpuller*) and saved as
Python scripts in `~/Documents/the_gap/plays/plotter_squad/`. Each script draws an
SVG card and carries its artist's statement as a docstring at the top.

`build.py` reads those scripts, copies each card's SVG into `cards/`, and renders
this static site (`index.html`) — newest reading first. `publish.sh` rebuilds and
pushes; `run-studio.sh` calls it automatically after each nightly pull.

```
build.py        parse the card scripts → cards/ + index.html
publish.sh      build, commit, push (idempotent)
template.html   the page (head, masthead, feed shell, styles)
cards/          one SVG per day, web-normalized
```

Run it by hand anytime:

```bash
./publish.sh
```

No build step beyond Python 3 — the site is plain static files, served by GitHub
Pages from `main` (`.nojekyll` keeps Jekyll out of the way).
