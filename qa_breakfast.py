"""Breakfast page and cross-scope regression checks; run after build.py."""
import csv
import html
from pathlib import Path
from data import PLACES,TYPES,AREAS,BREAKFAST_NAMES
from guide_export import HOSTED_GOOGLE

root=Path(__file__).parent
names=[r[0] for r in PLACES]
assert len(names)==len(set(names))==89
assert len(BREAKFAST_NAMES)==len(set(BREAKFAST_NAMES))==8
assert set(BREAKFAST_NAMES)<=set(names)
assert TYPES['breakfast']=='Breakfast & Brunch'
for slug,expected in [('all/amsterdam',89),('types/breakfast',8),('neighbourhoods/de-pijp',19),('neighbourhoods/oud-west',11),('neighbourhoods/jordaan',12)]:
    for source in ('exports','exports/google'):
        rows=list(csv.DictReader((root/source/(slug+'.csv')).open()))
        assert len(rows)==expected,(source,slug,len(rows),expected)
        assert len({r['Name'] for r in rows})==expected
br=(root/'types/breakfast.html').read_text()
assert all(br.count('<h3>'+html.escape(name)+'</h3>')==1 for name in BREAKFAST_NAMES)
assert 'No hosted custom map has been published for this category yet' in br
assert 'Breakfast &amp; Brunch' in (root/'index.html').read_text()
assert '85 of 89 current stops' in (root/'index.html').read_text()
for name,slug in [('De Wasserette','de-pijp'),('Bakers & Roasters De Pijp','de-pijp'),('Staring at Jacob','oud-west'),('Kessens','jordaan')]:
    assert '<h3>'+html.escape(name)+'</h3>' in (root/'neighbourhoods'/(slug+'.html')).read_text()
    assert html.escape(name) in br
for slug,prior in [('de-pijp',17),('oud-west',10),('jordaan',11)]:
    assert f'{prior} of ' in (root/'neighbourhoods'/(slug+'.html')).read_text()
    assert HOSTED_GOOGLE['neighbourhoods/'+slug]['count']==prior
print('BREAKFAST_QA: 89 unique venues; 8 breakfast picks; 4 new across 3 areas; scoped CSVs, pages and stale-map disclosure verified')
