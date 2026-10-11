from pathlib import Path
import html, json, re, urllib.parse
from data import AREAS,AREA_SOURCES,TYPES,PLACES
from guide_export import export
from events_data import EVENTS
from background_data import CITY_BACKGROUND,CITY_SOURCES,AREA_BACKGROUND
try:
 from data import DISCOVERY_SOURCES
except ImportError:
 DISCOVERY_SOURCES={}
ROOT=Path(__file__).parent
credits=json.loads((ROOT/'image-credits.json').read_text())
remote_images=json.loads((ROOT/'remote-images.json').read_text())
VENUE_PHOTOS={'Albert Cuyp Market':'market','Foodhallen':'foodhallen','Foam — Hailun Ma / Kander':'venue-foam','Huis Marseille':'venue-huis-marseille','Stedelijk':'venue-stedelijk','STRAAT':'venue-straat','Concerto':'venue-concerto','Rijksmuseum':'venue-rijksmuseum','Van Gogh Museum':'venue-van-gogh-museum'}
H=lambda s:html.escape(str(s),quote=True)
def pic(key,prefix=''):
 c=credits[key]
 portrait=' portrait' if key=='venue-foam' else ''
 return f'<div class="card-photo{portrait}"><img loading="lazy" src="{prefix}{H(c["local"])}" alt="{H(c.get("description") or c["title"].removeprefix("File:"))}"><span class="photo-badge">Photographed at the venue</span></div>'
def remote_pic(info):
 return f'<div class="card-photo"><img loading="lazy" referrerpolicy="no-referrer" src="{H(info["url"])}" alt="{H(info["alt"])}"><span class="photo-badge">Venue photo</span></div>'
def linkmap(q):return 'https://maps.apple.com/?q='+urllib.parse.quote(q)
def path(link,prefix):return prefix+link

def shell(title,body,prefix='',active=''):
 nav=''.join(f'<a href="{prefix}{dest}" '+('aria-current="page"' if active==dest else '')+f'>{label}</a>' for dest,label in [('neighbourhoods/index.html','Neighbourhoods'),('types/index.html','Place types'),('events.html','Events'),('selection.html','How picks are made')])
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#ffffff"><meta name="description" content="A concise, photo-led Amsterdam directory: local coffee, art, vinyl, independent clothes, food and neighbourhood walks."><title>{H(title)} · Amsterdam / Field Guide</title><link rel="stylesheet" href="{prefix}style.css"></head><body><header><nav aria-label="Primary"><a class="brand" href="{prefix}index.html">AMS<span>/</span>FIELD GUIDE</a><div class="navlinks">{nav}</div></nav></header><main>{body}</main><footer><span>Independent city directory · researched October 2026 · recheck hours and bookings</span><a href="{prefix}credits.html">Photo sources & licences</a></footer></body></html>'''

def tile(name,description,key,href,prefix=''):
 c=credits[key]
 return f'<a class="tile" href="{prefix}{href}"><img loading="lazy" src="{prefix}{H(c["local"])}" alt="{H(c["title"].removeprefix("File:"))}"><div class="tile-copy"><h3>{H(name)}</h3><p>{H(description)}</p></div></a>'

def card(row,prefix=''):
 name,area,typ,summary,site,query,detail,_=row
 photo_key=VENUE_PHOTOS.get(name)
 remote=remote_images.get(name) if not photo_key else None
 media=pic(photo_key,prefix) if photo_key else (remote_pic(remote) if remote else '')
 photo_note=(f'<p>Photograph: <a href="{H(credits[photo_key]["page"])}">Wikimedia Commons</a> ({H(credits[photo_key]["license"])}); cropped for display.</p>' if photo_key else (f'<p>Image from <a href="{H(remote["source"])}" target="_blank" rel="noopener">{H(remote["credit"])} ↗</a>; displayed from the credited source, not copied here.</p>' if remote else ''))
 source_links=''.join(f'<li><a href="{H(url)}" target="_blank" rel="noopener">{H(label)}</a></li>' for label,url in DISCOVERY_SOURCES.get(name,[]))
 sources=f'<p>Discovery & evidence:</p><ul>{source_links}</ul>' if source_links else ''
 return f'<article class="card{"" if (photo_key or remote) else " no-photo"}">{media}<div class="card-body"><div class="card-meta"><a href="{prefix}neighbourhoods/{area}.html">{H(AREAS[area][0])}</a> / <a href="{prefix}types/{typ}.html">{H(TYPES[typ])}</a></div><h3>{H(name)}</h3><p>{H(summary)}</p><div class="card-links"><a href="{H(linkmap(query))}" target="_blank" rel="noopener">Apple Maps ↗</a><a href="{H(site)}" target="_blank" rel="noopener">Official / source ↗</a></div><details><summary>Hours, bookings & sources</summary><p>{H(detail)}</p>{sources}{photo_note}</details></div></article>'

def event_card(item):
 image=item.get('image')
 media=(f'<div class="card-photo event-photo"><img loading="lazy" referrerpolicy="no-referrer" src="{H(image)}" alt="{H(item["alt"])}"><span class="photo-badge">Event / exhibition image</span></div>' if image else '')
 credit=(f'<p>Image: <a href="{H(item["url"])}" target="_blank" rel="noopener">{H(item["credit"])} ↗</a>; displayed from the credited source, not copied here.</p>' if image else '')
 return f'<article class="card event-card{"" if image else " no-photo"}">{media}<div class="card-body"><div class="card-meta">{H(item["date"])} / {H(item["kind"])}</div><h3>{H(item["title"])}</h3><p>{H(item["summary"])}</p><div class="card-links"><a href="{H(item["url"])}" target="_blank" rel="noopener">Official event ↗</a></div><details><summary>Timing, caveats & source</summary><p>{H(item["detail"])}</p>{credit}</details></div></article>'

def context_block(title,paragraphs,sources):
 paragraphs_html=''.join(f'<p>{H(paragraph)}</p>' for paragraph in paragraphs)
 source_html=' · '.join(f'<a href="{H(url)}" target="_blank" rel="noopener">{H(label)} ↗</a>' for label,url in sources)
 return f'<section class="context-block columns-{len(paragraphs)}" aria-label="Background"><div class="eyebrow">Where you are</div><h2>{H(title)}</h2><div class="context-copy">{paragraphs_html}</div><div class="context-sources">Background sources: {source_html}</div></section>'

def write(rel,content):
 p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8')
area_tile_blurbs={'de-pijp':'Worker-built streets, the market, coffee and small record shops.','oud-west':'Ten Katemarkt, converted halls and independent cafés.','jordaan':'Working-class canals, galleries and second-hand records.','nine-streets':'Seventeenth-century canal crossings and independent browsing.','centrum':'The medieval core, with better shops off the busiest strip.','haarlemmerbuurt':'A historic westward route of cafés and independent shopfronts.','canal-belt':'Planned canals, photography museums and deep record digging.','oost':'Dappermarkt, Javastraat and a slower green edge.','noord':'A ferry, a reclaimed shipyard and large-scale street art.','museumkwartier':'Rijks, Van Gogh and Stedelijk in one museum district.','de-baarsjes':'Amsterdam School brickwork and a quieter coffee detour.'}
area_tiles=''.join(tile(v[0],area_tile_blurbs[k],v[2],f'neighbourhoods/{k}.html') for k,v in AREAS.items())
type_images={'coffee-matcha':'de-pijp','street-food':'market','restaurants':'oost','vinyl':'centrum','clothes':'nine-streets','art':'museumkwartier','bars-music':'noord','markets':'oud-west'}
type_blurbs={'coffee-matcha':'Tea-forward stops and properly made coffee.','street-food':'Roti rolls, onigiri, sandwiches, burgers and market bites.','restaurants':'Worth arranging a table—or leaving flexible.','vinyl':'Jazz, soul, city-pop luck and electronic records.','clothes':'Independent stores, sharp labels and Dutch design.','art':'Photography and contemporary work first; the classics remain optional.','bars-music':'Cocktails, wine and dates that actually overlap.','markets':'Working streets and the pleasure of an unscheduled walk.'}
type_tiles=''.join(tile(name,type_blurbs[k],type_images[k],f'types/{k}.html') for k,name in TYPES.items())
hero='<section class="hero"><div class="eyebrow">Pocket directory / Amsterdam</div><h1>Amsterdam<span style="color:#087549">.</span></h1><p>An old river port, planned canals, worker-built streets and a former shipyard across the IJ: Amsterdam changes character block by block. Start with the city’s layers below, then browse by neighbourhood or by what you want to do.</p>'+export('all','amsterdam','All stops',PLACES)+'</section>'
home=hero+context_block('How the city grew',CITY_BACKGROUND,CITY_SOURCES)+'<section class="section"><div class="section-head"><h2>In the city</h2><a href="events.html">All events →</a></div><p class="intro">A short edit of music, print, photography and city-wide dates—not every listing in town.</p><div class="cards">'+''.join(event_card(EVENTS[i]) for i in (0,6,9))+'</div></section><section class="section"><div class="section-head"><h2>Neighbourhoods</h2><a href="neighbourhoods/index.html">See all →</a></div><div class="tiles">'+area_tiles+'</div></section><section class="section"><div class="section-head"><h2>Place types</h2><a href="types/index.html">See all →</a></div><div class="tiles">'+type_tiles+'</div></section>'
sections=[]
for slug,label,intro in [('music','Concerts & parties','Choose for the lineup and the energy you will actually have.'),('city','Festivals & city dates','Two worthwhile public events, not a generic festival calendar.'),('art','Exhibitions on now','Photography and music history worth a timed visit.')]:
 rows=[event for event in EVENTS if event['group']==slug]
 sections.append(f'<section class="group" id="{slug}"><h2>{label}</h2><p class="intro">{intro}</p><div class="cards">'+''.join(event_card(event) for event in rows)+'</div></section>')
events_hero='<section class="hero"><div class="eyebrow">October 2026 / selected city dates</div><h1>On now.</h1><p>Independent print, specific gigs, dancefloors and exhibitions that match this guide. Each listing links to the organiser; times and tickets can change.</p><p>Doka and SANAM overlap on Sunday evening. The marathon affects streets that weekend. ADE begins on 21 October, outside this selection.</p></section>'
write('events.html',shell('Events',events_hero+'<nav class="subnav" aria-label="Event groups"><a href="#music">Concerts & parties</a><a href="#city">Festivals & city dates</a><a href="#art">Exhibitions</a></nav>'+''.join(sections),'','events.html'))
write('index.html',shell('Amsterdam',home))
write('neighbourhoods/index.html',shell('Neighbourhoods','<section class="hero"><div class="eyebrow">Browse by neighbourhood</div><h1>Areas.</h1><p>Separate pockets with different reasons to go. A good day needs only one or two.</p></section><section class="section"><div class="tiles">'+''.join(tile(v[0],area_tile_blurbs[k],v[2],f'neighbourhoods/{k}.html','../') for k,v in AREAS.items())+'</div></section>','../','neighbourhoods/index.html'))
write('types/index.html',shell('Place types','<section class="hero"><div class="eyebrow">Browse across the city</div><h1>Find a place.</h1><p>Cross-neighbourhood shortlists, without searching through an itinerary.</p></section><section class="section"><div class="tiles">'+''.join(tile(v,type_blurbs[k],type_images[k],f'types/{k}.html','../') for k,v in TYPES.items())+'</div></section>','../','types/index.html'))
for slug,(name,blurb,img) in AREAS.items():
 rows=[r for r in PLACES if r[1]==slug]
 sections=''
 for k,label in TYPES.items():
  group=[r for r in rows if r[2]==k]
  if group: sections+=f'<section class="group" id="{k}"><h2>{H(label)}</h2><div class="cards">'+''.join(card(r,'../') for r in group)+'</div></section>'
 hcls=' class="long-title"' if len(name)>12 else ''
 area_photo=credits[img]
 area_figure=f'<figure class="area-photo"><img loading="eager" src="../{H(area_photo["local"])}" alt="{H(area_photo.get("description") or area_photo["title"].removeprefix("File:"))}"><figcaption>Area photograph, not a venue recommendation · <a href="{H(area_photo["page"])}" target="_blank" rel="noopener">Photo source ↗</a></figcaption></figure>'
 area_export=export('neighbourhoods',slug,name,rows,'../')
 head=f'<section class="hero"><div class="eyebrow"><a href="index.html">← All neighbourhoods</a> / {len(rows)} stops</div><h1{hcls}>{H(name)}.</h1><p>{H(blurb)}</p>{area_export}{area_figure}</section>'
 area_context=context_block('The neighbourhood',AREA_BACKGROUND[slug],[('Area research',AREA_SOURCES[slug])])
 sub='<div class="subnav" aria-label="Place types in this area">'+''.join(f'<a href="#{k}">{H(label)}</a>' for k,label in TYPES.items() if any(r[2]==k for r in rows))+'</div>'
 if slug=='noord':sub+='<p class="note">NDSM/STRAAT and Garage Noord are in different parts of Noord. Do not plan them as a short walk between neighbouring venues.</p>'
 if slug=='de-pijp':sub+='<p class="note">On marathon Sunday, markets are shut and several bordering roads are affected. Keep the day flexible; use the organiser’s route and live GVB planner.</p>'
 write(f'neighbourhoods/{slug}.html',shell(name,head+area_context+sub+sections,'../','neighbourhoods/index.html'))
for slug,name in TYPES.items():
 rows=[r for r in PLACES if r[2]==slug]
 sections=''
 for a,(label,_,_) in AREAS.items():
  group=[r for r in rows if r[1]==a]
  if group:sections+=f'<section class="group" id="{a}"><h2><a href="../neighbourhoods/{a}.html">{H(label)} ↗</a></h2><div class="cards">'+''.join(card(r,'../') for r in group)+'</div></section>'
 type_export=export('types',slug,name,rows,'../')
 head=f'<section class="hero"><div class="eyebrow"><a href="index.html">← All place types</a> / {len(rows)} stops</div><h1>{H(name)}.</h1><p>{H(type_blurbs[slug])}</p>{type_export}</section>'
 write(f'types/{slug}.html',shell(name,head+sections,'../','types/index.html'))
selection_body='''<section class="hero"><div class="eyebrow">Editorial notes</div><h1>Why these?</h1><p>These are places to consider, not an algorithmic top-ten. An account can know Amsterdam and still have entirely different taste. We treat Instagram as a way to find leads, then check who made the recommendation, what they actually tried, whether the place still exists at that address, and whether it fits this guide.</p></section><section class="section"><div class="group"><h2>Calibrate the source first</h2><p class="intro">For coffee, <a href="https://www.instagram.com/reel/DGIxyL5MhRV/">The Coffeevine’s Amsterdam six</a> explicitly favour bars focused on exceptional coffee rather than hot-food menus; its repeat specialty coverage is useful for coffee, not a blanket vote on art or dinner. It sells coffee subscriptions, so we still check individual venue claims. For casual food, <a href="https://www.instagram.com/p/DMdKqixt28C/">Forking Delicious</a> describes a real burger tasting while saying Le Smash was not a personal favourite: that nuance is more useful than a viral “best” reel. For matcha, posts that discuss tea origin, bitterness, texture and preparation carry more weight than colour or a long queue.</p></div><div class="group"><h2>Then verify the place</h2><p class="intro">A venue’s own post can confirm an exhibition, menu or move, but is not an independent quality endorsement. Exact dated Instagram captions and specialist reviews appear under “Hours, bookings & sources” on supported cards; not every listed place has an independently accessible Instagram post. Official venue pages are used for current location, schedule and tickets. Verify same-day hours—especially market stalls and pop-ups. The separate <a href="events.html">events edit</a> is researched for a narrow October window from organiser/venue pages: confirm the exact date, location, price and ticket status again before committing. It excludes children’s festivals, off-date ADE parties and events with no clear match to the guide’s music, art or independent-print interests.</p></div><div class="group"><h2>Useful negatives</h2><p class="intro">We rejected a five-matcha-spots reel that put a Rotterdam tearoom in Amsterdam. We did not route to Suki’s old Elandsgracht address, Rush Hour’s old street number or DAK’s roastery instead of its public showroom. City Records is held while its announced move to Nieuwe Hoogstraat is confirmed. A gallery’s older post or a New York exhibition is not evidence that the same show is on in Amsterdam now.</p></div><div class="group"><h2>Photography & maps</h2><p class="intro">Photos are either reusable real-area or venue images with <a href="credits.html">credits and licences</a>, or displayed directly from an official venue page with source attribution. We do not copy Google or Apple Maps customer photos. Apple Maps does not provide a token-free multi-pin embed for this static site; each card has an Apple Maps link, and the home, neighbourhood and category pages offer separate Guide links built from verified current place pins. A few venues with stale or absent Apple Maps listings are omitted from those Guide links and are named in the export notes; complete CSV downloads retain every website pick.</p></div></section>'''
write('selection.html',shell('How places are picked',selection_body,'','selection.html'))
credit_rows=''
for key,c in credits.items():
 artist=re.sub('<[^>]+>','',html.unescape(c.get('artist',''))).strip()
 license_url=c.get('license_url','')
 license_label=f'<a href="{H(license_url)}">{H(c["license"])}</a>' if license_url else H(c['license'])
 credit_rows+=f'<li><strong>{H(key.replace("-"," ").title())}</strong>: <a href="{H(c["page"])}">{H(c["title"].removeprefix("File:"))}</a> — {H(artist or "Creator credited on source page")} · {license_label}. Resized and cropped for display.</li>'
for name,c in remote_images.items():
 credit_rows+=f'<li><strong>{H(name)}</strong>: <a href="{H(c["source"])}" target="_blank" rel="noopener">Original credited page</a> — {H(c["credit"])}. Image displayed from its original host; it is not copied into this site.</li>'
for event in EVENTS:
 if event.get('image'):
  credit_rows+=f'<li><strong>{H(event["title"])} (event)</strong>: <a href="{H(event["url"])}" target="_blank" rel="noopener">Official event page</a> — {H(event["credit"])}. Displayed from its original host; not copied into this site.</li>'
credits_body='<section class="hero"><div class="eyebrow">Provenance</div><h1>Images.</h1><p>Licensed real Amsterdam neighbourhood photos and selected venue photos, plus images displayed directly from their credited hosts. Cards without a verified venue image remain text-only rather than showing an unrelated street scene. Hosted venue images can change or disappear; local licensed photographs were resized and cropped as noted below.</p></section><section class="section"><ul class="credits">'+credit_rows+'</ul></section>'
write('credits.html',shell('Photo credits',credits_body,'','credits.html'))
print('Generated',len(PLACES),'venues,',len(AREAS),'area pages,',len(TYPES),'type pages,',len(list(ROOT.rglob('*.html'))),'HTML files')
