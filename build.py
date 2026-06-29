#!/usr/bin/env python3
"""
The News Reader — static site builder.

Reads the daily card scripts in plotter_squad/, extracts each card's metadata
and artist's statement, copies its SVG into cards/, and renders index.html.

A card is one day. The day makes the card. Run after each new pull.
"""
import re, os, glob, json, shutil, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.expanduser('~/Documents/the_gap/plays/plotter_squad')
CARDS_OUT = os.path.join(HERE, 'cards')

# ─────────────────────────────────────────────────────────── parsing ──

def kwarg(text, key):
    m = re.search(rf"{key}\s*=\s*(['\"])(.*?)\1", text)
    return m.group(2).strip() if m else None

def extract_statement(text):
    """The artist's statement always sits ABOVE the `frame = CardFrame(...)` call
    (everything below it is drawing code/comments). Within that prefix it's either
    a triple-quoted docstring or a run of # comments — and it may come after the
    import lines, not just at the very top. Returns the prose, or None."""
    m = re.search(r'CardFrame\s*\(', text)
    # the import of CardFrame has no paren; the instantiation does. fall back to whole file.
    prefix = text[:m.start()] if (m and '(' in text[m.start():m.start()+12]) else text
    # 1. a triple-quoted docstring anywhere in the prefix
    dm = re.search(r'("""|\'\'\')(.*?)\1', prefix, re.DOTALL)
    if dm and len(dm.group(2).strip()) > 40:
        return re.sub(r'\n{3,}', '\n\n', dm.group(2).strip())
    # 2. comment lines in the prefix (blank-comment lines become paragraph breaks)
    lines = []
    for ln in prefix.splitlines():
        st = ln.strip()
        if st.startswith('#!') or st.startswith('# -*-'):
            continue
        if st.startswith('#'):
            lines.append(st.lstrip('#').strip())
        elif st == '' and lines:
            lines.append('')
    block = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines).strip())
    return block if len(block) > 40 else None

def save_prefix(text):
    """Resolve the prefix passed to frame.save(svg, X) — literal or a variable
    assigned 'out = ...'. Returns the basename used for {prefix}_card.svg."""
    m = re.search(r"frame\.save\(\s*svg\s*,\s*(['\"])(.*?)\1", text)
    if m:
        return os.path.basename(m.group(2))
    m = re.search(r"frame\.save\(\s*svg\s*,\s*([A-Za-z_]\w*)\s*\)", text)
    if m:
        var = m.group(1)
        vm = re.search(rf"{var}\s*=\s*(['\"])(.*?)\1", text)
        if vm:
            return os.path.basename(vm.group(2))
    return None

MONTHS = ['January','February','March','April','May','June','July','August',
          'September','October','November','December']

def clean_statement(stmt, name):
    """The site shows the card name, date, and image already, so strip the two
    kinds of redundancy older statements carry: a leading title line ("THE NARROWS
    — June 23, 2026") and any paragraph that describes the drawing ("The card: …").
    New cards are written without these (see the daily-card skill), but this keeps
    the whole archive clean."""
    if not stmt:
        return stmt
    name_up = (name or '').upper()
    # 1. drop a leading line that is just the card's name (± a date tail)
    lines = stmt.split('\n')
    if lines:
        head = re.split(r'[—–\-·:]', lines[0].strip())[0].strip().upper()
        if head and head == name_up:
            lines.pop(0)
            while lines and not lines[0].strip():
                lines.pop(0)
    stmt = '\n'.join(lines)
    # 2. drop any paragraph that describes the image rather than the day
    paras = re.split(r'\n\s*\n', stmt)
    paras = [p for p in paras
             if not re.match(r'^\s*(the card|the image)\b[:\s]', p, re.I)]
    return re.sub(r'\n{3,}', '\n\n', '\n\n'.join(paras).strip()) or None

def parse_all():
    records = []
    for path in sorted(glob.glob(os.path.join(SRC, 'card_2026_*.py'))):
        fn = os.path.basename(path)
        m = re.match(r'card_(\d{4})_(\d{2})_(\d{2})(_first)?\.py', fn)
        if not m or m.group(4):
            continue  # skip superseded _first pulls
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        text = open(path, encoding='utf-8', errors='replace').read()
        prefix = save_prefix(text)
        svg_src = None
        if prefix:
            cand = os.path.join(SRC, f'{prefix}_card.svg')
            if os.path.exists(cand):
                svg_src = cand
        date = datetime.date(y, mo, d)
        records.append({
            'date': date.isoformat(),
            'date_long': f'{MONTHS[mo-1]} {d}, {y}',
            'weekday': date.strftime('%A'),
            'number': kwarg(text, 'number') or '',
            'name': kwarg(text, 'name') or '',
            'keywords': kwarg(text, 'keywords') or '',
            'reading_1': kwarg(text, 'reading_1') or '',
            'reading_2': kwarg(text, 'reading_2') or '',
            'date_roman': kwarg(text, 'date_roman') or '',
            'statement': clean_statement(extract_statement(text), kwarg(text, 'name')),
            '_svg_src': svg_src,
        })
    records.sort(key=lambda r: r['date'], reverse=True)
    return records

# ─────────────────────────────────────────────────────────── build ──

SVG_NS = 'http://www.w3.org/2000/svg'

STROKE_BOOST = 2.5  # plotter hairlines (0.25–0.55) vanish on screen; give the pen weight

def normalize_svg(text):
    """Prepare a plotter SVG for the web:
    1. inject the default SVG namespace (the frame only declares inkscape's),
       or browsers won't render it in an <img>;
    2. boost hairline stroke widths and make them non-scaling, so the ink reads
       the same whether the card is a thumbnail or full size."""
    if 'xmlns="' not in text:
        text = re.sub(r'<svg\b', f'<svg xmlns="{SVG_NS}"', text, count=1)
    text = re.sub(
        r'stroke-width="([0-9.]+)"',
        lambda m: f'stroke-width="{float(m.group(1)) * STROKE_BOOST:.3g}"',
        text)
    # The card is drawn as a 3.5×5.5in tarot card (frame ≈ 240–576 × 264–792)
    # positioned on a full letter sheet. Crop the viewBox to the card + a small
    # margin so it fills its space on the web, and drop the physical width/height
    # so CSS controls the size.
    text = re.sub(r'\s(width|height)="[^"]*"', '', text, count=2)
    text = re.sub(r'viewBox="[^"]*"', 'viewBox="204 228 408 600"', text, count=1)
    # constant on-screen stroke width at any scale
    text = re.sub(r'(<svg\b[^>]*>)', r'\1<style>*{vector-effect:non-scaling-stroke}</style>',
                  text, count=1)
    return text

def copy_svgs(records):
    os.makedirs(CARDS_OUT, exist_ok=True)
    kept = []
    for r in records:
        if not r['_svg_src']:
            continue
        dst_name = f"{r['date']}.svg"
        text = open(r['_svg_src'], encoding='utf-8', errors='replace').read()
        with open(os.path.join(CARDS_OUT, dst_name), 'w', encoding='utf-8') as f:
            f.write(normalize_svg(text))
        r['svg'] = f'cards/{dst_name}'
        del r['_svg_src']
        kept.append(r)
    return kept

def e(s):
    return html.escape(s or '')

def title_case(s):
    return (s or '').title()

def render_entry(r):
    keys = ''.join(f'<span>{e(k)}</span>'
                   for k in (r['keywords'] or '').split() if k)
    keys_html = f'<div class="entry-keys">{keys}</div>' if keys else ''
    if r['statement']:
        body = (f'<div class="entry-stmt"><span class="stmt-label">The statement</span>'
                f'{e(r["statement"])}</div>')
    else:
        body = ('<p class="entry-noStmt">No statement was written this day — '
                'only the reading.</p>')
    return f'''<article class="entry" id="{e(r['date'])}">
  <div class="entry-art">
    <a class="paper" href="{e(r['svg'])}" target="_blank" rel="noopener" aria-label="Open the full card for {e(r['date_long'])}">
      <img loading="lazy" src="{e(r['svg'])}" alt="{e(title_case(r['name']))} — the card for {e(r['date_long'])}">
    </a>
  </div>
  <div class="entry-text">
    <p class="entry-num">{e(r['number'])} <span>· day of the year</span></p>
    <h2 class="entry-name">{e(title_case(r['name']))}</h2>
    <p class="entry-dateline">{e(r['weekday'])} · {e(r['date_long'])} · {e(r['date_roman'])}</p>
    {keys_html}
    <p class="entry-poem"><span>{e(r['reading_1'])}</span><span>{e(r['reading_2'])}</span></p>
    {body}
  </div>
</article>'''

def render(records):
    count = len(records)
    latest = records[0] if records else None
    with_stmt = sum(1 for r in records if r['statement'])
    feed = '\n'.join(render_entry(r) for r in records)
    page = TEMPLATE.replace('<!--__FEED__-->', feed)
    page = page.replace('__COUNT__', str(count))
    page = page.replace('__WITH_STMT__', str(with_stmt))
    page = page.replace('__LATEST_NUM__', e(latest['number']) if latest else '')
    with open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(page)
    # GitHub Pages: serve as-is, don't run Jekyll over it
    open(os.path.join(HERE, '.nojekyll'), 'w').close()
    return count

# The template lives in template.html next to this script for editability.
TEMPLATE = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()

if __name__ == '__main__':
    recs = parse_all()
    recs = copy_svgs(recs)
    n = render(recs)
    miss = sum(1 for r in recs if not r['statement'])
    print(f'The News Reader — {n} cards ({n-miss} with statements, {miss} reading-only)')
    if recs:
        print(f'  latest: {recs[0]["date"]}  {recs[0]["number"]}  {recs[0]["name"]}')
