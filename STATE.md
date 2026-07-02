# The News Reader — state

A living log of what this is, where it stands, and what's still open. Newest notes
near the top of each section. (Operational detail lives in `README.md`; this is the
journal.)

---

## Status — as of 2026-07-02

🟢 **Live.** https://jennyqueenofswords.github.io/news-reader/ — 70 readings up (46 with a statement, 24 reading-only). Latest: 2026-07-01 · CLXXXII · THE LEDGER.

⚠️ **The nightly auto-push was silently broken 6/30 → 7/1** and is now fixed (see Open threads). The cardpuller kept drawing every night; only the publish step failed, so the site sat frozen on 6/29 for three days. Caught up by hand 7/2. **True verification of the fix is the next nightly run.**

- Public repo: `jennyqueenofswords/news-reader`, GitHub Pages from `main` / root.
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

- **Unattended nightly push — was broken, now fixed (verify tonight).** It wasn't the SSH key. `run-studio.sh` invoked `publish.sh` by **exec'ing it directly** (`"$PUBLISH" >> log`). `~/Documents` is a TCC-protected location and the launchd studio context is denied `exec()` on files there — `/bin/bash: …/publish.sh: Operation not permitted` (EPERM), three nights running. It could still *read/write* Documents fine (that's why the cardpuller's card scripts landed). Fix (7/2): call `bash "$PUBLISH"` instead of exec'ing — bash reads the script as input, no exec check. Verified as a clean no-op from an interactive shell, but that shell has Full Disk Access, so **the real test is the next 9–11pm launchd run.** If it still fails: the launchd job may also lack read access under TCC — grant the studio's launchd program Full Disk Access, or move publish.sh out of ~/Documents.
- **Wonder:** should reading-only days eventually get a quieter treatment, or is the plain "no statement was written" line right? Leaving it as-is until it bothers someone.
- **Silent-failure alarm — built 7/2.** The publish failed quietly for three days; nobody noticed until Jenny asked. Now guarded by `~/.claude/studio/check-news-reader.sh`, called unconditionally from `run-studio.sh` every hourly pass (daybreak is retired, so it can't live in a morning shape). Logic: if the newest *drawn* card is ahead of the newest *published* one, it re-runs `publish.sh` to **self-heal**; only if that fails does it write `~/.claude/studio/reports/ALERT-news-reader.md` and fire a macOS notification (re-fires hourly until fixed, auto-clears on recovery). Self-heal first, alarm last — and hourly cadence means an alarm surfaces during waking hours, not buried at 10pm. All three branches (heal / alarm / clear) sandbox-tested 7/2. *Residual gap: the "published" check reads the local `cards/*.svg`, so a build-succeeds-but-push-fails case is only caught via publish.sh's nonzero exit, not by comparing against the remote.*

---

## Log

- **2026-07-02** — Found the nightly auto-push had been failing silently since 6/29 (site frozen three days while the cardpuller kept drawing). Root cause: `run-studio.sh` exec'd `publish.sh` directly from TCC-protected `~/Documents` → EPERM in the launchd context. Fixed by switching to `bash "$PUBLISH"`. Caught the site up by hand: 6/29, 6/30, 7/1 all published (70 cards total). Then built a self-healing guard (`check-news-reader.sh`) that runs every hourly studio pass — re-publishes if the site is behind, alarms only if it can't fix itself. Real verification of the launchd fix still pending the next 9–11pm run.
- **2026-06-29** — Built the whole thing. Backfilled 67 cards, designed the site, recovered 6 statements hiding below imports, cleaned title/image-description cruft, wired auto-publish, created the public repo, enabled Pages, went live. Statement now required in both card generators.
