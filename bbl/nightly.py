#!/usr/bin/env python3
"""Best/worst performances of the night in BBL scoring.
Usage: python3 nightly.py box.txt pool.txt "<date label>"  -> writes nightly.html (HTML fragment)
Scoring: PTS 1, FGM 2, FGA -1, FTM 1, FTA -1, REB 1, AST 2, STL 4, BLK 4, TO -2, PF -1, 3PM 0."""
import sys, html, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
box, poolf, label = sys.argv[1], sys.argv[2], sys.argv[3]
lines=open(box).read().strip().splitlines()
hdr=lines[0].lstrip('#').split('|'); ngames,ndone,nlive=map(int,hdr)
owner={}; LOGO={}; CBSPOS={}
for l in open(poolf):
    p=l.rstrip('\n').split('|')
    if p[0]=='#LOGO' and len(p)>=3: LOGO[p[1]]=p[2]; continue
    if len(p)>=3: CBSPOS[p[0]]=p[2]
    if len(p)>=4: owner[p[0]]='Yours' if p[3]=='MINE' else (p[3][6:] if p[3].startswith('TAKEN:') else 'FA')
P=[]
for l in lines[1:]:
    f=l.split('|')
    try: n,t=f[0],f[1]; m,pts,fgm,fga,tpm,tpa,ftm,fta,reb,ast,to,stl,blk,pf=[int(float(x or 0)) for x in f[2:16]]
    except ValueError: continue
    fp=pts+2*fgm-fga+ftm-fta+reb+2*ast+4*stl+4*blk-2*to-pf
    ep=f[16] if len(f)>16 else ''
    if n in CBSPOS: elig=set(CBSPOS[n].split(','))
    else:
        mp={'PG':'G','SG':'G','G':'G','SF':'F','PF':'F','F':'F','C':'C','G-F':'GF','F-G':'GF','F-C':'FC','C-F':'FC'}
        elig=set(mp.get(ep.upper(),''))
    bon={'G':reb,'F':ast,'C':tpm}
    opts=[(bon[s],s) for s in 'GFC' if s in elig]
    b,slot=max(opts) if opts else (0,'')
    P.append(dict(n=n,t=t,m=m,pts=pts,fgm=fgm,fga=fga,tpm=tpm,tpa=tpa,ftm=ftm,fta=fta,reb=reb,ast=ast,to=to,stl=stl,blk=blk,pf=pf,base=fp,fp=fp+b,slot=slot,bonus=b))
def pct(a,b): return f'{a}-{b}'
def hot(p):
    e={}
    e['pts']='🔥' if p['pts']>=30 else ''
    e['reb']='🔥' if p['reb']>=12 else ''
    e['ast']='🔥' if p['ast']>=10 else ''
    e['stl']='🔥'*min(2,p['stl']-2) if p['stl']>=3 else ''
    e['blk']='🔥'*min(2,p['blk']-2) if p['blk']>=3 else ''
    e['to']='🔥' if p['to']==0 and p['m']>=28 else ('🧊' if p['to']>=5 else '')
    e['fg']='🔥' if p['fga']>=10 and p['fgm']/p['fga']>=0.6 else ('🧊' if p['fga']>=12 and p['fgm']/p['fga']<0.38 else '')
    e['ft']='🧊' if p['fta']>=4 and p['ftm']/p['fta']<0.6 else ''
    e['tpm']='🔥' if p['tpm']>=5 else ''
    return e
def cold(p):
    e={}
    e['fg']='🥶' if p['fga']>=8 and p['fgm']/p['fga']<0.35 else ''
    e['ft']='🥶' if p['fta']>=3 and p['ftm']/p['fta']<0.6 else ''
    e['to']='🤮' if p['to']>=4 else ''
    e['pf']='🤮' if p['pf']>=5 else ''
    e['pts']='🥶' if p['pts']<=4 else ''
    return e
MYTEAM=os.environ.get('BBL_MY_TEAM','')  # optional: your fantasy team name gets a ★ in the legend (set my_team in config.txt)
CC_LINK=os.environ.get('BBL_CC_LINK','')  # Command Center link in the share email ('' = none)
EMAIL=len(sys.argv)>4 and sys.argv[4] in ('email','short','share')
TOP10=len(sys.argv)>4 and sys.argv[4]=='top10'   # mobile top-10 image (rendered from nightly_top10.html)
CARD=len(sys.argv)>4 and sys.argv[4]=='card'   # shareable PNG infographic (rendered from nightly_card.html)
SHARE=(len(sys.argv)>4 and sys.argv[4]=='share') or CARD or TOP10  # league-friendly copy: no 'yours', owners shown by team name
SHORT=len(sys.argv)>4 and sys.argv[4]=='short'
BADGE={'Oobsidoobsie':('OOB','#c2410c'),'Binkas&Yams':('B&Y','#7c3aed'),'Deep Bag':('DB','#0f766e'),'My Shaila':('MS','#db2777'),
 'Phil the new champion':('PHIL','#2563eb'),'Pucs':('PUCS','#4d7c0f'),'Rudy Jobert':('RJ','#dc2626'),'SOGGY':('SOG','#0e7490'),
 'Tank You Very Much':('TANK','#475569')}
def badge(team):
    lab,col=BADGE.get(team,(None,None))
    if lab is None:
        if 'ɪɴᴏʟᴀ' in team or 'TINOLA' in team.upper(): lab,col='TIN','#a16207'
        else: lab,col=''.join(w[0] for w in team.split()[:3]).upper(),'#334155'
    return f'<span style="background:{col};color:#ffffff;font-size:10px;font-weight:700;padding:1px 5px;border-radius:3px;white-space:nowrap">{html.escape(lab)}</span>'
def logo(team,sz=18):
    if EMAIL: return ''
    u=LOGO.get(team)
    if not u: return ''
    src=u if u.startswith('data:') else u+'?width=48&height=48'
    return f'<img src="{src}" width="{sz}" height="{sz}" alt="" style="border-radius:4px;vertical-align:middle;margin-right:3px">' if u else ''
def own(n,stk=False):
    o=owner.get(n,'FA')
    k=STK.get(tname(n),0) if stk else 0
    if k>=2 and o!='FA':
        lab='★ yours' if o=='Yours' else html.escape(o)
        return f' {logo(MYTEAM if o=="Yours" else o)}<span style="{tagstyle(k)}">{lab}</span>'
    if o=='Yours' and SHARE: return f' <span style="font-size:11px;color:#667085">{html.escape(MYTEAM)}</span>'
    if o=='Yours': return f' {logo(MYTEAM)}<span style="font-size:11px;color:#c2410c;font-weight:600">★ yours</span>'
    if o=='FA': return ' <span style="font-size:11px;color:#667085">FA</span>'
    return f' {logo(o)}<span style="font-size:11px;color:#667085">{html.escape(o)}</span>'
def legend():
    if not LOGO or EMAIL: return ''
    items=sorted(LOGO,key=lambda t:(t!=MYTEAM,t.lower()))
    return '<p style="font-size:12px;line-height:24px">'+' &nbsp; '.join(f'<span style="white-space:nowrap">{logo(t,20)}{html.escape(t)}{" ★" if t==MYTEAM else ""}</span>' for t in items)+'</p>'
FPS='color:inherit;font-size:15px;font-weight:800;font-variant-numeric:tabular-nums'
fpt=lambda v: ('−'+str(abs(v))) if v<0 else str(v)
TH='style="text-align:left;padding:4px 6px;border-bottom:2px solid #dfe3ea;font-size:12px"'
TD='style="padding:4px 6px;border-bottom:1px solid #eef0f4;font-size:13px;white-space:nowrap"'

# ---- fun extras: milestone badges (80/90/100+ BBL pts) and a headline for the night's top performer
TIERS=[(100,'👑','Century (100+)','linear-gradient(90deg,#fde68a,#facc15 35%,#eab308 70%,#ca8a04)','#eab308',18),
       (90,'☄️','Supernova (90–99)','linear-gradient(rgba(168,85,247,.5),rgba(168,85,247,.5))','#9333ea',16),
       (80,'🔥','Scorcher (80–89)','linear-gradient(rgba(99,102,241,.5),rgba(99,102,241,.5))','#6366f1',15)]
def tier(fp):
    for t in TIERS:
        if fp>=t[0]: return t
    return None
def fpb(fp,email=None,size=15):
    """Best-slot number. 80/90/100+ get a soft marker highlight under the digits and an emoji sticker just past the top-right corner."""
    email=EMAIL if email is None else email
    t=tier(fp)
    if not t: return f'<b style="{FPS};font-size:{size}px">{fpt(fp)}</b>'
    if email:  # Yahoo strips backgrounds and positioning: coloured underline + raised emoji
        return f'<b title="{t[2]}" style="font-size:{size}px;border-bottom:2px solid {t[4]}">{fpt(fp)}</b><sup style="font-size:12px">{t[1]}</sup>'
    return (f'<span title="{t[2]}" style="display:inline-block;padding-right:{t[5]+6}px"><span style="position:relative;display:inline-block">'
            f'<b style="{FPS};font-size:{size}px;background:{t[3]} left bottom/100% 28% no-repeat;padding:0 2px 1px">{fpt(fp)}</b>'
            f'<span aria-hidden="true" style="position:absolute;left:100%;margin-left:1px;top:-9px;font-size:{t[5]}px;line-height:1;transform:rotate(12deg)">{t[1]}</span></span></span>')
def headline(p,email=False):
    n=p['n']; last=n.split()[-1] if n.split()[-1] not in ('Jr.','Sr.','II','III','IV') else n.split()[-2]
    st=p['stl']+p['blk']
    if p['fp']>=100: h=f"👑 {last.upper()} BROKE THE GAME"
    elif p['fp']>=90: h=f"☄️ {n} went supernova"
    elif p['fp']>=80: h=f"🔥 {n} set the league on fire"
    elif p['pts']>=40: h=f"💥 {n} served a {p['pts']}-piece"
    elif p['reb']>=15 and p['ast']>=10: h=f"🦄 {n} did everything"
    elif p['reb']>=15: h=f"🧲 {n} owned the glass"
    elif p['ast']>=12: h=f"🎩 {n} ran the show"
    elif st>=6: h=f"🧱 {n} built a wall"
    elif p['fgm']>=10 and p['fga'] and p['fgm']/p['fga']>=0.65: h=f"🎯 {n} couldn't miss"
    else: h=f"🔥 {n} Night!"
    bits=[f"{p['pts']} pts",f"{p['reb']} reb",f"{p['ast']} ast"]+([f"{p['stl']} stl"] if p['stl'] else [])+([f"{p['blk']} blk"] if p['blk'] else [])+[f"{p['fgm']}-{p['fga']} FG"]
    o=owner.get(n,'FA')
    if o=='Yours' and SHARE: o=MYTEAM
    who=' · and he’s YOURS ★' if o=='Yours' else (' · on '+html.escape(o) if o!='FA' else ' · still a free agent 👀')
    if email:
        return f'<div style="border-left:4px solid #4c1d95;padding:6px 10px;margin:6px 0 10px"><div style="font-size:18px;font-weight:800;color:#1b2230">{html.escape(h)}</div><div style="font-size:13px;color:#1b2230">{fpb(p["fp"],True,16)} <b>BBL pts</b> <span style="color:#667085">· {", ".join(bits)}{who}</span></div></div>'
    return (f'<div style="margin:6px 0 12px;padding:12px 16px;border-radius:12px;border:1px solid #e4e7ec;border-left:6px solid #4c1d95">'
            f'<div style="font:800 11px Arial,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#98a2b3">Player of the night · {html.escape(label)}</div>'
            f'<div style="font:900 24px/1.2 Arial,sans-serif;margin:2px 0 4px">{html.escape(h)}</div>'
            f'<div style="font-size:13px">{fpb(p["fp"],False,16)} <b>BBL pts</b> <span style="color:#8a94a6">· {", ".join(bits)}{who}</span></div></div>')

# ---- manager stacks: a plain callout with a slots tagline when ONE fantasy team has 3+ players in the night's top 10
def tname(n):
    o=owner.get(n,'FA')
    return MYTEAM if o=='Yours' else o
def stacks(top,mn=3):
    c={}
    for i,p in enumerate(top,1):
        o=tname(p['n'])
        if o!='FA': c.setdefault(o,[]).append((i,p))
    return sorted([(o,L) for o,L in c.items() if len(L)>=mn],key=lambda x:(-len(x[1]),-sum(p['fp'] for _,p in x[1])))
def shortn(n):
    w=n.split(); return w[-1] if w[-1] not in ('Jr.','Sr.','II','III','IV') else w[-2]
def stack_html(top,email=False):
    out=''
    for o,L in stacks(top):
        k=len(L); tot_=sum(p['fp'] for _,p in L)
        title={3:'🎰 JACKPOT!',4:'🎰 MEGA JACKPOT!!'}.get(k,'💎 GRAND JACKPOT!!!')
        line=f'{html.escape(o)} hit {k}-of-a-kind in the top 10'
        chips=' · '.join(f'#{rk(top,i)} {html.escape(shortn(p["n"]))} <b>{fpt(p["fp"])}</b>' for i,p in L)
        if email:
            out+=f'<div style="border-left:4px solid #b45309;padding:4px 10px;margin:6px 0 10px"><div style="font-size:16px;font-weight:800;color:#b45309">{title} <span style="color:#1b2230">{line}</span></div><div style="font-size:13px;color:#667085">{chips} · 💰 Payout <b style="color:#1b2230">{fpt(tot_)}</b> BBL pts</div></div>'
        else:
            out+=(f'<div style="margin:4px 0 12px;padding:10px 14px;border-radius:10px;border:1px solid rgba(148,163,184,.35);border-left:5px solid #d97706">'
                  f'<div style="font:800 16px/1.3 Arial,sans-serif"><span style="color:#d97706">{title}</span> {line}</div>'
                  f'<div style="font-size:13px;color:#8a94a6;margin-top:2px">{chips} · 💰 Payout <b style="color:inherit">{fpt(tot_)}</b> BBL pts</div></div>')
    return out
PAGE_STACK=not EMAIL and not SHARE   # Command Center page: 2+ players get a callout, rows get matching manager tags
STK={}   # owner -> count, filled for the top-10 table on the page
TAGS={2:'border:1px dashed var(--muted,#667085);color:inherit',
      3:'background:rgba(217,119,6,.16);color:var(--warn,#b45309);border:1px solid rgba(217,119,6,.5)',
      4:'background:linear-gradient(90deg,#7c3aed,#c026d3);color:#fff;border:1px solid transparent'}
def tagstyle(k): return 'font-size:11px;font-weight:700;border-radius:999px;padding:0 7px;white-space:nowrap;'+TAGS[min(k,4)]
def page_stacks(top):
    out=''
    for o,L in stacks(top,2):
        k=len(L); tot_=sum(p['fp'] for _,p in L); on=html.escape(o)
        ch=lambda bc,extra='':''.join(f'<span style="display:inline-block;font-size:12.5px;border:1px solid {bc};border-radius:999px;padding:1px 8px;margin:2px 3px 2px 0;white-space:nowrap;{extra}">#{rk(top,i)} {html.escape(shortn(p["n"]))} <b>{fpt(p["fp"])}</b></span>' for i,p in L)
        if k==2:
            out+=(f'<div style="font-size:13.5px;padding:5px 12px;margin:4px 0 8px;border-left:3px solid var(--muted,#667085);border-radius:6px">'
                  f'<span style="font:800 11px Arial,sans-serif;letter-spacing:.1em;color:var(--muted,#667085)">🤝 DOUBLE UP</span> <b>{on}</b> has 2 in the top 10 · {ch("var(--line,#dfe3ea)")} <span style="color:var(--muted,#667085)">· {fpt(tot_)} BBL pts</span></div>')
        elif k==3:
            out+=(f'<div style="margin:4px 0 10px;padding:12px 16px;border-radius:12px;border:1px solid rgba(217,119,6,.45);border-left:6px solid #d97706;background:rgba(217,119,6,.09)">'
                  f'<div style="font:800 18px/1.3 Arial,sans-serif"><span style="color:#d97706">🎰 JACKPOT!</span> {on} hit 3-of-a-kind in the top 10</div>'
                  f'<div style="font-size:13px;color:var(--muted,#667085);margin-top:3px">{ch("#d97706")} · 💰 Payout <b style="color:var(--fg,#1b2230)">{fpt(tot_)}</b> BBL pts</div></div>')
        else:
            title='💎 MEGA JACKPOT!!' if k==4 else '👑 GRAND JACKPOT!!!'
            out+=(f'<div style="margin:6px 0 12px;padding:18px 22px;border-radius:16px;color:#fff;background:linear-gradient(120deg,#7c3aed,#c026d3 55%,#f59e0b);box-shadow:0 0 0 3px rgba(192,38,211,.3),0 10px 30px rgba(124,58,237,.35)">'
                  f'<div style="font:800 11px Arial,sans-serif;letter-spacing:.25em;opacity:.85">{k} OF A KIND</div>'
                  f'<div style="font:900 italic 30px/1.1 \'Arial Black\',Arial,sans-serif;margin:2px 0 4px;text-shadow:0 2px 0 rgba(0,0,0,.25)">{title}</div>'
                  f'<div style="font-size:15px;margin-bottom:6px"><b>{on}</b> owns {k} of the top 10 tonight</div>'
                  f'<div>{ch("rgba(255,255,255,.55)","color:#fff;background:rgba(0,0,0,.18)")}</div>'
                  f'<div style="display:inline-block;margin-top:8px;font:800 13px Arial,sans-serif;background:#1b1030;color:#ffd23f;border-radius:999px;padding:4px 12px">💰 Payout {fpt(tot_)} BBL pts</div></div>')
    return out
def rk(L,i):
    '''Display rank for position i (1-based) in list L.'''
    return str(i)  # plain ranks; ties are already ordered by base score, then minutes
def table(rows,emo,col='#2b8a9e',hm=(),stk=False):
    cols=['#','Player','Best slot','Base','MIN','PTS','FG','FT','3PM','REB','AST','STL','BLK','TO','PF']
    h='<table style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif"><tr>'+''.join(f'<th {TH}>{c}</th>' for c in cols)+'</tr>'
    ALL=list(rows)+list(hm)
    for i,p in enumerate(rows,1):
        e=emo(p); g=lambda k:e.get(k,'')
        vals=[rk(ALL,i),f'<b>{html.escape(p["n"])}</b> <span style="font-size:11px;color:#667085">{p["t"]}</span>'+own(p["n"],stk),f'{fpb(p["fp"])} <span style="font-size:10px;color:#9fb3bd">{p["slot"]}{(" +"+str(p["bonus"])) if p["bonus"] else ""}</span>' if p['slot'] else fpb(p["fp"]),p['base'],p['m'],f'{p["pts"]}{g("pts")}',f'{pct(p["fgm"],p["fga"])}{g("fg")}',f'{pct(p["ftm"],p["fta"])}{g("ft")}',f'{p["tpm"]}{g("tpm")}',f'{p["reb"]}{g("reb")}',f'{p["ast"]}{g("ast")}',f'{p["stl"]}{g("stl")}',f'{p["blk"]}{g("blk")}',f'{p["to"]}{g("to")}',f'{p["pf"]}{g("pf")}']
        k=STK.get(tname(p['n']),0) if stk and owner.get(p['n'],'FA')!='FA' else 0
        if k>=3:
            edge='#d97706' if k==3 else '#c026d3'; w=4 if k==3 else 5
            TD0=TD[:-1]+f';box-shadow:inset {w}px 0 0 {edge}"'
            h+=('<tr style="background:rgba(192,38,211,.07)">' if k>=4 else '<tr>')+''.join(f'<td {TD0 if j==0 else TD}>{v}</td>' for j,v in enumerate(vals))+'</tr>'
        else:
            h+='<tr>'+''.join(f'<td {TD}>{v}</td>' for v in vals)+'</tr>'
    if hm:
        h+=f'<tr><td colspan="{len(cols)}" style="padding:10px 6px 3px;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#98a2b3;border-bottom:1px solid #eef0f4">Honorable mentions</td></tr>'
        TDH='style="padding:3px 6px;border-bottom:1px solid #eef0f4;font-size:11.5px;white-space:nowrap;opacity:.6"'
        for i,p in enumerate(hm,len(rows)+1):
            vals=[rk(ALL,i),f'{html.escape(p["n"])} <span style="font-size:10px;color:#667085">{p["t"]}</span>'+own(p["n"]),f'{p["fp"]} <span style="font-size:10px;color:#9fb3bd">{p["slot"]}{(" +"+str(p["bonus"])) if p["bonus"] else ""}</span>',p['base'],p['m'],p['pts'],pct(p['fgm'],p['fga']),pct(p['ftm'],p['fta']),p['tpm'],p['reb'],p['ast'],p['stl'],p['blk'],p['to'],p['pf']]
            h+='<tr>'+''.join(f'<td {TDH}>{v}</td>' for v in vals)+'</tr>'
    return h+'</table>'
if not P:
    out=f'<p>No completed NBA games for {html.escape(label)}.</p>'
else:
    best=sorted(P,key=lambda p:(-p['fp'],-p['base'],p['m']))   # ties: higher base, then fewer minutes
    q=[p for p in P if p['m']>=20]; worst=sorted(q,key=lambda p:(p['fp'],p['base'],-p['m']))   # ties: lower base, then more minutes
    hm=lambda L:', '.join(html.escape(p['n'])+f' ({p["fp"]}'+(', '+(('yours' if not SHARE else MYTEAM) if owner[p["n"]]=='Yours' else html.escape(owner[p["n"]])) if owner.get(p['n'],'FA')!='FA' else '')+')' for p in L)
    note=(f'<p style="font-size:12px;color:#667085">{ndone} of {ngames} games final; {nlive} still in progress and not included.</p>' if nlive else '')
    if PAGE_STACK: STK.update({o:len(L) for o,L in stacks(best[:10],2)})
    out=('<div style="overflow-x:auto">'+legend()+headline(best[0],EMAIL)+(page_stacks(best[:10]) if PAGE_STACK else stack_html(best[:10],EMAIL))+f'<h3>🔥 Top 10 performances of the night · {html.escape(label)}</h3>'+table(best[:10],hot,'#1f9d55',best[10:15],PAGE_STACK)+
         f'<h3>🤮 Top 10 worst performances of the night</h3>'+table(worst[:10],cold,'inherit')+
         f'<p><b>Honorable mentions:</b> {hm(worst[10:15])}</p><p style="font-size:12px;color:#667085"><b>How the lists are ranked.</b> Top 10: highest best-slot points; ties go to the higher base score (more of his points came from his own stats, not the slot bonus), then to fewer minutes played. Worst 10: lowest best-slot points among players with 20+ minutes; ties go to the lower base score, then to more minutes.</p>'+note+'</div>')
if TOP10 and P:   # mobile-friendly top-10 image (rendered from nightly_top10.html): best slot + base, stack callouts, honorable mentions as text
    import base64
    STK.update({o:len(L) for o,L in stacks(best[:10],2)})
    def mtag(p):
        o=tname(p['n'])
        if o=='FA': return '<span class="fa">Free agent</span>'
        k=STK.get(o,0); cls=f' t{min(k,4)}' if k>=2 else ''
        return f'{logo(o,30)}<span class="mt{cls}">{html.escape(o)}</span>'
    def row(i,p):
        k=STK.get(tname(p['n']),0) if tname(p['n'])!='FA' else 0
        rc=' e3' if k==3 else (' e4' if k>=4 else '')
        t=tier(p['fp']); em=f'<span class="em">{t[1]}</span>' if t else ''
        med={1:'🥇',2:'🥈',3:'🥉'}.get(i)
        rk=f'<div class="rk m">{med}</div>' if med else f'<div class="rk"><span>{i}</span></div>'
        sl=f'{p["slot"]}{(" +"+str(p["bonus"])) if p["bonus"] else ""}'
        return (f'<div class="row{rc}">{rk}<div class="who"><div class="nm">{html.escape(p["n"])} <em>{p["t"]}</em></div><div class="mg">{mtag(p)}</div></div>'
                f'<div class="bs"><b>{fpt(p["fp"])}</b>{em}<small>{sl}</small></div><div class="bz">{p["base"]}</div></div>')
    calls=''
    for o,L in stacks(best[:10],2):
        k=len(L); tot_=sum(p['fp'] for _,p in L); on=html.escape(o)
        ch=''.join(f'<span>#{i} {html.escape(shortn(p["n"]))} <b>{fpt(p["fp"])}</b></span>' for i,p in L)
        if k==2: calls+=f'<div class="c2"><div class="c2h">🤝 DOUBLE UP · <b>{on}</b> has 2 in the top 10</div><div class="cc">{ch}<span class="pay">{fpt(tot_)} PTS</span></div></div>'
        elif k==3: calls+=f'<div class="c3"><div class="c3h"><i>🎰 JACKPOT!</i> {on} hit 3-of-a-kind</div><div class="cc">{ch}<span class="pay">💰 {fpt(tot_)} PTS</span></div></div>'
        else:
            ttl='💎 MEGA JACKPOT!!' if k==4 else '👑 GRAND JACKPOT!!!'
            calls+=f'<div class="c4"><div class="c4k">{k} OF A KIND</div><div class="c4h">{ttl}</div><div class="c4l"><b>{on}</b> owns {k} of the top 10</div><div class="cc">{ch}<span class="pay">💰 {fpt(tot_)} PTS</span></div></div>'
    hmt=' · '.join(f'<span><b>{i}</b> {html.escape(p["n"])} <i>({html.escape(tname(p["n"]) if tname(p["n"])!="FA" else "Free agent")})</i> <b>{fpt(p["fp"])}</b></span>' for i,p in enumerate(best[10:15],11))
    LL=('<img class="ll" src="data:image/png;base64,'+base64.b64encode(open('league_logo.png','rb').read()).decode()+'" alt="BBL">') if os.path.exists('league_logo.png') else ''
    CSS="""*{box-sizing:border-box;margin:0}body{background:#070b24}
#card{width:1080px;padding:34px 40px 28px;font-family:Poppins,Inter,Arial,sans-serif;color:#fff;
 background:radial-gradient(60% 22% at 88% 3%,rgba(34,211,238,.33),transparent 70%),radial-gradient(70% 22% at 4% 6%,rgba(255,94,58,.36),transparent 70%),linear-gradient(180deg,#141a4d 0%,#0a0f30 35%,#070b24 100%)}
.head{display:flex;align-items:center;gap:24px;margin-bottom:20px}.ll{width:130px;filter:drop-shadow(0 8px 24px rgba(255,94,58,.45))}
.kick{display:inline-block;font:800 19px Inter,Arial;letter-spacing:.2em;color:#0a0f30;background:#22d3ee;padding:5px 12px;border-radius:8px;transform:skewX(-10deg)}
.title{font:900 74px/.95 'Inter Display',Inter,Arial;letter-spacing:-.02em;margin:10px 0 4px;transform:skewX(-8deg);background:linear-gradient(180deg,#fff7c2,#ffd23f 40%,#ff7a18 75%,#ff3d5a);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{font:700 25px Poppins,Arial;color:#c7d2fe}
.cc{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}.cc span{font:600 21px Inter,Arial;border-radius:999px;padding:4px 14px;white-space:nowrap}
.c2{border-left:5px solid #94a3b8;border-radius:12px;padding:10px 18px;margin:0 0 10px;background:rgba(148,163,184,.08)}
.c2h{font:600 23px Inter,Arial;color:#cbd5e1}.c2 .cc span{border:1px solid rgba(203,213,225,.35);color:#e2e8f0}.c2 .pay{color:#94a3b8!important}
.c3{border-radius:20px;padding:14px 22px;margin:0 0 12px;background:linear-gradient(100deg,#ffd23f,#ff9f1c 55%,#ff6b35);color:#2a1500;border:3px dashed #7c2d12}
.c3h{font:800 28px Poppins,Arial}.c3h i{font:900 italic 34px 'Inter Display',Inter,Arial}.c3 .cc span{background:#fff3c4;border:1px solid #b45309}.c3 .pay{background:#2a1500!important;color:#ffd23f;border:0!important;font-weight:800!important}
.c4{border-radius:24px;padding:22px 26px;margin:0 0 14px;background:linear-gradient(120deg,#7c3aed,#c026d3 55%,#f59e0b);box-shadow:0 0 0 4px rgba(192,38,211,.35),0 14px 40px rgba(124,58,237,.45)}
.c4k{font:800 17px Inter,Arial;letter-spacing:.25em;opacity:.85}.c4h{font:900 italic 46px/1.05 'Inter Display',Inter,Arial;margin:4px 0;text-shadow:0 3px 0 rgba(0,0,0,.25)}.c4l{font:500 23px Poppins,Arial}
.c4 .cc span{background:rgba(0,0,0,.2);border:1px solid rgba(255,255,255,.5)}.c4 .pay{background:#1b1030!important;color:#ffd23f;font-weight:800!important}
.colh{display:grid;grid-template-columns:76px 1fr 190px 110px;gap:16px;padding:14px 18px 8px;font:800 17px Inter,Arial;letter-spacing:.14em;color:#94a3b8}
.colh div:nth-child(3),.colh div:nth-child(4){text-align:center}.colh .hl{color:#ffd23f}
.row{display:grid;grid-template-columns:76px 1fr 190px 110px;gap:16px;align-items:center;padding:9px 18px;margin-bottom:8px;border-radius:18px;background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.09)}
.row.e3{box-shadow:inset 7px 0 0 #f59e0b;background:rgba(245,158,11,.10)}.row.e4{box-shadow:inset 8px 0 0 #d946ef;background:rgba(192,38,211,.16)}
.rk span{display:flex;width:64px;height:64px;align-items:center;justify-content:center;border-radius:16px;font:900 32px 'Inter Display',Inter,Arial;background:linear-gradient(135deg,#3b82f6,#a855f7)}
.rk.m{font-size:56px;line-height:64px;text-align:center}
.nm{font:700 31px/1.15 Poppins,Arial}.nm em{font:600 19px Inter,Arial;font-style:normal;color:#818cf8;letter-spacing:.06em}
.mg{display:flex;align-items:center;gap:8px;margin-top:6px;font:500 21px Inter,Arial;color:#c7d2fe}.mg img{border-radius:7px;margin:0!important}
.mt{padding:2px 0}.mt.t2{border:2px dashed #cbd5e1;border-radius:999px;padding:1px 12px;color:#fff;font-weight:700}
.mt.t3{background:#f59e0b;color:#2a1500;border-radius:999px;padding:2px 13px;font-weight:800}
.mt.t4{background:linear-gradient(90deg,#7c3aed,#d946ef);color:#fff;border-radius:999px;padding:2px 13px;font-weight:800}
.fa{color:#94a3b8;font-style:italic}
.bs{text-align:center;position:relative;border-radius:16px;padding:6px 0;background:rgba(255,210,63,.10);border:1px solid rgba(255,210,63,.28)}
.bs b{display:block;font:900 italic 58px/1 'Inter Display',Inter,Arial;color:#ffd23f}.bs small{display:block;font:700 17px Inter,Arial;color:#c7d2fe;letter-spacing:.08em;margin-top:2px}
.bs .em{position:absolute;top:-12px;right:-6px;font-size:34px}
.bz{text-align:center;font:800 38px 'Inter Display',Inter,Arial;color:#e2e8f0}
.hm{margin-top:16px;padding:14px 22px;border-radius:18px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);font:500 21px/1.65 Inter,Arial;color:#cbd5e1}
.hm .h{font:800 17px Inter,Arial;letter-spacing:.2em;color:#94a3b8;margin-bottom:6px}.hm b{color:#fff}.hm i{color:#94a3b8;font-style:normal}.hm span{white-space:nowrap}
.foot{margin-top:12px;font:500 17px/1.45 Inter,Arial;color:#8b93b8}.foot b{color:#c7d2fe}"""
    page=(f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=Poppins:wght@500;600;700;800;900&display=swap"><style>{CSS}</style></head><body><div id="card">'
          f'<div class="head">{LL}<div><div class="kick">BBL · TOP 10</div><div class="title">BEST OF<br>THE NIGHT</div><div class="sub">{html.escape(label)}</div></div></div>'
          f'{calls}<div class="colh"><div>#</div><div>PLAYER · MANAGER</div><div class="hl">BEST SLOT</div><div>BASE</div></div>'
          +''.join(row(i,p) for i,p in enumerate(best[:10],1))+
          f'<div class="hm"><div class="h">HONORABLE MENTIONS</div>{hmt}</div>'
          f'<div class="foot"><b>Best slot</b> = BBL points in his best eligible slot (G +1/reb · F +1/ast · C +1/3PM). <b>Base</b> = BBL points without the slot bonus. Ties go to the higher base, then fewer minutes. Highlighted managers have 2+ players in the top 10.</div>'
          '</div></body></html>')
    open('nightly_top10.html','w').write(page); print('top10 ok'); sys.exit(0)
if CARD and P:   # shareable PNG infographic: phone-first, high-energy poster (rendered from nightly_card.html)
    import re as _re, base64
    hl=_re.sub(r'<[^>]+>','',headline(best[0],True).split('</div>')[0]).strip()
    hl_emoji,hl_text=(hl.split(' ',1)+[''])[:2] if hl and not hl[0].isalnum() else ('🔥',hl)
    def chips(p,full=True):
        c=[(p['pts'],'PTS'),(p['reb'],'REB'),(p['ast'],'AST')]+([(p['stl'],'STL')] if p['stl'] else [])+([(p['blk'],'BLK')] if p['blk'] else [])
        if full and p['to']>=4: c.append((p['to'],'TO'))
        return ''.join(f'<span class="chip">{v}<i>{k}</i></span>' for v,k in c)+f'<span class="chip fg">{p["fgm"]}-{p["fga"]}<i>FG</i></span>'
    def mgr(p,sz=34):
        o=tname(p['n']); return (logo(o,sz) if o!='FA' else '<span class="fa">FA</span>')+(f'<span>{html.escape(o)}</span>' if o!='FA' else '<span>Free agent</span>')
    def slot(p): return f'{p["slot"]}{(" +"+str(p["bonus"])) if p["bonus"] else ""}'
    def num(p,cls='big'):
        t=tier(p['fp']); badge=f'<span class="em">{t[1]}</span>' if t else ''
        return f'<div class="{cls}"><b>{fpt(p["fp"])}</b>{badge}<small>{slot(p)}</small></div>'
    MED=['🥇','🥈','🥉']
    pod=''.join(f'<div class="pod p{k}"><div class="med">{MED[k]}</div><div class="pn">{html.escape(p["n"])}</div><div class="pt">{p["t"]}</div>{num(p,"pbig")}<div class="pm">{mgr(p,30)}</div><div class="pc">{chips(p,False)}</div></div>' for k,p in enumerate(best[:3]))
    def row(i,p,cls='row'):
        return (f'<div class="{cls}"><div class="rk"><span>{i}</span></div><div class="who"><div class="nm">{html.escape(p["n"])} <em>{p["t"]}</em></div>'
                f'<div class="mg">{mgr(p,28)}</div><div class="cs">{chips(p)}</div></div>{num(p)}</div>')
    rest=''.join(row(i,p) for i,p in enumerate(best[3:10],4))
    hmr=''.join(row(i,p,'row hm') for i,p in enumerate(best[10:15],11))
    wst=''.join(row(i,p,'row cold') for i,p in enumerate(worst[:5],1))
    jk=''
    for o,L in stacks(best[:10]):
        t={3:'JACKPOT!',4:'MEGA JACKPOT!!'}.get(len(L),'GRAND JACKPOT!!!')
        jk+=(f'<div class="jack"><div class="jl">🎰</div><div><div class="jt">{t}</div><div class="jd"><b>{html.escape(o)}</b> hit {len(L)}-of-a-kind in the top 10</div>'
             f'<div class="jp">'+''.join(f'<span>#{i} {html.escape(shortn(p["n"]))} <b>{fpt(p["fp"])}</b></span>' for i,p in L)+f'<span class="pay">💰 {fpt(sum(p["fp"] for _,p in L))} PTS</span></div></div></div>')
    b0=best[0]
    LL=('<img class="ll" src="data:image/png;base64,'+base64.b64encode(open('league_logo.png','rb').read()).decode()+'" alt="BBL">') if os.path.exists('league_logo.png') else ''
    CSS=f"""
*{{box-sizing:border-box;margin:0}}body{{background:#070b24}}
.card{{position:relative;width:1080px;padding:46px 46px 40px;font-family:Poppins,Inter,Arial,sans-serif;color:#fff;overflow:hidden;
 background:radial-gradient(60% 30% at 85% 4%,rgba(34,211,238,.35),transparent 70%),radial-gradient(70% 30% at 5% 10%,rgba(255,94,58,.38),transparent 70%),
 repeating-conic-gradient(from 200deg at 50% -10%,rgba(255,255,255,.045) 0 6deg,transparent 6deg 14deg),linear-gradient(180deg,#141a4d 0%,#0a0f30 40%,#070b24 100%)}}
.card:before{{content:"";position:absolute;inset:0;background:radial-gradient(rgba(255,255,255,.07) 1.2px,transparent 1.6px) 0 0/18px 18px;-webkit-mask:linear-gradient(180deg,#000,transparent 35%);mask:linear-gradient(180deg,#000,transparent 35%);pointer-events:none}}
.head{{position:relative;display:flex;align-items:center;gap:24px}}.ll{{width:190px;height:auto;filter:drop-shadow(0 8px 24px rgba(255,94,58,.45))}}
.kick{{display:inline-block;font:800 20px Inter,Arial;letter-spacing:.22em;color:#0a0f30;background:#22d3ee;padding:6px 14px;border-radius:8px;transform:skewX(-10deg)}}
.title{{font:900 92px/0.92 'Inter Display',Inter,Arial;letter-spacing:-.02em;margin:12px 0 6px;transform:skewX(-8deg);background:linear-gradient(180deg,#fff7c2 0%,#ffd23f 40%,#ff7a18 75%,#ff3d5a 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 4px 0 rgba(0,0,0,.35))}}
.sub{{font:700 26px Poppins,Arial;color:#c7d2fe}}.sub b{{color:#fff}}
.mvp{{position:relative;margin:30px 0 18px;border-radius:28px;padding:4px;background:linear-gradient(110deg,#ff7a18,#ff3d5a 35%,#a855f7 65%,#22d3ee)}}
.mvpin{{border-radius:24px;padding:26px 30px 24px;background:linear-gradient(135deg,#1d1450 0%,#0e1440 60%,#0b1238 100%);display:flex;gap:22px;align-items:center}}
.tag{{display:inline-block;font:900 18px Inter,Arial;letter-spacing:.2em;background:linear-gradient(90deg,#ff7a18,#ff3d5a);padding:6px 14px;border-radius:999px}}
.mh{{font:900 54px/1.05 'Inter Display',Inter,Arial;margin:12px 0 8px;letter-spacing:-.01em}}.mh .e{{font-size:58px;margin-right:6px}}
.mvpnum{{flex:none;text-align:center;min-width:200px}}.mvpnum b{{display:block;font:900 150px/0.9 'Inter Display',Inter,Arial;background:linear-gradient(180deg,#fff 0%,#ffe066 55%,#ffb020 100%);-webkit-background-clip:text;background-clip:text;color:transparent;transform:skewX(-8deg)}}.mvpnum span{{font:800 22px Inter,Arial;letter-spacing:.2em;color:#c7d2fe}}
.mm{{font:600 24px Poppins,Arial;color:#c7d2fe;margin-top:10px;display:flex;align-items:center;gap:10px}}.mm img,.pm img,.mg img{{border-radius:8px}}
.chip{{display:inline-flex;align-items:baseline;gap:5px;font:800 22px Inter,Arial;padding:6px 12px;margin:0 8px 8px 0;border-radius:12px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14)}}.chip i{{font-style:normal;font-size:14px;letter-spacing:.12em;color:#93c5fd}}.chip.fg i{{color:#fbbf24}}
.jack{{display:flex;gap:18px;align-items:center;margin:0 0 22px;padding:20px 26px;border-radius:24px;background:linear-gradient(100deg,#ffd23f,#ff9f1c 55%,#ff6b35);color:#2a1500;box-shadow:0 10px 30px rgba(255,159,28,.35);border:3px dashed rgba(42,21,0,.35)}}
.jl{{font-size:76px;line-height:1}}.jt{{font:900 46px/1 'Inter Display',Inter,Arial;letter-spacing:.02em;transform:skewX(-8deg)}}.jd{{font:600 24px Poppins,Arial;margin:6px 0 8px}}
.jp span{{display:inline-block;font:700 20px Inter,Arial;background:rgba(255,255,255,.55);border-radius:999px;padding:4px 12px;margin:0 8px 6px 0}}.jp .pay{{background:#2a1500;color:#ffd23f}}
.sec{{display:flex;align-items:center;gap:14px;margin:30px 0 14px}}.sec h2{{font:900 46px/1 'Inter Display',Inter,Arial;letter-spacing:.02em;transform:skewX(-8deg)}}.sec .bar{{flex:1;height:6px;border-radius:6px;background:linear-gradient(90deg,#ff7a18,#ff3d5a,#a855f7,#22d3ee)}}
.pods{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}}.pod{{position:relative;border-radius:24px;padding:18px 16px 14px;text-align:center;background:linear-gradient(180deg,rgba(255,255,255,.12),rgba(255,255,255,.04));border:2px solid rgba(255,255,255,.16)}}
.pod.p0{{border-color:#ffd23f;box-shadow:0 0 0 4px rgba(255,210,63,.18),0 14px 30px rgba(255,210,63,.18)}}.pod.p1{{border-color:#cbd5e1}}.pod.p2{{border-color:#f59e0b}}
.med{{font-size:64px;line-height:1}}.pn{{font:900 28px/1.1 Inter,Arial;margin-top:6px}}.pt{{font:700 18px Inter;color:#93c5fd;letter-spacing:.14em}}
.pbig b{{display:block;font:900 92px/1 'Inter Display',Inter,Arial;transform:skewX(-8deg);margin:6px 0 0}}.pbig small,.big small{{display:block;font:700 16px Inter;color:#94a3b8;letter-spacing:.08em}}.pbig .em{{position:absolute;top:8px;right:12px;font-size:34px}}
.pm{{display:flex;justify-content:center;align-items:center;gap:8px;font:600 19px Poppins,Arial;color:#c7d2fe;margin:10px 0 10px}}.pc .chip{{font-size:17px;padding:4px 8px;margin:0 4px 6px 0}}.pc .chip i{{font-size:11px}}
.row{{display:flex;align-items:center;gap:18px;margin:12px 0;padding:16px 20px;border-radius:22px;background:linear-gradient(90deg,rgba(255,255,255,.09),rgba(255,255,255,.03));border:1px solid rgba(255,255,255,.12)}}
.rk span{{display:flex;align-items:center;justify-content:center;width:66px;height:66px;border-radius:20px;font:900 34px Inter,Arial;background:linear-gradient(135deg,#3b82f6,#a855f7);transform:rotate(-6deg);box-shadow:0 6px 16px rgba(59,130,246,.35)}}
.who{{flex:1;min-width:0}}.nm{{font:900 32px/1.1 Inter,Arial;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.nm em{{font-style:normal;font-size:20px;color:#93c5fd;letter-spacing:.1em}}
.mg{{display:flex;align-items:center;gap:8px;font:600 20px Poppins,Arial;color:#c7d2fe;margin:6px 0 8px}}.fa{{font:900 13px Inter;letter-spacing:.1em;background:#334155;color:#cbd5e1;border-radius:6px;padding:4px 6px}}
.cs .chip{{font-size:18px;padding:4px 9px;margin:0 6px 4px 0}}.cs .chip i{{font-size:12px}}
.big{{position:relative;flex:none;text-align:right;min-width:130px}}.big b{{display:block;font:900 70px/1 'Inter Display',Inter,Arial;transform:skewX(-8deg)}}.big .em{{position:absolute;top:-12px;right:-12px;font-size:30px}}
.hm{{opacity:.55;padding:10px 18px;margin:8px 0}}.hm .rk span{{width:48px;height:48px;font-size:24px;border-radius:14px;background:#334155;box-shadow:none}}.hm .nm{{font-size:24px}}.hm .cs,.hm .mg{{display:none}}.hm .big b{{font-size:44px}}
.hml{{font:900 18px Inter;letter-spacing:.2em;color:#94a3b8;margin:22px 0 4px}}
.cold{{background:linear-gradient(90deg,rgba(56,189,248,.14),rgba(56,189,248,.03));border-color:rgba(125,211,252,.25)}}.cold .rk span{{background:linear-gradient(135deg,#38bdf8,#6366f1)}}
.foot{{margin-top:26px;font:500 18px/1.45 Poppins,Arial;color:#8ea0c2;text-align:center}}.foot b{{color:#fff}}
"""
    page=f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="card" id="card">
<div class="head">{LL}<div><span class="kick">BBL · BOMBASTIC BASKETBALL LEAGUE</span><div class="title">BEST &amp;<br>WORST</div><div class="sub">of the night · <b>{html.escape(label)}</b> · {ndone}/{ngames} games final</div></div></div>
<div class="mvp"><div class="mvpin"><div style="flex:1;min-width:0"><span class="tag">⭐ PLAYER OF THE NIGHT</span><div class="mh"><span class="e">{hl_emoji}</span>{html.escape(hl_text)}</div><div class="cs">{chips(b0,False)}</div><div class="mm">{mgr(b0,36)}</div></div><div class="mvpnum"><b>{fpt(b0['fp'])}</b><span>BBL PTS</span></div></div></div>
{jk}
<div class="sec"><h2>🔥 TOP 10</h2><div class="bar"></div></div>
<div class="pods">{pod}</div>
{rest}
{('<div class="hml">HONORABLE MENTIONS</div>'+hmr) if hmr else ''}
<div class="sec"><h2>🥶 OOF ZONE</h2><div class="bar" style="background:linear-gradient(90deg,#38bdf8,#6366f1)"></div></div>
<div style="font:600 20px Poppins;color:#93c5fd;margin:-6px 0 6px">Worst 5 of the night · 20+ minutes</div>
{wst}
<div class="foot"><b>BBL pts</b> = league scoring in the player's best slot (G +1/reb · F +1/ast · C +1/3PM) · ties: higher base score, then fewer minutes</div>
</div></body></html>"""
    open('nightly_card.html','w').write(page); print('card ok'); sys.exit(0)
if SHARE and not CARD and P:   # high-energy Best & Worst email (Yahoo-safe: tables, inline styles, bgcolor + borders, no positioning)
    import re as _re
    F="font-family:'Arial Black',Arial,Helvetica,sans-serif"; A="font-family:Arial,Helvetica,sans-serif"
    hl=_re.sub(r'<[^>]+>','',headline(best[0],True).split('</div>')[0]).strip()
    def ow(p):
        o=tname(p['n']); return 'Free agent' if o=='FA' else html.escape(o)
    def chips(p,small=False):
        c=[(p['pts'],'PTS'),(p['reb'],'REB'),(p['ast'],'AST')]+([(p['stl'],'STL')] if p['stl'] else [])+([(p['blk'],'BLK')] if p['blk'] else [])+([(p['to'],'TO')] if p['to']>=4 else [])+[(f"{p['fgm']}-{p['fga']}",'FG')]
        fs=12 if small else 13
        return ''.join(f'<span style="display:inline-block;font:700 {fs}px Arial;border:1px solid #c7d2fe;background:#eef2ff;border-radius:8px;padding:1px 6px;margin:0 3px 3px 0">{v} <font size="1" color="#4f46e5">{k}</font></span>' for v,k in c)
    def pts(p,sz=34,col='#1b2230'):
        t=tier(p['fp']); e=f'<sup style="font-size:{sz//2}px">{t[1]}</sup>' if t else ''
        u=f'border-bottom:4px solid {t[4]};' if t else ''
        return f'<span style="{F};font-size:{sz}px;font-weight:900;font-style:italic;color:{col};{u}line-height:1">{fpt(p["fp"])}</span>{e}<div style="{A};font-size:11px;color:#94a3b8;letter-spacing:1px">{p["slot"]}{(" +"+str(p["bonus"])) if p["bonus"] else ""}</div>'
    def rankbox(i,col1,col2):
        return f'<td width="56" valign="middle" style="padding:0 10px 0 0"><div style="width:46px;height:46px;line-height:46px;text-align:center;{F};font-size:22px;font-weight:900;color:#ffffff;background:{col1};background-image:linear-gradient(135deg,{col1},{col2});border-radius:12px">{i}</div></td>'
    def row(i,p,c1='#3b82f6',c2='#a855f7',bd='#e0e7ff'):
        return (f'<table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 10px;border:2px solid {bd};border-radius:16px"><tr><td style="padding:12px 14px"><table width="100%" cellpadding="0" cellspacing="0"><tr>{rankbox(i,c1,c2)}'
                f'<td valign="middle"><div style="{A};font-size:19px;font-weight:900;color:#0f172a">{html.escape(p["n"])} <span style="font-size:12px;color:#6366f1;letter-spacing:1px">{p["t"]}</span></div>'
                f'<div style="{A};font-size:13px;color:#475569;margin:2px 0 6px">{ow(p)}</div>{chips(p)}</td><td width="110" align="right" valign="middle">{pts(p)}</td></tr></table></td></tr></table>')
    MED=[('🥇','#f5b800','#fff8db'),('🥈','#94a3b8','#f1f5f9'),('🥉','#d97706','#fff1e0')]
    pod='<table width="100%" cellpadding="0" cellspacing="8" style="margin:0 0 6px"><tr>'+''.join(
        f'<td width="33%" valign="top" align="center" bgcolor="{MED[k][2]}" style="background:{MED[k][2]};border:3px solid {MED[k][1]};border-radius:18px;padding:12px 8px">'
        f'<div style="font-size:40px;line-height:1">{MED[k][0]}</div><div style="{A};font-size:17px;font-weight:900;color:#0f172a;margin-top:4px">{html.escape(p["n"])}</div>'
        f'<div style="{A};font-size:11px;color:#6366f1;letter-spacing:2px">{p["t"]}</div><div style="margin:6px 0 4px">{pts(p,44)}</div>'
        f'<div style="{A};font-size:12px;color:#475569;margin-bottom:6px">{ow(p)}</div>{chips(p,True)}</td>' for k,p in enumerate(best[:3]))+'</tr></table>'
    rest=''.join(row(i,p) for i,p in enumerate(best[3:10],4))
    hmr=''.join(f'<tr><td style="{A};font-size:13px;color:#94a3b8;padding:5px 8px;border-bottom:1px solid #eef0f4">{i}</td><td style="{A};font-size:13px;color:#64748b;padding:5px 8px;border-bottom:1px solid #eef0f4"><b>{html.escape(p["n"])}</b> {p["t"]} · {ow(p)}</td><td align="right" style="{F};font-size:16px;font-style:italic;color:#64748b;padding:5px 8px;border-bottom:1px solid #eef0f4">{fpt(p["fp"])}</td></tr>' for i,p in enumerate(best[10:15],11))
    wst=''.join(row(i,p,'#38bdf8','#6366f1','#bae6fd') for i,p in enumerate(worst[:5],1))
    b0=best[0]; t0=tier(b0['fp'])
    jk=''
    for o,L in stacks(best[:10]):
        tt={3:'JACKPOT!',4:'MEGA JACKPOT!!'}.get(len(L),'GRAND JACKPOT!!!')
        jk+=(f'<table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 16px"><tr><td bgcolor="#ffb020" style="background:#ffb020;background-image:linear-gradient(100deg,#ffd23f,#ff9f1c 55%,#ff6b35);border:3px dashed #b45309;border-radius:18px;padding:16px 20px">'
             f'<table cellpadding="0" cellspacing="0"><tr><td style="font-size:50px;padding-right:14px">🎰</td><td><div style="{F};font-size:32px;font-style:italic;font-weight:900;color:#2a1500;line-height:1">{tt}</div>'
             f'<div style="{A};font-size:16px;color:#2a1500;margin:4px 0 8px"><b>{html.escape(o)}</b> hit {len(L)}-of-a-kind in the top 10</div>'
             +''.join(f'<span style="display:inline-block;{A};font-size:14px;font-weight:700;color:#2a1500;background:#fff3c4;border:1px solid #b45309;border-radius:999px;padding:2px 10px;margin:0 6px 4px 0">#{i} {html.escape(shortn(p["n"]))} <b>{fpt(p["fp"])}</b></span>' for i,p in L)
             +f'<span style="display:inline-block;{A};font-size:14px;font-weight:900;color:#ffd23f;background:#2a1500;border-radius:999px;padding:3px 12px">💰 {fpt(sum(p["fp"] for _,p in L))} PTS</span></td></tr></table></td></tr></table>')
    sec=lambda t,c: f'<table width="100%" cellpadding="0" cellspacing="0" style="margin:22px 0 10px"><tr><td style="{F};font-size:30px;font-style:italic;font-weight:900;color:#0f172a;white-space:nowrap;padding-right:12px">{t}</td><td width="100%" style="border-bottom:6px solid {c}"></td></tr></table>'
    out=(f'<div style="{A};color:#0f172a;max-width:760px">'
      f'<table width="100%" cellpadding="0" cellspacing="0"><tr><td bgcolor="#141a4d" style="background:#141a4d;background-image:linear-gradient(135deg,#ff6b35 0%,#ff3d5a 30%,#7c3aed 65%,#0ea5e9 100%);border-radius:22px;padding:24px 26px;border:4px solid #ff7a18">'
      f'<div style="display:inline-block;{A};font-size:12px;font-weight:900;letter-spacing:3px;color:#0a0f30;background:#22d3ee;padding:4px 10px;border-radius:6px">BBL · BOMBASTIC BASKETBALL LEAGUE</div>'
      f'<div style="{F};font-size:56px;font-weight:900;font-style:italic;line-height:1;color:#fff7c2;margin:10px 0 4px;text-shadow:0 3px 0 #b91c1c">BEST &amp; WORST</div>'
      f'<div style="{A};font-size:17px;color:#ffffff;font-weight:700">of the night · {html.escape(label)} · {ndone}/{ngames} games final</div></td></tr></table>'
      +(f'<p style="margin:12px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:15px"><a href="{CC_LINK}" style="display:inline-block;color:#ffffff;background:#7c3aed;border:2px solid #7c3aed;border-radius:999px;padding:6px 16px;font-weight:700;text-decoration:none">📸 Save tonight\'s Top 10 image →</a> <span style="color:#64748b;font-size:12px">Command Center · Today → Best &amp; worst</span></p>' if CC_LINK else '')+
      f'<table width="100%" cellpadding="0" cellspacing="0" style="margin:16px 0"><tr><td bgcolor="#1d1450" style="background:#1d1450;border:4px solid #a855f7;border-left:12px solid #ff7a18;border-radius:20px;padding:18px 22px">'
      f'<table width="100%" cellpadding="0" cellspacing="0"><tr><td valign="middle"><div style="display:inline-block;{A};font-size:12px;font-weight:900;letter-spacing:3px;color:#ffffff;background:#ff3d5a;padding:4px 10px;border-radius:999px">⭐ PLAYER OF THE NIGHT</div>'
      f'<div style="{F};font-size:32px;font-weight:900;color:#ffffff;margin:8px 0 6px;line-height:1.1">{html.escape(hl)}</div><div style="{A};font-size:15px;color:#c7d2fe;margin-bottom:8px">{ow(b0)}</div>{chips(b0)}</td>'
      f'<td width="160" align="center" valign="middle"><div style="{F};font-size:84px;font-weight:900;font-style:italic;color:#ffd23f;line-height:1">{fpt(b0["fp"])}{(f"<sup style=font-size:30px>{t0[1]}</sup>") if t0 else ""}</div><div style="{A};font-size:13px;font-weight:900;letter-spacing:3px;color:#c7d2fe">BBL PTS</div></td></tr></table></td></tr></table>'
      +jk+sec('🔥 TOP 10','#ff7a18')+pod+rest
      +(f'<div style="{A};font-size:12px;font-weight:900;letter-spacing:3px;color:#94a3b8;margin:14px 0 4px">HONORABLE MENTIONS</div><table width="100%" cellpadding="0" cellspacing="0">{hmr}</table>' if hmr else '')
      +sec('🥶 OOF ZONE','#38bdf8')+f'<div style="{A};font-size:14px;color:#0369a1;margin:-4px 0 10px;font-weight:700">Worst 5 of the night · 20+ minutes</div>'+wst
      +f'<p style="{A};font-size:12px;color:#64748b;margin-top:16px"><b>BBL pts</b> = league scoring in the player\'s best slot (G +1 per reb · F +1 per ast · C +1 per 3PM). Top 10 ties go to the higher base score, then fewer minutes; worst list ties to the lower base score, then more minutes. Next to each player: the BBL team that owns him, or Free agent.</p></div>')
    open('nightly_share.html','w').write(_re.sub(r'\s+',' ',out))
    on=lambda p:(MYTEAM if owner.get(p['n'],'FA')=='Yours' else owner.get(p['n'],'FA'))
    open('nightly_share.txt','w').write(f'BBL Best & Worst · {label}\n\nTOP 10\n'+''.join(f"{i}. {p['n']} ({p['t']}, {on(p)}) {fpt(p['fp'])} BBL pts · {p['pts']} pts, {p['reb']} reb, {p['ast']} ast, {p['stl']} stl, {p['blk']} blk, {p['fgm']}-{p['fga']} FG\n" for i,p in enumerate(best[:10],1))+'\nWORST 5 (20+ min)\n'+''.join(f"{i}. {p['n']} ({p['t']}, {on(p)}) {fpt(p['fp'])} BBL pts · {p['pts']} pts, {p['reb']} reb, {p['ast']} ast, {p['fgm']}-{p['fga']} FG\n" for i,p in enumerate(worst[:5],1)))
    open('nightly_share_subject.txt','w').write(f'🏀 BBL Best & Worst · {label} · '+hl)
    print('share ok',len(P)); sys.exit(0)
if SHORT and P:
    def line(p):
        bits=[f"{p['pts']} pts",f"{p['reb']} reb",f"{p['ast']} ast"]+([f"{p['stl']} stl"] if p['stl']>=2 else [])+([f"{p['blk']} blk"] if p['blk']>=2 else [])+([f"{p['to']} TO"] if p['to']>=4 else [])+[f"{p['fgm']}-{p['fga']} FG"]
        o=owner.get(p['n'],'FA'); o='★ yours' if o=='Yours' else o
        return f"<b>{html.escape(p['n'])}</b> <span style='color:#667085;font-size:12px'>{p['t']} · {html.escape(o)}</span> — {fpb(p['fp'],True)} <span style='color:#9fb3bd;font-size:11px'>{p['slot']}</span> · {', '.join(bits)}"
    out=(headline(best[0],True)+stack_html(best[:10],True)+'<p style="margin:4px 0"><b>🔥 Best 5</b></p><ol style="margin:0 0 8px;padding-left:20px">'+''.join(f'<li>{line(p)}</li>' for p in best[:5])+'</ol>'
         '<p style="margin:4px 0"><b>🤮 Worst 5</b> <span style="color:#667085;font-size:12px">(20+ min)</span></p><ol style="margin:0;padding-left:20px">'+''.join(f'<li>{line(p)}</li>' for p in worst[:5])+'</ol>'
         +f'<p style="font-size:12px;color:#667085">{ndone} of {ngames} games final. Points = BBL best-slot. Full top 10s on the page (Today tab).</p>')
    open('nightly_short.html','w').write(out)
    open('nightly_short.txt','w').write('BEST 5\n'+''.join(f"{i}. {p['n']} ({p['t']}, {owner.get(p['n'],'FA')}) {p['fp']} — {p['pts']}p {p['reb']}r {p['ast']}a\n" for i,p in enumerate(best[:5],1))+'WORST 5 (20+ min)\n'+''.join(f"{i}. {p['n']} ({p['t']}, {owner.get(p['n'],'FA')}) {p['fp']} — {p['pts']}p {p['reb']}r {p['ast']}a\n" for i,p in enumerate(worst[:5],1)))
else:
    if SHARE:  # compact, email-safe copy (Yahoo): table attributes instead of per-cell styles, Arial wrapper
        out=out.replace(f' {TD}','').replace(f' {TH}',' align="left"')
        out=re.sub(r'<tr>(<td style="padding:3px 6px;border-bottom:1px solid #eef0f4;font-size:11.5px;white-space:nowrap;opacity:.6">)',r'<tr style="font-size:11px;color:#98a2b3">\1',out)
        out=out.replace(' style="padding:3px 6px;border-bottom:1px solid #eef0f4;font-size:11.5px;white-space:nowrap;opacity:.6"','')
        out=out.replace('<table style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif">','<table cellpadding="4" rules="rows" frame="hsides" bordercolor="#e5e7eb" style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif;font-size:13px">')
        out='<div style="font-family:Arial,sans-serif;color:#1b2230">'+re.sub(r'\s+',' ',out)+'</div>'
    open('nightly_share.html' if SHARE else ('nightly_email.html' if EMAIL else 'nightly.html'),'w').write(out)
    if SHARE and P:
        on=lambda p:(MYTEAM if owner.get(p['n'],'FA')=='Yours' else owner.get(p['n'],'FA'))
        open('nightly_share.txt','w').write(f'BBL Best & Worst · {label}\n\nTOP 10\n'+''.join(f"{i}. {p['n']} ({p['t']}, {on(p)}) {fpt(p['fp'])} BBL pts · {p['pts']} pts, {p['reb']} reb, {p['ast']} ast, {p['stl']} stl, {p['blk']} blk, {p['fgm']}-{p['fga']} FG\n" for i,p in enumerate(best[:10],1))+'\nWORST 10 (20+ min)\n'+''.join(f"{i}. {p['n']} ({p['t']}, {on(p)}) {fpt(p['fp'])} BBL pts · {p['pts']} pts, {p['reb']} reb, {p['ast']} ast, {p['fgm']}-{p['fga']} FG\n" for i,p in enumerate(worst[:10],1)))
    if SHARE and P: open('nightly_share_subject.txt','w').write(f'🏀 BBL Best & Worst · {label} · '+re.sub(r'<[^>]+>','',headline(best[0],True).split('</div>')[0]).strip())
print('ok',len(P),'players',ndone,'/',ngames)
