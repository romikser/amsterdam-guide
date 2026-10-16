"""Breakfast page and cross-scope regression checks; run after build.py."""
import csv
import html
from pathlib import Path
from data import PLACES,TYPES,AREAS,BREAKFAST_NAMES
from guide_export import HOSTED_GOOGLE

root=Path(__file__).parent
names=[r[0] for r in PLACES]
assert len(names)==len(set(names))==97
assert len(BREAKFAST_NAMES)==len(set(BREAKFAST_NAMES))==16
assert set(BREAKFAST_NAMES)<=set(names)
assert TYPES['breakfast']=='Breakfast & Brunch'
for slug,expected in [('all/amsterdam',97),('types/breakfast',16),('neighbourhoods/de-pijp',23),('neighbourhoods/oud-west',13),('neighbourhoods/jordaan',12)]:
    for source in ('exports','exports/google'):
        rows=list(csv.DictReader((root/source/(slug+'.csv')).open()))
        assert len(rows)==expected,(source,slug,len(rows),expected)
        assert len({r['Name'] for r in rows})==expected
br=(root/'types/breakfast.html').read_text()
assert len(BREAKFAST_NAMES)==16
assert all(br.count('<h3>'+html.escape(name)+'</h3>')==1 for name in BREAKFAST_NAMES)
assert 'No hosted custom map has been published for this category yet' in br
assert 'Breakfast &amp; Brunch' in (root/'index.html').read_text()
assert f'{len(PLACES)} current stops' in (root/'index.html').read_text()
for name,slug in [('De Wasserette','de-pijp'),('Bakers & Roasters De Pijp','de-pijp'),('Staring at Jacob','oud-west'),('Kessens','jordaan'),('Belly Pepper','oud-west'),('Bakkerij Louf Oud-West','oud-west'),('Fort Negen','de-baarsjes'),("Flo's Deli Utrechtsestraat",'centrum'),('BagelBoy Albert Cuyp','de-pijp'),('Florentin Brunch','de-pijp'),('LOCALS','de-pijp'),('Eggs Benaddicted De Pijp','de-pijp')]:
    assert '<h3>'+html.escape(name)+'</h3>' in (root/'neighbourhoods'/(slug+'.html')).read_text()
    assert html.escape(name) in br
for slug,prior in [('de-pijp',17),('oud-west',10),('jordaan',11)]:
    assert f'{prior} of ' in (root/'neighbourhoods'/(slug+'.html')).read_text()
    assert HOSTED_GOOGLE['neighbourhoods/'+slug]['count']==prior
print(f'BREAKFAST_QA: {len(PLACES)} unique venues; {len(BREAKFAST_NAMES)} breakfast picks; Instagram-led additions, scoped CSVs, pages and stale-map disclosure verified')
