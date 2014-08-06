from __future__ import print_function
import json, sys, codecs, hashlib
import urllib, datetime, re
from pprint import pprint
from checkurl import *

#
#urlo = urllib.FancyURLopener({"http":"http://explorer.bl.uk:3127"})
#
urlo=urllib.URLopener()


# First, get the number of years for which we have data:
# this works by asking for a fifty year date range form 2000-2050, faceting by year, and only returning years that have results:
yq = "http://chrome.bl.uk:8080/solr/select/?q=*:*&rows=0&wt=json&indent=true&facet=true&facet.mincount=1&facet.date=timestamp&facet.date.gap=%2B1YEAR&facet.date.start=2000-01-01T00:00:00Z&facet.date.end=2050-01-01T00:00:00Z"
urlo.retrieve(yq , "total-urls-per-year.json")
# Now parse out the years:
years = list()
with open( "total-urls-per-year.json" ) as data_file:    
    data = json.load(data_file)
    for item in data['facet_counts']['facet_dates']['timestamp']:
    	if item == "gap" or item == "start" or item == "end":
    		continue
    	timestamp = datetime.datetime.strptime( item, "%Y-%m-%dT%H:%M:%SZ" )
    	years.append(timestamp.year)

# Sort them
years = sorted(years)

output_template = "sample-of-%s/sample-for-%s.csv"

# Now use the sort=random_{SEED} parameter to generate random samples:
q = "http://chrome.bl.uk:8080/solr/select/?q=*:*&rows=%s&sort=random_%s desc&wt=json&indent=true&fq=timestamp:[%s-01-01T00:00:00Z TO %s-01-01T00:00:00Z%%2B1YEAR]&fl=wct_url,wct_wayback_date,timestamp,title,text"
# Loop over samples:
for size in [100,1000]: #,10000,100000]:
    for y in years:
        with codecs.open( output_template % (size,y), "w", "utf-8") as out_file:
     	    url = q % (size,size,y,y)
    	    output = "temp.json"
    	    urlo.retrieve(url , output)

            # Now open up the JSON and process it:
            with open( "temp.json" ) as data_file:
                print("Processing year %s, sample size %s..." % ( y, size ) )
                data = json.load(data_file) 

                for doc in data['response']['docs']:
                    item_url = doc['wct_url']
                    wct_wayback_date = doc['wct_wayback_date']

                    bin_hash = getBinHash(item_url, wct_wayback_date)

                    # Normalise the title
                    title = ''
                    if doc.has_key('title'):
                        title = normaliseText(doc['title'][0])

                    # Normalise the text
                    text = ''
                    if doc.has_key('text'):
                        text = normaliseText(doc['text'][0])

                    if text != None:
                        first_fragment = text[:200]
                    fh = fuzzyHash(text)

                    print( '"%s"\t"%s"\t"%s"\t"%s"\t"%s"\t"%s"' % ( doc['timestamp'], item_url, title, first_fragment, fh, bin_hash ), file=out_file ) 

            data_file.close()
