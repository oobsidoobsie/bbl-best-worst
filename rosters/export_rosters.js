// BBL roster export — runs as a browser bookmark ("bookmarklet") on the CBS league site.
// It only READS pages you can already see while signed in (standings, each team page,
// and CBS's player lists for positions) and saves them to a file called bbl_rosters.txt
// in your Downloads folder. It never changes anything on CBS and never touches your password.
// Output lines: name|nba_team|positions|owner   (owner = TAKEN:<fantasy team> or FA)
//               #LOGO|<fantasy team>|<small logo as data URI>
(async () => {
  const box = document.createElement('div');
  box.style.cssText = 'position:fixed;z-index:2147483647;top:16px;right:16px;max-width:340px;padding:14px 16px;border-radius:12px;background:#141a4d;color:#fff;font:600 14px/1.4 -apple-system,Helvetica,Arial,sans-serif;box-shadow:0 8px 30px rgba(0,0,0,.35)';
  const say = (t) => { box.textContent = '🏀 BBL roster export · ' + t; };
  document.body.appendChild(box);
  const done = (t, ms = 6000) => { say(t); setTimeout(() => box.remove(), ms); };
  if (!/\.basketball\.cbssports\.com$/.test(location.hostname)) {
    return done('Open your CBS league site first (…basketball.cbssports.com), sign in, then click this bookmark again.', 9000);
  }
  try {
    const page = async (u) => new DOMParser().parseFromString(await (await fetch(u, { credentials: 'include' })).text(), 'text/html');
    say('reading teams…');
    const sd = await page('/standings/overall');
    const TEAMS = {};
    for (const a of sd.querySelectorAll('a[href*="/teams/"]')) {
      const id = (a.getAttribute('href').match(/\/teams\/(\d+)/) || [])[1];
      const t = a.textContent.trim();
      if (id && t && !TEAMS[id]) TEAMS[id] = t;
    }
    if (!Object.keys(TEAMS).length) return done('No teams found — are you signed in to CBS?', 9000);
    const OWN = {}, LOGO = {};
    let i = 0;
    for (const [id, tn] of Object.entries(TEAMS)) {
      say(`rosters ${++i}/${Object.keys(TEAMS).length}…`);
      const d = await page('/teams/' + id);
      const lg = [...d.querySelectorAll('img')].map((x) => x.getAttribute('src') || '').find((s) => s.includes('/team_logo/' + id + '-'));
      if (lg) LOGO[tn] = lg.split('?')[0];
      for (const tr of d.querySelectorAll('tr')) {
        const c = [...tr.cells].map((x) => x.textContent.trim().replace(/\s+/g, ' '));
        const m = c.join(' | ').match(/([A-Z][^|•]*?) ([CFG](?:,[CFG])*) • (\w+)/);
        if (m && c.length > 4 && !OWN[m[1].trim()]) OWN[m[1].trim()] = { tn, pos: m[2], team: m[3] };
      }
    }
    const P = {};
    for (const pos of ['G', 'F', 'C']) {
      say(`player positions (${pos})…`);
      const d = await page('/stats/stats-main/all:' + pos + '/restofseason:p/standard/projections?print_rows=9999');
      for (const r of d.querySelectorAll('tr')) {
        const c = [...r.cells].map((x) => x.textContent.trim().replace(/\s+/g, ' '));
        if (c.length < 3) continue;
        const m = (c[2] || '').match(/^(.*?) ([CFG](?:,[CFG])*) • (\w+)/) || (c[1] || '').match(/^(.*?) ([CFG](?:,[CFG])*) • (\w+)/);
        if (m && !P[m[1]]) P[m[1]] = { team: m[3], pos: m[2] };
      }
    }
    // rostered players missing from the projection lists still get their CBS position
    for (const [n, o] of Object.entries(OWN)) if (!P[n]) P[n] = { team: o.team, pos: o.pos };
    say('logos…');
    for (const [t, u] of Object.entries(LOGO)) {
      try {
        const bm = await createImageBitmap(await (await fetch(u)).blob());
        const cv = document.createElement('canvas'); cv.width = cv.height = 48;
        const s = Math.min(bm.width, bm.height);
        cv.getContext('2d').drawImage(bm, (bm.width - s) / 2, (bm.height - s) / 2, s, s, 0, 0, 48, 48);
        LOGO[t] = cv.toDataURL('image/png');
      } catch (e) { delete LOGO[t]; }
    }
    const lines = Object.entries(P).map(([n, p]) => [n, p.team, p.pos, OWN[n] ? 'TAKEN:' + OWN[n].tn : 'FA'].join('|'));
    const txt = '# BBL rosters exported ' + new Date().toISOString() + ' from ' + location.hostname + '\n' + lines.join('\n') + '\n' +
      Object.entries(LOGO).map(([t, u]) => '#LOGO|' + t + '|' + u).join('\n') + '\n';
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([txt], { type: 'text/plain' }));
    a.download = 'bbl_rosters.txt';
    document.body.appendChild(a); a.click(); a.remove();
    done(`saved bbl_rosters.txt to Downloads ✓ (${Object.keys(OWN).length} rostered players, ${Object.keys(TEAMS).length} teams)`, 9000);
  } catch (e) {
    done('something went wrong: ' + e.message, 12000);
  }
})();
