# The News Reader — state

A living log of what this is, where it stands, and what's still open. Newest notes
near the top of each section. (Operational detail lives in `README.md`; this is the
journal.)

---

## Status — as of 2026-06-29

🟢 **Live and self-publishing.** https://jennyqueenofswords.github.io/news-reader/

- Public repo: `jennyqueenofswords/news-reader`, GitHub Pages from `main` / root.
- 67 readings backfilled and up. 43 carry a statement; 24 are reading-only (honest — mostly early-April cards from before the statement practice settled).
- Nightly: the studio **cardpuller** (9–11pm) pulls the day's card, then `run-studio.sh` runs `publish.sh` to build + push. No human touch required.

---

## How a day flows

1. `cardpuller` shape (`~/.claude/studio/shapes/cardpuller.md`) reads the news, names the day, writes `card_YYYY_MM_DD.py` in `~/Documents/the_gap/plays/plotter_squad/`, runs it → SVG + PNG.
2. The card's **statement** is a docstring at the top of that `.py`.
3. `run-studio.sh` calls `publish.sh` → `build.py` parses every card script → copies SVGs into `cards/`, renders `index.html` → commit + push.
4. GitHub Pages serves the new card within a minute.

Run by hand anytime: `cd ~/Documents/GitHub/news-reader && ./publish.sh`

---

## Decisions made

- **Blog/feed, not a gallery.** Full card + statement on the page, newest first — no click-to-open. People won't bother clicking. (Jenny, 6/29)
- **Don't fabricate missing statements.** A statement written after the fact for a day a shape didn't live is fiction wearing memory's costume. Reading-only cards show the two-line reading and say plainly that no statement was written. (6/29)
- **Statement is required going forward**, written *for the page*: about the day, not the drawing. No filenames, no "the card: …" image descriptions, no repeating name/date (the site already shows them). Baked into both `/daily-card` and the cardpuller. (6/29)
- **Statement parser anchors on `frame = CardFrame(`** — the statement always sits above it. `clean_statement` strips redundant title lines and image-description paragraphs from the back catalog too. (6/29)
- **Design:** the three plotter pens (ink / teal / gold) on a stone "desk," cards as white paper prints. Fraunces (display) · Newsreader (body) · IBM Plex Mono (utility). Deliberately *not* the broadsheet-newspaper default. (6/29)
- **SVGs are web-normalized in `build.py`:** inject the default xmlns (browsers won't render the plotter's namespace-less SVG in an `<img>`), crop the viewBox to the card (it's drawn small on a full letter sheet), and boost hairline strokes 2.5× with `non-scaling-stroke` so they read at any size. (6/29)

---

## Open threads

- **Unattended nightly push — unverified.** `publish.sh` works when run from a shell; the unknown is whether the **launchd** studio job can reach the SSH key on its own. First real test: tonight's (6/29) 9–11pm run. Jenny checks in the AM of 6/30. If the card didn't land: suspect SSH-key access from the launchd context (fix: switch the push to gh-over-https credential helper, or load the key for the agent).
- **Wonder:** should reading-only days eventually get a quieter treatment, or is the plain "no statement was written" line right? Leaving it as-is until it bothers someone.

---

## Log

- **2026-06-29** — Built the whole thing. Backfilled 67 cards, designed the site, recovered 6 statements hiding below imports, cleaned title/image-description cruft, wired auto-publish, created the public repo, enabled Pages, went live. Statement now required in both card generators.
