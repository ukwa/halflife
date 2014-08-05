import urllib, re, json
from BeautifulSoup import BeautifulSoup, Comment
from readability.readability import Document
from checkurl import *


pattern = re.compile('[\W_]+')

url = "http://www.hackwriters.com/QueenandCat.htm"
url = "http://www.bbc.co.uk/news/world-asia-22039373"
# url = "http://www.bbc.co.uk/news/world-asia-22037844" # RELATED

html = urllib.urlopen(url).read()

soup = BeautifulSoup(html,convertEntities=BeautifulSoup.HTML_ENTITIES)
[ elem.extract() for elem in soup.findAll(['script', 'link', 'style']) ]

comments = soup.findAll(text=lambda text:isinstance(text, Comment))
[comment.extract() for comment in comments]

texts = [ unicode(x) for x in soup.body(text=True) ]
text =  soup.title.string + " ".join(texts)
text = re.sub(r"&amp;","&", text)
text = pattern.sub(" ",text)
text = re.sub(r"\s+"," ",text)
print(text)

fh1 = fuzzyHash(text)

print(fh1)

with open("sample-text-1.json") as data_file:
    data = json.load(data_file)

for doc in data['response']['docs']:
    item_url = doc['wct_url']
    wct_wayback_date = doc['wct_wayback_date']

    bin_hash = getBinHash(item_url, wct_wayback_date)

    title = ''
    if doc.has_key('title'):
        title = doc['title'][0]
    title = re.sub(r"\s+"," ", title)


    # Normalise whitespace:
    text = ''
    if doc.has_key('text'):
        text = doc['text'][0]
        text = pattern.sub(" ",text)
        text = re.sub(r"\s+"," ",text)

    first_fragment = text[:200]
    fh2 = fuzzyHash(text)
    print( '"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % ( doc['timestamp'], item_url, title, first_fragment, fh2, bin_hash ) )
    print(text)

    print(fuzzyHashCompare(fh1, fh2))
