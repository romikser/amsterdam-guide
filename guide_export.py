"""Static Apple Maps Guide links and complete CSV exports for public city-guide scopes.

Apple Maps URLs open a shareable Guide; visitors choose Add to Guides themselves.
Only confirmed business/venue POIs are encoded. Unmapped cards remain in CSV.
"""
import base64,csv,html,io,json,urllib.parse
from pathlib import Path

ROOT=Path(__file__).parent
PLACES=json.loads((ROOT/'apple-maps-places.json').read_text())
LOOKUP={p['name']:p for p in PLACES}


def varint(value):
    result=bytearray()
    while value>=128:
        result.append((value&127)|128)
        value>>=7
    result.append(value)
    return bytes(result)


def field(num,payload):
    return varint((num<<3)|2)+varint(len(payload))+payload


def guide_url(title,place_ids):
    payload=field(1,title.encode('utf-8'))
    for place_id in place_ids:
        poi=int(place_id[1:],16)
        item=varint(1<<3)+varint(9902)+varint(2<<3)+varint(poi)
        payload+=field(2,item)
    return 'https://maps.apple.com/guides?user='+urllib.parse.quote(base64.b64encode(payload).decode('ascii'),safe='')


def export(scope,slug,title,rows,prefix=''):
    """Write the complete CSV and return accessible, scope-specific export controls."""
    names=[r[0] for r in rows]
    assert len(names)==len(set(names)) and set(names)<=set(LOOKUP)
    mapped=[LOOKUP[n] for n in names if LOOKUP[n]['id']]
    missing=[LOOKUP[n] for n in names if not LOOKUP[n]['id']]
    assert len(mapped)+len(missing)==len(rows)
    csvpath=ROOT/'exports'/scope/(slug+'.csv')
    csvpath.parent.mkdir(parents=True,exist_ok=True)
    with csvpath.open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f,lineterminator='\n')
        writer.writerow(['Name','Neighbourhood','Category','Official/source URL','Apple Maps URL','Export note'])
        for n,area,typ,_,site,query,_,_ in rows:
            poi=LOOKUP[n]
            mapsurl=('https://maps.apple.com/place?place-id='+poi['id'] if poi['id'] else 'https://maps.apple.com/?q='+urllib.parse.quote(query))
            writer.writerow([n,area,typ,site,mapsurl,poi['reason']])
    url=guide_url('Amsterdam · '+title,[p['id'] for p in mapped])
    esc=lambda text:html.escape(str(text),quote=True)
    h=f'<div class="export-box"><div class="export-actions"><a class="export-button" href="{esc(url)}" target="_blank" rel="noopener" aria-label="Open {esc(title)} in Apple Maps as a Guide">Open Apple Maps Guide · {len(mapped)} places ↗</a><a class="export-button secondary" href="{prefix}exports/{scope}/{slug}.csv" download>Download complete list · {len(rows)} places ↓</a></div><p>Apple Maps: open the Guide, then choose Add to Guides to save it. The CSV includes every listed stop.</p>'
    if missing:
        details=''.join(f'<li><strong>{esc(p["name"])}</strong> — {esc(p["reason"])} <a href="{esc("https://maps.apple.com/?q="+urllib.parse.quote(p["query"]))}" target="_blank" rel="noopener">Search manually ↗</a></li>' for p in missing)
        h+=f'<details class="export-caveat"><summary>{len(missing)} of {len(rows)} stops have no verified Apple Maps pin; they remain in the complete CSV</summary><ul>{details}</ul></details>'
    return h+'</div>'
