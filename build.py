import json, os, re, html

PACK = os.path.expanduser('~/Developer/HitItStraight/deliverables/pack/full-pack.json')
OUT  = os.path.expanduser('~/Developer/HitItStraight/preview')
d = json.load(open(PACK))
pages = {p['pageKey']: p for p in d['pages']}

NAV = [('index.html','Home'), ('lessons.html','Lessons'), ('mission.html','Our Mission'),
       ('coach.html','Coach Dion'), ('donate.html','Donate')]
FILE = {'home':'index.html','lessons':'lessons.html','about':'mission.html',
        'dion':'coach.html','donate':'donate.html'}

PHONE_D = '(708) 323-9980'; PHONE_T = '7083239980'

def esc(t): return html.escape(t or '')

def chips(t):
    """Render [CLIENT INPUT: ...] placeholders as visible highlighted chips."""
    if not t: return ''
    t = esc(t)
    t = re.sub(r'\[CLIENT INPUT:\s*(.*?)\]',
               r'<span class="need" title="We need this from you">NEEDED: \1</span>', t, flags=re.S)
    t = re.sub(r'\[(.*?)\]', r'<span class="need">\1</span>', t)
    return t

def paras(t):
    if not t: return ''
    return ''.join(f'<p>{chips(b.strip())}</p>' for b in re.split(r'\n\s*\n', t.strip()) if b.strip())

COLRE = re.compile(r'COLUMN\s*\d+\s*heading:\s*(.*?)[.:]\s*Body:\s*(.*)', re.I|re.S)
def as_columns(bl):
    """Turn 'COLUMN 1 heading: X. Body: Y' bullets into real columns."""
    out=[]
    for b in bl or []:
        m=COLRE.match(b.strip())
        if not m: return None
        out.append((m.group(1).strip(), m.group(2).strip()))
    return out or None

def short_note(t, n=1):
    """First sentence of a long imageNote, for a photo slot label."""
    if not t: return ''
    t=re.sub(r'\[CLIENT INPUT:.*?\]','',t,flags=re.S).strip()
    parts=re.split(r'(?<=[.!?])\s+', t)
    return ' '.join(parts[:n]).strip()

def is_internal(s):
    blob = f"{s.get('sectionName','')} {s.get('godaddySectionType','')}".upper()
    return ('INTERNAL' in blob or 'NOT A PAGE SECTION' in blob
            or 'SITE HEADER' in blob or 'FOOTER (SITE' in blob)

def kind(s):
    t = (s.get('godaddySectionType','') + ' ' + s.get('sectionName','')).lower()
    if 'video' in t: return 'video'
    if 'menu/price' in t or 'price list' in t: return 'list'
    if 'review' in t: return 'reviews'
    if 'contact' in t: return 'contact'
    if 'cover' in t or 'hero' in t: return 'hero'
    if 'call to action' in t: return 'cta'
    if 'gallery' in t or 'photo' in t: return 'gallery'
    return 'content'

def render(s, first):
    k = kind(s); k = 'hero' if first else k
    hl, sub = s.get('headline',''), s.get('subhead','')
    body, bl = s.get('body',''), s.get('bullets') or []
    cta, tgt = s.get('ctaLabel',''), (s.get('ctaTarget','') or '')
    img, alt = s.get('imageNote',''), s.get('altText','')

    href = f'tel:{PHONE_T}' if ('phone' in tgt.lower() or PHONE_D in tgt) else \
           ('donate.html' if 'donate' in tgt.lower() else
            'lessons.html' if ('lesson' in tgt.lower() or 'inquiry' in tgt.lower()) else
            'mission.html' if ('mission' in tgt.lower() or 'h-i-s-g-a' in tgt.lower()) else
            'coach.html' if 'madkins' in tgt.lower() else '#')
    btn = f'<a class="btn" href="{href}">{esc(cta)}</a>' if cta else ''

    if k == 'hero':
        dup = (href == f'tel:{PHONE_T}') or (PHONE_D in (cta or ''))
        second = '<a class="btn big" href="lessons.html">Request a Lesson</a>' if dup else btn
        return f'''<section class="hero">
  <div class="wrap">
    <h1>{chips(hl)}</h1>
    {f'<p class="lede">{chips(sub)}</p>' if sub else ''}
    <div class="hero-body">{paras(body)}</div>
    <div class="btns"><a class="btn big" href="tel:{PHONE_T}">Call {PHONE_D}</a>{second}</div>
  </div>
  <div class="hero-photo"><span>Photo slot<em>{esc(short_note(img)) or "Replace with a photo from the Ravisloe shoot."}</em></span></div>
</section>'''

    if k == 'video':
        return f'''<section class="sec video"><div class="wrap narrow">
  <h2>{chips(hl)}</h2>{f'<p class="lede">{chips(sub)}</p>' if sub else ''}
  <div class="vid"><iframe src="https://player.vimeo.com/video/339743333" title="Dion Madkins on Golf Channel"
    frameborder="0" allow="fullscreen; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>
  {paras(body)}{btn}</div></section>'''

    if k == 'list':
        items = ''.join(f'<li>{chips(b)}</li>' for b in bl) or f'<li>{chips(body)}</li>'
        return f'''<section class="sec alt"><div class="wrap narrow">
  <h2>{chips(hl)}</h2>{f'<p class="lede">{chips(sub)}</p>' if sub else ''}
  <ul class="pricelist">{items}</ul>{btn}</div></section>'''

    if k == 'reviews':
        cards = ''.join(f'<blockquote>{chips(b)}</blockquote>' for b in bl) or paras(body)
        return f'''<section class="sec alt"><div class="wrap">
  <h2>{chips(hl)}</h2><div class="cards">{cards}</div></div></section>'''

    if k == 'contact':
        rows = ''.join(f'<li>{chips(b)}</li>' for b in bl)
        return f'''<section class="sec contact"><div class="wrap narrow">
  <h2>{chips(hl)}</h2>{f'<p class="lede">{chips(sub)}</p>' if sub else ''}
  {paras(body)}{f'<ul class="plain">{rows}</ul>' if rows else ''}
  <form onsubmit="alert('Preview only. The real form will live in GoDaddy.');return false">
    <label>Name<input required></label><label>Phone<input type="tel" required></label>
    <label>Email<input type="email" required></label><label>Message<textarea rows="3"></textarea></label>
    <button class="btn" type="submit">Send</button>
  </form>
  <p class="callout">Or just call <a href="tel:{PHONE_T}">{PHONE_D}</a>.</p></div></section>'''

    if k == 'cta':
        return f'''<section class="sec band"><div class="wrap narrow center">
  <h2>{chips(hl)}</h2>{paras(body)}
  <div class="btns"><a class="btn big" href="tel:{PHONE_T}">Call {PHONE_D}</a>{btn}</div></div></section>'''

    if k == 'gallery':
        return f'''<section class="sec"><div class="wrap"><h2>{chips(hl)}</h2>{paras(body)}
  <div class="gal">{''.join(f'<div class="ph"><span>PHOTO SLOT {i}</span></div>' for i in range(1,5))}</div>
  <p class="note">Photo slots fill from the Ravisloe shoot.</p></div></section>'''

    cols = as_columns(bl)
    if cols:
        cards = ''.join(f'<div class="col"><h3>{chips(a)}</h3><p>{chips(b)}</p></div>' for a,b in cols)
        return f'''<section class="sec"><div class="wrap">
  <h2>{chips(hl)}</h2>{f'<p class="lede">{chips(sub)}</p>' if sub else ''}
  {paras(body)}<div class="cols">{cards}</div>{btn}</div></section>'''

    lis = f'<ul class="plain">{"".join(f"<li>{chips(b)}</li>" for b in bl)}</ul>' if bl else ''
    return f'''<section class="sec"><div class="wrap narrow">
  <h2>{chips(hl)}</h2>{f'<p class="lede">{chips(sub)}</p>' if sub else ''}
  {paras(body)}{lis}{btn}</div></section>'''

def page(key):
    p = pages[key]; me = FILE[key]
    nav = ''.join(f'<a href="{h}"{" class=on" if h==me else ""}>{t}</a>' for h,t in NAV)
    secs = [s for s in sorted(p['sections'], key=lambda x:x.get('order',0)) if not is_internal(s)]
    body = ''.join(render(s, i==0) for i,s in enumerate(secs))
    asks = p.get('clientInputNeeded') or []
    asklist = ''.join(f'<li>{esc(a)}</li>' for a in asks)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{esc(p.get('seoTitle') or p['pageTitle'])}</title>
<meta name="description" content="{esc(p.get('seoDescription',''))}">
<link rel="stylesheet" href="style.css"></head><body>
<div class="pv">PREVIEW &mdash; not the live site &middot; built for Hit It Straight Golf Academy by Ghetto Media Group</div>
<header class="site"><div class="wrap bar">
  <a class="brand" href="index.html"><b>Hit It Straight</b><span>Golf Academy</span></a>
  <nav>{nav}</nav>
  <a class="btn sm" href="tel:{PHONE_T}">{PHONE_D}</a>
</div></header>
<main>{body}</main>
{f'<section class="sec asks"><div class="wrap narrow"><h2>What we still need from you for this page</h2><p class="lede">Everything marked NEEDED above is waiting on an answer.</p><ol>{asklist}</ol></div></section>' if asks else ''}
<footer class="site"><div class="wrap">
  <p class="fbrand">Hit It Straight Golf Academy</p>
  <p>Ravisloe Country Club, 18231 South Park Avenue, Homewood, IL 60430<br>
  <a href="tel:{PHONE_T}">{PHONE_D}</a></p>
  <p class="legal">Hit It Straight Golf Academy NFP is a registered 501(c)(3) nonprofit organization.<br>
  EIN 86-2045382. Donations are tax deductible to the extent allowed by law.</p>
  <p class="legal">Preview build. Content subject to client review.</p>
</div></footer></body></html>'''

for k in FILE:
    open(os.path.join(OUT, FILE[k]),'w').write(page(k))
    print("built", FILE[k])
