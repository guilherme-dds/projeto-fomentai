from bs4 import BeautifulSoup
import re

path = 'resultados_site_crawler/html_febrace.html'
with open(path, encoding='utf-8') as f:
    s = f.read()

soup = BeautifulSoup(s, 'html.parser')

print('TITLE:', soup.title.string.strip() if soup.title and soup.title.string else None)

hs = soup.find_all(['h1', 'h2', 'h3'])
print('\nHEADINGS (h1/h2/h3):')
for h in hs[:30]:
    print('-', h.get_text(separator=' ', strip=True))

# meta og:title
meta_og = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'og:title'})
print('\nOG:TITLE:', meta_og.get('content') if meta_og and meta_og.get('content') else None)

# search for candidate classes
candidates = []
for elem in soup.find_all(True):
    cls_list = elem.get('class')
    cls = ' '.join(cls_list) if cls_list else ''
    if re.search(r'title|heading|nome|event|feira|mostra|name|titulo', cls, re.IGNORECASE):
        text = elem.get_text(separator=' ', strip=True)
        if text and len(text) < 200:
            candidates.append((cls, text))

print('\nCANDIDATE CLASSES (class, text) sample:')
for c in candidates[:30]:
    print('-', c)

print('\nSaved HTML path:', path)
