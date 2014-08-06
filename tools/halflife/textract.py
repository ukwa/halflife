import urllib, re, json, hashlib
from BeautifulSoup import BeautifulSoup, Comment
from readability.readability import Document
from checkurl import *


url = "http://www.hackwriters.com/QueenandCat.htm"
#url = "http://www.bbc.co.uk/news/world-asia-22039373"
#url = "http://www.bbc.co.uk/news/world-asia-22037844" # RELATED
url = "http://www.flickr.com/photos/17223773@N00/archives/date-posted/2009/12/06/"

state = checkUrl(url)
pprint(state)

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
        text = re.sub(r"\s+"," ",text)

    first_fragment = text[:200]
    fh = fuzzyHash(text)
    print( '"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % ( doc['timestamp'], item_url, title, first_fragment, fh, bin_hash ) )
    print(text)

    print(fuzzyHashCompare(state['fh'], fh))
