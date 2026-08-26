# The News Reader — state

What this is, where it stands, what's still open. Describes what IS, not what
happened — the temporal record is the `## Log` at the bottom, newest first.
(Operational detail lives in `README.md`; this is the state.)

---

## Status — as of 2026-08-26

🟢 **Live.** https://jennyqueenofswords.github.io/news-reader/ — 116 cards, current
through 2026-08-25. Public repo `jennyqueenofswords/news-reader`, GitHub Pages from
`main` / root.

The pipeline is proven unattended: it drew, published and pushed through a full
redesign and five consecutive clean nights without intervention.

**Coverage is imperfect and that's recorded, not hidden.** 8 missing days between
07-09 and today: 07-24, 07-25, 07-26, 07-27, 08-06, 08-14, 08-15, 08-19. Two causes
are confirmed (08-06 `ENOTFOUND`, 08-19 `SSL certificate hostname mismatch` — both
stale network state after a sleep/wake, both now retried). 07-23 died on "connection
closed mid-response." **The 07-24→07-27 cluster is unexplained** — those runs logged
no error and still produced no card. Worth a real look if it recurs. Per the
no-fabrication rule, missing days stay missing.

---

## How a day flows

1. Mac wakes 21:00 (`pmset repeat wakeorpoweron`), studio fires 21:01 (launchd
   `StartCalendarInterval` minute :01).
2. `cardpuller` shape (`~/.claude/studio/shapes/cardpuller.md`, run as `claude` via
   `run-shape.sh`) reads the news, records its sources, writes
   `card_YYYY_MM_DD.py` in `~/Documents/the_gap/plays/plotter_squad/`, runs it → SVG + PNG.
3. **As its required final step the cardpuller runs `publish.sh` itself** →
   `build.py` parses every card script → SVGs into `cards/`, renders `index.html` →
   commit + push. It runs here because this Claude process has the Documents access
   bare bash lacks (see TCC, below).
4. GitHub Pages serves within a minute.
5. Every hourly studio pass, `check-news-reader.sh` curls the live site and alarms if
   it has fallen behind yesterday.

**In practice cards land mid-morning, not at 21:05.** The run starts on time, then
clamshell sleep suspends it until the lid opens. `caffeinate -i` cannot defeat a
closed lid and nothing else will either; this is accepted, not broken. The tripwire's
grace window already tolerates it.

By hand anytime: `cd ~/Documents/GitHub/news-reader && ./publish.sh`

---

## Decisions made

- **The card is the subject; the page stops transcribing it.** (Jenny, 8/21) Five of
  the six per-entry text elements — serial, name, keywords, couplet, roman date —
  are already drawn on the card in plotter strokes. Only the statement is unique to
  the page, so the statement carries the entry and the rest was cut. The name
  survives on the dateline `<h2>` for document outline, anchors and search.
- **Newspaper archive, monochrome UI.** (8/21) **This reverses the 6/29 decision**
  that the design should be "deliberately *not* the broadsheet-newspaper default."
  The old teal/gold chrome competed with the art on the art's own frequencies — the
  plots draw in ink, teal, gold and rust. UI is now black-on-newsprint so the pens
  own all the colour. No webfonts at all.
- **Sources are recorded and published.** (8/26) `SOURCES = [(publisher, label, url)]`
  per card. The label exists because a statement can braid two unrelated stories and
  a reader needs to know which link is which. **URLs are never invented** — a missing
  source costs nothing, a plausible dead link in an archive is corrosive.
- **Retry only on connection failures.** (8/21) Budget caps and tool errors are never
  retried, so a partly-finished draw can't be duplicated into two cards for one day.
- **Blog/feed, not a gallery.** (Jenny, 6/29) Full card + statement, newest first.
- **Don't fabricate missing statements or missing days.** (6/29) A statement written
  after the fact for a day nobody lived is fiction wearing memory's costume.
  Reading-only cards say plainly that no statement was written.
- **Statement parser anchors on `frame = CardFrame(`** — everything above that line is
  the statement. **This is why `SOURCES` must sit below it**; above, it gets published
  as prose.
- **SVGs are web-normalized in `build.py`** — inject the default xmlns, crop the
  viewBox to the card, boost hairline strokes 2.5× with `non-scaling-stroke`.
- **The double dash stays.** (Jenny, 8/26) ` -- ` in statements is typewriter
  register, not a defect. It's the minority (9 of 77 dashed statements) and the
  archive stays mixed rather than being retroactively normalised.

---

## Environment traps

- **TCC / Full Disk Access is per-binary, and it bites two different ways.**
  The launchd/bash studio context cannot read `~/Documents`, so any bash-based
  publish silently no-ops — this caused three multi-day outages (6/29–7/1, 7/3–7/6)
  and is why publishing lives inside the cardpuller's Claude run. **And the inverse:**
  TCC records Documents access per Claude Code *version binary*
  (`~/.local/share/claude/versions/2.1.x`), so when Claude Code auto-updates under a
  long-running session, that session starts failing `EPERM` on reads while `ls` still
  works and FDA-gated paths still read fine. Nothing is misconfigured — restart the
  session. Happened 8/22 and 8/26. Check with:
  `sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db "SELECT client,auth_value FROM access WHERE service='kTCCServiceSystemPolicyDocumentsFolder' ORDER BY last_modified DESC LIMIT 5;"`
- **`publish.sh` stages the whole working tree.** Anything left in this directory gets
  committed and served publicly by the next nightly draw. Two `.bak` files sat live on
  the site 8/22–8/26 that way. Do scratch work outside the repo.
- **Never diagnose a studio failure by running it in your own session** — an
  interactive session usually has access the launchd path doesn't, and it will tell
  you everything is fine.

---

## Open threads

- **First sources land tomorrow (8/27).** Worth checking the labels read at a glance
  and the URLs are real. The build drops a malformed URL but cannot tell a plausible
  wrong link from a right one.
- **The 07-24→07-27 four-day gap is unexplained.** Logs show runs with no error and
  no card. If it recurs, that's the thread to pull.
- **The couplet is no longer anywhere on the page as text** — only inside the card
  art as plotter strokes, so it isn't selectable, searchable or readable by a screen
  reader. Accepted for now; the alt text carries the card's name.
- **The card no longer pins beside a long statement.** Note that it never actually
  did: `position: sticky` was set for the site's whole life with zero travel
  (`align-items: start` makes the art column exactly the card's height). Declined on
  8/22 — only 14% of entries have text taller than the card, and scroll-driven motion
  is the register the restyle removed.
- **Wonder:** should reading-only days get a quieter treatment, or is the plain "no
  statement was written" line right? Leaving it until it bothers someone.

---

## Log

- **2026-08-26** — Sources. `cardpuller.md` gains step 6: record
  `(publisher, label, url)` per story, never invent a URL. `build.py` gains
  `extract_sources()` — `ast.literal_eval`, never `exec`; drops non-http URLs, wrong
  shapes, blank publishers and the prompt's unfilled `...` placeholder; caps at 4.
  Renders as a mono citation row under the statement. Also fixed the masthead byline
  URL (`queenofswords.ai` → `.co` — the old one didn't resolve at all) and removed two
  `.bak` files that `publish.sh` had swept in and Pages had been serving since 8/22.
  Found in passing: **this file had been stale for seven weeks** while its content was
  being duplicated into `~/.claude` memory and a handoff. That's the duplication the
  state-file model exists to prevent.
- **2026-08-21** — The restyle, and the reason for it. Jenny asked why the site was
  stale; cause was one dead run (8/19 21:01, stale TLS after a sleep/wake, no retry).
  Fixed with a narrow retry in `run-shape.sh` plus a `set -e` bug that had been
  swallowing those failures so completely they left no exit line, no report, and
  leaked temp files. Then a full page redesign — bigger card, no display headline,
  merged mono title, newsprint grey `#f1f0ed`, statement carrying the entry, 17 rules
  of dead CSS removed. Separately: `build.py` now emits statements as real `<p>`
  paragraphs — 47 of 87 were rendering as ragged mid-sentence stubs because
  `white-space: pre-line` honoured the cardpuller's typing. Every design call was
  Jenny's; the useful contribution was measurement.
- **2026-07-09** — First real miss the working alarm caught. Not TCC, not publish: the
  cardpuller hit its `$2 --max-budget-usd` ceiling and died before drawing (folding
  publish into the run made $2 too tight). Raised to **$4** — a ceiling, not a target.
  The studio runs on Jenny's Claude Code subscription, **not** a metered API key, so
  that number is a quota guardrail, not a dollar bill. Jenny's calls: 7/8 left as an
  honest gap, 7/9 drawn by the scheduled run. Added a snooze to
  `check-news-reader.sh` (`reports/SNOOZE-news-reader` = a date).
- **2026-07-07** — Third outage (7/3–7/6 drawn but unpublished, no alarm). Found the
  true root cause behind all three: **the launchd/bash context has no Full Disk
  Access to `~/Documents`**, so every bash-based publish silently no-op'd and only
  ever "worked" when a human with FDA ran it by hand. Rebuilt: publishing folded into
  the cardpuller's own Claude run, alarm rewritten web-only. **Zero new OS
  permissions.**
- **2026-07-03** — The Mac slept through the 9–11pm window, and `run-studio.sh` did
  `exit 0` before reaching the guard whenever no shape was scheduled — so the guard
  only ran in the cardpuller window, never on the 21 hourly passes that would have
  caught it. Extracted `news_reader_guard()`, called on both paths. Added
  `caffeinate -i -w $$` and switched launchd to `StartCalendarInterval`.
- **2026-07-02** — Found the nightly push had been failing silently since 6/29 (site
  frozen three days while the cardpuller kept drawing). `run-studio.sh` exec'd
  `publish.sh` directly from TCC-protected `~/Documents` → EPERM. Fixed with
  `bash "$PUBLISH"`. Caught up 6/29–7/1 by hand. Built the self-healing guard.
- **2026-06-29** — Built the whole thing. Backfilled 67 cards, designed the site,
  recovered 6 statements hiding below imports, wired auto-publish, created the public
  repo, enabled Pages, went live.
