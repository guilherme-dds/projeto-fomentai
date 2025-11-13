from bs4 import BeautifulSoup
import re
import urllib.parse

path = 'resultados_site_crawler/html_femic.html'
with open(path, encoding='utf-8') as f:
    s = f.read()

soup = BeautifulSoup(s, 'html.parser')

print('TITLE:', soup.title.string.strip() if soup.title and soup.title.string else None)
meta_og = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'og:title'})
print('OG_TITLE:', meta_og.get('content') if meta_og and meta_og.get('content') else None)

hs = soup.find_all(['h1','h2','h3'])
print('\nHEADINGS (first 20):')
for h in hs[:20]:
    print('-', h.get_text(separator=' ', strip=True))

# Encontrar links para PDF e candidatos a editais/regulamentos/formularios
patterns = [r'edital', r'regulamento', r'regras', r'inscri', r'documento', r'formul', r'formul[áa]rio', r'download', r'pdf', r'regra']
links = []
for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(separator=' ', strip=True)
    href_lower = href.lower()
    score = 0
    if href_lower.endswith('.pdf'):
        score += 5
    for p in patterns:
        if re.search(p, href_lower, re.IGNORECASE) or re.search(p, text, re.IGNORECASE):
            score += 3
    if score > 0:
        full = urllib.parse.urljoin('https://femic.com.br/', href)
        links.append((score, full, text))

# Ordena por score e elimina duplicatas por URL
seen = set()
links_sorted = []
for sc, u, t in sorted(links, key=lambda x: (-x[0], x[1])):
    if u not in seen:
        seen.add(u)
        links_sorted.append((sc, u, t))

print('\nCANDIDATE DOCUMENT LINKS (score, url, anchor_text) top 30:')
for item in links_sorted[:30]:
    print(item)

# Também listar PDFs mesmo que não contenham padrões
pdfs = set()
for a in soup.find_all('a', href=True):
    href = a['href']
    if href.lower().endswith('.pdf'):
        pdfs.add(urllib.parse.urljoin('https://femic.com.br/', href))

print('\nALL PDF LINKS (sample 30):')
for i,u in enumerate(sorted(pdfs)):
    if i<30:
        print('-', u)

print('\nSaved HTML path:', path)
