"""Static Apple Maps Guide links and Apple/Google My Maps CSVs for guide scopes.

Apple Maps URLs open a shareable Guide; visitors choose Add to Guides themselves.
Only confirmed business/venue POIs are encoded in Apple URLs. Google My Maps
imports locations from a separate CSV; a few ambiguous spots need user review.
"""
import base64,csv,html,io,json,urllib.parse
from pathlib import Path

ROOT=Path(__file__).parent
PLACES=json.loads((ROOT/'apple-maps-places.json').read_text())
LOOKUP={p['name']:p for p in PLACES}
GOOGLE_QUERIES={
    'Upstream — Leegte / Rozendaal':'upstream Gallery Kloveniersburgwal 95 Amsterdam',
    'Beef Chief at Transit':'Beef Chief // Transit Bar Aambeeldstraat 38 Amsterdam',
    'Middle East Archive × Foam':'Mercatorplein Amsterdam',
}


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
    googlepath=ROOT/'exports'/'google'/scope/(slug+'.csv')
    googlepath.parent.mkdir(parents=True,exist_ok=True)
    with googlepath.open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f,lineterminator='\n')
        writer.writerow(['Name','Location','Neighbourhood','Category','Official URL','Location note'])
        for n,area,typ,_,site,query,_,_ in rows:
            poi=LOOKUP[n]
            # Exact address where checked; otherwise the public search query.
            # My Maps geocodes on import: this is not a verified Google POI ID.
            location=GOOGLE_QUERIES.get(n) or poi.get('apple_destination') or query
            note=('Outdoor exhibition: this pin is the square, not the artwork. Check on arrival.' if n=='Middle East Archive × Foam' else '')
            writer.writerow([n,location,area,typ,site,note])
    url=guide_url('Amsterdam · '+title,[p['id'] for p in mapped])
    esc=lambda text:html.escape(str(text),quote=True)
    h=f'<div class="export-box"><div class="export-actions"><a class="export-button" href="{esc(url)}" target="_blank" rel="noopener" aria-label="Open {esc(title)} in Apple Maps as a Guide">Open Apple Maps Guide · {len(mapped)} places ↗</a><a class="export-button secondary" href="{prefix}exports/google/{scope}/{slug}.csv" download aria-label="Download {esc(title)} for import into Google My Maps">Google My Maps CSV · {len(rows)} stops ↓</a><a class="export-button secondary" href="{prefix}exports/{scope}/{slug}.csv" download>Complete list · {len(rows)} stops ↓</a></div><p>Apple: open and choose Add to Guides. Google: import the CSV into My Maps; it does not auto-save to your account.</p><details class="export-caveat"><summary>How to save it in Google Maps</summary><p>On a computer, open <a href="https://www.google.com/mymaps" target="_blank" rel="noopener">Google My Maps ↗</a>, create a map and import the CSV. Choose Location for pins and Name for labels. Check the pins, then view your custom map in the Google Maps app under <strong>You → Maps</strong>. My Maps is separate from standard Saved lists.</p></details>'
    if missing:
        details=''.join(f'<li><strong>{esc(p["name"])}</strong> — {esc(p["reason"])} <a href="{esc("https://maps.apple.com/?q="+urllib.parse.quote(p["query"]))}" target="_blank" rel="noopener">Search manually ↗</a></li>' for p in missing)
        h+=f'<details class="export-caveat"><summary>{len(missing)} of {len(rows)} stops have no verified Apple Maps pin; they remain in the complete CSV</summary><ul>{details}</ul></details>'
    if 'Middle East Archive × Foam' in names:
        h+='<details class="export-caveat"><summary>One Google map pin is the square, not the exhibition</summary><p>Middle East Archive × Foam is outdoors at Mercatorplein without a distinct place pin. Check the square on arrival.</p></details>'
    return h+'</div>'
